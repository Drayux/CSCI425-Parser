from enum import Enum
import sys

# DEFINE LL AND LR PARSE TABLES

# Table for LL(1) parser
class LLParseTable:
	def __init__(self, grammar):
		# if type(grammar) is not Grammar.Grammar:
		# 	raise TypeError(f"Parse Table expects Grammar type but got '{type(grammar)}'")

		self.data = None                # Renamed from table
		self.rowLabels = []            # Renamed from N_indexes
		self.colLabels = []            # Renamed from T_indexes
		self.empty = grammar.empty

		self.createLabels(grammar)      # Renamed from fill_indices
		self.populate(grammar)          # Renamed from fill_table

	def createLabels(self, grammar):
		for nt in grammar.nonterminals:
			self.rowLabels.append(nt)

		for term in grammar.terminals:
			self.colLabels.append(term)
		self.colLabels.sort()

	def populate(self, grammar):
		self.data = [[-1] * len(self.colLabels) for i in range(len(self.rowLabels))]

		ruleno = 0
		for nt in grammar.nonterminals:
			row_i = self.rowLabels.index(nt)

			for rule in grammar.rules[nt]:
				predict = grammar.predictSet[ruleno]
				for terminal in predict:
					col_i = self.colLabels.index(terminal)
					self.data[row_i][col_i] = ruleno

				ruleno += 1

	# Return the production rule respective to the non-terminal and terminal entries
	def getProduction(self, nonterminal, terminal):
		row = self.rowLabels.index(nonterminal)
		column = self.colLabels.index(terminal)
		return self.data[row][column]

	# Output the production table
	def __str__(self):
		# Print column labels
		ret = "\t  ||\t"
		for label in self.colLabels:
			if label == self.empty: continue
			ret += f"{label}\t"
		ret += "\n"

		# Seperator bar
		for x in range(len(self.colLabels) + 1):
			ret += "========"
		ret += "\n"

		# Print the rows
		for x, row in enumerate(self.data):
			label = self.rowLabels[x]
			ret += f"{label}\t  ||\t"

			# Row data
			for y, val in enumerate(row):
				if self.colLabels[y] == self.empty: continue
				ret += f"{'-' if val < 0 else val}\t"

			ret += "\n"
		return ret


class ActionType(Enum):
	NONE = 0
	SHIFT = 1
	REDUCE = 2

class LRAction():
	# def __init__(self, action = ActionType.NONE, value = -1):
	def __init__(self, string):
		self.type = ActionType.NONE
		self.value = -1
		self.convert(string)

	# Convert a table string (ex: 'sh-2') into the respective Action and Value elements
	def convert(self, string):
		if len(string) == 0: return

		values = [s.lower() for s in string.split('-')]
		if not (len(values) == 2):
			print("WARNING: SLR table has invalid format; Entry skipped.")
			return

		state = None
		try: state = int(values[1])
		except ValueError:
			print("WARNING: SLR table has invalid format; Entry skipped.")
			return

		self.value = state

		# Shift action
		if values[0] == "sh": self.type = ActionType.SHIFT
		elif values[0] == "r": self.type = ActionType.REDUCE
		else: print("WARNING: SLR table has invalid format; Entry skipped.")

	# Convert back into string format
	def __str__(self):
		ret = None

		if self.type == ActionType.NONE: return ""
		elif self.type == ActionType.SHIFT: ret = "sh-"
		elif self.type == ActionType.REDUCE: ret = "r-"

		ret += str(self.value)
		return ret

# Table for LR(0) parser
class LRParseTable:
	def __init__(self, file):
		"""
		:param file: Can be the string to a file or a file object
		# Parse Table initialization
			The LR(0) parse table will take in a file of .lr type
			and create a LR table from it. It can take a file name
			as a string or as an actual file object.
		"""
		self.data = None                # Renamed from table
		self.row = []                   # This is the PARSING STATES
		self.colLabels = []				# This is the GRAMMAR SYMBOLS
		self.grammarMap = dict()        # This will come in handy for the interface
		# TODO: self.empty = grammar.empty

		# Nifty little guy to read a string or a file object
		if(type(file) == str):
			with open(file, 'r') as f: self.parseFile(f)

		# Get all the things from the *.lr file
		else: self.parseFile(file)

	def parseFile(self, file):
		result_list = []
		# open file and put it in an array of lines
		with open(file) as f:
			lines = f.readlines()

			# Read in the first line with all the grammar symbols
			line = lines[0]
			items = line.split(',')
			items[-1] = items[-1].replace("\n", "")  # remove newline if exists
			for i in range(len(items)):
				if items[i] == '.':
					continue
				else:
					self.colLabels.append(items[i])
					self.grammarMap[items[i]] = i-1

			# Read in the following lines to get all the parsing states
			for i, line in enumerate(lines):
				if i == 0:
					continue
				items = line.split(',')
				items[-1] = items[-1].replace("\n", "")  # remove newline if exists

				row = []
				for j in range(1, len(items)):
					row.append(LRAction(items[j]))
				self.row.append(row)

	def getAction(self, state, grammar_symbol: str = "f"):
		"""
		:param state: a tuple<int,str> or integer
		:param grammar_symbol: a string or empty if state is a tuple
		:return: a string representing parsing action in the LR table

		# Parse Table Lookup
			The getAction function will return the
			appropriate action. The function will accept a tuple
			of type <int, str> or can accept two parameters of type
			int and of type str

			Example:
			tup = (0, "f")
			print(lrTable.getAction(tup))
			print(lrTable.getAction(0, "f")
		"""
		row = state
		col = self.grammarMap[grammar_symbol]

		if type(state) is tuple:
			row = state[0]
			col = self.grammarMap[state[1]]

		try: return self.row[row][col]
		except IndexError: raise StopIteration		# Start symbol reached

		## This part is now deprecated ##
		if ret == '':
			ret = "ERROR"
		return ret
		#################################

	# Output the production table
	def __str__(self):
		"""
		This does not print out the best,
		but its good enough for government work
		:return: a table of the LR table when asked to print
		"""
		# Print column labels
		ret = "\t   ||\t"
		for label in self.colLabels:
			if label == 'lambda': continue
			ret += f"{label}\t"
		ret += "\n"

		# Seperator bar
		for x in range(len(self.colLabels) + 2):
			ret += "========"
		ret += "\n"

		# Print the rows
		for linenum, line in enumerate(self.row):
			ret += f"{linenum}\t   ||\t"
			for item in line:
				ret += f"{'-' if item.type == ActionType.NONE else str(item)}\t"
			ret += "\n"

		return ret


if __name__ == "__main__":
	# Optional testing/debug output
	print("TODO DEBUG STUFF")

	# -- LR TABLE DEBUG 11 --
	if len(sys.argv) < 2: input = "config/fisher-4-1/fischer-4-1.lr"
	else: input = sys.argv[1]

	lrTable = ParseTable_LR(input)

	print(lrTable)
	print(lrTable.getAction.__doc__)
