class ParseTree:
	def __init__(self, data, parent, pos = (0, 0)):
		self.data = data
		self.aux = ""
		(self.line, self.col) = pos
		self.parent = parent
		self.children = []

	# Adds child in the rightmost location
	# Returns the new child
	def addChild(self, data):
		if type(data) == ParseTree:
			data.parent = self
			self.children.append(data)
			return data

        # Else
		node = ParseTree(data, self)
		self.children.append(node)
		return node

	def removeChild(self, child):
        # Perhaps add a try-catch?
		self.children.remove(child)

	# Retrieves the child in the rightmost location
	def getChild(self):
		return self.children[-1]

	# Depth is str to represent parent association
	def output(self, depth):
		# Recursive base case - node is a leaf if no children
		if len(self.children) == 0: return ""

		ret = "\n"
		# Print the value of each child node
		for x, child in enumerate(self.children):
			ret += f"{depth}:{x} -> {child.data}\n"

		# Recursively call each child
		for x, child in enumerate(self.children):
			ret += child.output(depth + f":{x}")

		return ret

	# Write tree to file (moved from ParseTreeDebug)
	def format(self, output):
		# Node generation
		queue = []
		queue.append(self)
		visited = set()
		visited.add(self)
		counter = 0
		nodeMap = {}
		while len(queue) > 0:
			node = queue.pop(0)

			if node.data == "\\\\":
				node.data = "BAD NODE DATA: DOUBLE BACK SLASH"

			output.write("node{} {}\n".format(counter, node.data))
			nodeMap[node] = "node{}".format(counter)
			counter += 1

			for child in node.children:
				if child not in visited:
					visited.add(child)
					queue.append(child)

		# Edge generation
		queue.append(self)
		visited = set()
		visited.add(self)
		while len(queue) > 0:
			node = queue.pop(0)
			if len(node.children) > 0:
				output.write("\n{}".format(nodeMap[node]))
			for child in node.children:
				if child not in visited:
					visited.add(child)
					queue.append(child)

					output.write(" {}".format(nodeMap[child]))

		# Final newline
		output.write("\n")

	# Not the prettiest output but good enough for testing
	def __str__(self):
		return f"ROOT: {self.data}\n" + self.output("RT")

# Some tree output debugging code
if __name__ == "__main__":
	tree = ParseTree("ooga", None)
	tree.add_child("booga")
	child = tree.get_child()
	child.add_child("mr krabs")
	child.add_child("has nice hair")

	tree.add_child("my")
	tree.add_child("tortuga")
	child = tree.get_child()
	child.add_child("SPICY")

	print(tree)
	exit()
