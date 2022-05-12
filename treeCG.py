import DataSegment
from ParseTree import ParseTree


def treeCG(root_AST: ParseTree, regList_GP, regList_FP, data_Seg: DataSegment):
    """Produces a list of string instructions for the blang or buster assembly language
    Give an AST, a list of register names for GP and FP registers
    """

    list_of_instructions_essentially = []
    list_of_instructions_essentially.append("test")
    list_of_instructions_essentially.append("list")

    instruction = ""
    r1 = regList_GP[0]
    r2 = regList_GP[1]
    f1 = regList_FP[0]
    f2 = regList_FP[1]
    rx = None
    keys = []
    tooBigForLoadImmediate = False
    floatMin = 0
    floatMax = 1310.71
    intMin = -16384
    intMax = 16383

    if root_AST.parent is not None:
        parentKeys = root_AST.parent.dictionary.keys()
        keys = root_AST.dictionary.keys()
        if "domain" in parentKeys:
            if root_AST.parent.dictionary["domain"] == "float":
                rx = f1
            else:
                rx = r1
        elif "domain" in keys:
            if root_AST.dictionary["domain"] == "float":
                rx = f1
            else:
                rx = r1

    if root_AST.data.startswith("intval:"):
        value = root_AST.data[7:]
        instruction = "load " + r1 + ", #" + value
        tooBigForLoadImmediate = not (intMin <= int(value) <= intMax)
        if tooBigForLoadImmediate:
            instruction = "load " + r1 + ", @" + str(data_Seg.find_value(value))
    elif root_AST.data.startswith("floatval:"):
        value = root_AST.data[9:]
        instruction = "load " + f1 + ", #" + value
        tooBigForLoadImmediate = not (floatMin <= float(value) <= floatMax)
        if tooBigForLoadImmediate:
            instruction = "load " + f1 + ", @" + str(data_Seg.find_value(value))
    elif root_AST.data.startswith("id:"):
        value = root_AST.data[3:]
        instruction = "load " + rx + ", @" + str(data_Seg.find_value(value))
    elif "binary" in keys:
        left = root_AST.children[0]
        right = root_AST.children[1]
        if left.regCount > right.regCount:
            first = left
            second = right
        else:
            first = right
            second = left
        if root_AST.dictionary["binary"] == "assign":
            instruction = treeCG(root_AST.children[1], regList_GP, regList_FP, data_Seg)
            list_of_instructions_essentially.extend(instruction)
            value = left.data[3:]
            instruction = "store " + rx + ", @" + str(data_Seg.find_value(value))
            list_of_instructions_essentially.append(instruction)
            return list_of_instructions_essentially

    list_of_instructions_essentially.append(instruction)

    return list_of_instructions_essentially


if __name__ == "__main__":
    nodey = ParseTree("id:100.00", None)
    nodey.dictionary.update({"type": "int"})
    treeCG(nodey, ["R1", "R2"], ["F1", "F2"], None)
