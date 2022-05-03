# https://cs.mcprogramming.com/static/comp/hr/361f1520c2d31b0d/show_symbols-and-names.pdf
# Design choices:
# - Stack of tables, not using hash table implementation
# - No string interning

class SymbolAttributes():
    def __init__(self, type):  # todo: more attributes
        self.type = type

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
        self.tableStack = []

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
                return table

    def DeclaredLocally(self, name):
        pass

    def EmitTable(self, output):
        for (i, table) in enumerate(reversed(self.tableStack)):
            for sym in table.table:
                output.write(str(i) + "," + sym[1].type + "," + sym[0] + "\n")