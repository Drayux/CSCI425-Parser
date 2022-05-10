czar-testdata.tar.bz2 README
============================

Each input *.def file has several associated files, let's take
intexpr-3.def as an example:

  intexpr-3.def: the definition file as an input for your CZAR, the
  format is described in the wiki page.
  
  intexpr-3.pdf: a visual of the tree contained in intexpr-3.def 
  
  intexpr-3-24,24.czr, intexpr-3-24,24.map: the czar assembler output and
  memory map of global variables (and data, in some cases) when run
  against my CZAR with 24 general purpose and floating point registers
  (eg:  CZAR 24,24 intexpr-3.def intexpr-3-24,24.czr )
  
  intexpr-3-4,4.czr intexpr-3-4,4.map: the same as above but with
  4 registers of each type.

  intexpr-3.src: is the original source (in case you're curious), 
  in 2022 I had to make some small changes to zlang to support CZAR, so
  technically your ZOBOS project can't compile this source file.
  If you're *really* looking to procrastinate your exams, there is [3]

I've used working registers R0, R1, F0, and F1; so my output uses
allocatable registers in the treeCG algorithm from R2 or F2 "and up".

If you find any discrepancies or inconsistencies in any of the provided 
files please let me know ASAP.  If it is an error on my part, I'm sure
everyone would want it fixed sooner than later.

You will notice a lot of inefficient shuffling of values to and fro
memory in these examples, lots of:

  store @4w, #3
  load  R2, @4w

but we didn't cover algorithms to avoid this byte dance :(  I said we'd
write a compiler this semester, I didn't say *an efficient* compiler.

Please try to stick to the assembler syntax presented in the examples,
I don't care if you use absolute values (@16) instead of labeled values
(@4w), but the @ and # notation is sort of important.[1]

Also, if you choose to do the constant data and literals EXTRA CREDIT,
you'll notice that the examples double allocate memory for

  int x = 9999999;

this could have been avoided, but there are some pitfalls associated
with the naive solutions (aren't there always).[2]  I've opted for the
simplest algorithms that always work instead of more complex
implementations.


--
[1] I hope to get my emulator reliable enough for me to grade your
submissions with, in which case missing @ and # will just cause syntax
errors during grading and I'll have to resort to hand tracing :(

[2]
  int x = 9999999;
  const int y = 9999999;
  x = x + 1;

[3] https://cs.mcprogramming.com/static/comp/hr/c286d95debc3323e/czar.lr,
https://cs.mcprogramming.com/static/comp/hr/f7213ce5e7f63c52/czar.cfg
Keep in mind that rule numbers have changed so your SDT semantic actions
might need to be "readjusted" to the right rule number, depending on how
you implemented SDT.


