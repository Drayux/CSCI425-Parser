from ParseTree import ParseTree

LAMBDA = "lambda"

def RootReplace(node: ParseTree, data, children):
    node.data=data
    node.children = children

def replace_node_with_new_node(node: ParseTree, new_node: ParseTree):
    if node.parent is None:
        RootReplace(node, new_node.data, new_node.children)
        return
    for i in range(len(node.parent.children)):
        if node.parent.children[i] == node:
            node.parent.children[i] = new_node

def procedure_NUCLEUS(node: ParseTree):
    if node.children[0].data == "open":
        replace_node_with_new_node(node, node.children[1])
        return
    if node.children[0].data == "dot":
        replace_node_with_new_node(node, node.children[0])
        return
    for child in node.children:
        if child.data == "CHARRNG":
            if child.children[0].data == "lambda":
                node.removeChild(child)
                return
            else:
                rangeNode = ParseTree("range", node.parent)
                rangeNode.addChild(node.children[0])
                rangeNode.addChild(child.children[1])
                for forsakenChild in node.children:
                    node.children.pop()
                if len(node.children) == 1:
                    replace_node_with_new_node(node.children[0], rangeNode)
                else:
                    node.addChild(rangeNode)
                return


# Rule 9
def procedure_ATOM(node):
    for child in node.children:
        if child.data == "ATOMMOD":
            # Rule 12
            if child.children[0].data == LAMBDA:
                replace_node_with_new_node(node, node.children[0].children[0])
                return
            # Rule 11, Rule 10
            else:
                newAtom = ParseTree(child.children[0].data, node.parent)
                newAtom.addChild(node.children[0].children[0])
                replace_node_with_new_node(node, newAtom)


def AST_SDT_Procedure(node: ParseTree):
    if node.data == "NUCLEUS":
        procedure_NUCLEUS(node)
    if node.data == "ATOM":
        procedure_ATOM(node);


# Testing
if __name__ == "__main__":
    nuke = ParseTree("NUCLEUS", None)
    range = ParseTree("RANGE", None)
    root = ParseTree("ROOT", None)
    ATOM = ParseTree("ATOM", None)
    ATOMMOD = ParseTree("ATOMMOD", None)
    CHARRNG = ParseTree("CHARRNG", None)
    test = "CHARRNGlambda"

    if test == "ATOM":
        range.addChild("a")
        range.addChild("b")
        nuke.addChild(range)
        ATOMMOD.addChild(LAMBDA)
        ATOM.addChild(nuke)
        ATOM.addChild(ATOMMOD)
        root.addChild(ATOM)
        AST_SDT_Procedure(ATOM)
    if test == "paren":
        nuke.addChild("open")
        nuke.addChild("ALT")
        nuke.addChild("close")
        root.addChild(nuke)
        AST_SDT_Procedure(nuke)
    if test == "range":
        CHARRNG.addChild("dash")
        CHARRNG.addChild("d")
        nuke.addChild("a")
        nuke.addChild(CHARRNG)
        root.addChild(nuke)
        AST_SDT_Procedure(nuke)
    if test == "CHARRNGlambda":
        CHARRNG.addChild("lambda")
        nuke.addChild("q")
        nuke.addChild(CHARRNG)
        root.addChild(nuke)
        AST_SDT_Procedure(nuke)

    print(root)
