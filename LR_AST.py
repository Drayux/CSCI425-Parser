import sys

from ParseTree import ParseTree
from Util import SubstituteHex

LAMBDA = "lambda"
charLAMBDA = "_lambda"


def RootReplace(node: ParseTree, data, children):
	node.data = data
	node.children = children


def replace_node_with_new_node(node: ParseTree, new_node: ParseTree):
	RootReplace(node, new_node.data, new_node.children)
	return


def procedure_FUNTYPE(node: ParseTree):
	childData = "type:" + node.children[0].data
	newNode = ParseTree(childData, None)
	replace_node_with_new_node(node, newNode)


def procedure_GLOBTYPE(node: ParseTree):
	childData = "type:"
	for x, child in enumerate(node.children):
		if x != 0: childData += " "
		childData += child.data
	newNode = ParseTree(childData, None)
	replace_node_with_new_node(node, newNode)


def procedure_leaf(node: ParseTree):
	node.data = node.data + ":" + SubstituteHex(node.aux)


def procedure_VALUE(node: ParseTree):
	if len(node.children) == 1:
		childData = node.getChild().data
		if childData == "plus": node.getChild().data = "+"
		if childData == "minus": node.getChild().data = "-"
		if childData == "mult": node.getChild().data = "*"
		if childData == "div": node.getChild().data = "/"
		if childData == "mod": node.getChild().data = "%"
		replace_node_with_new_node(node, node.getChild())
	elif node.getChild().data == "rparen":
		replace_node_with_new_node(node, node.children[1])


def procedure_IF(node: ParseTree):
	assert (len(node.children) > 3)
	assert (node.children[0].data == "if")
	assert (node.children[1].data == "lparen")
	assert (node.children[3].data == "rparen")

	node.removeChild(node.children[3])  # Remove rparen
	node.removeChild(node.children[1])  # Remove lparen
	node.removeChild(node.children[0])  # Remove if
	# i = len(node.children) - 1
	# while i > 0:  # Skip if
	#     n = node.children[i]
	#     # Move the node down as a child of the if
	#     node.removeChild(n)
	#     node.children[0].addChild(n)
	#     i -= 1


def procedure_IFELSE(node: ParseTree):
	assert (len(node.children) > 6)
	assert (node.children[0].data == "if")
	assert (node.children[1].data == "lparen")
	assert (node.children[3].data == "rparen")
	assert (node.children[5].data == "else")
	node.removeChild(node.children[5])  # Remove else
	node.removeChild(node.children[3])  # Remove rparen
	node.removeChild(node.children[1])  # Remove lparen
	node.removeChild(node.children[0])  # Remove if


def procedure_WHILE(node: ParseTree):
	assert (len(node.children) > 4)
	assert (node.children[0].data == "while")
	assert (node.children[1].data == "lparen")
	assert (node.children[3].data == "rparen")
	node.removeChild(node.children[3])  # Remove rparen
	node.removeChild(node.children[1])  # Remove lparen
	node.removeChild(node.children[0])  # Remove while


def procecure_EXPR(node: ParseTree):
	assert (len(node.children) == 1)
	node.data = node.children[0].data
	node.children = node.children[0].children


def procedure_UNARY(node: ParseTree):
	operater = node.children[0]
	if operater.data == "not":
		operater.data = "!"
	if operater.data == "compl":
		operater.data = "~"
	operaterData = operater.data
	node.removeChild(operater)
	node.data = operaterData


def procedure_BINARY(node: ParseTree):
	if len(node.children) == 3:
		node.data = node.children[1].data
		node.removeChild(node.children[1])
	if len(node.children) == 1:
		replace_node_with_new_node(node, node.getChild())


def procedure_FUNCALL(node: ParseTree):
	node.removeChild(node.getChild())  # Removes rparen
	node.removeChild(node.children[1])  # Removes lparen


def procedure_BOOLS(node: ParseTree):
	childData = node.getChild().data
	if childData == "lt":
		node.getChild().data = "<"
	elif childData == "leq":
		node.getChild().data = "<="
	elif childData == "eq":
		node.getChild().data = "=="
	elif childData == "geq":
		node.getChild().data = ">="
	elif childData == "gt":
		node.getChild().data = ">"
	replace_node_with_new_node(node, node.getChild())


def procedure_CAST(node: ParseTree):
	node.data = node.children[0].data  # Takes the casting
	node.removeChild(node.children[3])  # removes rparen
	node.removeChild(node.children[1])  # removes lparen
	node.removeChild(node.children[0])	# removes cast type


def procedure_STMTS(node: ParseTree):
	if len(node.children) == 0:
		return  # Let the parent reduce this node (delete it)
	if len(node.children) == 1:
		if node.getChild().data == "lambda" or node.getChild().data == "STMTS":
			replace_node_with_new_node(node, node.getChild())
	else:
		if node.children[0].data == "lambda":
			node.removeChild(node.children[0])
			return
		firstChild = node.children[0]
		i = 0
		for child in firstChild.children:
			node.children.insert(i, child)
			i += 1
		node.removeChild(firstChild)


def procedure_BRACESTMTS(node: ParseTree):
	assert (len(node.children) == 3)
	assert (node.children[0].data == "lbrace")
	assert (node.children[1].data == "STMTS")
	assert (node.children[2].data == "rbrace")
	# Replace braces with scope tokens.
	node.children[0] = ParseTree("scope:open", None)
	node.children[2] = ParseTree("scope:close", None)


def procedure_ASSIGN(node: ParseTree):
	assert (len(node.children) == 3)
	assert ("id" in node.children[0].data)
	assert (node.children[1].data == "assign")
	# assert (node.children[2].data in [ "EXPR", "ASSIGN" ])	# Removed for EXPR procecure
	node.data = "="  # ASSIGN -> =
	node.removeChild(node.children[1])  # Remove assign token


def procedure_STATEMENT(node: ParseTree):
	assert (len(node.children) in [ 1, 2 ])
	if len(node.children) == 1:
		child = node.children[0]
		# assert (child.data == "BRACESTMTS")

		if (child.data == "BRACESTMTS"):
			# Replace node
			node.data = child.data
			node.children = child.children

	# if len(node.children) == 2:
	else:
		assert (node.children[1].data == "sc")
		node.removeChild(node.children[1])  # Remove sc token
		assert (node.getChild().data in [ "BRACESTMTS", "DECLLIST", "ASSIGN", "=", "IF", "IFELSE", "WHILE", "EMIT" ])


def procedure_MODULE(node: ParseTree):
	assert (len(node.children) == 2)
	assert (node.children[0].data == "MODPARTS")
	assert (node.children[1].data == "$")
	node.removeChild(node.children[1])  # Remove $
	# Working bottom up, so we know MODPARTS is composed of <node> or <node> <MODPARTS>
	# Now flatten the structure by adopting all children
	nodeHead = node.getChild()
	#print("HEAD: {}".format(nodeHead.data))
	while len(nodeHead.children) > 1:
		#print("ADOPTING: {}".format(nodeHead.children[0].data))
		node.addChild(nodeHead.children[0])  # Adopt the intermediate child
		nodeHead = nodeHead.children[1]
		#print("UPDATED HEAD: {}".format(nodeHead.data))
	node.addChild(nodeHead.getChild())  # Adopt the leaf child
	node.removeChild(node.children[0])  # Remove the MODPARTS child


def procedure_MODPARTS(node: ParseTree):
	assert (len(node.children) in [ 1, 2, 3 ])
	assert (node.children[0].data in [ "GCTDECLLIST", "GFTDECLLIST", "DECLLIST", "FUNSIG", "FUNCTION", "EMIT" ])
	#assert (node.children[0].data in [ "GCTDECLLIST", "GFTDECLLIST", "FUNSIG", "FUNCTION", "EMIT",    "DECLLIST" ])
	if len(node.children) > 1:
		if node.children[0].data == "FUNCTION":
			assert (node.children[1].data == "MODPARTS")
		else:
			assert (node.children[1].data == "sc")
			node.removeChild(node.children[1])  # Remove sc
	# Cleaned up the structure, now we have <node> or <node> <MODPARTS>
	# NOTE: don't flatten structure here, it will get messy! instead, flatten in MODULE procedure.
	#if len(node.children) == 1:
	#    replace_node_with_new_node(node, node.getChild())
	#else:


def procedure_PARAMLIST(node: ParseTree):
	# Flatten structure into single PARAMLIST with n PARAM children
	if len(node.children) == 1:
		assert (node.getChild().data == "NOPARAMS")
		assert (len(node.getChild().children) == 0)
		# Just remove the NOPARAMS
		node.removeChild(node.getChild())
	elif len(node.children) == 2:
		assert ("type" in node.children[0].data or node.children[0].data == "FUNTYPE")
		assert ("id" in node.children[1].data)
		# Make a wrapper PARAM node
		paramNode = ParseTree("PARAM", None)
		paramNode.addChild(node.children[0])
		paramNode.addChild(node.children[1])
		#replace_node_with_new_node(node.children[0], paramNode)
		# Manual fixup
		node.children[0] = paramNode
		node.children[0].parent = node
		node.removeChild(node.children[1])  # Remove the leftover
	elif len(node.children) > 2:
		assert ("type" in node.children[0].data or node.children[0].data == "FUNTYPE")
		assert ("id" in node.children[1].data)
		assert (node.children[2].data == "comma")
		assert (node.children[3].data in [ "PARAM", "PARAMLIST" ])
		if node.children[3].data == "PARAMLIST":
			# Iterate the children of the PARAMLIST and adopt
			for i in range(len(node.children[3].children)):
				assert (node.children[3].children[i].data == "PARAM")
				# Adopt
				node.addChild(node.children[3].children[i])
			node.removeChild(node.children[3])  # Remove the dead parent we stole children from, lol
		node.removeChild(node.children[2])  # Remove comma
		# Wrap our params with a PARAM
		paramNode = ParseTree("PARAM", None)
		paramNode.addChild(node.children[0])
		paramNode.addChild(node.children[1])
		#replace_node_with_new_node(node.children[0], paramNode)  # Replace the left, not the base node.
		# Manual fixup
		node.children[0] = paramNode
		node.children[0].parent = node
		node.removeChild(node.children[1])  # Remove the leftover


def procedure_FUNSIG(node: ParseTree):
	assert (len(node.children) == 5)
	assert ("type" in node.children[0].data or node.children[0].data == "FUNTYPE")
	assert ("id" in node.children[1].data)
	assert (node.children[2].data == "lparen")
	assert (node.children[3].data == "PARAMLIST")
	assert (node.children[4].data == "rparen")
	node.removeChild(node.children[4])  # Remove rparen
	node.removeChild(node.children[2])  # Remove lparen


def procedure_ARGLIST(node: ParseTree):
	# "First" element of the ARGLIST (end of ARGLIST tree)
	if len(node.children) <= 1: return

	# Else ARGLIST has multiple arguments
	new = ParseTree("ARGLIST", node.parent)
	for child in node.children:
		if child.data == "ARGLIST":
			for x in child.children: new.addChild(x)

		elif child.data != "comma":
			new.addChild(child)

	replace_node_with_new_node(node, new)


def procedure_FUNCTION(node: ParseTree):
	assert (len(node.children) == 6)
	assert (node.children[0].data == "FUNSIG")
	assert (node.children[1].data == "returns")
	assert ("id" in node.children[2].data)
	assert (node.children[3].data == "assign")
	# assert (node.children[4].data == "EXPR")		# Removed for EXPR procedure
	assert (node.children[5].data == "BRACESTMTS")
	node.children[3].data = "="  # assign -> =
	node.children[3].addChild(node.children[2])  # Adopt id
	node.children[3].addChild(node.children[4])  # Adopt EXPR
	node.removeChild(node.children[4])  # Remove EXPR
	node.removeChild(node.children[2])  # Remove id
	node.removeChild(node.children[1])  # Remove returns


def procedure_EMIT(node: ParseTree):
	new = ParseTree("EMIT", node.parent)
	for child in node.children:
		if child.data not in [ "emit", "lparen", "rparen" ]:
			new.addChild(child)

	replace_node_with_new_node(node, new)


def procedure_DECLIDS(node: ParseTree):
	# "First" element of the DECLIDS (end of DECLIDS tree)
	if len(node.children) <= 1: return

	# Else DECLIDS has multiple arguments
	new = ParseTree("DECLIDS", node.parent)
	for child in node.children:
		if child.data == "DECLIDS":
			for x in child.children: new.addChild(x)

		elif child.data != "comma":
			new.addChild(child)

	replace_node_with_new_node(node, new)


def procedure_DECLLIST(node: ParseTree):
	# DOES NOT FOLLOW GRAMMAR EXACTLY!!
	assert (len(node.children) == 2)
	new = ParseTree("DECLLIST", node.parent)
	new.addChild(node.children[0])

	for child in node.children[1].children:
		new.addChild(child)

	replace_node_with_new_node(node, new)


def LR_AST_SDT_Procedure(node: ParseTree):
	"""
	This will transform the node to its AST counterpart using the correct SDT
	:param node:
	:return: None / Transformation
	"""
	if node.data == "FUNTYPE":
		procedure_FUNTYPE(node)
	elif node.data == "GLOBTYPE":
		procedure_GLOBTYPE(node)
	elif node.data == "id" or \
			node.data == "intval" or \
			node.data == "floatval" or \
			node.data == "stringval":
		procedure_leaf(node)
	elif node.data == "VALUE":
		procedure_VALUE(node)
	elif node.data == "PLUS" or \
			node.data == "TIMES":
		procedure_VALUE(node)
	elif node.data == "IF":
		procedure_IF(node)
	elif node.data == "IFELSE":
		procedure_IFELSE(node)
	elif node.data == "WHILE":
		procedure_WHILE(node)
	elif node.data == "EXPR":
		procecure_EXPR(node)
	elif node.data == "UNARY":
		procedure_UNARY(node)
	elif node.data == "SUM" or \
			node.data == "PRODUCT" or \
			node.data == "AEXPR" or \
			node.data == "BEXPR":
		procedure_BINARY(node)
	elif node.data == "FUNCALL":
		procedure_FUNCALL(node)
	elif node.data == "BOOLS":
		procedure_BOOLS(node)
	elif node.data == "CAST":
		procedure_CAST(node)
	elif node.data == "STMTS":
		procedure_STMTS(node)
	elif node.data == "BRACESTMTS":
		procedure_BRACESTMTS(node)
	elif node.data == "ARGLIST":
		procedure_ARGLIST(node)

	# Non-control SDTs
	elif node.data == "ASSIGN":
		procedure_ASSIGN(node)
	elif node.data == "STATEMENT":
		procedure_STATEMENT(node)
	elif node.data == "MODULE":
		procedure_MODULE(node)
	elif node.data == "MODPARTS":
		procedure_MODPARTS(node)
	elif node.data == "PARAMLIST":
		procedure_PARAMLIST(node)
	elif node.data == "FUNSIG":
		procedure_FUNSIG(node)
	elif node.data == "FUNCTION":
		procedure_FUNCTION(node)
	elif node.data == "EMIT":
		procedure_EMIT(node)

	# Weird ones
	elif node.data == "DECLIDS":
		procedure_DECLIDS(node)
	elif node.data == "GCTDECLLIST":
		procedure_DECLLIST(node)
	elif node.data == "GFTDECLLIST":
		procedure_DECLLIST(node)


def LR_AST_EOP(node: ParseTree):
	"""
	Perform SDTs on each child of the given node.

	Since LR parsing has issues with ASTs, we have the children of the current parent node change into an AST
	:param node: ParseTree
	:return: None / Transformation of children
	"""
	for child in node.children:
		LR_AST_SDT_Procedure(child)
