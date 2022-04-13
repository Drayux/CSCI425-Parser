import sys
from Grammar import Grammar

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


# MAIN
# config -> Path to language definition file
# stream -> Regex expression (TODO: or path - perhaps add another parameter?)
# output -> Output file for tree visualization
def main(config, stream = None, output = None):
	grammar = Grammar(config)
	print("  -- GRAMMAR --")
	print(grammar)

	##########################################
	print("\n  -- PREDICTION --")

	# Output which non-terminals derive to lambda
	print("Derives to lambda:\n  ", end = "")
	for token in grammar.emptySet: print(token, end = " ")
	print()

	# Output first sets of all non-terminals
	print("\nFirst sets:")
	for key in grammar.nonterminals:
		print(f"  {key} :", end = "\t")
		print(grammar.firstSet[key])

	# Output follow sets of all non-terminals
	print("\nFollow sets:")
	for key in grammar.nonterminals:
		print(f"  {key} :", end = "\t")
		print(grammar.followSet[key])

	print("\nPredict sets:  (see GRAMMAR section for ruleno)")
	for x, predict in enumerate(grammar.predictSet):
		print(f"  {x} :", end = "\t")
		print(predict)

	##########################################
	print("\n\n  -- PARSING --")
	if stream is None:
		print("No token stream provided.")
		exit()

	print("Parse table:")
	print(grammar.table)

	# -- PARSE TREE --
	parseTree = grammar.parse(stream)

	# Old output format
	# if parseTree is not None:
	# 	print("Parse tree:  (forgive the currently jankey formatting)")
	# 	print(parseTree)

	if output is not None:
		with open(output, "w") as outf:
			print(f"Sending parse tree to {output}. Execute the following command to view the tree:")
			print(f"cat {output} | ./treevis.py | dot -Tpng -o parse.png")
			format_parse_tree(outf, parseTree)
	else:
		print("No tree output provided, skipping parse tree visualization.")

if __name__ == '__main__':
	argc = len(sys.argv)
	if (argc < 2 or argc > 4):
		print(f"Usage: {sys.argv[0]} <grammar config> [token stream]")
		exit(1)

	elif argc == 2: main(sys.argv[1])
	elif argc == 3: main(sys.argv[1], sys.argv[2])
	else: main(sys.argv[1], sys.argv[2], sys.argv[3])
