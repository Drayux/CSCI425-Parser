from io import TextIOWrapper
from ParseTree import ParseTree

# Subcomponent classes specific to the NFA Table class
# Dynamically adds rows and columns as necessary
class TransitionTable:
	def __init__(self):
		pass

	def addTransition(self, fromId: int, toId: int):
		pass

	def rowCount(self):
		return -1  # TODO

	# Returns a list of tuples [ (fromId, toId, char), (fromId, toId, char), ... ]
	def getRow(self, rowId):
		return list()

class NFATable:
	def __init__(self, tree: ParseTree):
		self.T = TransitionTable()	# Standard state transitions
		self.L = TransitionTable()			# Lambda state transitions

		# -- TODO --

	# Add a normal transition
	def addTransition(self, fromId, toId):
		self.T.addTransition(fromId, toId)

	# Add a normal transition
	def addLambda(self, fromId, toId):
		self.L.addTransition(fromId, toId)

	def writeToFile(self, lambdaChar, language: list, file: TextIOWrapper):
		# Sanity checks
		assert(type(lambdaChar) == str)
		assert(len(lambdaChar) == 1)
		assert(type(language) == str)
		assert(len(language) > 0)
		assert(not file.closed)
		
		# NFA file definition:
		# Header: # states, lambda char, alphabet...
		# States: - for normal or + for accepting, from state id, to state id, transition characters...

		nodeCount = self.T.rowCount()
		languageString = language.join(" ")

		file.write(f"{nodeCount} {lambdaChar} {languageString}\n")
		for i in range(nodeCount):
			transitions = self.T.getRow(i)
			lambdas = self.L.getRow(i)
			isAccepting = False  # TODO
			acceptingStr = "+" if isAccepting else "-"
			
			for fromId, toId, char in transitions:
				assert(char in language, f"Unrecognized transition character: {char}")
				file.write(f"{acceptingStr} {fromId} {toId} {char}\n")

			for fromId, toId, char in lambdas:
				assert(char == lambdaChar, f"Lambda char mismatch, found {char} but should be {lambdaChar}")
				file.write(f"{acceptingStr} {fromId} {toId} {char}\n")