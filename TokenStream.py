class TokenStream:
	def __init__(self, input, isPath = False):
		if isPath: self.generator = self.load(input)
		else:
			self.generator = self.scan(repr(input)[1:-1])
		self.front = None

	# Load a generated token stream from a file
	# Generally for debugging: Specify `isPath = True` for this option
	def load(self, path):
		with open(path, 'r') as inf:
			for line in inf:
				data = line.strip().split()
				hasValue = True if len(data) > 1 else False
				token = (data[0], None if not hasValue else data[1])
				yield token

	# Subroutine of scan():
	# Handles regex operator characters and escape sequences
	def consume(self, stream):
		c = stream.pop()
		if c == '|': return ("pipe", '|')
		elif c == '*': return ("kleene", '*')
		elif c == '+': return ("plus", '+')
		elif c == '(': return ("open", '(')
		elif c == ')': return ("close", ')')
		elif c == '.': return ("dot", '.')
		elif c == '-': return ("dash", '-')
		# Proposed changes
		elif c == '\\':
			nextCharacter = stream.pop();
			return ("char", "\\" + nextCharacter)
		# end proposed changes
		else: return ("char", c)

	# Generate a regex token stream for parsing with config/regex.cfg
	def scan(self, string):
		stream = list(string)
		stream.reverse()

		# Loop through regex string
		while stream:
			token = self.consume(stream)
			yield token

	def next(self):
		self.front = next(self.generator)
		return self.front


