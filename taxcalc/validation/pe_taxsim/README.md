Validation against policyengine-taxsim
=====================================

**Status: under construction.**  `generate_sample.py` (step 1),
`run_pe.py` (step 2), `taxsim_to_tc.py` (step 3), and `run_tc.py`
(step 4) are done.  The other Python scripts in this folder were
copied from the earlier TAXSIM-35 validation and have not yet been
revised; they do not work yet.

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
    --dumpdb --dumpvars ../dumpvars.txt --silent
```

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
