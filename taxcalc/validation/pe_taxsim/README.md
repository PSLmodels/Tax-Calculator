Validation against policyengine-taxsim
=====================================

This folder compares Tax-Calculator's **federal** income and payroll
tax results with those of
[policyengine-taxsim](https://github.com/PolicyEngine/policyengine-taxsim)
for random samples of filing units in each year 2021 through 2025.
Each sample is identified by an assumption-set letter `L` (`a`, `b`,
or `c`) and a two-digit year `YY`.  The comparison runs in five steps:

1. `generate_sample.py` writes a TAXSIM-format sample `samples/LYY.in.csv.gz`
   (always `state=0`, `idtl=2`).
2. `run_pe.py` runs policyengine-taxsim on the sample and writes
   `pe_output/LYY.out-pe.csv.gz` plus a version stamp
   `pe_output/LYY.out-pe.stamp.json`.
3. `taxsim_to_tc.py` translates the sample into a Tax-Calculator input file.
4. `run_tc.py` runs the Tax-Calculator CLI with the `pe_emulation.json`
   reform and converts its output to TAXSIM format.
5. `compare.py` compares the two outputs and checks the differences
   against `expected_differences/LYY-taxdiffs-expect.csv`.

The samples and PE outputs are committed, so steps 3-5 can be rerun
using only the `taxcalc-dev` conda environment.  Generated working
files are written to the git-ignored `work/` folder.

Other files in this folder:
[`VARIABLES.md`](VARIABLES.md) documents how each TAXSIM input and
output variable corresponds to Tax-Calculator variables;
[`Differences_Explained.md`](Differences_Explained.md) explains every
expected difference; [`pe_pin.json`](pe_pin.json) pins the PE version;
[`pe_emulation.json`](pe_emulation.json) is the Tax-Calculator reform
that adopts PE's conventions; and `dumpvars.txt` lists the
Tax-Calculator variables that step 4 writes.

Rerunning the comparison
------------------------

From the top-level repository folder, in the `taxcalc-dev` conda
environment, run:

```
python taxcalc/validation/pe_taxsim/validate.py
```

This runs steps 3-5 for all fifteen samples (letters `a`, `b`, `c`
times years 2021-2025) in about one minute and ends with a PASS/FAIL
summary.  Neither uv nor PolicyEngine is needed.  Every comparison
should pass.  A failure means that a Tax-Calculator change altered at
least one compared result: look at
`work/actual_differences/LYY-taxdiffs-actual.csv` and decide whether
the change fixes a bug (then update
[`Differences_Explained.md`](Differences_Explained.md) and the expect
file) or introduces one.  See [Running all the
steps](#running-all-the-steps) for options.

Results summary
---------------

Results are for the pinned PE version (policyengine-taxsim 3.0.1,
commit `3e2a758`, with policyengine-us 2.30.1) and 10,000 random
filing units in each sample.  The three assumption sets are:

- `a`: wages, ages of head and spouse, and up to five dependents;
- `b`: adds pensions, Social Security benefits, dividends, interest,
  capital gains and losses, unemployment compensation, rental income,
  and self-employment, business, and S-corporation income (each of
  the last three nonzero in only 25% of units);
- `c`: adds property taxes, mortgage interest, other itemized
  deductions, and child care expenses.

Twenty-three TAXSIM output variables are compared (see
[`VARIABLES.md`](VARIABLES.md)).  After the corrections listed below,
all of them agree to within $1 except for the explained differences.
This table counts the units with at least one difference and the
units with a `fiitax` (federal income tax) difference:

| Sample | 2021 units / fiitax | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| `a` | 2,617 / 0 | 1,193 / 0 | 1,257 / 0 | 1,377 / 0 | 2,259 / 0 |
| `b` | 1,013 / 4 | 6 / 6 | 8 / 6 | 7 / 6 | 898 / 12 |
| `c` | 1,090 / 8 | 12 / 8 | 14 / 7 | 10 / 7 | 945 / 5 |

Payroll taxes (`fica`, `tfica`, `addmed`, and the `v44` Medicare
rate) and many income tax items (AGI, taxable unemployment
compensation and Social Security benefits, the standard deduction,
exemptions, EITC, the 2021 recovery rebate credit, and NIIT) agree in
every unit of every sample.  Most
of the remaining differences are in intermediate amounts that do not
affect tax: AMT income (`v26`) and, in 2021, the refundable part of
the child tax credit (`actc`).  The few `fiitax` differences are
explained by PE AMT errors for filers under 19 and by PE's
assumption that everyone aged 5-17 is a full-time student.

The comparison found these Tax-Calculator bugs, which have been fixed
on `master`:

- the 2023 aged/blind standard deduction amounts for single and
  head-of-household filers, and the 2022-2024 amounts for surviving
  spouses, were wrong (`STD_Aged`);
- the kiddie-tax AMT exemption cap applied only to children under 18
  rather than under 19 (`AMT_child_em_c_age`);
- in 2021 the credit for other dependents was refundable
  (`ODC_is_refundable`), but ARPA made only the child credit refundable;
- in 2021 the phase-out of the ARPA child tax credit increase lacked
  the section 24(i)(4)(B) cap (`CTC_new`);
- the kiddie-tax AMT exemption cap was applied to joint filers under
  19, although section 1(g)(2)(C) excludes a child who files a joint
  return (PE still has this error, so it now causes differences).

The remaining differences, all explained in
[`Differences_Explained.md`](Differences_Explained.md), are:

| Variables | Years | Cause | Class |
|---|---|---|---|
| `v26` | all | PE floors taxable income at zero when computing AMT income | PE bug, no tax effect |
| `v26` | 2025 | PE does not add the senior deduction back to AMT income | PE bug, no tax effect |
| `actc` | 2021 | PE's refundable CTC ignores the ARPA first-stage reduction and includes ODC | PE output definition |
| `v27`, `fiitax`, others | all | PE's kiddie-tax AMT base omits the standard-deduction add-back | PE bug |
| `v27`, `fiitax` | 2021, 2022 | PE applies the kiddie-tax AMT exemption cap to joint filers | PE bug |
| `v24`, `fiitax` | 2022-2024 | PE treats a spouse aged 17 as a full-time student for the CDCC | convention |
| `v18`, `v26` | 2021, 2023, 2025 | itemizing choice when both deductions give the same (zero) tax | convention, no tax effect |
| `v17`, `v26` | 2025 | PE limits the SALT deduction to AGI | PE output definition, no tax effect |

The only `pe_emulation.json` entries assume full take-up of the EITC
and the refundable child tax credit, as PE does.

Validation of a new tax year
----------------------------

To add a year, change `LAST_YEAR` in all six scripts, check the
year-specific logic in `run_tc.py` and [`VARIABLES.md`](VARIABLES.md)
for the new year's law changes, generate the samples and PE outputs
for the new year (steps 1 and 2), and examine every difference the
way the existing ones were examined before creating the new expect
files.  To move to a newer PE version, change `pe_pin.json`,
regenerate all fifteen PE outputs with `run_pe.py --force`, and
re-examine every difference; the samples need not change.

Environment setup
-----------------

Steps 1, 3, 4, and 5 run in the `taxcalc-dev` conda environment from
the top-level repository folder, so the working-tree Tax-Calculator
code is the code being validated.

Step 2 runs policyengine-taxsim in an ephemeral environment managed
by [uv](https://docs.astral.sh/uv/); no PolicyEngine package is ever
installed in `taxcalc-dev`.  Install uv with the Astral installer,
which puts `uv` and `uvx` in `~/.local/bin`:

```
curl -LsSf https://astral.sh/uv/install.sh | env INSTALLER_NO_MODIFY_PATH=1 sh
```

and update it later with `uv self update`.

The policyengine-taxsim commit, the `policyengine-us` version, the
Python version, and the extra policyengine-taxsim options are pinned
in [`pe_pin.json`](pe_pin.json).  Step 2 is equivalent to this command:

```
uvx --python 3.13 \
    --from git+https://github.com/PolicyEngine/policyengine-taxsim@3e2a7589c8acda0edd2aa9e748d726c9ca9262d0 \
    --with policyengine-us==2.30.1 \
    policyengine-taxsim policyengine LYY.in.csv --output LYY.out-pe.csv \
    --scorp-treatment active
```

`python run_pe.py L YYYY` builds and runs this command from
`pe_pin.json`, first checking that the uv environment resolves to the
pinned `policyengine-us`, `policyengine-core`, and Python versions.
It refuses to overwrite an existing PE output unless `--force` is
given, and it checks that the output has the expected columns and the
same `taxsimid` and `year` values as the input sample.  A 10,000-unit
run takes about two minutes.

The `--with policyengine-us==...` option is required, because
policyengine-taxsim does not set an upper bound on its
`policyengine-us` dependency.  Change the pin only deliberately,
because doing so requires regenerating all the committed PE outputs
and re-examining all the differences.

Step 3
------

`python taxsim_to_tc.py L YYYY` translates `samples/LYY.in.csv.gz`
into the Tax-Calculator CLI input file `work/LYY.in-tc.csv`, following
the input tables in [`VARIABLES.md`](VARIABLES.md).  It stops if a
TAXSIM input that has no translation (`nonprop`, `transfers`,
`rentpaid`, `pprofinc`, `sprofinc`) is nonzero, and it checks that
every output column is a Tax-Calculator input variable, that `MARS`
and `XTOT` agree with `mstat` and `depx`, that the wage and
self-employment totals equal the sums of their spouse parts, and that
the dependent counts are nested by age.

Step 4
------

`python run_tc.py L YYYY` runs the Tax-Calculator CLI on
`work/LYY.in-tc.csv`, which is equivalent to this command run in the
`work/` folder with the top-level repository folder on `PYTHONPATH`:

```
python -m taxcalc.cli.tc LYY.in-tc.csv 20YY --reform ../pe_emulation.json \
    --dumpdb --dumpvars ../dumpvars.txt --exact --silent
```

The `--exact` option makes Tax-Calculator round phase-out excesses
the way the statute and tax forms do (for example, the child tax
credit falls by $50 for each $1,000 "or fraction thereof" of income
above the threshold), as PE does; without it, Tax-Calculator phases
credits out smoothly, which differs from PE in 2021, whose $112,500
head-of-household threshold is not a multiple of $1,000.

It renames the CLI's SQLite output to `work/LYY.dumpdb` and converts
the `reform` table (current law plus `pe_emulation.json`) into the
TAXSIM-format file `work/LYY.out-tc.csv`, following the output table in
[`VARIABLES.md`](VARIABLES.md).  A 10,000-unit run takes about four
seconds.

Because the input file is neither `cps.csv` nor `tmd.csv`, the CLI
reads it with `Records(start_year=TAXYEAR, gfactors=None,
weights=None)`: the input values are used unchanged for TAXYEAR (no
growfactor aging), `FLPDYR` is set to TAXYEAR, and all weights are
zero, which matters only for the `--tables` and `--graphs` output that
step 4 does not use.

Step 5
------

`python compare.py L YYYY [--tolerance T]` compares
`pe_output/LYY.out-pe.csv.gz` with `work/LYY.out-tc.csv` for the
variables marked "Compare" in the output table in
[`VARIABLES.md`](VARIABLES.md) (`v13`, `v17`, and `v19` only for the
units described there).  It writes two files to
`work/actual_differences/`:

- `LYY-taxdiffs-actual.csv` has one row (`taxsimid`, `variable`, `pe`,
  `tc`, `diff`) for each compared value whose absolute difference,
  `diff = tc - pe`, exceeds the tolerance (default $1).
- `LYY-taxdiffs-summary.csv` has, for each compared variable, the
  number of units compared, the number of differences, and the
  maximum and mean absolute difference.

The comparison passes when the actual differences are exactly the same
as those in `expected_differences/LYY-taxdiffs-expect.csv` (the same
units, variables, and values to the cent), or when there are no actual
differences and no expected-differences file.  The exit code is 0 for
pass, 1 for fail, and 2 for an error.

Running all the steps
---------------------

`python validate.py` runs steps 3-5 for every letter and year using
the committed samples and PE outputs, prints each comparison, and ends
with a pass/fail summary; its exit code is 0 only when every
comparison passes.  All fifteen comparisons take about one minute.
Use `--letters` (e.g., `ab`) and `--years` (e.g., `2021,2023-2025`) to
run a subset, and `--tolerance` to change the tolerance.

With `--regen`, `validate.py` first runs steps 1 and 2
(`generate_sample.py` and `run_pe.py --force`), which **overwrites**
the samples and PE outputs.  Do that in the committed folders only
deliberately.  `--datadir DIR` makes `validate.py` use the
`samples`, `pe_output`, `expected_differences`, and `work` folders in
`DIR` instead of those next to the scripts, so a quick trial run with
a small sample leaves the committed files alone:

```
python validate.py --letters a --years 2021 --regen --size 100 \
    --datadir /some/scratch/folder
```
