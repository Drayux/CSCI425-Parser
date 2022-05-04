# Simple Parser

# ZOBOS  (Compilers Project 4)
## Big Ideas

1. Parse the token stream into a CST, check for syntax. Token stream provided in .tok files
2. During the parse, massage the tree into an AST
3. Check for semantic errors in the AST

## WORK TODOS

- [ ] Parse a token stream with LR - Liam
    - [X] Use LR knitting
    - [X] Use SLR table
    - [X] Use zlang.cfg
    - [ ] Check for syntax errors
    - [ ] print out
- [X] Develop SDTs to make an AST during the above parse - Konch and Andrew
    - [X] EXPR will be simplified to
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
        - [X] root and internal nodes are non-termianls:
            - [X] BOOLS
            - [X] PLUS
            - [X] TIMES
            - [X] UNARY
                - [X] Made test for UNARY
            - [x] CAST
                - [x] Made test for CAST
            - [X] FUNCALL
    - [X] Control Structures will be simplified
        - [X] IF
        - [X] IFELSE
        - [X] WHILE
        - [X] STMTS
        - [X] BRACESTMTS
    - [X] Simple Tree representation of AST to disk
    - [ ] Handle higher order colapsing
- [ ] Semantic checks on AST on variable, expression and function - Chris
    - [ ] Emit will write symbol tables to disk
    - [ ] Warnings and errors will be emitted
- [ ] ZOBOS will exit(0) if no errors, exit(1) on error
- [ ] Symtable
  - [ ] Location
  - [ ] Identifier
  - [ ] Type
  - [ ] `const` Flag
  - [ ] `used` or `used` flag
  - [ ] `Initialized` or `Uninitialized` Flag
  - [ ] Funtion Semantics
    - [ ] Function prototype encountered, `const` flag to false, but already init
    - [ ] Function definition is encountered, the symbol has its `const` and `initialized` flag to true
  - [ ] Emit
    - [ ] Global scope is scope 0
    - [ ] on Emit, print the following to the third command line argument, comma seperated
      - [ ] On one line
      - [ ] Scope
      - [ ] Type
        - if its a function, type is followed by //, so `int//`
      - [ ] id


# WRECK  (Compilers Project 3)
## ABOUT
This project is a collaborative project for CSCI425: Compiler Design *TODO TODO*  

## USAGE

`python wreck.py <grammar config> [token stream] [parse tree output file]`  

Grammar config defines a language in plain text (file extension: `.cfg`) EX:  

```
S -> A C $
C -> c
   | lambda
A -> a B C d
   | B Q
   | lambda
B -> b B | d
Q -> q
```

All grammar terminals are assumed to be lowercase.
- `->` denotes the production rule associate
- `|` is reserved for rule alternation
- `lambda` specifies the empty string  


Language config files define a stream of language tokens (intermediate format void a lexer framework; extension: `.tok`)

Each token is separated by newlines, each line containing either TOKEN or TOKEN TOKENVALUE  

## CLI example

```
python3 parser.py config/language-slides/language.cfg config/language-slides/src.tok
```
