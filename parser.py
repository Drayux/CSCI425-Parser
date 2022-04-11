from collections import deque
import copy
import sys

from CFG import *

# file_name : a file in the cwd of the script
# returns : a list of lines with newlines extra spaces removed
def parse_file(file_name: str) -> list:
	result_list = []
	# open file and put it in an array of lines
	with open(file_name) as f:
		lines = f.readlines()
		for i, line in enumerate(lines):
			items = line.split(' ')
			items[-1] = items[-1].replace("\n", "")  # remove newline if exists
			for i in range(len(items) - 1, -1, -1):  # trim empty spaces
				if items[i] == '':
					items.pop(i)
			result_list.append(' '.join(items))

	return result_list


# lines : a list of lines that describe production rules
# returns : a cfg dict
def generate_cfg(lines: list) -> dict:
	cfg = {}
	non_terminal = ""
	for line in lines:
		line.strip()
		# production grab the non-terminal and add rules for it
		if '->' in line:
			split = line.index('->')
			non_terminal = line[:split].strip()
			rhs = line[2 + split:].strip()
			rules = rhs.split('|')
			for rule in rules:
				if non_terminal in cfg:
					cfg[non_terminal].append(rule.strip())
				else:
					cfg[non_terminal] = [rule.strip()]
		elif non_terminal != "":  # | on its own line with a previously specified non-terminal
			if "|" in line:
				rules = line.split('|')
				for rule in [r.strip() for r in rules]:
					if rule != "":
						cfg[non_terminal].append(rule.strip())

	return cfg


def main(config, stream = None):
	lines = parse_file(config)
	cfg = generate_cfg(lines)

	# parser = Parser(config)

	##########################################

	print("  -- GRAMMAR --")

	# Print start symbol
	start_symbol = ""
	for key, val in cfg.items():
		for result in val:
			if "$" in result:
				print("Start Symbol:", key)
				start_symbol = key
				break

	# Print all rules
	rules = []  # tuple of NonTerminal -> Result
	# print("Rules:")
	rule_num = 0
	for key, val in cfg.items():
		for result in val:
			rules.append((key, result))
			print("  ", rule_num, " : \t", key, "->", result)
			rule_num += 1

	# Print non-terminals:
	print("\nNon-terminals:\n  ", end = "")
	for key in cfg.keys():
		print(key, end = " ")
	print("")

	# Print terminals
	# terminals = set()
	terminals = { '$' }
	for key, val in cfg.items():
		for v in val:
			for value in v.split(' '):
				if value not in cfg and value != '$':  # if not a non terminal
					terminals.add(value)

	print("\nTerminals:\n  ", end = "")
	for term in terminals:
		print(term, end = " ")
	print("\n")


	##########################################
	print("\n  -- PREDICTION --")
	grammar = CFG(cfg, rules, terminals, start_symbol)
	grammar.predict_set()       # Update the grammar's predict sets

	# Output which non-terminals derive to lambda
	print("Derives to lambda:\n  ", end = "")
	for key in grammar.cfg.keys():
		if grammar.derives_to_lambda(key):
			print(key, end = " ")
	print()

	# Output first sets of all non-terminals
	print("\nFirst sets:")
	for key in grammar.cfg.keys():
		print(f"  {key} :", end = "\t")
		first_set = grammar.first_set(key)[0]
		if len(first_set) < 1:
			print("NONE - (This is probably an error)")
			continue

		print(first_set)

	# Output follow sets of all non-terminals
	print("\nFollow sets:")
	for key in grammar.cfg.keys():
		print(f"  {key} :", end = "\t")
		follow_set = grammar.follow_set(key)[0]
		if len(follow_set) < 1:
			print("NONE")
			continue

		print(follow_set)

	print("\nPredict sets:  (see GRAMMAR section for ruleno)")
	for x, predict_set in enumerate(grammar.predict_sets):
		print(f"  {x} :", end = "\t")

		if len(predict_set[1]) < 1:
			print("NONE")
			continue

		print(predict_set[1])


	##########################################
	print("\n\n  -- PARSING --")
	if stream is None:
		print("No token stream provided.")
		exit()

	grammar.build_parse_table()

	print("Parse table:  (lambda denoted by '#'; rules are indexed as shown in GRAMMAR section)")
	print(grammar.parse_table)

	parse_tree = grammar.build_parse_tree(stream)
	print("Parse tree:  (forgive the currently jankey formatting)")
	print(parse_tree)


if __name__ == '__main__':
	argc = len(sys.argv)
	if (argc < 2):
		print(f"Usage: {sys.argv[0]} <grammar config> [token stream]")
		exit(1)

	elif argc == 2:
		main(sys.argv[1])

	else:
		main(sys.argv[1], sys.argv[2])
