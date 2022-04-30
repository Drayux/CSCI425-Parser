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


    def test_GLOBTYPE_leaf_procedure(self):
        parentData = "GCTDECLLIST"
        expectedfuntype = "type:const bool"
        parent = ParseTree(parentData, None)
        parent.addChild("GLOBTYPE")
        parent.children[0].addChild("const bool")
        parent.addChild("DECLIDS")
        LR_AST_EOP(parent)
        self.assertEqual(parentData, parent.data)
        self.assertEqual(expectedfuntype, parent.children[0].data)


if __name__ == '__main__':
    unittest.main()
