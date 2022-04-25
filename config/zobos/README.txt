ZOBOS RESOURCES
===============

File extensions and contents
----------------------------
.syn:  Source with syntax errors
.src:  Use the source, Luke!
.tok:  Token stream from .src
.out:  ${COMPGRADING}/output-line filtered results, what your ZOBOS will
       be graded against.
.vrb:  My own more verbose output, contains REASON lines detailing why
       each SYNTAX, ERROR, or WARNING is generated; as well as some
	   symbol table and identifier declaration messages.
.pdf:  AST tree visual
.sym:  emit symtable output (if it is generated in source)


Particular files for testing and debug
--------------------------------------
Each type of non-syntax semantic check has a corresponding *-?.src file,
for instance noident-2.src is for the NOIDENT semantic checks.  In my
own little world, I call these "ISSUE" files because they are meant to
focus on just one particular semantic issue that must be tested.

These files have been constructed to test a wide array of the particular
semantic issues, and in most cases, NO OTHER SEMANTIC issues should be 
reported for the file.  The exceptions being conv-4.src and
reident-4.src file, where demonstrating particular semantic issues
required one or two CONST warnings to be emitted as well.

In all cases the accompanying .out files show precisely the error or 
warning messages your code should generate.  Output will be sorted by
line number, column, and ID before grading comparisons, so it doesn't
matter the order of your output lines.

Keep in mind that the particular ZOBOS assignment for your semester
probably doesn't have you test *all* the possible types of issues.  The
project wiki page and grader.sh scripts are adjusted accordingly, but 
_all_ issue files are still provided in the ZOBOS resources.  So there
are likely to be .src issue files _without_ errors or warnings in their
.out files --- in this semester, that's the cookie crumbled.  In all
cases, your ZOBOS OUTPUT should match the .out file for all .src or .syn
inputs.

Most of these issue files require VERY SILLY recursive calls within 
function definitions, they are typically the last statement of the 
function and typically the function requiring this is actually called
"silly".  Why?  Take for instance reident-1.src, without the recursive
call ZOBOS should issue an UNUSED warning for the silly() function, since
it is not on the RHS of any assignments.  If I want issue files to only 
one type of semantic concern reported, this won't do :)  It also happens
to make regression testing during changes and development a hair easier.

Non-issue source
----------------
Source files not named after semantic errors or warning messages
should have at most one UNUSED warning message (as shown by their own
.out files). Some of these source use semantic acrobatics to avoid
an UNUSED warning. The more "practical" of them less so.

