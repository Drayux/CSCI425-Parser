Big ideas

1. Read in an AST like from ZOBOS
2. Make an assembler language out of the AST

We need to implement:

1. Integer Arithmetic with variables and immediate values
2. Floating point arithmetic with immediate values
3. emit instructions for integer and floating point values

DO NOT NEED TO MANAGE:

1. Functions - all symbols are global in scope. 
2. Casting - no need to change registers for general purpose and floating point
3. No complex arithmetic - bit wise, Boolean ANDs and ORs
4. Complex architecture - floats are the same size as words

EXTRA CREDIT

1. Constant globals literals such as value too large for immediate values,
   string data, and emit statements
2. if-then and if-then-else control structures


TODOS:

- [ ] Input
    - [ ] Argument 1
        - [ ] R_n,F_n
            - [X] This is the absolute number of general purpose and
              floatingpoint registers in the CPU. 
                  - Example input: 16,16 ; 8,5 
            - [X] Registers use integer notation, so first register will be
              called R0
            - [ ] GP and floating point values/registers are 4 bytes
            - [ ] Instructions are 4 bytes
            - [ ] We need to dicide which registers are work registers
            - [ ] all other registers are allocatable registers 
            - [ ] R_n >= F_n >= 5
            - [ ] Immediate integer values can be : [−16384,16383] 
            - [ ] Immediate floating points can be : [0,1310.71] 
                - FP only supports 2 decimal places worth of precision
    - [X] Argument 2
        - [X] Annotated AST
            - [X] File type will be of type .def
                - Example: [program.def]
            - [X] Will be read into out ParseTree object
                - there will be no logic/syntax/semantic errors.
            - [X] Read in the node values
                - [X] parent or leaf
                - [X] node type, prefixed with :
                - [X] a value, prefixed with : LEAVES ONLY 
                - [X] attributes in key:value format
    - [ ] Argument 3
        - [ ] The output file with the assembly language

- [ ] Symbol table generation
    - [ ] traverse the tree and collect:
        - [ ] Global symbols
        - [ ] EC: constant globale litterals
- [ ] Data Segment
    - [ ] data segment starts at base memory and grows upward
    - [ ] For each global identifier in the symbol table, calculate its location
      size. Augment each identifiers symbol table entry with its absolue memory
      location
      - remember that a four byte float should be at a memory divisible by four,
        but strings can be stored at any offset.
    - [ ] Store or calculate the required data segment in bytes
- [ ] Frames ??? we are not doing functions
- [X] registerNeeds() calculates the register needs for each node
- [ ] treeCG as a basis for generating the instructions for each expression tree
    - [X] When LOADing global values, use their memory locations calculated in
      dataSeg and stored with the identifier in the symbol table
    - [X] Handle assign nodes with STORE instructions
    - [ ] Handle immediate arithmetic operations ( + R3, R3, #x0f )
    - [X] Handle immediate LOADs such as LD R4,#2
- [ ] imageData
    - [ ] DATA where global variables, const, and synthetic variables are stored
    - [ ] EXEC all program instructions
    - [ ] INIT instructions at global scope
- [ ] imageInit 
    - [ ] generate the instructions for globally scoped code
    - [ ] Tell the machine where these instructions should be written in memory
      with the init statement. 
          - determins size of the dataSeg, pad it for alignmentm and write `init
          @24`
        - if we are not using global variables, then init @0 because ther is no
          data segment to the memory map
    - [ ] Traverse the AST, IGNORING FUNCTION NODES, and write out the
      instructions generated for all expression evaluations, control structures
      and emit statements.
          - this is all the treeCG generated instructions at global scope.
    - [ ] write a single return statement when done


Questions I have:

- fp numbers can be [0,1310.71], but cgldata has a floating point of #197483.00, what dis
- some inputs have 4,4 for reg count, but instructions say 5 is the minimum number of regs