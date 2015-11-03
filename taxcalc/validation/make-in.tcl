# MAKE-IN.TCL writes an Internet-TAXSIM-9.3-formatted input file to stdout
# USAGE: tclsh make-in.tcl calyear letter [rng_offset]
# PRODUCTION: tclsh make-in.tcl yyYY L > LYY.in

if { $argc < 2 || $argc > 3 } {
    puts stderr "USAGE: tclsh make-in.tcl calyear letter \[rng_offset\]"
    exit 1
}
set cyr [lindex $argv 0]
if { $cyr < 2013 || $cyr > 2020 } {
    puts stderr "ERROR: calyear=$cyr not in \[2013,2020\] range"
    exit 1
}
set letter [lindex $argv 1]
if { $argc == 3 } {
    set offset [lindex $argv 2]
} else {
    set offset 0
}
if { $offset < 0 || $offset > 1000 } {
    puts stderr "ERROR: rng_offset=$offset not in \[0,1000\] range"
    exit 1
}
switch $letter {
    a { # assumptions for aYY.in sample:
        set num 100000
        set max_wage_yng 300
        set max_wage_old  20
        set max_pnconpct 0
        set max_pnben  40
        set max_ssben  40
        set max_ucomp  5
        set max_divinc 10
        set max_intinc 0
        set max_scgain 10
        set max_lcgain 10
        set max_ided_pref 0
        set max_ided_nopref 0
        set max_ccexp 0
    }
    b { # assumptions for bYY.in sample:
        set num 100000
        set max_wage_yng 300
        set max_wage_old  20
        set max_pnconpct 0
        set max_pnben  40
        set max_ssben  40
        set max_ucomp  5
        set max_divinc 10
        set max_intinc 0
        set max_scgain 10
        set max_lcgain 10
        set max_ided_pref 40
        set max_ided_nopref 40
        set max_ccexp 0
    }
    c { # assumptions for cYY.in sample:
        # same as b except add child care expenses, ivar[17]
        set num 100000
        set max_wage_yng 300
        set max_wage_old  20
        set max_pnconpct 0
        set max_pnben  40
        set max_ssben  40
        set max_ucomp  5
        set max_divinc 10
        set max_intinc 0
        set max_scgain 10
        set max_lcgain 10
        set max_ided_pref 40
        set max_ided_nopref 40
        set max_ccexp 12
    }
    default {
        puts stderr "ERROR: undefined letter $letter"
        exit 1
    }
}

set seed [expr 4321*($cyr%100) + $offset]
tcl::mathfunc::srand $seed

proc uniform { lo hi } {
    return [expr round($lo+rand()*($hi-$lo))]
}

# write $num TAXSIM-input lines, one for each filing unit
for {set id 1} {$id <= $num} {incr id} {
    set raw_ms [uniform 1 5]
    set pnconpct 0
    switch $raw_ms {    
        1 { set ms 1
            set elders [uniform 0 1]
            set numdeps 0
            set ccdeps 0
            set ccexp 0
            if { $elders > 0 } {
                set wage1 [expr 100*[uniform 0 [expr 10*$max_wage_old]]]
                set wage2 0
                set pnben [expr 1000*[uniform 0 $max_pnben]]
                set ssben [expr 1000*[uniform 0 $max_ssben]]
                set ucomp [expr 1000*[uniform 0 $max_ucomp]]
            } else {
                set wage1 [expr 100*[uniform 0 [expr 10*$max_wage_yng]]]
                set wage2 0
                if { $wage1+$wage2 > 0.0 } {
                    set pnconpct [uniform 0 $max_pnconpct]
                }
                set pnben 0
                set ssben 0
                set ucomp [expr 1000*[uniform 0 $max_ucomp]]
            }
        }
        2 -
        3 -
        4 { set ms 2
            set elders [uniform 0 2]
            if { $elders > 0 } {
                set numdeps 0
                set ccdeps 0
                set ccexp 0
                set wage1 [expr 100*[uniform 0 [expr 10*$max_wage_old]]]
                set wage2 [expr 100*[uniform 0 [expr 10*$max_wage_old]]]
                if { $wage1+$wage2 > 0.0 } {
                    set pnconpct [uniform 0 $max_pnconpct]
                }
                set pnben [expr 2000*[uniform 0 $max_pnben]]
                set ssben [expr 2000*[uniform 0 $max_ssben]]
                set ucomp [expr 1000*[uniform 0 $max_ucomp]]
            } else {
                set numdeps [uniform 0 3]
                set ccdeps [uniform 0 $numdeps]
                if { $ccdeps > 0 && $max_ccexp > 0 } {
                    set ccexp [expr  1000*[uniform 0 $max_ccexp]]
                }
                set wage1 [expr 100*[uniform 0 [expr 10*$max_wage_yng]]]
                set wage2 [expr 100*[uniform 0 [expr 10*$max_wage_yng]]]
                if { $wage1+$wage2 > 0.0 } {
                    set pnconpct [uniform 0 $max_pnconpct]
                }
                set pnben [expr  500*[uniform 0 $max_pnben]]
                set ssben [expr  500*[uniform 0 $max_ssben]]
                set ucomp [expr 1000*[uniform 0 $max_ucomp]]
            }
        }
        5 { set ms 3
            set elders [uniform 0 1]
            if { $elders > 0 } {
                set numdeps [uniform 1 1]
                set ccdeps 0
                set ccexp 0
                set wage1 [expr 100*[uniform 0 [expr 10*$max_wage_old]]]
                set wage2 0
                if { $wage1+$wage2 > 0.0 } {
                    set pnconpct [uniform 0 $max_pnconpct]
                }
                set pnben [expr 1000*[uniform 0 $max_pnben]]
                set ssben [expr 1000*[uniform 0 $max_ssben]]
                set ucomp [expr 1000*[uniform 0 $max_ucomp]]
            } else {
                set numdeps [uniform 1 3]
                set ccdeps [uniform 0 $numdeps]
                if { $ccdeps > 0 && $max_ccexp > 0 } {
                    set ccexp [expr  1000*[uniform 0 $max_ccexp]]
                }
                set wage1 [expr 100*[uniform 0 [expr 10*$max_wage_yng]]]
                set wage2 0
                if { $wage1+$wage2 > 0.0 } {
                    set pnconpct [uniform 0 $max_pnconpct]
                }
                set pnben 0
                set ssben 0
                set ucomp [expr 1000*[uniform 0 $max_ucomp]]
            }
        }
    } ;# end switch $ms
    if { $max_divinc > 0 } {
        set divinc [expr 1000*[uniform 0 $max_divinc]]
    } else {
        set divinc 0
    }
    if { $max_intinc > 0 } {
        set intinc [expr 1000*[uniform 0 $max_intinc]]
    } else {
        set intinc 0
    }
    if { $max_scgain > 0 } {
        set scgain [expr 1000*[uniform 0 $max_scgain]-5000]
    } else {
        set scgain 0
    }
    if { $max_lcgain > 0 } {
        set lcgain [expr 1000*[uniform 0 $max_lcgain]-5000]
    } else {
        set lcgain 0
    }
    if { $max_ided_pref > 0 } {
        set total_pref [uniform 0 $max_ided_pref]
        set retax_frac [expr 1.0-$total_pref/double($max_ided_pref)]
        set retax_amt [expr round(1000*$retax_frac*$total_pref)]
        set ided_pref [expr round(1000*$total_pref-$retax_amt)]
        if { $ided_pref < 0 } { set ided_pref 0 }
    } else {
        set retax_amt 0
        set ided_pref 0
    }
    if { $max_ided_nopref > 0 } {
        set ided_nopref [expr 1000*[uniform 0 $max_ided_nopref]]
    } else {
        set ided_nopref 0
    }
    set tot_ded [expr $retax_amt + $ided_pref + $ided_nopref]
    if { $tot_ded > 0 } {
        set max_ded [expr 0.5*($wage1 + $wage2 + $divinc + $pnben + $ssben)]
        if { $max_ded < 0 } { set max_ded 0 }
        if { $tot_ded >= $max_ded } {
            set frac_retax [expr $retax_amt/double($tot_ded)]
            set retax_amt [expr round($frac_retax*$max_ded)]
            set frac_pref [expr $ided_pref/double($tot_ded)]
            set ided_pref [expr round($frac_pref*$max_ded)]
            set ided_nopref [expr round($max_ded - $retax_amt - $ided_pref)]
            if { $ided_nopref < 0 } { set ided_nopref 0 }
        }
    }
    set part0108 [format "%d %d %d %d %d %d %d %d" \
                      $id $cyr 0 $ms $numdeps $elders $wage1 $wage2]
    set part0915 [format "%d %d %d %d %d %d %d" \
                      $divinc $intinc $pnben $ssben 0 0 $retax_amt]
    set part1620 [format "%d %d %d %d %d" \
                      $ided_pref $ccexp $ucomp $ccdeps $ided_nopref]
    set part2122 [format "%d %d" \
                      $scgain $lcgain]
    puts "$part0108 $part0915 $part1620 $part2122"
} ;# end for id loop
