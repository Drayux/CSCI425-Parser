# https://cs.mcprogramming.com/static/comp/hr/361f1520c2d31b0d/show_symbols-and-names.pdf
# Design choices:
# - Stack of tables, not using hash table implementation
# - No string interning

#from tkinter import W
import sys
from ParseTree import ParseTree

def remove_prefix(node, prefix):
    if node.data.startswith(prefix):
        if len(node.data) > len(prefix):
            return node.data[len(prefix):]
        print(f"Node: {node.data} has no data after prefix: {prefix}")
        return ""
    print(f"Unexpected Prefix on Node: {node.data}, expected prefix: {prefix}")
    return ""

def verify_node(node, expected_data):
    if node.data != expected_data:
        print(f"Expected node: {expected_data}, found node: {node.data}")
    return node

class SymbolAttributes():
    def __init__(self, type, cons):  # todo: more attributes
        self.type = type
        self.cons = cons

class TableScope():
    def __init__(self):
        self.table = {}

    def SearchSymbol(self, name):
        if name in self.table:
            return self.table[name]
        else:
            return None

    def AddSymbol(self, name, attributes):
        assert name not in self.table
        self.table[name] = (name, attributes)

class SymbolTable():
    def __init__(self):
        self.tableStack = [TableScope()]

    def OpenScope(self):
        self.tableStack.insert(0, TableScope())

    def CloseScope(self):
        self.tableStack.pop(0)

    def EnterSymbol(self, name, attributes):
        self.tableStack[0].AddSymbol(name, attributes)

    def RetrieveSymbol(self, name):
        for (i, table) in enumerate(self.tableStack):
            val = table.SearchSymbol(name)
            if val != None:
                return table.table[name]

    def ReportError(self, id, r, c):
        if id in ["UNINIT", "REIDENT"]:
            sys.stdout.write(f":WARN: {r} {c} :{id}:\n")
        elif id in ["CALL"]:
            sys.stdout.write(f":ERROR: {r} {c} :{id}:\n")
        elif id in ["SYNTAX"]:
            sys.stdout.write(f":SYNTAX: {r} {c} :{id}:\n")

    def DeclaredLocally(self, name):
        pass

    def EmitTable(self, output):
        for (i, table) in enumerate(reversed(self.tableStack)):
            for key in table.table:
                (name, attr) = table.table[key]
                typ = attr.type
                if attr.cons:
                    typ = "const " + typ
                output.write(str(i) + "," + typ + "," + name + "\n")

    def populate_from_ast(self, node):
        #####################
        # Function Node
        #####################
        if node.data == "FUNCTION":
            r_typ = "" 
            f_typ = ""  
            r_id = "" 
            f_id = ""
            params = []
            # Get return type and function name from FUNSIG node
            fnsig_node = verify_node(node.children[0], "FUNSIG")
            r_typ = remove_prefix(fnsig_node.children[0], "type:")
            f_id = remove_prefix(fnsig_node.children[1], "id:")
            # Get fn parameters from PARAMLIST node
            pl_node = verify_node(fnsig_node.children[2], "PARAMLIST")
            for child in pl_node.children:
                # Get individual fn parameter from a PARAM node
                param_node = verify_node(child, "PARAM")
                p_typ = remove_prefix(param_node.children[0], "type:")
                p_id = remove_prefix(param_node.children[1], "id:")
                params.append((p_typ, p_id))
            # Get return var name from = node
            eq_node = verify_node(node.children[1], "=")
            r_id = remove_prefix(eq_node.children[0], "id:")
            # Add fn entry to SymbolTable
            # NOTE: f_typ has format: return_type//param1_type/param2type/.../paramlast_type
            f_typ = r_typ + "//"
            if params:
                (p_typ, _) = params[0]
                f_typ = f_typ + p_typ 
            for (p_typ, _) in params[1:]:
                f_typ = f_typ + "/" + p_typ     
            self.EnterSymbol(f_id, SymbolAttributes(f_typ, True))
            # Recursively populate using body of fn from BRACESTMTS node
            brc_node = verify_node(node.children[2], "BRACESTMTS")
            self.OpenScope()
            for (p_typ, p_id) in params:
                self.EnterSymbol(p_id, SymbolAttributes(p_typ, True))
            self.EnterSymbol(r_id, SymbolAttributes(r_typ, False))
            stmts_node = verify_node(brc_node.children[1], "STMTS")
            self.populate_from_ast(stmts_node)
            self.CloseScope()
            return
        #########################
        # Declist Node
        #########################
        if node.data == "DECLIST":
            d_typ = remove_prefix(node.children[0], "type:")
            for child in node.children[1:]:
                dec_node = verify_node(child, "DECLID")
                eq_node = verify_node(dec_node.children[0], "=")
                d_id = remove_prefix(eq_node.children[0], "id:")
                self.EnterSymbol(d_id, SymbolAttributes(d_typ, False))  # TODO: support const
            return
        #####################################
        # Funsig Node (undefined functions)
        #####################################
        if node.data == "FUNSIG":
            params = []
            fnsig_node = verify_node(node, "FUNSIG")
            r_typ = remove_prefix(fnsig_node.children[0], "type:")
            f_id = remove_prefix(fnsig_node.children[1], "id:")
            # Get fn parameters from PARAMLIST node
            pl_node = verify_node(fnsig_node.children[2], "PARAMLIST")
            for child in pl_node.children:
                # Get individual fn parameter from a PARAM node
                param_node = verify_node(child, "PARAM")
                p_typ = remove_prefix(param_node.children[0], "type:")
                p_id = remove_prefix(param_node.children[1], "id:")
                params.append((p_typ, p_id))
            # Add fn entry to SymbolTable
            # NOTE: f_typ has format: return_type//param1_type/param2type/.../paramlast_type
            f_typ = r_typ + "//"
            if params:
                (p_typ, _) = params[0]
                f_typ = f_typ + p_typ 
            for (p_typ, _) in params[1:]:
                f_typ = f_typ + "/" + p_typ     
            self.EnterSymbol(f_id, SymbolAttributes(f_typ, True))
        #########################
        # Funcall Nodes
        #########################
        if node.data == "FUNCALL":
            # collect ast data
            f_id = remove_prefix(node.children[0], "id:")
            args_node = verify_node(node.children[1], "ARGLIST")
            arg_count = len(args_node.children)
            # evaluate args
            for arg in args_node.children:
                self.populate_from_ast(arg)
            # check that fn id maps to fn 
            entry = self.RetrieveSymbol(f_id)
            if not entry:
                self.ReportError("CALL", 0, 0)  # TODO: support row/column
                return
            (_, attr) = entry
            # check that number of passed args matches expected
            pars = attr.type.split("//")[1]
            par_count = len(pars.split("/")) 
            if arg_count != par_count:
                self.ReportError("CALL", 0, 0)  # TODO: support row/column
        #########################
        # Scope Nodes
        #########################
        if node.data == "scope:open":
            self.OpenScope()
        if node.data == "scope:close":
            self.CloseScope()
        #########################
        # Emit Node
        #########################
        if node.data == "EMIT":
            self.EmitTable(sys.stdout)
        #########################
        # Default Node
        #########################
        for child in node.children:
            self.populate_from_ast(child)

            
# Testing for AST
def testST():
    st = SymbolTable();
    assert (len(st.tableStack) == 1)
    st.OpenScope();
    assert (len(st.tableStack) == 2)
    st.EnterSymbol("tmp", SymbolAttributes("int", False)) 
    (_, attr) = st.RetrieveSymbol("tmp")
    assert (attr.type == "int")
    print("Symbol Table Tests Pass!")

def testPopulate():
    root = ParseTree("MODULE", None)
    declist1 = ParseTree("DECLIST", root)
    declist1.addChild(ParseTree("type:string", declist1))
    declid1_1 = ParseTree("DECLID", declist1)
    eq1 = ParseTree("=", declid1_1)
    eq1.addChild(ParseTree("id:m", eq1))
    eq1.addChild(ParseTree("stringval:helloworld", eq1))
    declid1_1.addChild(eq1)
    declist1.addChild(declid1_1)
    root.addChild(declist1)
    root.addChild(ParseTree("EMIT", root))
    st = SymbolTable();
    st.populate_from_ast(root)
    (_, attr) = st.tableStack[0].table["m"] 
    #print(f"type: {typ}")
    assert (attr.type == "string")
    print("Populate from AST Tests Pass!")

def testPopulateFn():
    # Root Node
    root = ParseTree("MODULE", None)
    # Func Node
    func = ParseTree("FUNCTION", root)
    # Func Signature Node
    fnsg = ParseTree("FUNSIG", func)
    fnsg.addChild(ParseTree("type:int", fnsg))
    fnsg.addChild(ParseTree("id:main", fnsg))
    # Parameter List Node
    plst = ParseTree("PARAMLIST", fnsg)
    # Parameter Node
    parm = ParseTree("PARAM", plst)
    parm.addChild(ParseTree("type:int", parm))
    parm.addChild(ParseTree("id:x", parm))
    plst.addChild(parm)
    fnsg.addChild(plst)
    func.addChild(fnsg)
    # Default Return Node
    eq   = ParseTree("=", func)
    eq.addChild(ParseTree("id:r", eq))
    func.addChild(eq)
    # Brace Statements Node
    brst = ParseTree("BRACESTMTS", func)
    brst.addChild(ParseTree("scope:open", brst))
    # Statements Node
    stms = ParseTree("STMTS", brst)
    stms.addChild(ParseTree("EMIT", stms))
    brst.addChild(stms)
    brst.addChild(ParseTree("scope:close", brst))
    func.addChild(brst)
    root.addChild(func)
    st = SymbolTable()
    st.populate_from_ast(root)
    (_, attr) = st.tableStack[0].table["main"]  
    assert (attr.type == "int//int")
    print("Populate from AST with Fn Tests Pass!")

def testErrorCall():
    # Root Node
    root = ParseTree("Module", None)
    # Funsig Node (undefined func)
    fnsg = ParseTree("FUNSIG", root)
    fnsg.addChild(ParseTree("type:int", fnsg))
    fnsg.addChild(ParseTree("id:main", fnsg))
    # Parameter List Node
    plst = ParseTree("PARAMLIST", fnsg)
    # Parameter Node
    parm = ParseTree("PARAM", plst)
    parm.addChild(ParseTree("type:int", parm))
    parm.addChild(ParseTree("id:x", parm))
    plst.addChild(parm)
    fnsg.addChild(plst)
    root.addChild(fnsg)
    # Function Call Node
    fnc1 = ParseTree("FUNCALL", root)
    fnc1.addChild(ParseTree("id:a", fnc1))
    fnc1.addChild(ParseTree("ARGLIST", fnc1))
    root.addChild(fnc1)
    # Function Call Node
    fnc2 = ParseTree("FUNCALL", root)
    fnc2.addChild(ParseTree("id:main", fnc2))
    # Arg List Node
    args = ParseTree("ARGLIST", fnc2)
    args.addChild(ParseTree("id:a", args))
    args.addChild(ParseTree("id:b", args))
    fnc2.addChild(args)
    root.addChild(fnc2)
    st = SymbolTable()
    print("Expecting 2 Call Errors:")
    st.populate_from_ast(root)
    print("Call Error Tests Pass!")


if __name__ == "__main__":
    testST()
    testPopulate()
    testPopulateFn()
    testErrorCall()