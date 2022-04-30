import unittest
from LR_AST import LR_AST_EOP
from ParseTree import ParseTree


class MyTestCase(unittest.TestCase):
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
        parentData = "PRODUCT"
        valueName = "floatval"
        valueValue = "2.2"
        expected = "floatval:2.2"
        parent = ParseTree(parentData, None)
        parent.addChild(parentData)
        parent.addChild("TIMES")
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

    def test_PLUS_TIMES_procedure(self):
        parentData = "SUM"
        expected = "minus"
        parent = ParseTree(parentData, None)
        parent.addChild("PRODUCT")
        parent.addChild("PLUS")
        parent.getChild().addChild("minus")
        parent.addChild("PRODUCT")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)
        self.assertEqual(expected, parent.children[1].data)
        expected = "div"
        parent.children[1].data = "TIMES"
        parent.children[1].addChild("div")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)  # Parent should not have changed
        self.assertEqual(expected, parent.children[1].data)

    def test_basic_if(self):
        t = ParseTree("IF", None)
        t.addChild("if")
        t.addChild("lparen")
        t.addChild("BEXPR")
        t.addChild("rparen")
        t.addChild("STATEMENT")
        LR_AST_EOP(t)
        self.assertEqual(t.children[0].data, "IF")
        self.assertEqual(t.children[1].data, "BEXPR")
        self.assertEqual(t.children[2].data, "STATEMENT")

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



if __name__ == '__main__':
    unittest.main()
