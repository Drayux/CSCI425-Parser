import sys
from ParseExceptions import GrammarError as ConfigError
from ParseTree import ParseTree
from TokenStream import TokenStream
# from ParseTable import ParseTable as Table

# Set/List utility function (that isn't natively included for some reason?)
def find(s, i):
	arr = None
	if type(s) is list: arr = s
	elif type(s) is set:
		arr = [x for x in s]
	else: raise TypeError("Cannot retrieve elements from non-set type")

	for x in arr:
		if x == i:
			return x

	return None


# Grammar class
# Contains set of grammar production rules and preliminary parse operations
# If third parameter is true, grammar is LR (else LL assumed)
class Grammar:
	def __init__(self, path, LL = False):
		self.rules = {}                                 # Dict of lists of nonterminals/symbols
		self.empty = 'lambda'                           # Name of empty rule character (as seen in the config file)
		self.prodend = '$'                              # Character representing the end of production
		self.start = None                               # Name of entry rule
		self.nonterminals = []                          # Set of non-terminals (strings) : Keys of rules dict
		self.terminals = { self.empty, self.prodend }   # Set of terminals (strings)

		# Elements that must be generated
		self.emptySet = None        					# Derives to lambda set
		self.firstSet = {}          					# Dict of first sets
		self.followSet = {}         					# Dict of follow sets
		self.predictSet = []        					# Arr of predict sets

		try: self.load(path, True)
		except ConfigError as ce:
			print("CONFIG ERROR:", ce)
			exit(1)

		# Grammar is LL and these are necessary
		if LL:
			self.calcEmpty()
			self.calcFirst()
			self.calcFollow()
			self.calcPredict()

		# Grammar is LR and this is necessary
		else:
			# TODO TABLE GENERATION
			pass

	def __str__(self):
		# ret = "-- GRAMMAR --\n"
		ret = ""
		if self.start is None:
			ret += "EMPTY"
			return ret

		# Start symbol
		ret += f"START: {self.start}\n"

		# Grammar rules
		ruleno = 0
		for nt in self.nonterminals:
			for rule in self.rules[nt]:
				ret += f"  {ruleno} : \t{nt} ->"
				ruleno += 1

				for symbol in rule: ret += f" {symbol}"
				ret += "\n"

		# Nonterminals
		ret += "\nTERMINALS:\n "
		for t in self.terminals: ret += f" {t}"

		# Terminals
		ret += "\n\nNON-TERMINALS:\n "
		for t in self.nonterminals: ret += f" {t}"
		ret += "\n"

		return ret

	# Loads a grammar from a configuration file
	# strict -> Should the rules follow strict naming convention (nonterms must contain a capital)
	def load(self, path, strict = False):
		config = None
		with open(path, "r") as inf: config = [l.strip().split() for l in inf]

		# Create a list of all of the nonterminal symbols
		# Nonterminals defined as anything that precedes an arrow ( -> )
		lineCount = 0
		for rule in config:
			lineCount += 1                  # For accurate error messages
			symbol = None
			try:
				symbol = rule[1]
				if symbol[0] == '#':		# Comment
					continue
			except IndexError: continue     # Empty line

			# Line contains a rulename
			if symbol == '->':
				symbol = rule[0]

				# Check for strict formatting rules
				if strict and symbol == symbol.lower():
					raise ConfigError(f"Nonterminal '{symbol}' does not contain a capital letter ({path}: line {lineCount})")

				# Check for invalid characters...could be revised with stricter formatting
				if symbol == '->' or symbol == '|' or symbol == self.empty or symbol == self.prodend:
					raise ConfigError(f"Unexpected symbol '{symbol}' at start of line {lineCount} ({path})")

				tmp = find(self.nonterminals, symbol)
				if tmp is None:
					self.nonterminals.append(symbol)
					self.rules[symbol] = []

		# Debug output
		# print(self.nonterminals)

		# Build the dict of grammar rules
		rulename = None     # Key under which to place rules in the grammar dictionary
		for lc, rule in enumerate(config):
			# Empty line, skip
			if len(rule) == 0 or rule[0][0] == '#': continue
			symbol = rule.pop(0)

			# Rule with explicit name
			if symbol in self.nonterminals:
				# Check length (Needs to be at least 3, but we popped the first element)
				if len(rule) < 2: raise ConfigError(f"Invalid rule ({path}: line {lc + 1})")
				rule.pop(0)     # Next token will be an arrow
				rulename = symbol

			# Config file syntax checking
			elif symbol != '|':
				raise ConfigError(f"Unexpected symbol '{symbol}' at start of line {lc + 1} ({path})")

			# Iterate through the rest of the line
			# Determine token type (operator, non-terminal, or symbol)
			rewrite = []        # Actual rule associated with the rulename
			for token in rule:
				pointer = None

				# Alternation: Save the new rule
				if token == '|':
					if len(rewrite) == 0:
						raise ConfigError(f"Zero-length rule in line {lc + 1} ({path})")

					self.rules[rulename].append(rewrite)
					rewrite = []
					continue

				# End or production: Save rule as start goal
				if token == self.prodend:
					if self.start is not None and self.start != rulename:
						raise ConfigError(f"Multiple start symbols '{rulename}' and '{self.start}' ({path}: line {lc + 1})")
					elif self.start is None: self.start = rulename

					# Use the same pointer
					rewrite.append(self.prodend)
					continue

				# Lambda rule: Can later be expanded to use special lamda char
				if token == self.empty:
					if len(rewrite) > 0:
						raise ConfigError(f"Unexpected lambda in nonempty rewrite rule ({path}: line {lc + 1})")

					rewrite.append(self.empty)
					break

				# -- APPEND THE RULE COMPONENT --
				# Find the item in the set to return the same pointer, prevents memory duplicates
				pointer = find(self.nonterminals, token)

				# If nothing, token was a terminal
				if pointer is None:
					if strict and (token != token.lower()):
						raise ConfigError(f"Terminal '{token}' contains a capital letter ({path}: line {lc + 1})")

					self.terminals.add(token)
					pointer = find(self.terminals, token)

				rewrite.append(pointer)

			if len(rewrite) == 0:
				raise ConfigError(f"Zero-length rule in line {lc + 1} ({path})")
			self.rules[rulename].append(rewrite)

		# Ensure that the start rule is configured correctly
		if self.start is None: raise ConfigError(f"Grammar has no start symbol")
		for rule in self.rules[self.start]:
			symbol = rule[-1]
			if symbol != self.prodend:
				raise ConfigError(f"Inconsistent end of production rules, symbol: '{self.start}'")

	# Returns an array of tuples the production rules in order
	# *I should have thought to write this sooner: Might be worth refactoring some code*
	def ruleList(self):
		rules = []
		for nt in self.nonterminals:
			for rule in self.rules[nt]:
				rules.append((nt, rule))
		return rules

	# Returns True if the specified state number is an accepting state
	def isAccept(self, x):
		l = self.ruleList()
		if l[x][0] == self.start: return True
		return False

	# Subroutine of symbolEmpty()
	def ruleEmpty(self, rule, empty, nonempty, ignore):
		for token in rule:
			if token == self.empty: return True
			if token in self.terminals: return False

			# Else it's a nonterminal
			if not self.symbolEmpty(token, empty, nonempty, ignore): return False
		return True

	# Subroutone of calcEmpty()
	def symbolEmpty(self, symbol, empty, nonempty, ignore):
		if symbol in empty: return True
		if symbol in nonempty: return False
		if symbol in ignore: return False

		ignore.add(symbol)
		for rule in self.rules[symbol]:
			if self.ruleEmpty(rule, empty, nonempty, ignore):
				empty.add(symbol)
				return True

		nonempty.add(symbol)
		return False

	# Calculate the derives to lambda set
	def calcEmpty(self):
		empty = set()
		nonempty = set()

		# Symbol empty automatically adds the nonterminal to the respecitve set
		for nt in self.nonterminals:
			self.symbolEmpty(nt, empty, nonempty, set())

		self.emptySet = empty

	# Subroutine of calcFirst() and calcFollow()
	def ruleFirst(self, rule, ignore = set()):
		first = set()
		for token in rule:
			# Skip if lambda
			if token == self.empty:
				break

			# Terminal
			if token in self.terminals:
				first.add(token)
				break

			# Non-terminal
			if token not in self.firstSet: self.symbolFirst(token, ignore)
			first = first | self.firstSet[token]

			# Check if non-terminal derives to lambda
			if token not in self.emptySet: break
		return first

	# Subroutine of calcFirst()
	def symbolFirst(self, symbol, ignore = set()):
		if symbol in ignore:
			raise ConfigError(f"Grammar has left recursion in nonterminal '{symbol}'")

		first = set()
		for rule in self.rules[symbol]:
			first = first | self.ruleFirst(rule, ignore | { symbol })

		self.firstSet[symbol] = first

	# Calculate the first sets
	def calcFirst(self):
		for nt in self.nonterminals:
			if nt in self.firstSet: continue
			self.symbolFirst(nt)

	# Subroutine of calcFollow()
	def symbolFollow(self, symbol, ignore = set()):
		# DEBUG OUTPUT
		# print("Following:", symbol)
		# print("Ignore:", ignore)

		follow = set()
		if symbol in ignore:
			self.followSet[symbol] = follow
			return

		# Find all rule occurences of the nonterminal
		for nt in self.nonterminals:
			for rule in self.rules[nt]:
				for x, token in enumerate(rule):
					if token == symbol:
						arr = rule[(x + 1):]
						follow = follow | self.ruleFirst(arr)

						# Check if the follow set of another nonterminal must be added
						atEnd = True
						for x in arr:
							if x not in self.emptySet:
								atEnd = False
								break

						if atEnd:
							if nt not in self.followSet: self.symbolFollow(nt, ignore | { symbol })
							follow = follow | self.followSet[nt]
						break

		self.followSet[symbol] = follow

	# Calculate the follow sets
	def calcFollow(self):
		for nt in self.nonterminals:
			self.symbolFollow(nt)

	# Calculate the predict sets
	def calcPredict(self):
		for nt in self.nonterminals:
			for rule in self.rules[nt]:
				predict = self.ruleFirst(rule)

				# Determine if rule derives to lambda
				# (Had I known this routine beforehand I would have formatted calcEmpty differnetly)
				empty = True
				for token in rule:
					if token != self.empty and token not in self.emptySet:
						empty = False
						break

				if empty: predict = predict | self.followSet[nt]
				self.predictSet.append(predict)


if __name__ == "__main__":
	pathgrammar = sys.argv[1]
	pathtokens = sys.argv[2]
	#path = 'llre.cfg'
	grammar = Grammar(pathgrammar)
	tree = grammar.parse(pathtokens)

	print(grammar)
	print(tree)
