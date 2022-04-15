from ParseTree import ParseTree

LAMBDA = "lambda"

def replace_node_with_new_node(node: ParseTree, new_node: ParseTree):
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
                replace_node_with_new_node(node, node.children[0])
                return
            else:
                rangeNode = ParseTree("range", node.parent)
                rangeNode.addChild(node.children[0])
                rangeNode.addChild(child.children[1])
                replace_node_with_new_node(node, rangeNode)




def AST_SDT_Procedure(node: ParseTree):
    if node.data == "NUCLEUS":
        procedure_NUCLEUS(node)


# Testing
if __name__ == "__main__":
    nuke = ParseTree("NUCLEUS", None)
    root = ParseTree("ROOT", None)
    CHARRNG = ParseTree("CHARRNG", None)
    test = "CHARRNGlambda"

    if test == "paren":
        nuke.addChild("open")
        nuke.addChild("ALT")
        nuke.addChild("close")
    if test == "range":
        CHARRNG.addChild("dash")
        CHARRNG.addChild("d")
        nuke.addChild("a")
        nuke.addChild(CHARRNG)
    if test == "CHARRNGlambda":
        CHARRNG.addChild("lambda")
        nuke.addChild("q")
        nuke.addChild(CHARRNG)

    root.addChild(nuke)
    AST_SDT_Procedure(nuke)
    print(root)
