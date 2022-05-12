import sys

from Grammar import Grammar
from NFA import NFATable
from Parser import LLParser as Parser
from ParseExceptions import ParseError
from TokenStream import TokenStream
from Util import SubstituteHex, SubstituteHexInverse, VerifyLambda

# MOVED TO UTIL.PY
# Util code from Andrew's luther
# def SubstituteHex(inStr):
# 	i = 0
# 	while i < len(inStr):
# 		if inStr[i] == "x":
# 			hex = inStr[i + 1] + inStr[i + 2]
# 			before = inStr[0 : i]
# 			after = inStr[i + 3 : ]
# 			inStr = before + chr(int(hex, 16)) + after
# 		i += 1
# 	return inStr
#
# def SubstituteHexInverse(str):
# 	outStr = ""
# 	for c in str:
# 		if c.isalnum() and c != "x":
# 			outStr += c
# 		else:
# 			hexStr = hex(ord(c))
# 			hexStr = hexStr[2:]  # Trim the 0x
# 			if len(hexStr) == 1:
# 				hexStr = "0" + hexStr
# 			outStr += "x" + hexStr
# 	return outStr
#
# def VerifyLambda(hexLanguage, hexLambdaChar):
# 	if type(hexLambdaChar) != str:
# 		raise "Lambda character should be a string"
# 	if hexLambdaChar[0] != "x":
# 		raise "Lambda character should be hex encoded"
# 	if hexLanguage.find(hexLambdaChar) != -1:
# 		raise "Lambda character isn't unique... uhoh"

class Regex:
	def __init__(self, string, tokenName, substitue = None):
		self.string = string
		self.tokenName = tokenName
		self.substitute = substitue

def CompileRegex(regex, language):
	# PART ONE - Feed regex to scanner
	grammar = Grammar("config/regex.cfg")		# This will always be regex so we can hard-code it
	regexParser = Parser(grammar)				# Build the LL(1) parser from the regex grammar
	#stream = TokenStream(regex, False)			# False denotes that we are passing in a regex string, not a path
	#regexCST = regexParser.parse(stream)		# Might need a try-catch for syntax errors? Haven't looked at the files yet
	stream = TokenStream(regex, False)			# False denotes that we are passing in a regex string, not a path

	regexAST = None
	try: regexAST = regexParser.parse(stream, True)  # Same thing as above, but now in FABULOUS AST
	except ParseError as e:
		print(e)
		exit(2)					# Exit with status two if a syntax error was found

	nfaTable = NFATable(regex.tokenName, language, regexAST)
	return nfaTable

# -- DONE -- #
	# 1. Load .lut file
	# 2. make a concrete syntax tree
	# 3. convert to AST
	# 4. generate L and T tables


	# 5. Change L an T table into an NFA file
	#print("...")

	# ---------- #

def main():
	if len(sys.argv) != 3:
		print("ERROR: A lexing config file and a scanner config file must be provided")
		print(f"Usage: {sys.argv[0]} <lexing config (.lut)> <scanner output (.u)>")
		exit(1)

	with open(sys.argv[1], "r") as lexingConfig, open(sys.argv[2], "w") as scannerConfig:
		lexConfigLines = lexingConfig.readlines()
		originalLanguage = lexConfigLines[0].strip().replace(" ", "")

		# The following two are
		hexLanguage = SubstituteHex(originalLanguage)
		basicLanguageList = [ c for c in hexLanguage ]
		basicLanguageList.sort()

		# Determine the lambda character
		charVal = ord(basicLanguageList[-1]) + 1
		hexVal = hex(charVal % 256)[2:]
		lambdaStr = f"x{'0' if len(hexVal) < 2 else ''}{hexVal}"

		regexes = []
		for i in range(1, len(lexConfigLines)):
			substitute = None
			line = lexConfigLines[i].strip()
			lineAttributes= line.split()
			if len(lineAttributes) == 3:
				regex, tokenName, substitute = lineAttributes
			else:
				regex, tokenName = lineAttributes
			regex = regex.strip()
			tokenName = tokenName.strip()
			regexes.append(Regex(regex, tokenName, substitute))

		# Begin output of scan.u file
		scannerConfig.write(f"{SubstituteHexInverse(hexLanguage)}\n")

		nfas = []
		for regex in regexes:
			nfas.append(CompileRegex(regex, basicLanguageList))
			scannerConfig.write(f"{regex.tokenName}.tt\t\t{regex.tokenName}")
			if regex.substitute is not None: scannerConfig.write(f"\t\t{regex.substitute}\n")
			else: scannerConfig.write("\n")

		for nfa in nfas:
			with open(nfa.tokenName + ".nfa", "w") as nfaFile:
				# nfa.writeToFile(lambdaChar, basicLanguageList, nfaFile)
				nfa.writeToFile(lambdaStr, nfaFile)
				print(f"Created nfa file {nfa.tokenName}.nfa")

	print(f"Wrote scanner config to {sys.argv[2]}")

if __name__ == "__main__":
	main()
