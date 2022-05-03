import sys

import LL_AST as AST
from Grammar import Grammar
from ParseExceptions import ParseError
from ParseTable import LLParseTable as LLTable
from ParseTable import LRParseTable as LRTable
from ParseTable import ActionType
from ParseTree import ParseTree
from TokenStream import TokenStream

# DEFINE LL AND LR PARSER CLASSES

# LL(1) Parser
class LLParser:
	def __init__(self, grammar):
		# Grammar can be passed as string to definition or grammar obj itself
		if type(grammar) is not Grammar: grammar = Grammar(grammar)

		self.grammar = grammar					# Grammar definition
		self.table = LLTable(grammar)			# Generate the parse table

	# LL parsing algorithm
	def parse(self, stream: TokenStream, ast_Tree = False):
		token = stream.next()[0]

		symbols = [self.grammar.start]			# This is the stack of tokens
		line = 1								# Current line of token stream
		tree = ParseTree("ROOT", None)			# Final parse tree
		curNode = tree							# Active tree node

		rules = self.grammar.ruleList()

		# Continue parsing nodes until the queue is empty
		while len(symbols) > 0:
			symbol = symbols.pop()
			# token = stream.front[0]      # Token value not currently necessary

			# Debug output
			# print("STACK: ", symbols)
			# print("FROM STACK: ", symbol)
			# print("QUEUE: ", tokens)
			# print("FROM QUEUE: ", token)
			# print()

			# Check for end of production marker
			if symbol == '*':
				if ast_Tree: AST.AST_SDT_Procedure((curNode)) # This applies AST procedures for REGEX, turn off if otherwise
				curNode = curNode.parent
				continue

			# Check if the stack is a terminal and continue
			if symbol in self.grammar.terminals:
				if symbol == self.grammar.empty:
					curNode.addChild(symbol)
					continue

				if symbol == token:
					# Remove the terminal from the queue
					############################################################
					# NOTE: I have changed this from wreck. Parse trees now
					#		have an aux parameter to store identifiers
					#		Be careful using other grammars with a 'char' token
					aux = stream.front[1]
					############################################################
					lasttok = token
					try: token = stream.next()[0]
					except StopIteration: token = self.grammar.prodend

					line += 1
					curNode.addChild(lasttok)
					curNode.getChild().aux = aux
					continue

				# Terminals do not line up
				# print("SYNTAX ERROR!")
				# print(f"Parser expected '{symbol}' but got '{token}' (Line {line})")
				# return None		# return tree for debug
				raise ParseError(f"SYNTAX ERROR: Parser expected '{symbol}' but got '{token}' (Line {line})")

			# If no token, there was a syntax error
			# This condition should be impossible
			if token is None:
				# print("SYNTAX ERROR!")
				# print(f"Unexpected end of token stream (Line {line})")
				# return None 	# return tree for debug
				raise ParseError(f"SYNTAX ERROR: Unexpected end of token stream (Line {line})")

			# Get the next production rule from the table
			try: rule_i = self.table.getProduction(symbol, token)
			except ValueError:
				# print("PARSING ERROR!")
				# print(f"Symbol '{token}' not defined in this grammar (Line {line})")
				# return None
				raise ParseError(f"PARSING ERROR: Symbol '{token}' not defined in this grammar (Line {line})")
			LHS, RHS = rules[rule_i]

			# More debug
			# print("RULE: ", LHS, " -> ", RHS)

			# Add the new rule to the stack
			symbols.append('*')                         # End of production marker
			for r in reversed(RHS):
				symbols.append(r)

			# Update the tree
			curNode = curNode.addChild(LHS)

		if curNode != tree:
			# print("SYNTAX ERROR!")
			raise ParseError(f"SYNTAX ERROR: Mismatched end of production (Line {line})")
		AST.AST_SDT_Procedure(tree)
		return tree

	def __str__(self):
		return str(self.table)


# LR(0) Parser
class LRParser:
	def __init__(self, grammar, tablepath):
		# Grammar can be passed as string to definition or grammar obj itself
		if type(grammar) is not Grammar: grammar = Grammar(grammar)

		self.grammar = grammar					# Grammar definition
		self.table = LRTable(tablepath)
		# self.table = LRTable(grammar)			# Generate the parse table (TODO), currently just read from file

	def next(self, arr, stream = None):
		if type(arr) is not list:
			raise TypeError("Invalid usage of LRParser.next()")

 		# - Called to get the next item in the stack -
		if stream is None:
			try: return arr[-1]
			except IndexError: return None
		# --------------------------------------------

		if type(stream) is not TokenStream:
			raise TypeError("Invalid usage of LRParser.next()")

		# Otherwise, called to get next item in dequeue
		# Will always pop for consistency with the TokenStream API
		# Always returns a ParseTree type
		if len(arr) > 0: return arr.pop(0)
		try:
			ret = stream.next()
			return ParseTree(ret[0], None)
		except StopIteration: return ParseTree(self.grammar.prodend, None)
		# ----------------------------------------------

	def parse(self, stream: TokenStream):
		stack = [ (0, None) ]		# Stack of state numbers
		queue = []					# Queue of nonterminal transitions (call stream.next() if empty)

		# Every stack element refers to an index in this array for storing intermediate trees
		# trees = [ None for x in range(len(self.table.row)) ]

		symbol = self.next(queue, stream)
		# -- PARSING LOOP --
		while True:
			# Update the state
			state = self.next(stack)

			# DEBUG INFO
			print("\nSTATE:", state[0])
			print("SYMBOL:", symbol.data)

			# Get the table value
			action = self.table.getAction(state[0], symbol.data)
			print("ACTION:", action)

			# try: action = self.table.getAction(state[0], symbol.data)
			# except StopIteration:
			# 	if type(symbol) is ParseTree and symbol.data == self.grammar.start: return symbol
			# 	raise ParseError("SYNTAX ERROR (1)")

			# -- SHIFT ACTION --
			if action.type == ActionType.SHIFT:
				# Build the tuple for the stack
				knit = (action.value, symbol)
				stack.append(knit)			# Push state onto stack (TODO: what if duplicate state??)

				# Pop the queue
				symbol = self.next(queue, stream)
				continue

			# -- REDUCE ACTION --
			if action.type == ActionType.REDUCE:
				# Get the production rule
				rule = self.grammar.ruleList()[action.value]
				length = len(rule[1])
				print("RULE:", rule)

				# Create the new rule tree
				tree = ParseTree(rule[0], None)
				states = []

				# Pop as many elements as there were rules
				for x in range(length):
					states.append(stack.pop()[1])

				# Append freshly-popped states
				states.reverse()
				for s in states:
					tree.addChild(s)

				print("================================")
				print(tree)
				print("================================")

				queue.insert(0, tree)
				symbol = self.next(queue, stream)

				# Exit the parse if we've reduced the start symbol
				if rule[0] == self.grammar.start: return tree
				continue

			# -- NO ACTION --
			raise ParseError("SYNTAX ERROR (No S/R action)")

		# Debug testing
		# result = self.table.getAction(10, '$')
		# print("TYPE:", type(result))
		# print(f"RESULT: {result.type} / {result.value}")
		# raise NotImplementedError("LR(0) Parsing (Parser.py)")

	def __str__(self):
		return str(self.table)


# TABLE TESTING
if __name__ == "__main__":
	grammar = Grammar("config/zlang.cfg", False)
	parser = LRParser(grammar, "config/zlang.lr")
	stream = TokenStream("config/zobos/allgood-1.tok", True)

	# print("GRAMMAR:")
	# print(grammar)

	# print("LR TABLE:")
	# print(parser)

	tree = parser.parse(stream)
	print(tree)

	# cst stuff for wreck
	# llgrammar = Grammar("config/regex.cfg")
	# llparser = LLParser(llgrammar)
	# LLstream = TokenStream(r"((\n|\s|\\)|\+0-9(:|\+|<))*(@?>=|<)", False)
	# CSTtree = llparser.parse(LLstream, True)
	# print(CSTtree)
	# end cst stuff for wreck
