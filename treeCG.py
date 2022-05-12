import DataSegment
from ParseTree import ParseTree

mappy = {
    "plus": "+",
    "minus": "-",
    "mult": "*",
    "div": "/",
    "rem": "%"
}


def treeCG(root_AST: ParseTree, regList_GP, regList_FP, data_Seg: DataSegment):
    """Produces a list of string instructions for the blang or buster assembly language
    Give an AST, a list of register names for GP and FP registers
    """

    list_of_instructions_essentially = []
    instruction = ""
    r1 = regList_GP[0]
    r2 = None
    if len(regList_GP) > 1:
        r2 = regList_GP[1]
    f1 = regList_FP[0]
    f2 = None
    if len(regList_FP) > 1:
        f2 = regList_FP[1]
    rx1 = None
    rx2 = None
    keys = []
    floatMin = 0
    floatMax = 1310.71
    intMin = -16384
    intMax = 16383

    if root_AST.parent is not None:
        parentKeys = root_AST.parent.dictionary.keys()
        keys = root_AST.dictionary.keys()
        if "domain" in parentKeys:
            if root_AST.parent.dictionary["domain"] == "float":
                rx1 = f1
                rx2 = f2
            else:
                rx1 = r1
                rx2 = r2
        elif "domain" in keys:
            if root_AST.dictionary["domain"] == "float":
                rx1 = f1
                rx2 = f2
            else:
                rx1 = r1
                rx2 = r2

    if root_AST.data.startswith("intval:"):
        value = root_AST.data[7:]
        instruction = "load " + r1 + ", #" + value + "w"
        tooBigForLoadImmediate = not (intMin <= int(value) <= intMax)
        if tooBigForLoadImmediate or data_Seg.find_value(int(value)) is not None:
            instruction = "load " + r1 + ", @" + str(data_Seg.find_value(int(value))) + "w"
    elif root_AST.data.startswith("floatval:"):
        value = root_AST.data[9:]
        instruction = "load " + f1 + ", #" + value + "w"
        tooBigForLoadImmediate = not (floatMin <= float(value) <= floatMax)
        if tooBigForLoadImmediate or data_Seg.find_value(float(value)) is not None:
            instruction = "load " + f1 + ", @" + str(data_Seg.find_value(float(value))) + "w"
    elif root_AST.data.startswith("id:"):
        value = root_AST.data[3:]
        instruction = "load " + rx1 + ", @" + str(data_Seg.map[value].pos) + "w"
    elif root_AST.data == "EMIT":
        for childNode in root_AST.children:
            list_of_instructions_essentially.extend(treeCG(childNode, regList_GP, regList_FP, data_Seg))
            if childNode.dictionary["domain"] == "float":
                rx1 = f1
            else:
                rx1 = r1
            list_of_instructions_essentially.append("emit " + rx1)
            return list_of_instructions_essentially
    elif "op" in keys:
        if root_AST.dictionary["op"] == "unary":
            if root_AST.dictionary["unary"] == "minus":
                instruction = treeCG(root_AST.children[0], regList_GP, regList_FP, data_Seg)
                instruction.append("chs " + rx1)
                list_of_instructions_essentially.extend(instruction)
                return list_of_instructions_essentially
        left = root_AST.children[0]
        right = root_AST.children[1]

        if root_AST.data == "=":
            instruction = treeCG(right, regList_GP, regList_FP, data_Seg)
            list_of_instructions_essentially.extend(instruction)
            value = left.data[3:]
            instruction = "store " + rx1 + ", @" + str(data_Seg.map[value].pos) + "w"
            list_of_instructions_essentially.append(instruction)
            return list_of_instructions_essentially
        if root_AST.dictionary["op"] == "binary":
            value = root_AST.data
            if rx1 == r1:
                new_regList = regList_GP
            else:
                new_regList = regList_FP
            if left.regCount >= len(new_regList) and right.regCount >= len(new_regList):
                instruction = treeCG(left, regList_GP, regList_FP, data_Seg)
                list_of_instructions_essentially.extend(instruction)
                list_of_instructions_essentially.append("push " + rx1)
                instruction = treeCG(right, regList_GP, regList_FP, data_Seg)
                list_of_instructions_essentially.extend(instruction)
                list_of_instructions_essentially.append("pop " + rx2)
                list_of_instructions_essentially.append(value+" "+rx1+", "+rx2+", "+rx1)
                return list_of_instructions_essentially
            if left.regCount > right.regCount:
                if rx1 == r1:
                    list_of_instructions_essentially.extend(treeCG(left, regList_GP, regList_FP, data_Seg))
                    list_of_instructions_essentially.extend(treeCG(right, regList_GP[1:], regList_FP, data_Seg))
                    list_of_instructions_essentially.append(value + " " + rx1 + ", " + rx1 + ", " + rx2)
                    return list_of_instructions_essentially
                else:
                    list_of_instructions_essentially.extend(treeCG(left, regList_GP, regList_FP, data_Seg))
                    list_of_instructions_essentially.extend(treeCG(right, regList_GP, regList_FP[1:], data_Seg))
                    list_of_instructions_essentially.append(value + " " + rx1 + ", " + rx1 + ", " + rx2)
                    return list_of_instructions_essentially
            else:
                if rx1 == r1:
                    list_of_instructions_essentially.extend(treeCG(right, regList_GP, regList_FP, data_Seg))
                    list_of_instructions_essentially.extend(treeCG(left, regList_GP[1:], regList_FP, data_Seg))
                    list_of_instructions_essentially.append(value + " " + rx1 + ", " + rx2 + ", " + rx1)
                    return list_of_instructions_essentially
                else:
                    list_of_instructions_essentially.extend(treeCG(right, regList_GP, regList_FP, data_Seg))
                    list_of_instructions_essentially.extend(treeCG(left, regList_GP, regList_FP[1:], data_Seg))
                    list_of_instructions_essentially.append(value + " " + rx1 + ", " + rx2 + ", " + rx1)
                    return list_of_instructions_essentially
    else:
        for nodeChild in root_AST.children:
            instruction = treeCG(nodeChild, regList_GP, regList_FP, data_Seg)
            if instruction != "":
                list_of_instructions_essentially.extend(instruction)
        return list_of_instructions_essentially

    if instruction != "":
        list_of_instructions_essentially.append(instruction)

    return list_of_instructions_essentially
