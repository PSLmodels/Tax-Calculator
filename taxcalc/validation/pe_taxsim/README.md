Validation against policyengine-taxsim
=====================================

**Status: under construction.**  `generate_sample.py` (step 1) is
done.  The other Python scripts in this folder were copied from the
earlier TAXSIM-35 validation and have not yet been revised; they do
not work yet.

This folder compares Tax-Calculator's **federal** income and payroll
tax results with those of
[policyengine-taxsim](https://github.com/PolicyEngine/policyengine-taxsim)
for random samples of filing units in each year 2021 through 2025.
Each sample is identified by an assumption-set letter `L` (`a`, `b`,
or `c`) and a two-digit year `YY`.  The comparison runs in five steps:

1. `generate_sample.py` writes a TAXSIM-format sample `samples/LYY.in.csv.gz`
   (always `state=0`, `idtl=2`).
2. `run_pe.py` runs policyengine-taxsim on the sample and writes
   `pe_output/LYY.out-pe.csv.gz`.
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

The `--with policyengine-us==...` option is required, because
policyengine-taxsim does not set an upper bound on its
`policyengine-us` dependency.  Change the pin only deliberately,
because doing so requires regenerating all the committed PE outputs
and re-examining all the differences.
