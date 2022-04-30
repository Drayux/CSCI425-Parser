# ZOBOS

## Big Ideas

1. Parse the token stream into a CST, check for syntax. Token stream provided in .tok files
2. During the parse, massage the tree into an AST
3. Check for semantic errors in the AST

## WORK TODOS

- [ ] Parse a token stream with LR - Liam
	- [ ] Use LR knitting
	- [ ] Use SLR table 
	- [ ] Use zlang.cfg
	- [ ] Check for syntax errors
- [ ] Develop SDTs to make an AST during the above parse - Konch and Andrew
    - [ ] EXPR will be simplified to 
        - [X] leaves are literals or variables
            - [X] BEXPR
            - [X] AEXPR
              - [X] PRODUCT
              - [X] SUM
                  - [X] FUNTYPE
                    - [X] Made test
                  - [X] GLOBTYPE
                      - [X] Made test
                  - [X] VALUE
                    - [X] Made test for value literals 
                    - [X] Made test for lparen EXPR rparen 
        - [ ] root and internal nodes are non-termianls:
            - [X] BOOLS
            - [X] PLUS
            - [X] TIMES
            - [X] UNARY
                - [X] Made test for UNARY 
            - [ ] CAST
                - [ ] Made test for CAST
            - [X] FUNCALL
    - [ ] Control Structures will be simplified
        - [ ] IF
        - [ ] IFELSE
        - [ ] WHILE
        - [ ] STMTS
        - [ ] BRACESTMTS
    - [ ] Simple Tree representation of AST to disk
- [ ] Semantic checks on AST on variable, expression and function - Chris
	- [ ] Emit will write symbol tables to disk 
	- [ ] Warnings and errors will be emitted 
- [ ] ZOBOS will exit(0) if no errors, exit(1) on error

