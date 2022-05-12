import sys

import ParseTree
from ReadAST import ReadAst
from SymbolTable import SymbolTable
from treeCG import treeCG
from DataSegment import DataSegment, Entry

num_GP_Reg = 0
num_FP_Reg = 0

def main():
	if len(sys.argv) != 4:
		print("ERROR: A lexing config file and a scanner config file must be provided")
		print(f"Usage: {sys.argv[0]} x,x .def .czr")
		exit(1)


	num_Regs= sys.argv[1]
	def_File = sys.argv[2]
	czr_File = sys.argv[3]
	with open(def_File, "r") as def_AST, open(czr_File, "w") as czr_OutFile:
		# Read in the number of regs
		num_GP_Reg, num_FP_Reg = num_Regs.split(",")
		regList_GP = []
		regList_FP = []
		for i in range(int(num_GP_Reg)): regList_GP.append("R"+str(i))
		for i in range(int(num_FP_Reg)): regList_FP.append("F"+str(i))

		# Reading in the AST file into a ParseTree - Konch
		root_AST: ParseTree = ReadAst(def_AST)

		# Create Symbol table object, pass in the AST - Chris

		# Take from the symbol table and make dataSegments for it,
		# make a map of symbols and literals to the dataspace stored - Chris
		data_Seg = DataSegment()
		data_Seg.visit_pass(root_AST)

		# Develop register needs - Konch
		root_AST.registerNeeds()

		# Using the register needs, develop - Konch
		list_of_instructions = treeCG(root_AST, regList_GP, regList_FP, data_Seg)

		# Do Jumps for ec

		# Print to czr_OutFile
		# data part
		imageData(data_Seg, czr_OutFile)

		# instruction part
		imageInit(list_of_instructions, data_Seg, czr_OutFile)


def imageData(data_segment, output):
    for var in data_segment.map:
        entry = data_segment.map[var]
        output.write(f"label @{entry.pos}w {entry.name}\n")
        if entry.value:
            output.write(f"data @{entry.pos}w {entry.value}\n")    # TODO: support initial values



def imageInit(a, b, c):
    pass

if __name__ == "__main__":
	main()
