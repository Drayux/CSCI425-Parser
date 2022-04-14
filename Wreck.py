import sys

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
    # 1. feed regex to scanner
    # 2. make a concrete syntax tree
    # 3. convert to AST
    # 4. generate L and T tables
    print("...")

def main():
    if len(sys.argv) != 3:
        print("Incorrect usage, a lexing config file and a scanner config file must be provided")
        exit(1)

    with open(sys.argv[1], "r") as lexingConfig, open(sys.argv[2], "w") as scannerConfig:
        lexConfigLines = lexingConfig.readlines()
        originalLanguage = lexConfigLines[0].strip().replace(" ", "")
        hexLanguage = SubstituteHex(originalLanguage)

        regexes = []
        for i in range(1, len(lexConfigLines)):
            line = lexConfigLines[i].strip()
            regex, tokenName = line.split(" ")
            regex = regex.strip()
            tokenName = tokenName.strip()
            regexes.append(Regex(regex, tokenName))

        lambdaChar = "x01"
        VerifyLambda(hexLanguage, lambdaChar)

        nfas = []
        for regex in regexes:
            nfas.append(CompileRegex(regex, hexLanguage))

        # Write out to file...

if __name__ == "__main__":
    main()