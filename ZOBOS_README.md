# ZOBOS

## WORK TODOS

- [ ] Parse a token stream with LR
	- [ ] Use LR knitting
	- [ ] Use SLR table 
	- [ ] Use zlang.cfg
	- [ ] Check for syntax errors
- [ ] Develop SDTs to make an AST during the above parse
	- [ ] EXPR will be simplified to 
		- [ ] leaves are literals or variables
		- [ ] root and internal nodes are non-termianls:
			- [ ] BOOLS
			- [ ] PLUS
			- [ ] MULT
			- [ ] UNARY
			- [ ] CAST
			- [ ] FUNCALL
	- [ ] Control Structures will be simplified
		- [ ] IF
		- [ ] IFELSE
		- [ ] WHILE
		- [ ] STMTS
		- [ ] BRACESTMTS
	- [ ] Simple Tree representation of AST to disk
- [ ] Semantic checks on AST on variable, expression and function
	- [ ] Emit will write sybol tables to disk 
	- [ ] Warnings and errors will be emitted 
- [ ] ZOBOS will exit(0) if no errors, exit(1) on error

## Big Ideas

1. Pasre the token stream into a CST, check for syntax. Token stream provided in .tok files
2. During the parse, massage the tree into an AST
3. Check for semantic errors and write to disk in the .out

