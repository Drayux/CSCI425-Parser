class ParseTable:
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
