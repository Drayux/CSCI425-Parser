import sys

from Grammar import Grammar
from Parser import LLParser as Parser
from TokenStream import TokenStream

# Util code from Andrew's luther
def SubstituteHex(inStr):
    i = 0
    while i < len(inStr):
        if inStr[i] == "x":
            hex = inStr[i + 1] + inStr[i + 2]
            before = inStr[0 : i]
            after = inStr[i + 3 : ]
            inStr = before + chr(int(hex, 16)) + after
        i += 1
    return inStr

def SubstituteHexInverse(language, str):
    outStr = ""
    for c in str:
        if c.isalnum() and c != "x":
            outStr += c
        else:
            hexStr = hex(ord(c))
            hexStr = hexStr[2:]  # Trim the 0x
            if len(hexStr) == 1:
                hexStr = "0" + hexStr
            outStr += "x" + hexStr
    return outStr

def VerifyLambda(hexLanguage, hexLambdaChar):
    if type(hexLambdaChar) != str:
        raise "Lambda character should be a string"
    if hexLambdaChar[0] != "x":
        raise "Lambda character should be hex encoded"
    if hexLanguage.find(hexLambdaChar) != -1:
        raise "Lambda character isn't unique... uhoh"

class Regex:
    def __init__(self, string, tokenName):
        self.string = string
        self.tokenName = tokenName

def CompileRegex(regex, language):
    # PART ONE - Feed regex to scanner
    grammar = Grammar("config/regex.cfg")		# This will always be regex so we can hard-code it
    regexParser = Parser(grammar)				# Build the LL(1) parser from the regex grammar
    stream = TokenStream(regex, False)			# False denotes that we are passing in a regex string, not a path
    regexCST = regexParser.parse(stream)		# Might need a try-catch for syntax errors? Haven't looked at the files yet
    regexAST = regexParser.parse(stream, True)  # Same thing as above, but now in FABULOUS AST


# -- DONE -- #
    # 1. Load .lut file
    # 2. make a concrete syntax tree

# -- TODO -- #

    # 3. convert to AST
    # 4. generate L and T tables
    # 5. Change L an T table into an NFA file
    #print("...")

    # ---------- #

def main():
    if len(sys.argv) != 3:
        print("Incorrect usage, a lexing config file and a scanner config file must be provided")
        exit(1)

    with open(sys.argv[1], "r") as lexingConfig, open(sys.argv[2], "w") as scannerConfig:
        lexConfigLines = lexingConfig.readlines()
        originalLanguage = lexConfigLines[0].strip().replace(" ", "")
        noHexLanguage = SubstituteHexInverse(originalLanguage)
        hexLanguage = SubstituteHex(originalLanguage)

        basicLanguageList = [ c for c in noHexLanguage ]

        regexes = []
        for i in range(1, len(lexConfigLines)):
            line = lexConfigLines[i].strip()
            regex, tokenName = line.split()
            regex = regex.strip()
            tokenName = tokenName.strip()
            regexes.append(Regex(regex, tokenName))

        lambdaChar = "x01"
        VerifyLambda(hexLanguage, lambdaChar)

        nfas = []
        for regex in regexes:
            nfas.append(CompileRegex(regex, hexLanguage))

        for nfa in nfas:
            with open(nfa.tokenName + ".nfa", "w") as nfaFile:
                nfa.writeToFile(SubstituteHexInverse(lambdaChar), basicLanguageList, nfaFile)

if __name__ == "__main__":
    main()
