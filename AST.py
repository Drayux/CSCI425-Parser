import sys

from ParseTree import ParseTree

# DONE      RE -> ALT $
# DONE?     ALT -> SEQ ALTLIST
# DONE ALTLIST -> pipe SEQ ALTLIST
# DONE          | lambda
# DONE     SEQ -> ATOM SEQLIST
# DONE 	     | lambda
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
charLAMBDA = "_lambda"


def RootReplace(node: ParseTree, data, children):
    node.data=data
    node.children = children


def replace_node_with_new_node(node: ParseTree, new_node: ParseTree):
    RootReplace(node, new_node.data, new_node.children)
    return


def semantic_Check(node: ParseTree):
    if node.data == "range":
        lowerCase = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
        upperCase = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        lefty = node.children[0].data
        righty = node.children[1].data
        if all(x in lowerCase for x in [lefty, righty]) or \
        all(x in upperCase for x in [lefty, righty])    or \
        all(x in numbers for x in [lefty, righty]):
            pass
        else:
            print("SEMANTIC ERROR: the two values are of different cases or types")
            sys.exit(2)
        try:
            if lefty > righty:
                raise ValueError("Left")
        except Exception:
            print("SEMANTIC ERROR: Left value is greater than right value in range")
            sys.exit(2)


def procedure_NUCLEUS(node: ParseTree):
    # open ALT close
    if node.children[0].data == "open":
        node.removeChild(node.children[2])
        node.removeChild(node.children[0])
        return
    # dot
    if node.children[0].data == "dot":
        return
    # char CHARRNG to range
    for child in node.children:
        if child.data == "CHARRNG":
            if child.children[0].data == "lambda":
                node.removeChild(child)
                return
            else:
                rangeNode = ParseTree("range", node.parent)
                rangeNode.addChild(node.children[0])
                rangeNode.addChild(child.children[1])
                semantic_Check(rangeNode)
                replace_node_with_new_node(child, rangeNode)
                node.removeChild(node.children[0])
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


def procedure_SEQ(node: ParseTree):
    for child in node.children:
        if child.data == "SEQLIST":
            # Diswon SEQLIST but raise its children as your own
            # Adopt SEQLISTS children
            for adoptedChildren in child.children:
                node.addChild(adoptedChildren)
            # Disown disgraced SEQLIST
            node.removeChild(child)
    if len(node.children) == 1:
        replace_node_with_new_node(node, node.children[0])


def procedure_ALTLIST(node: ParseTree):
    for child in node.children:
        if child.data == LAMBDA and len(node.children) == 1:
            node.parent.removeChild(node)
            return
        if child.data == "pipe":
            continue
        node.parent.addChild(child)
    node.parent.removeChild(node)


def procedure_ALT(node: ParseTree):
    if len(node.children) == 1:
        replace_node_with_new_node(node, node.children[0])
        return


def procedure_RE(node: ParseTree):
    if node.children[1].data == "$":
        replace_node_with_new_node(node, node.children[0])


def procedure_ROOT(node: ParseTree):
    replace_node_with_new_node(node, node.children[0])


def AST_SDT_Procedure(node: ParseTree):
    if node.data == "NUCLEUS":
        procedure_NUCLEUS(node)
    elif node.data == "ATOM":
        procedure_ATOM(node);
    elif node.data == "SEQLIST":
        procedure_SEQLIST(node)
    elif node.data == "SEQ":
        procedure_SEQ(node)
    elif node.data == "ALTLIST":
        procedure_ALTLIST(node)
    elif node.data == "ALT":
        procedure_ALT(node)
    elif node.data == "RE":
        procedure_RE(node)
    elif node.data == "ROOT":
        procedure_ROOT(node)


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
    ALTLIST = ParseTree("ALTLIST", None)
    ALT = ParseTree("ALT", None)
    RE = ParseTree("RE", None)
    test = "SEQLISTlambda"

    if test == "RE":
        RE.addChild(SEQ)
        RE.addChild("$")
        root.addChild(RE)
        print(root)
        AST_SDT_Procedure(RE)
    if test == "ALTsinglechild":
        ALT.addChild(SEQ)
        root.addChild(ALT)
        print(root)
        AST_SDT_Procedure(ALT)
    if test == "ALTLISTlambda":
        ALTLIST.addChild(LAMBDA)
        ALT.addChild(ALTLIST)
        root.addChild(ALT)
        print(root)
        AST_SDT_Procedure(ALTLIST)
    if test == "SEQsinglechild":
        SEQ.addChild("range")
        root.addChild(SEQ)
        print(root)
        AST_SDT_Procedure(SEQ)
    if test == "SEQ":
        SEQ.addChild("range")
        SEQLIST.addChild("dot")
        SEQLIST.addChild("plus and stuff")
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
        print(root)
        AST_SDT_Procedure(ATOM)
    if test == "paren":
        nuke.addChild("open")
        nuke.addChild("ALT")
        nuke.addChild("close")
        root.addChild(nuke)
        print(root)
        AST_SDT_Procedure(nuke)
    if test == "range":
        CHARRNG.addChild("dash")
        CHARRNG.addChild("d")
        nuke.addChild("a")
        nuke.addChild(CHARRNG)
        root.addChild(nuke)
        print(root)
        AST_SDT_Procedure(nuke)
    if test == "CHARRNGlambda":
        CHARRNG.addChild("lambda")
        nuke.addChild("q")
        nuke.addChild(CHARRNG)
        root.addChild(nuke)
        print(root)
        AST_SDT_Procedure(nuke)

    print(root)

