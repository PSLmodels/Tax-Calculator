# earnings_shifting.awk summarizes output written by earnings_shifting.py
# USAGE: python earnings_shifting.py ... | awk -f earnings_shifting.awk 

# extract CLI args used to execute earnings_shifting.py script
NR==2 {
    taxyear = $2
    wage_amt = $3
    min_earnings = $4
    min_savings = $5
    shift_prob = $6
}

# extract total number of individuals who shift earnings
$0~/==> CALC4/ && $0~/number of/ {
    nes += $NF
}

# extract total number of dollars in shifted earnings
$0~/==> CALC4/ && $0~/earnings of/ {
    des += $NF
}

# extract change in combined tax revenue after income shifting
$0~/==> CALC4 vs CALC1/ {
    in_4vs1_block = 1
}
in_4vs1_block==1 && $0~/Difference/ {
    in_4vs1_diff_block = 1
}
in_4vs1_diff_block==1 && $1~/A/ {
    taxdiff = $6
}

END {
    frmt = "%4d %9.2f %10.2f %9.2f %6.3f : %7.3f %9.3f %12.1f\n"
    printf(frmt, taxyear, wage_amt, min_earnings, min_savings, shift_prob,
           nes, des, taxdiff)
}
