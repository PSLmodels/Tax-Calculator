# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this
repository.

## Sole purpose: structural enhancements

Claude Code is used in this repository for exactly one task: **preparing a local
git branch containing a tested Tax-Calculator structural enhancement** — that is,
code changes that enable the model to simulate a specified policy reform that
cannot be simulated by the current version of Tax-Calculator. The workflow to
follow is in `./structural-enhancement.md`; read it at the start of every session
and follow its steps in order.

Do **not** use this repository to analyze parametric tax reforms (reforms that
can be simulated by the current model simply by changing existing policy
parameter values). That kind of analysis is the focus of a different repository
containing a Tax-Calculator Assistant agent that uses a collection of MCP tools
with an existing version of Tax-Calculator. If asked to analyze a parametric
reform here, point the user to that Assistant instead.

## The workflow (summary)

`./structural-enhancement.md` is authoritative; in brief:

1. **Gather information** — ask the user for the repository folder, the
   specified reform that cannot currently be simulated, and the new branch name.
2. **Create the git branch** off `master` with the specified name.
3. **Plan and develop the branch changes** (see next section for where changes go).
4. **Test the branch changes** with the four test commands below, revising until
   all four pass.
5. **Ask before committing** — confirm no additional changes are needed, then
   commit.

## Where structural-enhancement changes go

Tax-Calculator is an open-source microsimulation model (PSL-cataloged, package
name `taxcalc`) for static analysis of USA federal individual income and payroll
taxes. Supported Python versions are 3.11–3.13. A structural enhancement
typically touches these files:

- **`taxcalc/policy_current_law.json`** — add any new policy parameters
  (paramtools schema: value + validation + indexing metadata per parameter,
  keyed by year). Avoid creating new `section_1` and `section_2` values; reuse
  existing section headings. Parameters span `JSON_START_YEAR = 2013` through
  `LAST_BUDGET_YEAR`. Keep the JSON coding-style clean — `make cstest` runs
  `pycodestyle` over the JSON files too.

- **`taxcalc/records_variables.json`** — add any new input or output variables,
  placed in either the `read` or `calc` section as appropriate.

- **`taxcalc/calcfunctions.py`** — the actual tax logic: one function per tax
  concept (`EI_PayrollTax`, `AGI`, `StdDed`, `ItemDed`, `EITC`, `AMT`, `C1040`,
  `IITAX`, etc.), invoked in order by the `Calculator`. Each operates in-place
  on the NumPy arrays of a `Records` object using scalar `Policy` parameters.
  New code must use the new parameters and variables and follow the current
  function-arguments ordering scheme used throughout the module.

- **`taxcalc/tests/test_calcfunctions.py`** — add unit tests for new
  parameters, variables, and code to maintain coverage. Ask the user for
  guidance on the nature of the unit tests (possibly an example). **Always
  calculate expected unit-test results without referring to the new code in
  `calcfunctions.py`** (work them out independently, e.g. by hand from the
  reform specification).

Supporting architecture context (all classes re-exported from
`taxcalc/__init__.py`):

- **`Calculator`** (`calculator.py`) orchestrates: `calc_all()` runs the full
  sequence of calcfunctions for the current year; the core ordering lives in
  `_calc_one_year()`, which computes tax both with the standard deduction and
  with itemized deductions, then picks whichever yields lower tax per filing
  unit. If an enhancement adds a new calcfunction, it must be wired into this
  ordering.
- **`Policy`** (`policy.py`) extends `Parameters` (`parameters.py`, a
  `paramtools` subclass); defaults come from `policy_current_law.json`.
- **`Records`** (`records.py`) extends `Data` (`data.py`); variable metadata is
  declared in `records_variables.json`.
- **JIT decorators** (`decorators.py`) — `iterate_jit`/`JIT` wrap calcfunctions
  so numba compiles them and vectorizes the per-filing-unit loop. Set env var
  `NOTAXCALCJIT` to run pure Python when debugging, since JIT'd code is not
  steppable and obscures tracebacks.

## Required test commands

Execute these in the top-level repository folder until **all four pass**; if
any fails, return to revising the branch changes (Step 3 of the workflow):

- `make cstest > rescs` — coding-style checks (`pycodestyle` + `pylint`).
  **Fails if the `rescs` file is not empty.**
- `make pytest-all > respy` — full test suite; requires `puf.csv` and `tmd.csv`
  present in the repo root.
  **Fails if the last line of the `respy` file contains the word `failed`.**
- `make brtest > resbr` — behavioral-responses CLI tests.
  **Fails if any line of the `resbr` file contains the word `differ`.**
- `make idtest > resid` — input-data CLI tests.
  **Fails if any line of the `resid` file contains the word `differ`.**

During development, quicker iterations are available with `make package`
(build and `pip install -e .` the local package) and a single test run:

```
cd taxcalc && pytest tests/test_calcfunctions.py::test_SchXYZ
```

Note that structural enhancements often change expected results in existing
tests (e.g. `taxcalc/reforms/*.out.csv` companions or dump comparisons); such
changes are legitimate only when they follow directly from the enhancement —
never adjust expected values just to make a test pass.

## Coding style

CI enforces `pycodestyle` (ignoring W503, W504, E712) and `pylint` (disabling
`locally-disabled,duplicate-code,cyclic-import`, with quote-consistency checking
on) across everything except `docs/` and `taxcalc/validation/`. calcfunctions
use short mathematical variable names (`# pylint: disable=invalid-name`) that
mirror IRS form line items — match that convention rather than renaming for
clarity.

## Git conventions

Work happens on a new branch created off local `master` (Step 2 of the
workflow); never commit to `master` directly. Commit only after the user
confirms no additional changes are needed (Step 5). The repository follows the
fork-and-PR model against `PSLmodels/Tax-Calculator` `master`, but opening the
PR is the user's job, not part of this workflow.
