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

def SubstituteHexInverse(str):
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
