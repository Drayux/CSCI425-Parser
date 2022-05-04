class TokenStream:
	def __init__(self, input, isPath = False):
		if isPath: self.generator = self.load(input)
		else: self.generator = self.scan(input)
		self.front = None

	# Load a generated token stream from a file
	# Generally for debugging: Specify `isPath = True` for this option
	def load(self, path):
		with open(path, 'r') as inf:
			for line in inf:
				data = line.strip().split()

				ret = [data[0], None, -1, -1]	# Token type
				try:
					ret[1] = data[1]			# Token value
					ret[2] = data[2]			# Line of occurence
					ret[3] = data[3]			# Col of occurence
				except IndexError: pass

				yield ret

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
		elif c == '\\': return ("char", c + stream.pop())
		# end proposed changes
		else: return ("char", c)

	# Generate a regex token stream for parsing with config/regex.cfg
	def scan(self, regex):
		if type(regex) == type(""):
			pass
		else:
			regex = regex.string
		stream = list(regex)
		stream.reverse()

		# Loop through regex string
		while stream:
			token = self.consume(stream)
			yield token

	def next(self):
		self.front = next(self.generator)
		return self.front
