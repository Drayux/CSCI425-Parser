import unittest

import LR_AST
from LR_AST import LR_AST_EOP
from ParseTree import ParseTree


class ASTTestCase(unittest.TestCase):
    def test_FUNTYPE_leaf_procedure(self):
        parentData = "PARAMLIST"
        expected = "type:int"
        parent = ParseTree(parentData, None)
        parent.addChild("FUNTYPE")
        parent.children[0].addChild("int")
        parent.addChild("id")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual(expected, parent.children[0].data)

    def test_GLOBTYPE_leaf_procedure(self):
        parentData = "GCTDECLLIST"
        expected = "type:const bool"
        parent = ParseTree(parentData, None)
        parent.addChild("GLOBTYPE")
        parent.children[0].addChild("const bool")
        parent.addChild("DECLIDS")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual(expected, parent.children[0].data)

    def test_leaf_procedure(self):
        parentData = "DECLID"
        variableName = "eldenRing"
        expected = "id:" + variableName
        parent = ParseTree(parentData, None)
        parent.addChild("id")
        parent.getChild().aux = variableName
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual(expected, parent.getChild().data)
        parentData = "VALUE"
        valueName = "floatval"
        valueValue = "2.2"
        expected = "floatval:2.2"
        parent.data = parentData
        parent.children.pop()
        parent.addChild(valueName)
        parent.getChild().aux = valueValue
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual(expected, parent.getChild().data)

    def test_VALUE_procedure(self):
        # PRODUCT -> VALUE -> "floatval:2.2" : PRODUCT -> "floatval:2.2"
        parentData = "PRODUCT"
        valueName = "floatval"
        valueValue = "2.2"
        expected = "floatval:2.2"
        parent = ParseTree(parentData, None)
        parent.addChild(parentData)
        parent.addChild("TIMES")
        parent.getChild().addChild("mult")
        parent.addChild("VALUE")
        parent.getChild().addChild(valueName + ":" + valueValue)
        parent.getChild().getChild().aux = valueValue
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual(expected, parent.getChild().data)
        valueName = "stringval"
        valueValue = "Hello There"
        expected = "stringval:Hello There"
        parent.removeChild(parent.getChild())
        parent.addChild("VALUE")
        parent.getChild().addChild(valueName + ":" + valueValue)
        parent.getChild().getChild().aux = valueValue
        parent.getChild().aux = valueValue
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual(expected, parent.getChild().data)
        # PRODUCT -> VALUE -> lparen EXPR rparen : PRODUCT -> EXPR
        parent.removeChild(parent.getChild())
        parent.addChild("VALUE")
        VALUE = parent.getChild()
        VALUE.addChild("lparen")
        VALUE.addChild("+")
        VALUE.getChild().addChild("3")
        VALUE.getChild().addChild("4")
        VALUE.addChild("rparen")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual("+", parent.getChild().data)  # the only child should be the EXPR
        self.assertEqual("3", parent.getChild().children[0].data)  # The EXPR should have saved its children
        self.assertEqual("4", parent.getChild().children[1].data)  # Same here

    def test_PLUS_TIMES_procedure(self):
        parentData = "SUM"
        expected = "-"
        parent = ParseTree(parentData, None)
        parent.addChild("PRODUCT")
        parent.addChild("PLUS")
        parent.getChild().addChild("minus")
        parent.addChild("PRODUCT")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)
        self.assertEqual(expected, parent.children[1].data)
        expected = "/"
        parent.children[1].data = "TIMES"
        parent.children[1].addChild("div")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual(expected, parent.children[1].data)

    def test_basic_if(self):
        # I developed this test to look like the right of expr-3.pdf
        parent = ParseTree("STATEMENT", None)
        t = ParseTree("IF", None)
        t.addChild("if")
        t.addChild("lparen")
        t.addChild("BEXPR")
        BEXPR = t.getChild()
        BEXPR.addChild("int")
        BEXPR.getChild().addChild("id:tampa")
        BEXPR.addChild("==")
        BEXPR.addChild("intval:1")
        t.addChild("rparen")
        t.addChild("STATEMENT")
        parent.addChild(t)
        LR_AST_EOP(t)
        LR_AST_EOP(parent)
        self.assertEqual("IF", t.data)
        self.assertEqual("==", t.children[0].data)
        self.assertEqual("int", t.children[0].children[0].data)
        self.assertEqual("id:tampa", t.children[0].children[0].getChild().data)
        self.assertEqual("intval:1", t.children[0].children[1].data)
        self.assertEqual("STATEMENT", t.children[1].data)

    def test_UNARY_procedure(self):
        # VALUE -> UNARY -> not id:gogogo : VALUE -> ! -> id:gogogo
        parentData = "VALUE"
        childData = "UNARY"
        childChildData = "not"
        childchild2Data = "id:gogogo"
        parent = ParseTree(parentData, None)
        parent.addChild(childData)
        UNARY = parent.getChild()
        UNARY.addChild(childChildData)
        UNARY.addChild("VALUE")
        UNARY.getChild().addChild(childchild2Data)
        LR_AST_EOP(UNARY)
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual("!", parent.getChild().data)  # first child should be "!"
        self.assertEqual(childchild2Data, parent.getChild().getChild().data) # after "!" should be the val/var
        # VALUE -> UNARY -> minus id:gogogo : VALUE -> - -> id:gogogo
        childChildData = "-"
        parent.removeChild(parent.getChild())
        parent.addChild(childData)
        UNARY = parent.getChild()
        UNARY.addChild(childChildData)
        UNARY.addChild("VALUE")
        UNARY.getChild().addChild(childchild2Data)
        LR_AST_EOP(UNARY)
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual("-", parent.getChild().data)  # first child should be "-"
        self.assertEqual(childchild2Data, parent.getChild().getChild().data) # after "-" should be the val/var

    def test_SUM_procedure(self):
        # AEXPR -> SUM -> firsty + secondy : AEXPR -> + -> firsty secondy
        parentData = "AEXPR"
        parent = ParseTree(parentData, None)
        parent.addChild("SUM")
        SUM = parent.getChild()
        SUM.addChild("id:firsty")
        SUM.addChild("+")
        SUM.addChild("id:secondy")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual("+", parent.getChild().data)
        self.assertEqual("id:firsty", parent.getChild().children[0].data)
        self.assertEqual("id:secondy", parent.getChild().children[1].data)
        # AEXPR -> SUM -> intval:321 : AEXPR -> intval:321
        parent = ParseTree(parentData, None)
        parent.addChild("SUM")
        SUM = parent.getChild()
        SUM.addChild("intval:321")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual("intval:321", parent.getChild().data)
        self.assertEqual(0, len(parent.getChild().children))

    def test_PRODUCT_procedure(self):
        # AEXPR -> SUM -> firsty + secondy : AEXPR -> + -> firsty secondy
        parentData = "AEXPR"
        parent = ParseTree(parentData, None)
        parent.addChild("PRODUCT")
        SUM = parent.getChild()
        SUM.addChild("id:firsty")
        SUM.addChild("*")
        SUM.addChild("id:secondy")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual("*", parent.getChild().data)
        self.assertEqual("id:firsty", parent.getChild().children[0].data)
        self.assertEqual("id:secondy", parent.getChild().children[1].data)
        # AEXPR -> SUM -> intval:321 : AEXPR -> intval:321
        parent = ParseTree(parentData, None)
        parent.addChild("PRODUCT")
        SUM = parent.getChild()
        SUM.addChild("id:PizzaTime")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual("id:PizzaTime", parent.getChild().data)
        self.assertEqual(0, len(parent.getChild().children))

    def test_FUNCALL(self):
        parentData = "EXPR"
        functionId = "id:functionName"
        parent = ParseTree(parentData, None)
        parent.addChild("FUNCALL")
        FUNCALL = parent.getChild()
        FUNCALL.addChild(functionId)
        FUNCALL.addChild("lparen")
        FUNCALL.addChild("ARGLIST")
        FUNCALL.addChild("rparen")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual(2, len(parent.getChild().children))
        self.assertEqual(functionId, parent.getChild().children[0].data)
        self.assertEqual("ARGLIST", parent.getChild().getChild().data)

    def test_AEXPR_procedure(self):
        parentData = "EXPR"
        parent = ParseTree(parentData, None)
        parent.addChild("AEXPR")
        AEXPR = parent.getChild()
        AEXPR.addChild("+")
        AEXPR.getChild().addChild("3")
        AEXPR.getChild().addChild("4")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual(1, len(parent.children))
        self.assertEqual("+", parent.getChild().data)
        self.assertEqual("3", parent.getChild().children[0].data)
        self.assertEqual("4", parent.getChild().children[1].data)

    def test_BEXPR_BOOLS_procedure(self):
        BOOLS = ParseTree("BOOLS", None)
        BOOLS.addChild("lt")
        LR_AST.LR_AST_SDT_Procedure(BOOLS)
        self.assertEqual("<", BOOLS.data)
        BOOLS = ParseTree("BOOLS", None)
        BOOLS.addChild("leq")
        LR_AST.LR_AST_SDT_Procedure(BOOLS)
        self.assertEqual("<=", BOOLS.data)
        BOOLS = ParseTree("BOOLS", None)
        BOOLS.addChild("eq")
        LR_AST.LR_AST_SDT_Procedure(BOOLS)
        self.assertEqual("==", BOOLS.data)
        BOOLS = ParseTree("BOOLS", None)
        BOOLS.addChild("geq")
        LR_AST.LR_AST_SDT_Procedure(BOOLS)
        self.assertEqual(">=", BOOLS.data)
        BOOLS = ParseTree("BOOLS", None)
        BOOLS.addChild("gt")
        LR_AST.LR_AST_SDT_Procedure(BOOLS)
        self.assertEqual(">", BOOLS.data)
        parentData = "EXPR"
        firstExpr = "id:varName"
        secondExpr = "intval:10"
        boolExpr = "=="
        parent = ParseTree(parentData, None)
        parent.addChild("BEXPR")
        BEXPR = parent.getChild()
        BEXPR.addChild("AEXPR")
        BEXPR.getChild().addChild(firstExpr)
        BEXPR.addChild("BOOLS")
        BEXPR.getChild().addChild("eq")
        BEXPR.addChild("AEXPR")
        BEXPR.getChild().addChild(secondExpr)
        LR_AST_EOP(BEXPR)
        self.assertEqual("BEXPR", BEXPR.data)
        self.assertEqual(firstExpr, BEXPR.children[0].data)
        self.assertEqual(boolExpr, BEXPR.children[1].data)
        self.assertEqual(secondExpr, BEXPR.children[2].data)
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual("==", parent.getChild().data)
        self.assertEqual(firstExpr, parent.getChild().children[0].data)
        self.assertEqual(secondExpr, parent.getChild().children[1].data)

    def test_CASTR_procedure(self):
        parentData = "VALUE"
        castType = "bool"
        exprVal = "id:tampa"
        parent = ParseTree(parentData, None)
        parent.addChild("CAST")
        CAST = parent.getChild()
        CAST.addChild(castType)
        CAST.addChild("lparen")
        CAST.addChild(exprVal)
        CAST.addChild("rparen")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)
        self.assertEqual(castType, parent.getChild().data)
        self.assertEqual(exprVal, parent.getChild().getChild().data)

    def test_while_procedure(self):
        # From litteralrabbits
        t = ParseTree("STATEMENT", None)
        t.addChild("WHILE")
        t.getChild().addChild("while")
        t.getChild().addChild("lparen")
        t.getChild().addChild("BEXPR")
        t.getChild().addChild("rparen")
        t.getChild().addChild("STATEMENT")
        t.getChild().children[2].addChild("AEXPR")
        t.getChild().children[2].addChild("BOOLS")
        t.getChild().children[2].children[1].addChild("lt")
        t.getChild().children[2].addChild("AEXPR")
        LR_AST_EOP(t)
        self.assertEqual("STATEMENT", t.data)
        self.assertEqual("WHILE", t.getChild().data)
        self.assertIn(t.getChild().children[0].data, [ "lt", "BEXPR"] )  # Depends on if BEXPR gets simplified via SDT or not
        self.assertEqual("STATEMENT", t.getChild().children[1].data)

    def test_STMTS_procedure(self):
        # I am basing this off expr-1
        # We will test three levels of STMT calls
        grandParentData = "BRACESTMTS"
        parentData = "STMTS"
        halflife = "lambda"
        STATEMENT1 = "STATEMENT1"
        STATEMENT2 = "STATEMENT2"
        STATEMENT3 = "STATEMENT3"
        grandParent = ParseTree(grandParentData, None)
        top_STMTS = ParseTree(parentData, None)
        upper_mid_STMTS = ParseTree(parentData, None)
        mid_STMTS = ParseTree(parentData, None)
        bot_STMTS = ParseTree(parentData, None)
        # Building the tree from the bottom, have bot_STMT run SDT on lambda
        # We expect no result form this
        bot_STMTS.addChild("lambda")
        LR_AST_EOP(bot_STMTS)
        self.assertEqual(parentData, bot_STMTS.data)
        self.assertEqual(halflife, bot_STMTS.getChild().data)
        # In the LR parser, we are going to make the mid_STMT
        # We expect bot_STMTS to be replaced with lambda
        mid_STMTS.addChild(bot_STMTS)
        mid_STMTS.addChild(STATEMENT1)
        mid_STMTS.getChild().addChild("id:mrfreeman")  # I put this in here to check if this survives
        LR_AST_EOP(mid_STMTS)
        self.assertEqual(parentData, mid_STMTS.data)
        self.assertEqual(halflife, mid_STMTS.children[0].data)
        self.assertEqual(STATEMENT1, mid_STMTS.children[1].data)
        self.assertEqual(2, len(mid_STMTS.children))
        # We add a third layer, upper_mid
        # We expect mid_STMT to have only STATEMENT1 child
        upper_mid_STMTS.addChild(mid_STMTS)
        upper_mid_STMTS.addChild(STATEMENT2)
        LR_AST_EOP(upper_mid_STMTS)
        self.assertEqual(parentData, upper_mid_STMTS.data)
        self.assertEqual(parentData, upper_mid_STMTS.children[0].data)
        self.assertEqual(STATEMENT1, upper_mid_STMTS.children[0].getChild().data)
        self.assertEqual(STATEMENT2, upper_mid_STMTS.getChild().data)
        # We now load the top_STMT, and after EOP of top, mid will kill lambda
        top_STMTS.addChild(upper_mid_STMTS)
        top_STMTS.addChild(STATEMENT3)
        top_STMTS.getChild().addChild("id:ALYX")
        LR_AST_EOP(top_STMTS)
        self.assertEqual(parentData, top_STMTS.data)
        self.assertEqual(parentData, top_STMTS.children[0].data)
        self.assertEqual(2, len(top_STMTS.children[0].children))
        self.assertEqual(STATEMENT1, top_STMTS.children[0].children[0].data)
        self.assertEqual(STATEMENT2, top_STMTS.children[0].children[1].data)
        self.assertEqual(STATEMENT3, top_STMTS.getChild().data)
        # Now for grandad. Once top runs through the SDT, it should opnly have statement children
        grandParent.addChild(top_STMTS)
        LR_AST_EOP(grandParent)
        top_STMTS = grandParent.getChild()
        self.assertEqual(grandParentData, grandParent.data)
        self.assertEqual(parentData, top_STMTS.data)
        self.assertEqual(3, len(top_STMTS.children))
        self.assertEqual(STATEMENT1, top_STMTS.children[0].data)
        self.assertEqual(STATEMENT2, top_STMTS.children[1].data)
        self.assertEqual(STATEMENT3, top_STMTS.getChild().data)

    def test_IFELSE_procedure(self):
        t = ParseTree("STATEMENT", None)
        t.addChild("IFELSE")
        t.getChild().addChild("if")
        t.getChild().addChild("lparen")
        t.getChild().addChild("BEXPR")
        t.getChild().children[2].addChild("AEXPR")
        t.getChild().children[2].addChild("BOOLS")
        t.getChild().children[2].addChild("AEXPR")
        t.getChild().addChild("rparen")
        t.getChild().addChild("BRACESTMTS")
        t.getChild().addChild("else")
        t.getChild().addChild("STATEMENT")
        LR_AST_EOP(t)
        self.assertEqual(len(t.getChild().children), 3)
        self.assertEqual(t.getChild().children[0].data, "BEXPR")
        self.assertEqual(t.getChild().children[1].data, "BRACESTMTS")
        self.assertEqual(t.getChild().children[2].data, "STATEMENT")

    def test_STMTS_procedure(self):
        t = ParseTree("FUNCTION", None)
        t.addChild("FUNSIG")
        t.addChild("=")
        t.addChild("BRACESTMTS")
        t.children[2].addChild("lbrace")
        t.children[2].addChild("STMTS")
        t.children[2].children[1].addChild("STATEMENT")
        t.children[2].addChild("rbrace")
        LR_AST_EOP(t)
        self.assertEqual(len(t.getChild().children), 3)
        self.assertEqual(t.getChild().data, "BRACESTMTS")
        self.assertEqual(t.getChild().children[0].data, "scope:open")
        self.assertEqual(t.getChild().children[1].data, "STMTS")
        self.assertEqual(t.getChild().children[2].data, "scope:close")
        self.assertEqual(t.getChild().children[1].getChild().data, "STATEMENT")


if __name__ == '__main__':
    unittest.main()
