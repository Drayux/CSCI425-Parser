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


def procedure_FUNTYPE(node: ParseTree):
    childData = "type:" + node.children[0].data
    newNode = ParseTree(childData, None)
    replace_node_with_new_node(node, newNode)


def procedure_leaf(node: ParseTree):
    node.data = node.data + ":" + node.aux


def procedure_VALUE(node: ParseTree):
    if len(node.children) == 1:
        replace_node_with_new_node(node, node.getChild())


def LR_AST_SDT_Procedure(node: ParseTree):
    """
    This will transform the node to its AST counterpart using the correct SDT
    :param node:
    :return: None / Transformation
    """
    if node.data == "FUNTYPE":
        procedure_FUNTYPE(node)
    elif node.data == "GLOBTYPE":
        procedure_FUNTYPE(node)
    elif node.data == "id" or \
            node.data == "intval" or \
            node.data == "floatval" or \
            node.data == "stringval":
        procedure_leaf(node)
    elif node.data == "VALUE":
        procedure_VALUE(node)
    elif node.data == "PLUS" or \
            node.data == "TIMES":
        procedure_VALUE(node)


def LR_AST_EOP(node: ParseTree):
    """
    Perform SDTs on each child of the given node.

    Since LR parsing has issues with ASTs, we have the children of the current parent node change into an AST
    :param node: ParseTree
    :return: None / Transformation of children
    """
    for child in node.children:
        LR_AST_SDT_Procedure(child)
