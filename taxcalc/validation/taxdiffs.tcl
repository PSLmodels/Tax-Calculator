# TAXDIFFS.TCL calls TAXDIFF.AWK for each of several tax output variables in
#              the two specified tax output files that are formatted like
#              Internet-TAXSIM generated output
# NOTE: taxdiff.awk file must be in same directory as this taxdiffs.tcl file.
# USAGE: tclsh taxdiffs.tcl \
#              [--ovar4 | --ovar4-eitc | --drake] \
#              1st-out-file 2nd-out-file [dump]
# WHERE --ovar4 option computes differences only for output variable 4
# WHERE --ovar4-eitc option uses variable 4 net of variable 25
#    OR --drake option skips output variables not in Drake Software output
# AND optional dump causes all ovar4 differences greater than $10 to be shown

proc usage {} {
    set options "--ovar4|--ovar4-eitc|--drake"
    set args "\[$options\] \[--dump\] file1 file2"
    puts stderr "USAGE: tclsh taxdiffs.tcl $args"
    set details "computes diffs only for output variable 4"
    puts stderr "       WHERE using --ovar4 option $details"
    set details "computes diffs for ovar4 net of ovar25"
    puts stderr "          OR using --ovar4-eitc option $details"
    set details "skips output not in Drake Software files"
    puts stderr "          OR using --drake option $details"
    set details "shows all ovar4 diffs greater than \$10"
    puts stderr "       WHERE using --dump option $details"
}

proc taxdiff { awkfilename vnum out1 out2 dump } {
    set awkcmd "dump=$dump"
    if { [catch {exec awk -f $awkfilename -v col=$vnum $out1 $out2 \
                 dump=$dump} res] } {
        puts stderr "ERROR: problem executing $awkfilename for col=$vnum:\n$res"
        exit 1
    }
    if { [string length $res] > 0 } {
        puts stdout $res
    }
}

if { $argc < 2 || $argc > 4 } {
    puts stderr "ERROR: number command-line arguments must be 2, 3, or 4"
    usage
    exit 1
}
set ovar4 0
set ovar4_net_eitc 0
set drake 0
set dump 0
if { $argc >= 3 } {
    # $argc >= 3 implies some options are specified
    set option [lindex $argv 0]
    if { [string compare $option "--ovar4"] == 0 } {
        set ovar4 1
    } elseif { [string compare $option "--ovar4-eitc"] == 0 } {
        set ovar4_net_eitc 1
    } elseif { [string compare $option "--drake"] == 0 } {
        set drake 1
    } elseif { [string compare $option "--dump"] == 0 } {
        set dump 1
    } else {
        puts stderr "ERROR: illegal first command-line option: $option"
        usage
        exit 1
    }
    if { $argc == 4 } {
        set option [lindex $argv 1]
        if { [string compare $option "--dump"] == 0 } {
            set dump 1
        } else {
            puts stderr "ERROR: illegal second command-line option: $option"
            usage
            exit 1
        }
    }
}
set iarg [expr $argc - 2]
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
if { $ovar4 == 1 } {
    taxdiff $awkfilename  4 $out1_filename $out2_filename $dump
    exit 0
} elseif { $ovar4_net_eitc == 1} {
    taxdiff $awkfilename 4-25 $out1_filename $out2_filename $dump
    exit 0
}
taxdiff $awkfilename  6 $out1_filename $out2_filename $dump
if { $drake == 1 } {
    # skip 7 and 9
} else {
    taxdiff $awkfilename  7 $out1_filename $out2_filename $dump
    taxdiff $awkfilename  9 $out1_filename $out2_filename $dump
}
taxdiff $awkfilename 10 $out1_filename $out2_filename $dump
if { $drake == 1 } {
    # skip 11
} else {
    taxdiff $awkfilename 11 $out1_filename $out2_filename $dump
}
taxdiff $awkfilename 12 $out1_filename $out2_filename $dump
taxdiff $awkfilename 14 $out1_filename $out2_filename $dump
taxdiff $awkfilename 15 $out1_filename $out2_filename $dump
taxdiff $awkfilename 16 $out1_filename $out2_filename $dump
taxdiff $awkfilename 17 $out1_filename $out2_filename $dump
taxdiff $awkfilename 18 $out1_filename $out2_filename $dump
taxdiff $awkfilename 19 $out1_filename $out2_filename $dump
taxdiff $awkfilename 22 $out1_filename $out2_filename $dump
taxdiff $awkfilename 23 $out1_filename $out2_filename $dump
taxdiff $awkfilename 24 $out1_filename $out2_filename $dump
taxdiff $awkfilename 25 $out1_filename $out2_filename $dump
if { $drake == 1 } {
    # skip 26
} else {
    taxdiff $awkfilename 26 $out1_filename $out2_filename $dump
}
taxdiff $awkfilename 27 $out1_filename $out2_filename $dump
if { $drake == 1 } {
    # skip 28
} else {
    taxdiff $awkfilename 28 $out1_filename $out2_filename $dump
}
taxdiff $awkfilename  4 $out1_filename $out2_filename $dump
exit 0
