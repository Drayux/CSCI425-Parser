from copy import copy
from io import TextIOWrapper
from ParseTree import ParseTree

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

	# Opted to remove this one as I'm just storing it as a member variable
	# def rowCount(self):
	# 	return -1


class NFATable:
	def __init__(self, tree: ParseTree):
		self.T = TransitionTable()			# Standard state transitions
		self.L = TransitionTable()			# Lambda state transitions

		# -- TODO --

	# Add a normal transition
	def addTransition(self, fromId, toId, char):
		self.T.addTransition(fromId, toId, char)

	# Add a lambda transition
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

		nodeCount = self.T.rowCount
		languageString = language.join(" ")

		file.write(f"{nodeCount} {lambdaChar} {languageString}\n")
		for i in range(nodeCount):
			transitions = self.T.getRow(i)
			lambdas = self.L.getRow(i)
			isAccepting = False  # TODO
			acceptingStr = "+" if isAccepting else "-"

			for fromId, toId, char in transitions:
				# assert(char in language, f"Unrecognized transition character: {char}")
				file.write(f"{acceptingStr} {fromId} {toId} {char}\n")

			for fromId, toId, char in lambdas:
				# assert(char == lambdaChar, f"Lambda char mismatch, found {char} but should be {lambdaChar}")
				file.write(f"{acceptingStr} {fromId} {toId} {char}\n")


# Code testing
if __name__ == "__main__":
	print("EMPTY:")
	table = TransitionTable()
	print(table)
	print()

	# Add some transitions
	table.addTransition(1, 1)
	table.addTransition(3, 6)
	table.addTransition(1, 4, 'a')
	table.addTransition(5, 4, 'b')
	table.addTransition(3, 3, 'c')
	table.addTransition(0, 1, 'd')
	table.addTransition(0, 1, 'e')
	table.addTransition(2, 0, 'f')

	print("\nMODIFIED:")
	print(table)
	print()

	print("\nROWS:")
	for x in range(table.rowCount):
		print("row:", x)
		print(table.getRow(x))
