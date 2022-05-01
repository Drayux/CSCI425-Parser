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
        childData = node.getChild().data
        if childData == "plus": node.getChild().data = "+"
        if childData == "minus": node.getChild().data = "-"
        if childData == "mult": node.getChild().data = "*"
        if childData == "div": node.getChild().data = "/"
        if childData == "mod": node.getChild().data = "%"
        replace_node_with_new_node(node, node.getChild())
    elif node.getChild().data == "rparen":
        replace_node_with_new_node(node, node.children[1])


def procedure_IF(node: ParseTree):
    assert (len(node.children) > 3)
    assert (node.children[0].data == "if")
    assert (node.children[1].data == "lparen")
    assert (node.children[3].data == "rparen")

    node.removeChild(node.children[3])  # Remove rparen
    node.removeChild(node.children[1])  # Remove lparen
    node.removeChild(node.children[0])  # Remove if
    # i = len(node.children) - 1
    # while i > 0:  # Skip if
    #     n = node.children[i]
    #     # Move the node down as a child of the if
    #     node.removeChild(n)
    #     node.children[0].addChild(n)
    #     i -= 1


def procedure_WHILE(node: ParseTree):
    assert (len(node.children) > 4)
    assert (node.children[0].data == "while")
    assert (node.children[1].data == "lparen")
    assert (node.children[3].data == "rparen")
    node.removeChild(node.children[3])  # Remove rparen
    node.removeChild(node.children[1])  # Remove lparen
    node.removeChild(node.children[0])  # Remove while


def procedure_UNARY(node: ParseTree):
    operater = node.children[0]
    if operater.data == "not":
        operater.data = "!"
    if operater.data == "compl":
        operater.data = "~"
    operaterData = operater.data
    node.removeChild(operater)
    node.data = operaterData


def procedure_BINARY(node: ParseTree):
    if len(node.children) == 3:
        node.data = node.children[1].data
        node.removeChild(node.children[1])
    if len(node.children) == 1:
        replace_node_with_new_node(node, node.getChild())


def procedure_FUNCALL(node: ParseTree):
    node.removeChild(node.getChild())  # Removes rparen
    node.removeChild(node.children[1])  # Removes lparen


def procedure_BOOLS(node: ParseTree):
    childData = node.getChild().data
    if childData == "lt":
        node.getChild().data = "<"
    elif childData == "leq":
        node.getChild().data = "<="
    elif childData == "eq":
        node.getChild().data = "=="
    elif childData == "geq":
        node.getChild().data = ">="
    elif childData == "gt":
        node.getChild().data = ">"
    replace_node_with_new_node(node, node.getChild())


def procedure_CAST(node: ParseTree):
    node.data = node.children[0].data  # Takes the casting
    node.removeChild(node.getChild())  # removes rparen
    node.removeChild(node.children[0])  # removes lparen


def procedure_STMTS(node: ParseTree):
    if len(node.children) == 1:
        if node.getChild().data == "lambda":
            replace_node_with_new_node(node, node.getChild())
    else:
        if node.children[0].data == "lambda":
            node.removeChild(node.children[0])
            return
        firstChild = node.children[0]
        for child in firstChild.children:
            node.children.insert(0, child)
        node.removeChild(firstChild)



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
    elif node.data == "IF":
        procedure_IF(node)
    elif node.data == "WHILE":
        procedure_WHILE(node)
    elif node.data == "UNARY":
        procedure_UNARY(node)
    elif node.data == "SUM" or \
            node.data == "PRODUCT" or \
            node.data == "AEXPR" or \
            node.data == "BEXPR":
        procedure_BINARY(node)
    elif node.data == "FUNCALL":
        procedure_FUNCALL(node)
    elif node.data == "BOOLS":
        procedure_BOOLS(node)
    elif node.data == "CAST":
        procedure_CAST(node)
    elif node.data == "STMTS":
        procedure_STMTS(node)


def LR_AST_EOP(node: ParseTree):
    """
    Perform SDTs on each child of the given node.

    Since LR parsing has issues with ASTs, we have the children of the current parent node change into an AST
    :param node: ParseTree
    :return: None / Transformation of children
    """
    for child in node.children:
        LR_AST_SDT_Procedure(child)
