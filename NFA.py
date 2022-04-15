from ParseTree import ParseTree

# Subcomponent classes specific to the NFA Table class
# Dynamically adds rows and columns as necessary
class TransitionTable:
	def __init__(self):
		pass

	def addTransition(self, from: int, to: int):
		pass

class NFATable:
	def __init__(self, tree: ParseTree):
		self.transitions = TransitionTable()	# Standard state transitions
		self.lambda = TransitionTable()			# Lambda state transitions

		# -- TODO --

	# Add a normal transition
	def addTransition(self, from, to):
		self.transitions.addTransition(from, to)

	# Add a normal transition
	def addLambda(self, from, to):
		self.lambda.addTransition(from, to)
