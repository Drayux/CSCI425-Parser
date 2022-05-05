###################################
# OFFICIAL MAIN FOR ZOBOS PROJECT #
###################################

# System imports
import sys

# Project imports
from Grammar import Grammar
from Parser import LRParser as Parser
from TokenStream import TokenStream


# -- GLOBALS --
GRAMMARPATH = "config/zlang.cfg"
TABLEPATH = "config/zlang.lr"


# -- MAIN --
def main(streamPath: str, astPath: str, tablePath: str):
	global GRAMMARPATH
	global TABLEPATH

	grammar = Grammar(GRAMMARPATH, False)
	parser = Parser(grammar, TABLEPATH, tablePath)
	stream = TokenStream(streamPath, True)

	# Primary ZOBOS logic
	tree = parser.parse(stream)		# Parse the token stream
	with open(astPath, "w+") as astFile:
		tree.format(astFile)			# Output the tree to the specified file


# -- ARG PARSING --
if __name__ == "__main__":
	# TEMP
	for a in sys.argv:
		print("ARG: {}".format(a))
	if len(sys.argv) != 4:
		print(f"Usage: {sys.argv[0]} <token stream (.tok)> <ast output (.dat)> <symtable output (.sym)")
		exit(1)

	# Print warnings for likely faulty use
	streamPath = sys.argv[1]
	astPath = sys.argv[2]
	tablePath = sys.argv[3]
	check = False

	# Check if streamPath ends with the .tok extension
	tmp = streamPath.split('.')
	if tmp[-1] != "tok":
		print(f"WARNING: Potentially erroneous token stream (.tok) file: {streamPath}")
		check = True

	# Check if astPath ends with the .dat extension
	tmp = astPath.split('.')
	if tmp[-1] != "dat":
		print(f"WARNING: Potentially erroneous AST (.dat) file: {astPath}")
		check = True

	# Check if tablePath ends with the .sym extension
	tmp = tablePath.split('.')
	if tmp[-1] != "sym":
		print(f"WARNING: Potentially erroneous symbol table (.sym) file: {tablePath}")
		check = True

	# Provide the user a chance to exit to protect potential overwrite of unintended files
	# We *may* need to disable this for the final submission
	if check:
		try: input("Press enter to continue...\n")
		except KeyboardInterrupt:
			exit(1)

	main(streamPath, astPath, tablePath)
