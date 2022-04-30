import sys

from ParseTree import ParseTree

LAMBDA = "lambda"
charLAMBDA = "_lambda"


def RootReplace(node: ParseTree, data, children):
    node.data = data
    node.children = children


def replace_node_with_new_node(node: ParseTree, new_node: ParseTree):
    RootReplace(node, new_node.data, new_node.children)
    return


def semantic_Check(node: ParseTree):
    if node.data == "range":
        lowerCase = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                     "u", "v", "w", "x", "y", "z"]
        upperCase = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                     "U", "V", "W", "X", "Y", "Z"]
        numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        lefty = node.children[0].data
        righty = node.children[1].data
        if all(x in lowerCase for x in [lefty, righty]) or \
                all(x in upperCase for x in [lefty, righty]) or \
                all(x in numbers for x in [lefty, righty]):
            pass
        else:
            print("SEMANTIC ERROR: the two values are of different cases or types")
            sys.exit(3)
        if lefty > righty:
            print("SEMANTIC ERROR: Left value is greater than right value in range")
            sys.exit(3)


def procedure_FUNTYPE(node: ParseTree):
    childData = "type:"+node.children[0].data
    newNode = ParseTree(childData, None)
    replace_node_with_new_node(node, newNode)

def procedure_id(node: ParseTree):
    node.data = node.data + ":" + node.aux

def LR_AST_SDT_Procedure(node: ParseTree):
    """
    This will transform the node to its AST counterpart using the correct SDT
    :param node:
    :return: None / Transformation
    """
    if node.data == "FUNTYPE":
        procedure_FUNTYPE(node)
    elif node.data == "id":
        procedure_id(node)


def LR_AST_EOP(node: ParseTree):
    """
    Perform SDTs on each child of the given node.

    Since LR parsing has issues with ASTs, we have the children of the current parent node change into an AST
    :param node: ParseTree
    :return: None / Transformation of children
    """
    for child in node.children:
        LR_AST_SDT_Procedure(child)
