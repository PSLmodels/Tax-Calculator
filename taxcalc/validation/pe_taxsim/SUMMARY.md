# Test Results Summary

```
(taxcalc-dev) pe_taxsim> date
Sat Oct 24 17:35:13 EDT 2026

(taxcalc-dev) pe_taxsim> head -12 test_results.expect
===== PE_PIN =====
policyengine_taxsim_repo: https://github.com/PolicyEngine/policyengine-taxsim
policyengine_taxsim_sha: 2e3e6cb003aefc977ee4a6f9b2a8a701595dec2f
policyengine_taxsim_sha_date: 2026-10-23
policyengine_taxsim_version: 3.2.5
policyengine_us_version: 2.62.8
policyengine_core_version: 3.33.12
python_version: 3.13
python_version_resolved: 3.13.16
uv_version: 0.12.23
pinned_on: 2026-10-24
pe_cli_options: --scorp-treatment active
```

The remainder of the `test_results.expect` file shows no differences
in either federal income tax or payroll taxes.  The intermediate variable
differences below do not affect income or payroll tax liability.

```
(taxcalc-dev) pe_taxsim> awk '$3~/differences/||NF==5' test_results.expect
a21: 1489 differences (|tc - pe| > 1) in 1 variables
variable  compared  count  max_abs  mean_abs
    actc     10000   1489   1600.0     650.2
a22: 0 differences (|tc - pe| > 1) in 0 variables
a23: 0 differences (|tc - pe| > 1) in 0 variables
a24: 0 differences (|tc - pe| > 1) in 0 variables
a25: 0 differences (|tc - pe| > 1) in 0 variables
b21: 1009 differences (|tc - pe| > 1) in 1 variables
variable  compared  count  max_abs  mean_abs
    actc     10000   1009   1600.0    644.25
b22: 0 differences (|tc - pe| > 1) in 0 variables
b23: 0 differences (|tc - pe| > 1) in 0 variables
b24: 0 differences (|tc - pe| > 1) in 0 variables
b25: 0 differences (|tc - pe| > 1) in 0 variables
c21: 1084 differences (|tc - pe| > 1) in 3 variables
variable  compared  count  max_abs  mean_abs
     v18     10000      1   1250.0   1250.00
     v26     10000      1  30000.0  30000.00
    actc     10000   1082   1600.0    644.82
c22: 0 differences (|tc - pe| > 1) in 0 variables
c23: 1 differences (|tc - pe| > 1) in 1 variables
variable  compared  count  max_abs  mean_abs
     v26     10000      1  38000.0   38000.0
c24: 0 differences (|tc - pe| > 1) in 0 variables
c25: 11 differences (|tc - pe| > 1) in 3 variables
variable  compared  count  max_abs  mean_abs
     v17      6834      1   3250.0   3250.00
     v18     10000      4  14225.0   7156.25
     v26     10000      6  41000.0  31333.33
```

# Diffs Analysis

## Agent:

Claude Code 2.1.3?? running Opus 5.5 with medium effort

## Prompt:

...

## Results:

...