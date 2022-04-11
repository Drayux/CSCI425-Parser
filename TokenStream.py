class TokenStream:
	def __init__(self, path):
		self.generator = self.load(path)
		self.front = None

	def load(self, path):
		with open(path, 'r') as inf:
			for line in inf:
				data = line.strip().split(" ")
				hasValue = True if len(data) > 1 else False
				token = (data[0], None if not hasValue else data[1])
				yield token
		# raise StopIteration

	def next(self):
		self.front = next(self.generator)
		return self.front
