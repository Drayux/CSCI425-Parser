from copy import copy
from io import TextIOWrapper
from ParseExceptions import StructureError
from ParseTree import ParseTree

# Utility function for output
# Takes any input encoding, converts all alphanums to plain output, every other to hex encoded.
def formatOutput(str):
	outStr = ""
	i = 0
	while i < len(str):
		c = str[i]
		if c == "x":
			# Might need to convert to plain encoding, otherwise skip
			hexStr = str[i + 1] + str[i + 2]
			decoded = chr(int(hexStr, 16))
			# Don't decode x
			if decoded.isalnum() and decoded != "x":
				outStr += decoded
			else:
				outStr += str[i : i + 3]
			i += 3  # hex is three characters, which we need to skip past.
		elif c.isalnum():
			# Do nothing
			outStr += c
			i += 1
		else:
			# Convert to hex encoding
			hexStr = hex(ord(c))
			hexStr = hexStr[2:]  # Trim the 0x
			if len(hexStr) == 1:
				hexStr = "0" + hexStr
			outStr += "x" + hexStr
			i += 1
		if i != 0: outStr += " "
	return outStr

# Subcomponent classes specific to the NFA Table class
# Dynamically adds rows and columns as necessary
class TransitionTable:
	def __init__(self):
		self.rowCount = 1		# Rows indicate the 'from' state
		self.colCount = 1		# Cols indicate the 'to' state
		self.accepting = []		# List of 'from state ids' that are accepting states
		self.data = [[-1]]		# -1 indicates no transition, 0 indicates transition with empty char

	def __str__(self):
		ret = "\t|"

		# Column labels
		for x in range(self.colCount): ret += f" {x}\t "
		ret += "\n========|"

		# Seperator bar
		for x in range(self.colCount): ret += "========"

		# Rows
		for x in range(self.rowCount):
			ret += f"\n  {x}\t|"

			for y in range(self.colCount):
				val = self.data[x][y]
				data = '-'
				if val > 0: data = chr(self.data[x][y])
				elif val == 0: data = '+'
				ret += f" {data}\t "

		return ret

	def addTransition(self, fromId: int, toId: int, tr = 0):
		# Type checks
		if fromId < 0 or toId < 0:
			raise ValueError("State IDs must be non-negative")

		if type(tr) is str:
			tr = ord(tr[0])

		# If toId exceeds the current number of cols, add them
		diff = (toId + 1) - self.colCount
		if diff > 0:
			# annex = [-1 for x in range(diff)]
			# for x in range(self.rowCount):
			# 	row = self.data[x] + annex
			# 	self.data[x] = row
			for row in self.data:
				for x in range(diff):
					row.append(-1)

			self.colCount += diff

		# If fromId exceeds the current number of rows, add them
		diff = (fromId + 1) - self.rowCount
		if diff > 0:
			row = [-1 for x in range(self.colCount)]
			for x in range(diff):
				self.data.append(copy(row))

			self.rowCount += diff

		# Check for duplicate additions
		if not self.data[fromId][toId] < 0:
			print(f"WARNING: Adding duplicate transition (fromId: {fromId}, toId: {toId})")

		# Add the transition itself
		self.data[fromId][toId] = tr

	# Returns a list of tuples [ (fromId, toId, char), (fromId, toId, char), ... ]
	def getRow(self, rowId):
		row = None
		ret = []
		try: row = self.data[rowId]
		except IndexError:
			print(f"WARNING: Invalid row ID specifed in getRow({rowId})")
			return ret

		# Begin building the tuple list
		# NOTE: Would be safer to just use len(row) but if this fails, something in the data structure is fucked
		for x in range(self.colCount):
			val = row[x]
			if val < 0: continue
			elif val == 0: val = 'lambda'		# TODO: Not sure what interface we're going for with lambda chars
			else: val = chr(val)

			ret.append((rowId, x, val))

		return ret

class TTable:
	def __init__(self):
		self.stateCount = 1
		self.data = [{}]

	def addTransition(self, fromState, transitionChar, toState):
		#Type Checks
		if fromState < 0 or toState < 0:
			print(f"WARNING: fromState: {fromState}, toState: {toState}")
			raise ValueError("State IDs must be non-negative")
		if type(transitionChar) is str:
			if transitionChar == r'\\':
				transitionChar = ord('\\')
			elif len(transitionChar) == 2:
				transitionChar = ord(transitionChar[1])
			else:
				transitionChar = ord(transitionChar[0])
        #AddEntries if not present
		while fromState >= self.stateCount:
			self.data.append({})
			self.stateCount += 1
        #Add Transition
		self.data[fromState][transitionChar] = toState

	def getRow(self, fromState):
		#Checks
		row = None
		ret = []
		try: row = self.data[fromState]
		except IndexError:
			print(f"WARNING: Invalid row ID specifed in getRow({rowId})")
			return ret
		#Accumulate output
		for transitionChar, toState in row.items():
			ret.append((fromState, transitionChar, toState))
		return ret

class NFATable:
	def __init__(self, name: str, alphabet: list, tree: ParseTree):
		self.tokenName = name
		self.alphabet = alphabet
		self.stateCount = 2
		self.T = TTable()			# Standard state transitions
		self.L = TransitionTable()			# Lambda state transitions
		# -- TODO --
		self.processNode(tree, 0, 1)

	def processNode(self, tree, fromId, toId):
		#Alt Node
		if tree.data == "ALT":
			for child in tree.children:
				childFromId = self.stateCount
				self.stateCount += 1
				childToId = self.stateCount
				self.stateCount += 1
				self.L.addTransition(fromId, childFromId)
				self.L.addTransition(childToId, toId)
				self.processNode(child, childFromId, childToId)
		#SEQ Node
		elif tree.data == "SEQ":
			childFromId = fromId
			childToId = self.stateCount
			self.stateCount += 1
			for child in tree.children:
				self.processNode(child, childFromId, childToId)
				childFromId = childToId
				childToId = self.stateCount
				self.stateCount += 1
			self.L.addTransition(childFromId, toId)
		#Kleen Node
		elif tree.data == "kleene": 	
			childFromId = self.stateCount
			self.stateCount += 1
			childToId = self.stateCount
			self.stateCount += 1 
			self.L.addTransition(childFromId, childToId)
			self.L.addTransition(childToId, childFromId)
			self.L.addTransition(childToId, toId)
			self.L.addTransition(fromId, childFromId)
			self.processNode(tree.children[0], childFromId, childToId)
		#Plus Node
		elif tree.data == "plus": 
			childFromId = self.stateCount
			self.stateCount += 1
			childToId = self.stateCount
			self.stateCount += 1 
			self.L.addTransition(childToId, childFromId) 
			self.L.addTransition(childToId, toId)
			self.L.addTransition(fromId, childFromId)
			self.processNode(tree.children[0], childFromId, childToId)
		#Range Leaf 
		elif tree.data == "range":
			start = tree.children[0].data
			stop = tree.children[1].data
			for n in range(ord(start), ord(stop) + 1):
				if chr(n) in self.alphabet:
					self.T.addTransition(fromId, chr(n), toId)
		#Lambda Leaf
		elif tree.data == "lambda":
			self.L.addTransition(fromId, toId)
		#Dot Leaf
		elif tree.data == "dot":
			for char in self.alphabet:
				self.T.addTransition(fromId, char, toId)
		#Char leaf
		else:
			self.T.addTransition(fromId, tree.data, toId)


	# Add a normal transition
	def addTransition(self, fromId, toId, char):
		self.T.addTransition(fromId, toId, char)

	# Add a lambda transition
	def addLambda(self, fromId, toId):
		self.L.addTransition(fromId, toId)

	def writeToFile(self, lambdaChar, file: TextIOWrapper):
		# Sanity checks
		assert(type(lambdaChar) == str)
		assert(len(lambdaChar) == 3)
		assert(len(self.alphabet) > 0)
		assert(not file.closed)

		# NFA file definition:
		# Header: # states, lambda char, alphabet...
		# States: - for normal or + for accepting, from state id, to state id, transition characters...

		# print(self.tokenName)
		# print(self.L)
		# print()

		languageString = "".join(self.alphabet)
		file.write(f"{self.stateCount + 1} {lambdaChar} {formatOutput(languageString)}")

		# Get character transitions for all NFA states
		for i in range(self.T.stateCount):
			transitions = self.T.getRow(i)

			# NOTE: getRow(1) should return an empty list
			# This is because it is the only accepting state
			# assert((len(transitions) + len(lambdas) == 0), "NFA tables are malformed!")
			# if i == 1 and (len(transitions) + len(lambdas)) > 0:
			# 	raise StructureError("NFA tables are malformed")

			for fromId, char, toId in transitions:
				# assert((char in self.language), f"Unrecognized transition character: {char}")
				char = chr(char)
				file.write(f"\n- {fromId} {toId} {formatOutput(char)}")

		# Get lambda transitions for all NFA states
		for i in range(self.L.rowCount):
			lambdas = self.L.getRow(i)

			for fromId, toId, _ in lambdas:
				# assert((char == lambdaChar), f"Lambda char mismatch, found {char} but should be {lambdaChar}")
				file.write(f"\n- {fromId} {toId} {formatOutput(lambdaChar)}")

		# Every RegEx NFA will have exactly 1 accepting state
		file.write("\n+ 1 1\n")


# Code testing
import sys
if __name__ == "__main__":
	alphabet = [ 'a', 'b', 'c' ]
	parseTree = ParseTree("SEQ", None)
	parseTree.addChild(ParseTree("a", None))
	subTree = ParseTree("ALT", None)
	subTree.addChild(ParseTree("b", None))
	subTree.addChild(ParseTree("c", None))
	parseTree.addChild(subTree)
	nfaTable = NFATable(parseTree)
	nfaTable.writeToFile("#", alphabet, sys.stdout)

#print("EMPTY:")
#table = TransitionTable()
#print(table)
#print()

# Add some transitions
#table.addTransition(1, 1)
#table.addTransition(3, 6)
#table.addTransition(1, 4, 'a')
#table.addTransition(5, 4, 'b')
#table.addTransition(3, l, 'c')
#table.addTransition(0, 1, 'd')
#table.addTransition(0, 1, 'e')
#table.addTransition(2, 0, 'f')

#print("\nMODIFIED:")
#print(table)
#print()

#print("\nROWS:")
#for x in range(table.rowCount):
#	print("row:", x)
#	print(table.getRow(x))
#print()

#print ("\nNFA TABLE FILE OUT:")
#nfaTable = NFATable(tree=ParseTree(data="", parent=None))
#nfaTable.T = table
   #nfaTable.writeToFile("#", [ 'a', 'b', 'c', 'd', 'e', 'f', 'g' ], sys.stdout)
