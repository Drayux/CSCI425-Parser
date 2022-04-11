import sys
from Grammar import Grammar

def main(config, stream = None):
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

	parseTree = grammar.parse(stream)
	if parseTree is not None:
		print("Parse tree:  (forgive the currently jankey formatting)")
		print(parseTree)

if __name__ == '__main__':
	argc = len(sys.argv)
	if (argc < 2):
		print(f"Usage: {sys.argv[0]} <grammar config> [token stream]")
		exit(1)

	elif argc == 2:
		main(sys.argv[1])

	else:
		main(sys.argv[1], sys.argv[2])
