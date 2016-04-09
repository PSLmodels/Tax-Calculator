# TAXDIFFS.TCL calls TAXDIFF.AWK for each of several tax output variables in
#              the two specified tax output files that are formatted like
#              Internet-TAXSIM generated output
# NOTE: taxdiff.awk file must be in same directory as this taxdiffs.tcl file.
# USAGE: tclsh taxdiffs.tcl [--ovar4 | --taxcalc] 1st-out-file 2nd-out-file
# WHERE --ovar4 option computes differences only for output variable 4
#    OR --taxcalc option skips output variables not produced by SAS TAXCALC

proc usage {} {
    set args "\[--ovar4 | --taxcalc\] 1st-out-file 2nd-out-file"
    puts stderr "USAGE: tclsh taxdiffs.tcl $args"
    set details "computes diffs only for output variable 4"
    puts stderr "       WHERE using --ovar4 option $details"
    set details "skips output not produced by SAS TAXCALC"
    puts stderr "          OR using --taxcalc option $details"
}

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
    puts stderr "ERROR: number command-line arguments must be two or three"
    usage
    exit 1
}
if { $argc == 2 } {
    set iarg 0
    set ovar4 0
    set taxcalc 0
} else {
    # $argc == 3
    set iarg 1
    set option [lindex $argv 0]
    if { [string compare $option "--ovar4"] == 0 } {
        set ovar4 1
    } elseif { [string compare $option "--taxcalc"] == 0 } {
        set taxcalc 1
    } else {
        puts stderr "ERROR: illegal command-line option: $option"
        usage
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
if { $ovar4 == 0 } {
    if { $taxcalc == 0 } {
        taxdiff $awkfilename  6 $out1_filename $out2_filename
        taxdiff $awkfilename  7 $out1_filename $out2_filename
        taxdiff $awkfilename  9 $out1_filename $out2_filename
    }
    taxdiff $awkfilename 10 $out1_filename $out2_filename
    if { $taxcalc == 0 } {
        taxdiff $awkfilename 11 $out1_filename $out2_filename
    }
    taxdiff $awkfilename 12 $out1_filename $out2_filename
    if { $taxcalc == 0 } {
        taxdiff $awkfilename 14 $out1_filename $out2_filename
        taxdiff $awkfilename 15 $out1_filename $out2_filename
    }
    taxdiff $awkfilename 16 $out1_filename $out2_filename
    taxdiff $awkfilename 17 $out1_filename $out2_filename
    taxdiff $awkfilename 18 $out1_filename $out2_filename
    taxdiff $awkfilename 19 $out1_filename $out2_filename
    taxdiff $awkfilename 22 $out1_filename $out2_filename
    taxdiff $awkfilename 23 $out1_filename $out2_filename
    taxdiff $awkfilename 24 $out1_filename $out2_filename
    if { $taxcalc == 0 } {
        taxdiff $awkfilename 25 $out1_filename $out2_filename
    }
    taxdiff $awkfilename 26 $out1_filename $out2_filename
    taxdiff $awkfilename 27 $out1_filename $out2_filename
    taxdiff $awkfilename 28 $out1_filename $out2_filename
}
taxdiff $awkfilename  4 $out1_filename $out2_filename
exit 0
