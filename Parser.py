import sys
from Grammar import Grammar
from ParseExceptions import ParseError
from ParseTable import LLParseTable as LLTable
from ParseTable import LRParseTable as LRTable
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
	def parse(self, stream: TokenStream):
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
					# NOTE: This seems to be specific to the regex grammar
					#		Be careful using other grammars with a 'char' token
					if token == 'char': lasttok = stream.front[1]
					############################################################
					else: lasttok = token
					try: token = stream.next()[0]
					except StopIteration: token = self.grammar.prodend

					line += 1
					curNode.addChild(lasttok)
					continue

				# Terminals do not line up
				print("SYNTAX ERROR!")
				print(f"Parser expected '{symbol}' but got '{token}' (Line {line})")
				return None		# return tree for debug

			# If no token, there was a syntax error
			# This condition should be impossible
			if token is None:
				print("SYNTAX ERROR!")
				print(f"Unexpected end of token stream (Line {line})")
				return None 	# return tree for debug

			# Get the next production rule from the table
			try: rule_i = self.table.getProduction(symbol, token)
			except ValueError:
				print("PARSING ERROR!")
				print(f"Symbol '{token}' not defined in this grammar (Line {line})")
				return None
			LHS, RHS = rules[rule_i]

			# More debug
			# print("RULE: ", LHS, " -> ", RHS)

			# Add the new rule to the stack
			symbols.append('*')                         # End of production marker
			for r in reversed(RHS):
				symbols.append(r)

			# Update the tree
			curNode = curNode.addChild(LHS)

		if curNode != tree: print("SYNTAX ERROR!")
		return tree

	def __str__(self):
		return str(self.table)


# LR(0) Parser
class LRParser:
	def __init__(self, path):
		# Grammar can be passed as string to definition or grammar obj itself
		if type(grammar) is not Grammar: grammar = Grammar(grammar)

		self.grammar = grammar					# Grammar definition
		# self.table = LRTable(self.grammar)		# Generate the parse table (TODO), currently just read from file
		self.table = LRTable(path)

	def parse(self, stream: TokenStream):
		raise NotImplementedError("LR(0) Parsing (Parser.py)")

	def __str__(self):
		return str(self.table)
