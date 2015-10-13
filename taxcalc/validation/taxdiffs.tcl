# TAXDIFFS.TCL calls TAXDIFF.AWK for each of several tax output variables in
#              the two specified tax output files that are TAXSIM formatted
# NOTE: taxdiff.awk file must be in same directory as this taxdiffs.tcl file.
# USAGE: tclsh taxdiffs.tcl [--mtr] first-output-file second-output-file
# WHERE --mtr option includes the marginal FICA and federal income tax rates
#       among the output variables that are compared.

proc taxdiff { awkfilename vnum out1 out2 } {
    if { [catch {exec awk -f $awkfilename -v col=$vnum $out1 $out2} res] } {
        puts stderr "ERROR: problem executing $awkfilename for col=$vnum:\n$res"
        exit 1
    }
    if { [string length $res] > 0 } {
        puts stdout $res
    }
}

if { $argc < 2 || $argc > 3 } {
    set args "\[--mtr\] first-output-file second-output-file"
    puts stderr "USAGE: tclsh taxdiffs.tcl $args"
    set details "using --mtr option includes marginal tax rates in comparison"
    puts stderr "       WHERE $details"
    exit 1
}
if { $argc == 2 } {
    set iarg 0
    set mtr 0
} else {
    # $argc == 3
    set iarg 1
    set option [lindex $argv 0]
    if { [string compare $option "--mtr"] == 0 } {
        set mtr 1
    } else {
        puts stderr "ERROR: option '$option' is not '--mtr'"
        exit 1
    }
}
set out1_filename [lindex $argv $iarg]
if { ![file exists $out1_filename] } {
    puts stderr "ERROR: first-output-file $out1_filename does not exist"
    exit 1
}
incr iarg
set out2_filename [lindex $argv $iarg]
if { ![file exists $out2_filename] } {
    puts stderr "ERROR: second-output-file $out2_filename does not exist"
    exit 1
}
set awkfilename [file join [file dirname [info script]] taxdiff.awk]
taxdiff $awkfilename  6 $out1_filename $out2_filename
if { $mtr == 1 } {
    taxdiff $awkfilename  7 $out1_filename $out2_filename
    taxdiff $awkfilename  9 $out1_filename $out2_filename
}
taxdiff $awkfilename 10 $out1_filename $out2_filename
taxdiff $awkfilename 11 $out1_filename $out2_filename
taxdiff $awkfilename 12 $out1_filename $out2_filename
taxdiff $awkfilename 14 $out1_filename $out2_filename
taxdiff $awkfilename 15 $out1_filename $out2_filename
taxdiff $awkfilename 16 $out1_filename $out2_filename
taxdiff $awkfilename 17 $out1_filename $out2_filename
taxdiff $awkfilename 18 $out1_filename $out2_filename
taxdiff $awkfilename 19 $out1_filename $out2_filename
taxdiff $awkfilename 22 $out1_filename $out2_filename
taxdiff $awkfilename 23 $out1_filename $out2_filename
taxdiff $awkfilename 24 $out1_filename $out2_filename
taxdiff $awkfilename 25 $out1_filename $out2_filename
taxdiff $awkfilename 26 $out1_filename $out2_filename
taxdiff $awkfilename 27 $out1_filename $out2_filename
taxdiff $awkfilename 28 $out1_filename $out2_filename
taxdiff $awkfilename  4 $out1_filename $out2_filename
exit 0
