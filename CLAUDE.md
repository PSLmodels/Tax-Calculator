# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when
working in this repository.

## Never edit files on the master branch

Before making **any** file change, check the current branch using the
`git branch --show-current` command.

- If the current branch is `master`, do not edit anything. Ask the
  user what the new branch name should be, then confirm the working
  tree is clean, synchronize master with the central GitHub repository
  using `make git-sync`, and create the new branch off master.
  If the current branch is not `master`, work on that branch as usual.

This rule applies to every kind of task, not just the workflow described below.
Never commit to `master` directly.

## Which workflow to follow

- **Structural enhancements**: if the user asks for a model
enhancement that would allow simulation of a policy reform that the
current version of Tax-Calculator cannot simulate, follow the workflow
in `taxcalc/structural-enhancement.md`.  Read that file at the start
of such a session and follow its five steps in order; it is
authoritative, and the summary below is only a reminder:

1. Gather information — repository folder, the specified reform, reform details
   (first applicable year, inflation indexing), and the new branch name.
2. Create the git branch.
3. Make the branch changes.
4. Test the branch changes.
5. Ask whether to commit; do not push or open a pull request.

- **Everything else**: for any other request (code refactoring, bug
searching, documentation, test cleanup, answering questions about the
code, etc.) follow no special workflow.  Just do the requested work,
subject to the master-branch rule above and the coding style described
below.

## Repository orientation

Tax-Calculator is an open-source microsimulation model (PSL-cataloged,
package name `taxcalc`) for conventional analysis of USA federal
individual income and payroll taxes. Supported Python versions are
3.11–3.13.

- **`taxcalc/policy_current_law.json`**: policy parameters in
  paramtools schema (value + validation + indexing metadata per
  parameter, keyed by year), spanning `JSON_START_YEAR = 2013` through
  `LAST_BUDGET_YEAR`.

- **`taxcalc/records_variables.json`**: input variables (`read`
  section) and calculated variables (`calc` section).

- **`taxcalc/calcfunctions.py`**: the tax logic: one function per tax
  concept (`EI_PayrollTax`, `AGI`, `StdDed`, `ItemDed`, `EITC`, `AMT`,
  `C1040`, `IITAX`, etc.), each operating in-place on the NumPy arrays
  of a `Records` object using scalar `Policy` parameters, with a
  consistent function-arguments ordering scheme.

- **`Calculator`** (`calculator.py`) orchestrates:
  `calc_all()` runs the full sequence for the current year; the core
  ordering lives in `_calc_one_year()`, which computes tax both with
  the standard deduction and with itemized deductions and picks
  whichever yields lower tax per filing unit.

- **`Policy`**: (`policy.py`) extends `Parameters` (`parameters.py`, a
  `paramtools` subclass);

- **`Records`** (`records.py`) extends `Data` (`data.py`).

- **JIT decorators** (`decorators.py`): `iterate_jit`/`JIT` let
  numba compile calcfunctions and vectorize the per-filing-unit
  loop. Set env var `NOTAXCALCJIT` to run pure Python when debugging,
  since JIT'd code is not steppable and obscures tracebacks.

- **`docs/guide/*.md`** files (`policy_params.md`, `input_vars.md`,
  `output_vars.md`, `assumption_params.md`) are generated from the
  JSON files by scripts in `docs/guide/make`; never hand-edit them.

## Test commands

Run these from the top-level repository folder. The fast `pytest
taxcalc/tests/test_calcfunctions.py` command catches inconsistencies
among `calcfunctions.py`, `calculator.py`, `policy_current_law.json`,
and `records_variables.json` without the cost of the slower commands
below.

- `make cstest > rescs 2>&1` — coding-style checks; fails if `rescs`
  is not empty.

- `make pytest-all > respy 2>&1 ; echo EXIT=$?` - full test suite;
  fails if the EXIT value is not zero. Diagnose failures by consulting
  `respy`; do not rely on its last line alone, since collection errors
  and crashes are reported differently from test failures.
  
- `make brtest > resbr 2>&1` and, if tmd data files are present,
  `make idtest > resid 2>&1` — CLI tests. Both always exit zero, so
  check them with `grep -Ei 'differ|error|traceback' resbr resid`; any
  output means failure.  The `idtest` requires `tmd.csv`,
  `tmd_weights.csv.gz`, and `tmd_growfactors.csv` in the top-level
  repo folder. `pytest-all` uninstalls the local package that `brtest`
  and `idtest` build and install, so run `pytest-all` before them.

The `rescs`, `respy`, `resbr`, and `resid` files are not git-ignored;
delete them when done, and check `git status` for stray test output
such as `df-??-#-*` files left behind by an aborted `pytest-all` run.

Never revise a test, or a file containing expected test results, in
order to make a failing test pass without first asking the user for
approval. A failing comparison against stored expected results
indicates a bug in the branch changes.

## Coding style

CI enforces `pycodestyle` (ignoring W503, W504, E712) and `pylint`
(disabling `locally-disabled,duplicate-code,cyclic-import`, with
quote-consistency checking on) across everything except `docs/` and
`taxcalc/validation/`. The calcfunctions use short mathematical
variable names (`# pylint: disable=invalid-name`) that mirror IRS form
line items — match that convention rather than renaming for clarity.
