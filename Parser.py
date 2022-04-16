import sys

import AST
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
					# NOTE: This is specific to the regex grammar
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

	def parse(self, stream: TokenStream):
		result = self.table.getAction(9, 'a')
		print("TYPE:", type(result))
		print(f"RESULT: '{result}'")
		# raise NotImplementedError("LR(0) Parsing (Parser.py)")

	def __str__(self):
		return str(self.table)


# TABLE TESTING
if __name__ == "__main__":
	grammar = Grammar("assignments/LGA-22/fischer-4-1.cfg")
	parser = LRParser(grammar, "assignments/LGA-22/cytron-67.lr")
	stream = TokenStream("assignments/LGA-22/fischer-4-1t_src.tok")

	print("GRAMMAR:")
	print(grammar)

	print("LR TABLE:")
	print(parser)

	tree = parser.parse(stream)
	print(tree)

	# cst stuff for wreck
	llgrammar = Grammar("config/regex.cfg")
	llparser = LLParser(llgrammar)
	LLstream = TokenStream(r"((\n|\s|\\)|\+0-9(:|\+|<))*(@?>=|<)", False)
	CSTtree = llparser.parse(LLstream, True)
	print(CSTtree)
	# end cst stuff for wreck