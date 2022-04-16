from ParseTree import ParseTree

# TODO      RE -> ALT $
# TODO     ALT -> SEQ ALTLIST
# TODO ALTLIST -> pipe SEQ ALTLIST
# TODO          | lambda
# TODO     SEQ -> ATOM SEQLIST
# TODO 	     | lambda
# DONE SEQLIST -> ATOM SEQLIST
# DONE 		 | lambda
# DONE    ATOM -> NUCLEUS ATOMMOD
# DONE ATOMMOD -> kleene | plus | lambda
# DONE NUCLEUS -> open ALT close
# DONE          | char CHARRNG
# DONE          | dot
# DONE CHARRNG -> dash char
# DONE          | lambda

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
    # open ALT close
    if node.children[0].data == "open":
        replace_node_with_new_node(node, node.children[1])
        return
    # dot
    if node.children[0].data == "dot":
        replace_node_with_new_node(node, node.children[0])
        return
    # char CHARRNG
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


# Rule 9    ATOM -> NUCLEUS ATOMMOD
def procedure_ATOM(node):
    for child in node.children:
        if child.data == "ATOMMOD":
            # ATOM MOD to lambda
            if child.children[0].data == LAMBDA:
                replace_node_with_new_node(node, node.children[0].children[0])
                return
            # ATOM MOD to plus or kleene
            else:
                newAtom = ParseTree(child.children[0].data, node.parent)
                newAtom.addChild(node.children[0].children[0])
                replace_node_with_new_node(node, newAtom)


# Rule 7 SEQLIST -> ATOM SEQLIST
def procedure_SEQLIST(node: ParseTree):
    for child in node.children:
        # If SEQLIST child is a SEQLIST-> lamda, eliminate that child
        if child.data == LAMBDA:
            node.parent.removeChild(node)
            return
    if node.parent.data == "SEQLIST":
        for adoptedChildren in node.children:
            node.parent.children.append(adoptedChildren)
        node.parent.removeChild(node)



def AST_SDT_Procedure(node: ParseTree):
    if node.data == "NUCLEUS":
        procedure_NUCLEUS(node)
    elif node.data == "ATOM":
        procedure_ATOM(node);
    elif node.data == "SEQLIST":
        procedure_SEQLIST(node)


# Testing
if __name__ == "__main__":
    nuke = ParseTree("NUCLEUS", None)
    range = ParseTree("RANGE", None)
    root = ParseTree("ROOT", None)
    ATOM = ParseTree("ATOM", None)
    ATOMMOD = ParseTree("ATOMMOD", None)
    SEQLIST = ParseTree("SEQLIST", None)
    SEQ = ParseTree("SEQ", None)
    CHARRNG = ParseTree("CHARRNG", None)
    test = "SEQ"

    if test == "SEQ":
        SEQ.addChild("range")
        SEQLIST.addChild("dot")
        SEQLIST.addChild("plus")
        SEQ.addChild(SEQLIST)
        root.addChild(SEQ)
        print(root)
        AST_SDT_Procedure(SEQ)
    if test == "SEQLISTlambda":
        childSEQLIST = ParseTree("SEQLIST", None)
        childSEQLIST.addChild(LAMBDA)
        SEQLIST.addChild("a")
        SEQLIST.addChild(childSEQLIST)
        root.addChild(SEQLIST)
        print(root)
        AST_SDT_Procedure(childSEQLIST)
    if test == "SEQLISTcomplex":
        childSEQLIST = ParseTree("SEQLIST", None)
        childSEQLIST.addChild(LAMBDA)
        SEQLIST.addChild("plus with stuff")
        SEQLIST.addChild(childSEQLIST)
        parentSEQLIST = ParseTree("SEQLIST", None)
        parentSEQLIST.addChild("dot")
        parentSEQLIST.addChild(SEQLIST)
        root.addChild(parentSEQLIST)
        print(root)
        AST_SDT_Procedure(childSEQLIST)
        AST_SDT_Procedure(SEQLIST)
        AST_SDT_Procedure(parentSEQLIST)
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
