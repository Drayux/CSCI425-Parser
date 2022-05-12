import sys

import ParseTree
from ReadAST import ReadAST
from SymbolTable import SymbolTable
from DataSegment import DataSegment

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
		print(num_GP_Reg)

		# Reading in the AST file into a ParseTree - Konch
		root_AST: ParseTree = ReadAST(def_AST)

		# Create Symbol table object, pass in the AST - Chris
		sym_Table = SymbolTable()
		sym_Table.visit_pass(root_AST)

		# Take from the symbol table and make dataSegments for it,
		# make a map of symbols and literals to the dataspace stored - Chris
		data_Seg = DataSegment(sym_Table)

		# Develop register needs - Konch
		root_AST.registerNeeds()

		# Using the register needs, develop - Konch
		list_of_instructions_essential = treeCG(root_AST, num_GP_Reg, num_FP_Reg)

		# Do Jumps for ec

		# Print to czr_OutFile
		# data part
		next_dataSegment: int = imageData(data_Seg, czr_OutFile)
		# instruction part
		imageInit(list_of_instructions_essential, next_dataSegment, czr_OutFile)


def imageData(data_segment, output):
    for var in self.map:
        (pos, _) = self.map[var]
        output.write(f"label @{pos} {var}")
        if "val" in var:
            output.write(f"data @{pos} *Unimplemented*")    # TODO: support initial values


if __name__ == "__main__":
	main()
