import Util
from ParseTree import ParseTree


def addNodeToTree(placement, child: ParseTree, root: ParseTree):
    if len(placement) == 1:
        root.addChild(child)
    else:
        addNodeToTree(placement[1:], child, root.children[int(placement[0])])


def ReadAst(def_AST):
    root_AST = ParseTree("MODULE", None)

    with def_AST as file:
        lines = file.readlines()

        # Read in each line
        for lineData in lines[1:]:
            if len(lineData) < 3 or lineData == '\n':
                break
            attributes = lineData.split()
            lineAttr = 0
            colAttr = 0
            const = False
            res = []

            # The first element is the placement of this node in the tree
            placement = attributes[0]  # 0-0-1

            # The second element is whether the node is a parent or a leaf
            parent_or_leaf = attributes[1]

            # The node type is like :type, :id, intval ect
            node_Type = attributes[2][1:]
            x = 4
            if node_Type == "id":
                if attributes[3].startswith(":x"):
                    node_Type = "id:" + Util.SubstituteHex(attributes[3][1:])
                else:
                    node_Type = "id:" + attributes[3][1:]
            elif node_Type == "intval":
                node_Type = "intval:" + attributes[3][1:]
            elif node_Type == "floatval":
                inty , decimaly = attributes[3].split("x2e")
                decimaly = decimaly[:2]
                node_Type = "floatval" + inty + "." + decimaly
            elif node_Type.startswith("x"):
                node_Type = Util.SubstituteHex(node_Type)
            else:
                x = 3
            # Internal nodes can stop here, leaves and some parents can have more
            if len(attributes) <= 3:
                new_Node = ParseTree(node_Type, None)
                addNodeToTree(placement.split("-")[1:], new_Node, root_AST)
                continue

            for attribute in attributes[x:]:
                print(attribute)

                if attribute.startswith("type:"):
                    node_Type = attribute
                elif attribute.startswith("line:"):
                    lineAttr = int(attribute[5:])
                elif attribute.startswith("col:"):
                    colAttr = int(attribute[4:])
                elif attribute.startswith("const:"):
                    const = attribute[6] == "T"
                if ":" in attribute[1:]:
                    res.append(map(str.strip, attribute.split(":")))

            new_Node = ParseTree(node_Type, None, (lineAttr, colAttr))
            new_Node.const = const
            new_Node.dictionary = dict(res)
            addNodeToTree(placement.split("-")[1:], new_Node, root_AST)


    return root_AST
