import unittest
from LR_AST import LR_AST_EOP
from ParseTree import ParseTree

class MyTestCase(unittest.TestCase):
    def test_FUNTYPE_leaf_procedure(self):
        parentData = "PARAMLIST"
        expectedfuntype = "type:int"
        parent = ParseTree(parentData, None)
        parent.addChild("FUNTYPE")
        parent.children[0].addChild("int")
        parent.addChild("id")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)
        self.assertEqual(expectedfuntype, parent.children[0].data)

    def test_basic_if(self):
        t = ParseTree("STMT", None)
        t.addChild("IF")
        t.addChild("(")
        t.addChild("true")
        t.addChild(")")
        t.addChild("{")
        t.addChild("0")
        t.addChild("}")
        t.addChild("FI")
        LR_AST_EOP(t)
        self.assertEqual(t.children[0].data, "IF")
        self.assertEqual(t.children[1].data, "true")
        self.assertEqual(t.children[2].data, "0")


if __name__ == '__main__':
    unittest.main()
