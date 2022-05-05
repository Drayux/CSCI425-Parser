#!/usr/bin/env bash

# unlike SIM projects, each compiler project has a name of its own
PROGRAM=ZOBOS

# this shifts off ${1:-.} to COMPLOC
source "${COMPGRADING}/comp-lib.sh"

gradermodebackchannel

set -e

## make executable
#chmod +x "${graderloc}/normscanu"
## look for required execs
for x in tree-to-graphvis ; do 
	if ! test -x "${COMPGRADING}/$x" ; then 
		grader_echo "ERROR: '${COMPGRADING}/$x' can be executed."
		exit 1
	fi
done

# create a temporary dir to hold tests, this permits multiple 
# simultaneous grading sessions without stumbling over each other...
GRADERBIO="_zobostest"
mkdir -p "${GRADERBIO}"
mirror "${graderloc}/basicio" "${GRADERBIO}"
# some students need zlang.lr for run
test -s "zlang.lr" || cp "${graderloc}/zlang.lr" "."


NOTOKEN=_test_empty.scan-u_output_file

basiciotallydir="`grader_mktemp -d basiciotally`"

# RUBRIC 1 ###
# inaccessible program.tok
tally_missing_datafile "${basiciotallydir}/missingtok" "${comploc}/${PROGRAM}" MISSINGDATAFILE /dev/null /dev/null

# inaccessible output location - ast and sym file
rm -rf "${graderloc}/${GRADERBIO}/_dne"
tally_nooutput_exitnonzero "${basiciotallydir}/inaccessast" "${comploc}/${PROGRAM}" "${GRADERBIO}/ast.tok" "${GRADERBIO}/_dne/ast.ast" "${GRADERBIO}/_test.sym"

rm -rf "${graderloc}/${GRADERBIO}/_dne"
tally_nooutput_exitnonzero "${basiciotallydir}/inaccesssym" "${comploc}/${PROGRAM}" "${GRADERBIO}/sym.tok" "${GRADERBIO}/_test.ast" "${GRADERBIO}/_dne/sym.sym"

# failure on noperm file
nopermfile="${GRADERBIO}/_noperm.file"
touch_noperm_file "$nopermfile"
tally_nooutput_exitnonzero "${basiciotallydir}/nopermast" "${comploc}/${PROGRAM}" "${GRADERBIO}/ast.tok" "${nopermfile}" "${GRADERBIO}/_test.sym"
unlink_noperm_file "${nopermfile}"

# failure on noperm file
touch_noperm_file "$nopermfile"
tally_nooutput_exitnonzero "${basiciotallydir}/nopermsym" "${comploc}/${PROGRAM}" "${GRADERBIO}/sym.tok" "${GRADERBIO}/_test.ast" "${nopermfile}" 
unlink_noperm_file "${nopermfile}"

# should also fail w/ dirs
nopermfile="${GRADERBIO}/_noperm.dir"
touch_noperm_file -d "$nopermfile"
tally_nooutput_exitnonzero "${basiciotallydir}/nopermastd" "${comploc}/${PROGRAM}" "${GRADERBIO}/ast.tok" "${nopermfile}" "${GRADERBIO}/_test.sym"
unlink_noperm_file "${nopermfile}"

# failure on noperm file
touch_noperm_file "$nopermfile"
tally_nooutput_exitnonzero "${basiciotallydir}/nopermsymd" "${comploc}/${PROGRAM}" "${GRADERBIO}/sym.tok" "${GRADERBIO}/_test.ast" "${nopermfile}" 
unlink_noperm_file "${nopermfile}"

rm -rf "${GRADERBIO}"

show_tally_logic()
{
	grader_msg <<EoT
Total points may be fluid!  Have you noticed that the total points changes from
run to run?  This is because *extra* OUTPUT lines from your program increase
the total points that your count of correct OUTPUT lines is compared to in the
correct/total reported by grader.sh

Contemplate the arithmetic for a moment, and you'll realize that *extra* OUTPUT
lines actually make every good OUTPUT line count less.  If your ZOBOS *never*
generates extra OUTPUT lines, you'll never see fluid total points.
EoT
}

run_one_source()
{
	###
	# return status 0 --- should have generated ast and symtable output
	# return status 2 --- should be a SYNTAX error, ast and symtable not generated
	###
	# $1 = results.out, 3 tally dirs...
	# $5... command line
	local srcout="${1}"
	local glout="${graderloc}/results/${1}"
	local tallysyntax="${2}"
	local tallyerror="${3}"
	local tallywarn="${4}"
	local ees_test="-eq"
	local expected_es='exit status 0'
	local run_one_return=0
	if grep -E -e ':ERROR:' "${glout}" >/dev/null; then
		expected_es='exit status non 0'
		ees_test="-ne"
		ne0tally="${tallyerror}"
	elif grep -E -e ':SYNTAX:' "${glout}" >/dev/null; then
		expected_es='exit status non 0'
		ees_test="-ne"
		ne0tally="${tallysyntax}"
		run_one_return=2
	fi
	shift 4

	# specialized, modeled after grader-lib.sh:test_run
    grader_msg << EoT
Running 
  ${@} >__${srcout}
  ${COMPGRADING}/output-line <__${srcout} >_${srcout}
EoT
	# careful! preserve exit status of PROGRAM
	set +e
	( unset graderloc; "${@}" > "__${srcout}" )
	local r=$?
	set -e
	"${COMPGRADING}/output-line" <"__${srcout}" >"_${srcout}"
	if ! test $r ${ees_test} 0 ; then
		grader_echo "ERROR: exit status was $r, expected ${expected_es}."
		grader_keystroke
		case "${ees_test#?}" in
			eq ) touch ${tallywarn}.es.bad;;
			ne ) touch ${ne0tally}.es.bad;;
		esac
	else 
		case "${ees_test#?}" in
			eq ) touch ${tallywarn}.es.good ;;
			ne ) touch ${ne0tally}.es.good ;;
		esac
	fi
	# return whether or not it SHOULD HAVE exited zero or not,
	# tell the callee if process_ast and analyze_sym is run
	return ${run_one_return}
}


analyze_sym()
{
	#set -x
	local rsym="${1}"
	local glrsym="${graderloc}/results/${1}"
	local tally="${2}.${3%.sym}.bad"
	local ssym="${3}"
	# we there is a missing or empty results sym, just skip the test
	test -s "${glrsym}" || return 0
	v=r
	for f in "${glrsym}" "${ssym}"; do 
		# tricky sorting, we want numerical by scope and then alpha by name
		# replace second comma with % and sort twice , then return / to comma
		# !!! must use -s stable sort on last processing
		# --- ignore empty lines
		bn=`basename "${f}"`
		# does NOT sort them as one would expect, but does sort them deterministically
		# (tested with randomlines in the pipeline) and that is all we need
		tr -d '\040\011' <"${f}" |grep '.' | sort -n -k 1 -t , | sort -s -k 3 -t , > "_norm_${bn}" 
	done
	touch "${tally}"
#	for f in "_norm_${ssym}" "_norm_${rsym}" ; do 
#		echo >&2 "${f}"
#		cat "${f}"
#	done

	if ! diff -u "_norm_${ssym}" "_norm_${rsym}" >/dev/null ; then
		grader_msg <<EOT
The symbols output from your program is in ${3}, the expected results are at
  ${glrsym}
These have been normalized (sorted by scope, variable name) and the results 
are prefixed with _norm_ (YOUR's has one more underscore in its name).

You can see which lines differ using "visual diff" tool, or at the console with

  $ diff -u _norm_${ssym} _norm_${rsym}

(- lines would be removed from _norm_${ssym} and + lines would be added to 
match _norm_${rsym}).

IF YOU WANT TO INSPECT THIS FAILURE, CTRL-C now!
EOT
		grader_keystroke
	else 
		mv "${tally}" "${tally%.bad}.good"
		grader_echo "emit symtable results for test program ${rsym%.sym} are GOOD :)"
	fi
	rm -f "_norm_${ssym}" "_norm_${rsym}"
}


process_ast()
{
	# "${srcname}.pdf" "${tallyast}" "_${srcname}.ast"
	local rpdf="${graderloc}/results/${1}" 
	local tallyast="${2}"
	local sast="${3}"
	
	#set -x
	rm -f "${sast%.ast}.pdf"
	touch ${tallyast}.bad
	if test -s "${sast}" ; then
		###
		# slightly tricky stuff, if you run these blocks with set -e, your shell debug
		# goes into _dotgen_{direct,helper}.err (of course).
		# ALSO the exit status of test_run is that of the "always true"
		# predicate provided, so we must inspect ZOBOS exit status in a
		# secondary step.
		###
		if test_run -T -lt 0 dot -T pdf -o "${sast%.ast}.pdf" "${sast}" 2>_dotgen_direct.err ; test ${GraderRunES} -ne 0  ; then 
			if test_run -T -lt 0 "${COMPGRADING}/tree-to-graphvis" "${sast}" 2>_dotgen_togv.err ; test ${GraderRunES} -eq 0 && 
			   test_run -T -lt 0 dot -T pdf -o "${sast%.ast}.pdf" "${sast%.ast}.gv" 2>_dotgen_fromgv.err ; test ${GraderRunES} -ne 0 ; then 
				grader_echo "ERROR:  could not generate graph from '${sast}'."
			fi
		fi
	else 			
		grader_echo "ERROR:  AST graph data output does not exist or is empty."
	fi	

	if test -s "${sast%.ast}.pdf" ; then
		grader_echo "AST graph data for ${1%.pdf} generation seems to WORK (correctness evaluated by hand)."
		mv ${tallyast}.bad ${tallyast}.good
		if test -s "${rpdf}" ; then 
			# we will use this one for grading purposes, so put it in the backchannel
			# queue
			queuebackchannel `pwd` "${sast%.ast}.pdf" "${rpdf}" 	
		fi
	else 
		grader_msg <<EoT
The AST data generated from your program is in ${sast}, it could not be
converted to a graph directly by dot(1) or indirectly through a helper
script

  ${COMPGRADING}/tree-to-graphvis 

This will certainly result in a grading deduction.

The commands attempted in this process have been displayed on the terminal (before
this message).  stderr from these attempts have been stored in _dotgen_direct.err
(the direct use of dot(1)), _dotgen_togv.err (helper generation of .gv file), and
_dotgen_fromgv.err (dot(1) on the helper generated .gv).

IF YOU WANT TO INSPECT THIS FAILURE, CTRL-C now!
EoT
		grader_keystroke
	fi
	rm -f "${sast%.ast}.gv"
	rm -f "${sast%.ast}.pdf"
	rm -f _dotgen_{direct,togv,fromgv}.err
	#set +x
	return 0
}


_tid_to_class()
{
	# remove colons if they exist
	local t=${1#:}
	t=${t%:}
	case "${t}" in
		SYNTAX ) echo SYNTAX ;;
		NOVAR|CONV|EXPR) echo ERROR ;;
		REVAR|UNUSED|UNINIT|CONST ) echo WARN;;
		* ) grader_echo "ERROR?  unknown OUTPUT type '${1}'; categorizing as SYNTAX."
		    grader_keystroke
			echo SYNTAX
			;;
	esac
}

analyze_out()
{
	local TIDS='SYNTAX NOVAR CONV EXPR REVAR UNUSED UNINIT CONST'
	local rout="${graderloc}/results/${1}" 
	local tallysyntax="${2}"
	local tallyerror="${3}"
	local tallywarn="${4}"
	local sout="${5}"
	local tmpsed=`grader_mktemp`
	shift 5
	touch "${tmpsed}"
	cat "${rout}" | while read T L C I ; do
		local t
		local i
		t=${T#:} ; t=${t%:}
		i=${T#:} ; i=${i%:}
		#echo //$T $L $C $I//
		# does sout have an identical line?
		local thistally=`case "${T}" in
			:SYNTAX: ) echo "${tallysyntax}.$t.$L.$C.$i.good" ;;
			:ERROR:  ) echo "${tallyerror}.$t.$L.$C.$i.good" ;;
			:WARN:   ) echo "${tallywarn}.$t.$L.$C.$i.good" ;;
			* ) grader_echo "ERROR?  results are munged up in '${graderloc}' --- download again?"
			    exit 1
				;;
			esac`
		if cat "${sout}" |  grep -e "^$T $L $C $I"'$' >/dev/null ; then
			touch "${thistally}"
			# this is a good line, not an extra line
			echo "/^$T $L $C $I"'$/d' >> "${tmpsed}"
		else 
			# missing
			touch "${thistally%good}.$t.$L.$C.$i.bad"
			# keep track of the number missing -- 
			# we won't double count extra lines as also missing lines (imprecise, but to student's benefit)
			touch "${thistally%good}.$t.$L.$C.$i.missing"
		fi
	done
#	echo ${rout}
#	echo ${tmpsed}
#	echo ${tallysyntax} ${tallyerror} ${tallywarn}
	# look for extra lines that don't belong
	for typ in ${TIDS} ; do 
		local thistally=`case "$(_tid_to_class ${typ})" in
			SYNTAX ) echo "${tallysyntax}.SYNTAX" ;;
			ERROR  ) echo "${tallyerror}.ERROR" ;;
			WARN   ) echo "${tallywarn}.WARN" ;;
		esac`
		sed -f "${tmpsed}" "${sout}" | grep "${typ}"':$' | while read T L C I ; do
			i=${I#:}; i=${i%:}
			touch "${thistally}.$L.$C.$i.extra"
		done
		# remove a .extra marker for each .missing, this way we are sure not to count misformatted or "located" messages
		# as extra messages --- imprecise but to student's benefit
		paste <(eval ls -1 ${thistally}.*.${typ}.extra 2>/dev/null) <(eval ls -1 ${thistally}.*.${typ}.missing 2>/dev/null) | while read x m ; do
			test -z "${m}" && break 
			echo >&2 "reconciling '${x}' and '${m}'"
			rm -f "${x}" "${m}"
		done
		#ls -d ${thistally}.*.${typ}.extra >&2  || echo >&2 "No .extra for $typ"
		# remaining count of .extra files account for a messages *somewhere* in the output that doesn't belong
	done
	###
	# per source summary of errors now, things will be counted up and aggregated for a final rubric score after
	# all source has been processed
	if find `dirname "${tallysyntax}"` `dirname "${tallyerror}"` `dirname "${tallywarn}"` -type f | \
			grep -E -e '('"${tallysyntax}"'|'"${tallyerror}"'|'"${tallywarn}"').*(extra|missing)$' >/dev/null ; then 
		grader_msg <<EoT
The semantic analysis OUTPUT from your program is in _${sout} (note the two
leading underscores).  Your OUTPUT filtered result is in ${sout}, the expected
results are at
  ${rout}
Your OUTPUT filtered results do not compare favorably and will certainly result
in a grading deduction.

IF YOU WANT TO INSPECT THIS FAILURE, CTRL-C now!
EoT
		grader_keystroke
	else 
		grader_echo "Semantic analysis OUTPUT results for test program ${sout%.out} are GOOD :)"
	fi
	rm     "${tmpsed}"
	rm -f  "${sout}"
	rm -f _"${sout}"
	rm -f  "${seminconsistencies}"
}




test_thewhole_shebang()
{
	# $1=graderloc/test program name
	local srcname="${1%.???}"
	local tallyast="${tallyastdir}/${srcname}"
	local tallysym="${tallysymdir}/${srcname}"
	local tallysyntax="${tallysyntaxdir}/${srcname}"   # suffixed with ES (exitstatus) or syntax (mis specified location)
	local tallyerror="${tallyerrordir}/${srcname}"    # suffixed with ES (exitstatus) or semantic error id
	local tallywarn="${tallywarndir}/${srcname}"     # suffixed with ES (exitstatus) or semantic warn  id

	local testdir=_zobostest
	rm -rf "${testdir}/"*
	mkdir -p "${testdir}/"
	cp "${graderloc}/tests/${1}" "./${testdir}/${1}"
	# some students will need these to run
	for f in zlang.lr zlang.cfg zlang-pure.cfg; do 
		test -s "$f" || cp "${graderloc}/$f" ./
	done

	if run_one_source "${srcname}.out" "${tallysyntax}" "${tallyerror}" "${tallywarn}" \
			"${comploc}/${PROGRAM}" "${testdir}/${1}" "_${srcname}.ast" "_${srcname}.sym" ; then 
		analyze_sym "${srcname}.sym" "${tallysym}" "_${srcname}.sym"
		process_ast "${srcname}.pdf" "${tallyast}" "_${srcname}.ast"
	fi
	analyze_out "${srcname}.out" "${tallysyntax}" "${tallyerror}" "${tallywarn}" "_${srcname}.out"
	# readability
	grader_echo

	rm -rf "${testdir}"
	rm -f  "_${srcname}.ast" "_${srcname}.sym"
}


beginbackchannel

export tallysyntaxdir="`grader_mktemp -d syntax`"
export tallyastdir="`grader_mktemp -d ast`"
export tallysymdir="`grader_mktemp -d sym`"
export tallyerrordir="`grader_mktemp -d error`"
export tallywarndir="`grader_mktemp -d warn`"
export backchanneldir="`grader_mktemp -d bcq`"
for tst in `( cd "${graderloc}/tests/" && ls -1d *.tok )` ; do 
	test_thewhole_shebang "${tst}" 
done
#test_thewhole_shebang "symtable-2.tok" 
#test_thewhole_shebang "conv-1.tok" 

width=44
show_tallies $width ${basiciotallydir}  "Basic I/O tests"
show_tallies $width ${tallysyntaxdir}   "Detect and report SYNTAX errors correctly"
show_tallies $width ${tallyastdir} 		"AST simplification and graph information"
show_tallies $width ${tallysymdir} 		"emit symtable and symtable.dat requirements"
show_tallies $width ${tallyerrordir} 	"ERROR class semantic issues"
show_tallies $width ${tallywarndir} 	"WARN class semantic issues"
grader_echo

pushbackchannel
show_tally_logic

# always show cwd at the end, so grader is sure the correct results
# are recorded for the correct submission (the upload id is in the path)
grader_echo ""
pwd

