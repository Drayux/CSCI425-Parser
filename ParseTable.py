class ParseTable:
	def __init__(self, grammar):
		self.data = None                # Renamed from table
		self.row_labels = []            # Renamed from N_indexes
		self.col_labels = []            # Renamed from T_indexes

		self.create_labels(grammar)     # Renamed from fill_indices
		self.populate(grammar)          # Renamed from fill_table
		# self.table = ([None] * len(self.T_indexes)) * len(self.N_indexes)

	def create_labels(self, grammar):
		for N in grammar.cfg.keys():
			self.row_labels.append(N)

		for T in grammar.terminals:
			self.col_labels.append(T)
		self.col_labels.sort()

	def populate(self, grammar):
		# N = G.cfg.keys()
		# for A in N:
		#    A_index = self.N_indexes.index(A)
		#    for p in G.cfg[A]:
		#        for a in G.predict_set(p):
		#            a_index = self.T_indexes.index(a)
		#            self.table[A_index][a_index] = p

		self.data = [[-1] * len(self.col_labels) for i in range(len(self.row_labels))]
		for i in range(0, len(grammar.rules)):
			A, RHS = grammar.rules[i]
			A_index = self.row_labels.index(A)
			a_list = grammar.get_predict_set((A, RHS))

			# print((A, RHS))
			# print(a_list)

			if a_list == None:
				continue

			for a in a_list:
				a_index = self.col_labels.index(a)
				self.data[A_index][a_index] = i

	# Return the production rule respective to the non-terminal and terminal entries
	def get_production(self, nonterminal, terminal):
		row = self.row_labels.index(nonterminal)
		column = self.col_labels.index(terminal)
		return self.data[row][column]

	# Output the production table
	def __str__(self):
		# Print column labels
		ret = "\t  ||\t"
		for label in self.col_labels:
			if label == 'lambda': continue
			ret += f"{label}\t"
		ret += "\n"

		# Seperator bar
		for x in range(len(self.col_labels) + 1):
			ret += "========"
		ret += "\n"

		# Print the rows
		for x, row in enumerate(self.data):
			label = self.row_labels[x]
			ret += f"{label}\t  ||\t"

			# Row data
			for y, val in enumerate(row):
				if self.col_labels[y] == 'lambda': continue
				ret += f"{'-' if val < 0 else val}\t"

			ret += "\n"

		return ret
