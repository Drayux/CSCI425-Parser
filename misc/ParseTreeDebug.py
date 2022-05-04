# Moved out of debug.py to prevent circular import error.

def format_parse_tree(output, tree):
	# Node generation
	queue = []
	queue.append(tree)
	visited = set()
	visited.add(tree)
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
	queue.append(tree)
	visited = set()
	visited.add(tree)
	while len(queue) > 0:
		node = queue.pop(0)
		if len(node.children) > 0:
			output.write("\n{}".format(nodeMap[node]))
		for child in node.children:
			if child not in visited:
				visited.add(child)
				queue.append(child)

				output.write(" {}".format(nodeMap[child]))