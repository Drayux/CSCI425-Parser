import sys

import LL_AST as AST
from Grammar import Grammar
from ParseExceptions import ParseError
from ParseTable import LLParseTable as LLTable
from ParseTable import LRParseTable as LRTable
from ParseTable import ActionType
from ParseTree import ParseTree
from SymbolTable import SymbolAttributes, SymbolTable
from TokenStream import TokenStream
from LR_AST import LR_AST_EOP, LR_AST_SDT_Procedure

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
				# This applies AST procedures for REGEX, turn off if otherwise
				if ast_Tree: AST.AST_SDT_Procedure((curNode))
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
	def __init__(self, grammar, parsetablepath):
		# Grammar can be passed as string to definition or grammar obj itself
		if type(grammar) is not Grammar: grammar = Grammar(grammar)

		self.grammar = grammar						# Grammar definition
		self.parseTable = LRTable(parsetablepath)	# Generate the parse table (TODO), currently just read from file
		# self.symbolTableEmit = symbolTableEmit
		#self.table = LRTable(grammar)

	def next(self, arr, stream = None):
		if type(arr) is not list:
			raise TypeError("Invalid usage of LRParser.next()")

 		# --- Called to get the next item in the stack ---
		if stream is None:
			try: return arr[-1]
			except IndexError: return None
		# ------------------------------------------------

		if type(stream) is not TokenStream:
			raise TypeError("Invalid usage of LRParser.next()")

		# - Otherwise, called to get next item in dequeue -
		# Will always pop for consistency with the TokenStream API
		# Always returns a ParseTree type
		if len(arr) > 0: return arr.pop(0)
		try:
			ret = stream.next()
			tree = ParseTree(ret[0], None)
			tree.aux = ret[1]
			tree.line = ret[2]
			tree.col = ret[3]
			return tree
		except StopIteration: return ParseTree(self.grammar.prodend, None)
		# --------------------------------------------------

	def parse(self, stream: TokenStream, reduce = True):
		stack = [ (0, None) ]		# Stack of state numbers
		queue = []					# Queue of nonterminal transitions (call stream.next() if empty)

		# Every stack element refers to an index in this array for storing intermediate trees
		# trees = [ None for x in range(len(self.table.row)) ]

		symbol = self.next(queue, stream)
		# -- PARSING LOOP --
		while True:
			# Update the state
			state = self.next(stack)

			# DEBUG OUTPUT
			# print("\nSTATE:", state[0])
			# print("SYMBOL:", symbol.data)

			# Get the table value
			action = self.parseTable.getAction(state[0], symbol.data)
			# print("ACTION:", action)		# DEBUG OUTPUT

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
				# -1 offset is to adjust to 1-index of zlang.lr
				rule = self.grammar.ruleList()[action.value - 1]
				length = len(rule[1])
				# print("RULE:", rule)		# DEBUG OUTPUT

				# Create the new rule tree
				tree = ParseTree(rule[0], None)
				states = []

				# Pop as many elements as there were rules
				for x in range(length):
					# Ignore lambdas
					if rule[1][x] == self.grammar.empty: continue
					states.append(stack.pop()[1])

				# Append freshly-popped states
				states.reverse()
				for s in states:
					tree.addChild(s)

				# More debug stuff!
				# print("================================")
				# print(tree)
				# print("================================")

				########################################################################
				########################################################################
				# TODO:
				# Move SDT EOP and symtable stuff out of here, since we don't have any
				#   terminals at this point (need terminals for sym table)

				# Andrew: run sdt here..? should be fine
				if reduce: LR_AST_EOP(tree)

				# Handle symbol table stuff. ~~very~~ slightly less scuffed!
				#print("DATA: {}".format(tree.data))
				#if "emit" in tree.data.lower():
					#self.symbolTable.EmitTable(self.tablePath)

				#elif "lbrace" in tree.data.lower() or "scope:open" in tree.data.lower():
					#self.symbolTable.OpenScope()

				#elif "rbrace" in tree.data.lower() or "scope:close" in tree.data.lower():
					#self.symbolTable.CloseScope()

				#elif "id:" in tree.data.lower():
					#self.symbolTable.EnterSymbol("test", SymbolAttributes("unknown_type"))

				########################################################################
				########################################################################

				queue.insert(0, symbol)		# Put the symbol back into the queue
				symbol = tree

				# Exit the parse if we've reduced the start symbol
				if rule[0] == self.grammar.start:
					# POST PARSE
					# make sure to reduce the final MODULE node
					if reduce: LR_AST_SDT_Procedure(tree)
					return tree

				continue

			# -- NO ACTION --
			# raise ParseError(f"SYNTAX ERROR ({symbol.line}, {symbol.col})")
			print(f"OUTPUT :SYNTAX: {symbol.line} {symbol.col} :SYNTAX:")
			exit(1)

		# Debug testing
		# result = self.table.getAction(10, '$')
		# print("TYPE:", type(result))
		# print(f"RESULT: {result.type} / {result.value}")
		# raise NotImplementedError("LR(0) Parsing (Parser.py)")

	def __str__(self):
		return str(self.parseTable)


# Output now just uses path passed in from main
# def EmitSymbolTable(symbolTable: SymbolTable):
# 	if len(sys.argv) < 3:
# 		print("MISSING SYMBOL TABLE OUTPUT FILE CMDLINE ARG!")
# 		return
# 	with open(sys.argv[3], "w+") as f:
# 		symbolTable.EmitTable(f)

# TABLE TESTING
if __name__ == "__main__":
	treePath = "ZOBOSDEBUG/ast.dat"
	tablePath = "ZOBOSDEBUG/symtable.sym"

	#############################################
	# CHANGE ME TO TEST DIFFERENT TOKEN STREAMS #
	source = "config/zobos/allgood-1.tok"       #
	#############################################

	grammar = Grammar("config/zlang.cfg", False)
	parser = LRParser(grammar, "config/zlang.lr")
	stream = TokenStream(source, True)

	# print("GRAMMAR:")
	# print(grammar)
	#
	# print("LR TABLE:")
	# print(parser)

	tree = parser.parse(stream, False)
	tree.format(sys.stdout)
	# with open(output, "w+") as outf:
	# 	print(f"Sending parse tree to {output}. Execute the following command to view the tree:")
	# 	print(f"cat {output} | ./treevis.py | dot -Tpng -o parse.png")
	# 	tree.format(outf)

	# cst stuff for wreck
	# llgrammar = Grammar("config/regex.cfg")
	# llparser = LLParser(llgrammar)
	# LLstream = TokenStream(r"((\n|\s|\\)|\+0-9(:|\+|<))*(@?>=|<)", False)
	# CSTtree = llparser.parse(LLstream, True)
	# print(CSTtree)
	# end cst stuff for wreck
