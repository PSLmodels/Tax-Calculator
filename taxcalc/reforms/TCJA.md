TCJA FAQ
========

In Tax-Calculator release 0.15.0 and higher, the `policy_current_law`
file represents TCJA, not the pre-TCJA policy that was represented by
`policy_current_law.json` in releases before 0.15.0.

**1. How can I use pre-TCJA policy as the baseline?**

You need to use the new
[2017_law.json](https://github.com/open-source-economics/Tax-Calculator/blob/master/taxcalc/reforms/2017_law.json)
as a "reform", and then, if you want to compare that pre-TCJA policy
to an old reform, implement the old reform as usual.  This
compound-reform technique works well and is being used extensively in
the Tax-Calculator unit tests.  Here is a code fragment illustrating
the use of this compound-reform technique, where we want to analyze
the effects of the [Brown-Khanna EITC
reform](https://github.com/open-source-economics/Tax-Calculator/blob/master/taxcalc/reforms/BrownKhanna.json)
relative to pre-TCJA policy:
```
pol = Policy()  # pol is TCJA
param = Calculator.read_json_param_objects('...../2017_law.json', None)
pol.implement_reform(param['policy'])  # now pol is pre-TCJA law
if pol.reform_errors:
    print(pol.reform_errors)
    exit(1)
calc_base = Calculator(policy=pol, records=Records(), verbose=False)

param = Calculator.read_json_param_objects('...../BrownKhanna.json', None)
pol.implement_reform(param['policy'])  # now pol is EITC reform relative to pre-TCJA law
if pol.reform_errors:
    print(pol.reform_errors)
    exit(1)
calc_reform = Calculator(policy=pol, records=Records(), verbose=False)
```

**2. Does Tax-Calculator produce the same results for pre-TCJA policy
     as before?**

Yes, release 0.14.3 and 0.15.0 produce the same aggregate results for
pre-TCJA policy even though the contents of `current_law_policy.json`
have changed.

For an analysis that shows the pre-TCJA tax revenues for 2019 are the
same, see below at the heading **TCJA and pre-TCJA Comparisons**.

**3. Does Tax-Calculator produce the same results for TCJA policy as
     before?**

No, there is a small difference (less than one percent) in aggregate
income tax revenues between the Tax-Calculator releases 0.15.0 and
0.14.3.  This difference is caused by the fact that Tax-Calculator
0.15.0 adds several TCJA provisions that were not included in
Tax-Calculator 0.14.3.  See pull requests #1818 and #1819 for details
on the newly added TCJA provisions.

For an analysis of the 2019 difference in aggregate revenues, see
below at the heading **TCJA and pre-TCJA Comparisons**.

For a compound reform that shows the consistency of the new
`2017_law.json` file and the revised `TCJA_Reconciliation.json` file,
see below at the heading **A Round-Trip Compound Reform**.

**4. Does TCJA current-law policy incorporate any behavior responses?**

Beginning with release 0.25.0, Tax-Calculator incorporates a new CBO
budget outlook that presumably includes the effects of any behavioral
changes and growth effects that one might expect to be caused by TCJA.


TCJA and pre-TCJA Comparisons
-----------------------------

This addendum shows that the 2019 aggregate revenues are identical for
pre-TCJA policy and very close for TCJA policy.

Here are the contents of `aggresults.py`:
```
from __future__ import print_function
import sys
import urllib
import taxcalc
from taxcalc import Policy, Records, Calculator

if len(sys.argv) == 1:
    reform = 'clp'
else:
    base_url = ('https://raw.githubusercontent.com/'
                'open-source-economics/Tax-Calculator/{}/taxcalc/reforms/')
    if '0.14.3' in taxcalc.__version__:
        reform = 'TCJA_Reconciliation.json'
        reform_text = urllib.urlopen(base_url.format('0.14.3') + reform).read()
    else:
        reform = '2017_law.json'
        reform_text = urllib.urlopen(base_url.format('master') + reform).read()

cyr = 2019

print('taxcalc version', taxcalc.__version__)
print('policy regime', reform)
print('year', cyr)

pol = Policy()
if reform != 'clp':
    params = Calculator.read_json_param_objects(reform_text, None)
    pol.implement_reform(params['policy'])
    if pol.reform_errors:
        print(pol.reform_errors)
        exit(1)
calc = Calculator(policy=pol, records=Records(), verbose=False)
calc.advance_to_year(cyr)
calc.calc_all()
itax = calc.weighted_total('iitax') * 1e-9
ptax = calc.weighted_total('payrolltax') * 1e-9
ctax = itax + ptax
res = 'itax,ptax,combined($B) {:7.3f} {:7.3f} {:7.3f}'
print(res.format(itax, ptax, ctax))
```
Here are the content of the `testing.sh` bash script that executes
`aggresults.py` in four different ways:
```
#!/bin/bash
date
# stop if not on master branch
pushd ../tax-calculator 2>&1 > /dev/null
git branch | awk '$1~/\*/{if($2~/master/){exit 0}else{exit 1}}'
if [ $? -ne 0 ]; then
    echo "STOPPING: not on master branch of local git repo"
    exit 1
fi
popd 2>&1 > /dev/null
# generate results using taxcalc 0.14.3
echo Starting 0.14.3 work ...
conda install -c ospc taxcalc=0.14.3 --yes 2>&1 > /dev/null
python aggresults.py     > 0143-2017.aggres
python aggresults.py ref > 0143-tcja.aggres
# generate results using taxcalc 0.15.0
echo Starting 0.15.0 work ...
pushd ../tax-calculator/conda.recipe 2>&1 > /dev/null
./install_local_taxcalc_package.sh 2>&1 > /dev/null
popd 2>&1 > /dev/null
python aggresults.py     > 0150-tcja.aggres
python aggresults.py ref > 0150-2017.aggres
date
# show results
set -x
cat 0150-2017.aggres
diff 0143-2017.aggres 0150-2017.aggres
diff 0143-tcja.aggres 0150-tcja.aggres
```
And here are the results generated by executing `testing.sh`:
```
+ cat 0150-2017.aggres
taxcalc version unknown
policy regime 2017_law.json
year 2019
itax,ptax,combined($B) 1858.468 1187.071 3045.539
+ diff 0143-2017.aggres 0150-2017.aggres
1,2c1,2
< taxcalc version 0.14.3
< policy regime clp
---
> taxcalc version unknown
> policy regime 2017_law.json
+ diff 0143-tcja.aggres 0150-tcja.aggres
1,2c1,2
< taxcalc version 0.14.3
< policy regime TCJA_Reconciliation.json
---
> taxcalc version unknown
> policy regime clp
4c4
< itax,ptax,combined($B) 1662.372 1187.071 2849.442
---
> itax,ptax,combined($B) 1671.110 1187.071 2858.181
```
So, the new, more complete characterization of TCJA used in
Tax-Calculator 0.15.0 generates 2019 income tax revenue that is about
0.5% higher than the old, less complete characterization of TCJA used
in Tax-Calculator 0.14.3.

**A Round-Trip Compound Reform**

This addendum shows that the diagnostic table generated by the default
policy object, `Policy()`, is the same as the diagnostic table
generated by applying first the `2017_law.json` reform and then the
`TCJA_Reconciliation.json` reform to the default policy object.  So,
implementing these two reforms sequentially on the default policy
object produces a compound-reformed policy object that is identical to
the original default policy object.  In other words, the
`TCJA_Reconciliation.json` reform "undoes" the `2017_law.json` reform.

Here are the contents of `compoundreform.py`:
```
from __future__ import print_function
import sys
import urllib
import numpy as np
import taxcalc
from taxcalc import Policy, Records, Calculator

assert taxcalc.__version__ == 'unknown'  # that is, 0.15.0

base_url = ('https://raw.githubusercontent.com/'
            'open-source-economics/Tax-Calculator/master/taxcalc/reforms/')
reform1 = urllib.urlopen(base_url + '2017_law.json').read()
reform2 = urllib.urlopen(base_url + 'TCJA_Reconciliation.json').read()

fyear = 2016
nyears = 12

pol = Policy()  # pol represents TCJA

calc1 = Calculator(policy=pol, records=Records(), verbose=False)
calc1.advance_to_year(fyear)
diag1 = calc1.diagnostic_table(num_years=nyears)

param1 = Calculator.read_json_param_objects(reform1, None)
pol.implement_reform(param1['policy'])  # now pol represents 2017 pre-TCJA law
if pol.reform_errors:
    print(pol.reform_errors)
    exit(1)

param2 = Calculator.read_json_param_objects(reform2, None)
pol.implement_reform(param2['policy'])  # now pol represents TCJA law
if pol.reform_errors:
    print(pol.reform_errors)
    exit(1)

calc2 = Calculator(policy=pol, records=Records(), verbose=False)
calc2.advance_to_year(fyear)
diag2 = calc1.diagnostic_table(num_years=nyears)

for cyr in diag1:
    print('comparing diagnostic tables for', cyr)
    assert np.allclose(diag1[cyr], diag2[cyr])
```
Here are the results of executing `python compoundreform.py`:
```
comparing diagnostic tables for 2016
comparing diagnostic tables for 2017
comparing diagnostic tables for 2018
comparing diagnostic tables for 2019
comparing diagnostic tables for 2020
comparing diagnostic tables for 2021
comparing diagnostic tables for 2022
comparing diagnostic tables for 2023
comparing diagnostic tables for 2024
comparing diagnostic tables for 2025
comparing diagnostic tables for 2026
comparing diagnostic tables for 2027
```
None of the `assert` statements that compare year columns in the two
diagnostic tables failed.
