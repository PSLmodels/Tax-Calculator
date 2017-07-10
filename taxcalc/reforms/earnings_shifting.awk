# earnings_shifting.awk summarizes output written by earnings_shifting.py
# USAGE: python earnings_shifting.py ... | awk -f earnings_shifting.awk 

# extract CLI args used to execute earnings_shifting.py script
NR==1 {
    taxyear = $2
    min_earnings = $3
    min_savings = $4
    shift_prob = $5
}

# extract total number of individuals who shift earnings
$0~/==> CALC4/ && $0~/number of/ {
    nes += $NF
}

# extract total number of dollars in shifted earnings
$0~/==> CALC4/ && $0~/earnings shifted/ {
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
    frmt = "%4d %10.2f %9.2f %6.3f : %7.3f %9.3f %12.1f\n"
    printf(frmt, taxyear, min_earnings, min_savings, shift_prob,
           nes, des, taxdiff)
}
