# Plan: Tax-Calculator validation against PolicyEngine-TAXSIM

Branch: `validation-pe-taxsim`.  This file is the single source of
truth for this multi-session project.  Keep the **Status** table and
the **Session log** current; they are what a new session reads first.

## Goal

Find bugs in Tax-Calculator **federal** income and payroll tax logic by
comparing its results with those of
[policyengine-taxsim](https://github.com/PolicyEngine/policyengine-taxsim)
(a TAXSIM-35 emulator backed by `policyengine-us`) for random samples
of filing units in each year 2021 through 2025.  The comparison runs
in five steps for each sample (assumption set letter `L`, year `YY`):

1. Generate a TAXSIM-formatted sample `LYY.in` (always `state=0`, `idtl=2`).
2. Run policyengine-taxsim on `LYY.in` to get `LYY.out-pe`.
3. Translate `LYY.in` into a Tax-Calculator CLI input file `LYY.in-tc.csv`.
4. Run the Tax-Calculator CLI and convert its output to TAXSIM format: `LYY.out-tc`.
5. Compare `LYY.out-pe` with `LYY.out-tc` and check the result against the expected differences.

## Decisions already made (do not revisit without the user)

| Topic | Decision |
|---|---|
| Scope | Federal taxes only; every TAXSIM input row has `state=0`. |
| Environments | Approach A+C: steps 1, 3, 4, 5 run in the `taxcalc-dev` conda env; step 2 runs `policyengine-taxsim` via `uvx` at a **pinned commit SHA** in an ephemeral uv-managed env. No PolicyEngine package is ever installed in `taxcalc-dev` or added to `environment.yml`/`setup.py`. |
| uv install | Astral installer (no Homebrew on this Mac): `curl -LsSf https://astral.sh/uv/install.sh \| env INSTALLER_NO_MODIFY_PATH=1 sh`, which puts `uv`/`uvx` in `~/.local/bin` (already on PATH in every conda env); update with `uv self update`. |
| Code layout | Remove obsolete `taxcalc/validation/taxsim35/` tree and `tests_35.sh`; new code lives in `taxcalc/validation/pe_taxsim/`; rewrite `taxcalc/validation/README.md` to point there. |
| Salvage | Reuse logic from `taxsim_input.py`, `prepare_taxcalc_input.py`, `process_taxcalc_output.py`, `main_comparison.py`, `taxsim_emulation.json`, `Differences_Explained.md` (via `git mv` where a file is the clear ancestor, to keep history). |
| Samples | Reuse a/b/c assumption sets from `taxsim_input.py`, extended to 2021-2025; ~10,000 units per file (final N set in Phase 1 after timing PE); tiny N (e.g., 100) during development. |
| Emulation | A JSON reform `pe_emulation.json` makes Tax-Calculator mimic PE where PE uses a defensible but different convention; every entry carries a comment explaining why.  All other differences are fixed or documented as expected. |
| PE outputs | Commit compressed PE outputs (`LYY.out-pe.csv.gz`) plus a version stamp so steps 3-5 can be rerun without uv/PE. |
| Compare | Detailed TAXSIM `idtl=2` output variables (AGI, taxable income, regular tax, AMT, CTC/ACTC, CDCC, EITC, payroll tax, income tax, etc.) via a documented variable correspondence. |
| Plan storage | This file, committed on the branch. |
| Dependent ages | (2026-10-07) Generator specifies dependents with explicit `age1..ageN` (all ages >= 1), not `dep13/dep17/dep18`; TC child-count variables are derived from these ages. |
| S-corp NIIT | (2026-10-07) Every PE run uses `--scorp-treatment active`, matching TC current law (`NIIT_PT_taxed` false); recorded as `pe_cli_options` in `pe_pin.json`. |
| Old CSV docs | (2026-10-07) `CSV_INPUT_VARS.md`/`CSV_OUTPUT_VARS.md` removed; `VARIABLES.md` replaces them. |
| Work folder | `pe_taxsim/work/`, ignored by `pe_taxsim/.gitignore`. |

## Target layout

```
taxcalc/validation/
  README.md                  rewritten overview (points to pe_taxsim/)
  PLAN.md                    this file (delete or keep at PR time; ask user)
  pe_taxsim/
    README.md                how to run; environment setup; results summary
    VARIABLES.md             TAXSIM<->Tax-Calculator input and output correspondence
    Differences_Explained.md per-letter, per-year explanations of expected diffs
    pe_pin.json              policyengine-taxsim SHA, policyengine-us version, python version
    pe_emulation.json        Tax-Calculator reform emulating PE conventions
    dumpvars.txt             Tax-Calculator variables written by --dumpdb
    generate_sample.py       step 1 (ancestor: taxsim_input.py)
    run_pe.py                step 2 (new; subprocess call to uvx)
    taxsim_to_tc.py          step 3 (ancestor: prepare_taxcalc_input.py)
    run_tc.py                step 4 (ancestors: tc_sims.py, process_taxcalc_output.py)
    compare.py               step 5 (ancestor: main_comparison.py)
    validate.py              driver: runs steps 3-5 (and optionally 1-2) for letters x years
    samples/LYY.in.csv.gz            committed step-1 samples
    pe_output/LYY.out-pe.csv.gz      committed step-2 outputs
    expected_differences/LYY-taxdiffs-expect.csv
```

Generated working files (`*.in-tc.csv`, `*.out-tc`, SQLite dumps,
`actual_differences/`) are written to the git-ignored `pe_taxsim/work/` folder.

## Known facts gathered during planning (2026-10-07)

- policyengine-taxsim: `requires-python >=3.10`; depends on
  `policyengine-us>=1.711.0` (unpinned upper bound, so pin the
  taxsim SHA **and** record the resolved policyengine-us version);
  CLI `policyengine-taxsim policyengine IN.csv --output OUT.csv
  [--logs] [--sample N] [--disable-salt] [--scorp-treatment passive|active]`;
  years 2021+ route to PolicyEngine (earlier years to TAXSIM35).
- uv 0.12.23 installed 2026-10-07 at `~/.local/bin` (Homebrew is not
  installed on this Mac).
- The Tax-Calculator CLI no longer has the `--dump` option that the old
  `tc_sims.py` used; it now has `--dumpdb` (SQLite output) and
  `--dumpvars FILE`.  The old pipeline is therefore broken, not just obsolete.
- `tc` is not on PATH in `taxcalc-dev`; step 4 should call
  `python -m taxcalc.cli.tc` from the repo root so the working-tree
  code is validated without installing the package.
- `make cstest` excludes `taxcalc/validation/` (Makefile `EXCLUDED_PATHS`).
- `CSV_INPUT_VARS.md` / `CSV_OUTPUT_VARS.md`: thought to be unreferenced, but
  `test_records.py::test_csv_input_vars_md_contents` read the former
  (vacuously: the file had no table); see Phase 1 log.
- Old `taxsim_emulation.json` entries: `AMT_child_em_c_age=24`,
  `EITC_excess_InvestIncome_rt=1.0`, `AlimonyReceived_frac_in_AGI=1.0`
  — each must be re-justified (or dropped) for PE, not copied blindly.
- Old translation quirks to re-examine: `dep17 -> nu18` and `n24`,
  `dep13 -> f2441`, `dep18 -> EIC`, `scorp` added to `e02000`,
  `pbusinc/sbusinc` added to `e00900p/s`, `PT_SSTB_income=0`,
  `e00600=e00650` (all dividends qualified), `e01500=e01700`.

## Session protocol

At the start of every session:
1. `git branch --show-current` must print `validation-pe-taxsim`.
2. Read this file; resume at the first unchecked task in the Status table.

During a session:
- Work on one phase (or a clearly bounded part of one).
- Use tiny samples while developing; never paste large CSVs into the
  conversation — summarize with pandas instead.
- Long PE runs: start them in the background (or ask the user to run
  them outside Claude with `nohup`) and record the command here.
- Never edit an expected-differences file or emulation reform to make a
  comparison pass without the user's approval.
- Tax-Calculator logic bugs found here are reported to the user; ask
  whether to fix them on a separate branch off `master` (recommended)
  or on this branch.

At the end of every session:
1. Update the Status table and append a dated Session-log entry
   (what was done, what was learned, exact next step).
2. Delete stray test output; check `git status`.
3. Ask the user whether to commit.

## Phases

### Phase 0 — Tooling and PE smoke test  (≈1 session)
- [x] Install uv; record `uv --version` (0.12.23, 2026-10-07).
- [x] Choose the policyengine-taxsim commit SHA to pin (latest `main` at that time):
      `3e2a7589c8acda0edd2aa9e748d726c9ca9262d0` (2026-09-30, v3.0.1).
- [x] Run a 5-row hand-written TAXSIM file (`state=0`, `idtl=2`, one row per
      year 2021-2025) with
      `uvx --python 3.13 --from git+https://github.com/PolicyEngine/policyengine-taxsim@SHA policyengine-taxsim policyengine IN --output OUT`.
- [x] Record in `pe_pin.json`: SHA, resolved `policyengine-us` version
      (`uvx ... python -c 'import policyengine_us; ...'` or `uv pip list`), Python version.
- [x] Inspect the output columns actually produced at `idtl=2`; list them in the Session log.
- [x] Time a 1,000-unit run to set the final sample size N (target: one
      full LYY run well under an hour).
- [x] Find out from PE-taxsim source/docs: which TAXSIM input variables it
      honors (esp. dependent ages `age1..`, `dep13/17/18`, `scorp`,
      `pbusinc/pprofinc`, `otheritem`, `mortgage`, `childcare`), and the
      meaning of `--disable-salt` and `--scorp-treatment` (decide whether to use them).

### Phase 1 — Salvage, remove obsolete code, skeleton  (≈1 session)
- [x] `git mv` ancestors into `pe_taxsim/` under their new names
      (generate_sample.py, taxsim_to_tc.py, run_tc.py, compare.py,
      pe_emulation.json, Differences_Explained.md); keep the old content
      for now so history shows the evolution.
- [x] `git rm` the rest of `taxsim35/` (input_setup.py, tc_sims.py,
      tests_35.py, README.md, old expected_differences/) and `tests_35.sh`.
- [x] Decide with user whether `CSV_INPUT_VARS.md`/`CSV_OUTPUT_VARS.md` are kept, folded into `VARIABLES.md`, or removed.
- [x] Add a `.gitignore` in `pe_taxsim/` for the work folder.
- [x] Rewrite `taxcalc/validation/README.md` (short overview, link to `pe_taxsim/README.md`).
- [x] Stub `pe_taxsim/README.md` with environment setup (uv, pinned SHA).

### Phase 2 — Variable correspondence: `VARIABLES.md`  (1-2 sessions)
- [ ] Input table: each TAXSIM input variable used → Tax-Calculator
      variable(s) and transformation, including MARS from `mstat` +
      dependents, `XTOT`, child-age variables (`nu06`, `nu13`, `nu18`,
      `n24`, `f2441`, `EIC`, `elderly_dependents`), age of head/spouse,
      split wages, SE income, qualified dividends, cap gains, pensions,
      Social Security, UI, itemized deductions, child-care expenses,
      S-corp / business income and QBID inputs.
- [ ] Output table: each TAXSIM `idtl=2` variable (`fiitax`, `fica`,
      `v10`..`v28`, others PE emits) → Tax-Calculator expression,
      with year-specific notes (2021 fully refundable CTC/CDCC and RRC;
      2025 OBBBA provisions such as the senior deduction).
- [ ] Mark variables excluded from comparison and why.
- [ ] Get user review of VARIABLES.md before coding Phases 3-6.

### Phase 3 — Step 1: `generate_sample.py`  (≈1 session)
- [ ] Year range 2021-2025; `state=0`; `idtl=2`; CLI args: letter, year, N, seed offset.
- [ ] Keep a/b/c assumption sets; revise only where VARIABLES.md requires
      (e.g., dependent-age inputs PE honors).
- [ ] Deterministic seed per (letter, year); write `samples/LYY.in.csv.gz`.
- [ ] Self-check: required columns, value ranges, no NaNs.

### Phase 4 — Step 2: `run_pe.py`  (1 session to write; runs may span days)
- [ ] Reads `pe_pin.json`; builds the `uvx` command; runs via `subprocess`;
      never imports PolicyEngine.
- [ ] Writes `pe_output/LYY.out-pe.csv.gz`; refuses to overwrite without `--force`.
- [ ] Verifies output row count and ids match the input sample.
- [ ] Generate a21..a25 first (needed for Phase 7); then b, c.

### Phase 5 — Step 3: `taxsim_to_tc.py`  (≈1 session)
- [ ] Implement the input table from VARIABLES.md (replace old quirks
      where VARIABLES.md says so).
- [ ] Self-checks: `e00200 == e00200p + e00200s`, `e00900` likewise,
      valid MARS, `XTOT` consistency, child counts nested
      (nu06 ≤ nu13 ≤ nu18), no unknown columns
      (verify all names exist in `records_variables.json`).

### Phase 6 — Step 4: `run_tc.py`  (1-2 sessions)
- [ ] Verify how the CLI treats a custom input file for TAXYEAR (no
      extrapolation/growfactor aging, weights not needed); document the result.
- [ ] Run `python -m taxcalc.cli.tc LYY.in-tc.csv 20YY --reform pe_emulation.json --dumpdb --dumpvars dumpvars.txt --silent`.
- [ ] Read the SQLite dump; build TAXSIM-format output per VARIABLES.md
      (salvaging `process_taxcalc_output.py` logic, updated for 2021-2025).
- [ ] Start `pe_emulation.json` empty except entries justified in Phase 2.

### Phase 7 — Step 5: `compare.py` and `validate.py`  (≈1 session)
- [ ] Per-variable absolute differences; tolerance $1 (configurable).
- [ ] Write `actual_differences/LYY-taxdiffs-actual.csv` (id, variable,
      pe, tc, diff) plus a per-variable summary (count, max, mean abs).
- [ ] Pass/fail = actual diffs match expected diffs file exactly.
- [ ] `validate.py`: loop over letters × years; default runs steps 3-5
      from committed samples and PE outputs; `--regen` also runs 1-2.
- [ ] Run on a 100-unit a21 to shake out plumbing.

### Phase 8 — Triage assumption set `a` (wages, ages, dependents) 2021-2025  (several sessions)
- [ ] Run a21..a25; for each distinct difference pattern, find a
      representative unit and classify it:
      (1) translation/mapping error → fix Phase 2/5/6 code;
      (2) PE convention → `pe_emulation.json` entry (with user approval);
      (3) PE bug → note for upstream issue;
      (4) Tax-Calculator bug → report to user (fix per protocol).
- [ ] Document explained diffs in `Differences_Explained.md`; create
      `expected_differences/aYY-taxdiffs-expect.csv` with user approval.

### Phase 9 — Triage set `b` (adds non-labor and business income)  (several sessions)
- [ ] Same procedure as Phase 8 (expect SE tax, QBID, cap gains,
      Social Security, AMT issues).

### Phase 10 — Triage set `c` (adds itemized deductions, child care)  (several sessions)
- [ ] Same procedure as Phase 8 (expect itemizing choice, SALT cap,
      CDCC issues).

### Phase 11 — Finish  (≈1 session)
- [ ] Final `README.md` with results summary and rerun instructions.
- [ ] Optional: run `pycodestyle`/`pylint` on `pe_taxsim/*.py` even
      though `make cstest` skips them; ask user whether to include
      `pe_taxsim/` in cstest.
- [ ] Confirm `make pytest` is unaffected; clean up stray files.
- [ ] Draft list of upstream PE issues for the user.
- [ ] Ask user whether to keep or delete this PLAN.md, whether to commit,
      and whether to open a PR.

## Risks and open issues

- PE version churn: results depend on the pinned SHA and resolved
  `policyengine-us`; re-pinning means regenerating all committed PE
  outputs and re-triaging.  Re-pin only deliberately.
- `uvx --from git+...@SHA` alone still resolves `policyengine-us` at
  install time, so `run_pe.py` must always add
  `--with policyengine-us==<pe_pin.json value>` (verified 2026-10-07
  to give identical output to the unpinned run).
- TAXSIM output variables may not map one-to-one onto Tax-Calculator
  concepts (especially credit splits in 2021 and OBBBA items in 2025).
- 2025 is the least stable year in both models.
- numpy RNG changes could alter regenerated samples; committed samples
  are canonical, and the generator is only used to (re)create them deliberately.
- Repo size: 15 samples + 15 PE outputs at N=10,000, gzipped, should be
  a few MB; recheck after Phase 0 timing sets N.

## Status

| Phase | State |
|---|---|
| 0 Tooling / PE smoke test | done (2026-10-07) |
| 1 Salvage / skeleton | done (2026-10-07) |
| 2 VARIABLES.md | not started |
| 3 generate_sample.py | not started |
| 4 run_pe.py + PE outputs | not started |
| 5 taxsim_to_tc.py | not started |
| 6 run_tc.py | not started |
| 7 compare.py / validate.py | not started |
| 8 Triage a | not started |
| 9 Triage b | not started |
| 10 Triage c | not started |
| 11 Finish | not started |

## Session log

- 2026-10-07: Planning session.  Gathered decisions (table above),
  created branch `validation-pe-taxsim` from synced master, wrote this
  plan.  Homebrew is absent, so uv 0.12.23 was installed with the
  Astral installer into `~/.local/bin`.  Next step: Phase 0, choose
  the policyengine-taxsim SHA to pin and run the 5-row smoke test.
- 2026-10-07: Phase 0 session.
  * Pinned policyengine-taxsim `3e2a7589` (main, 2026-09-30, v3.0.1);
    resolved policyengine-us 2.30.1, policyengine-core 3.32.21,
    Python 3.13.16 (3.13 works although pyproject classifiers stop at
    3.12).  Recorded in `pe_taxsim/pe_pin.json` (new, uncommitted).
    Canonical step-2 command:
    `uvx --python 3.13 --from git+https://github.com/PolicyEngine/policyengine-taxsim@SHA --with policyengine-us==2.30.1 policyengine-taxsim policyengine IN.csv --output OUT.csv`
  * 5-row smoke test (one row per year 2021-2025) ran cleanly; values
    sane (e.g. 2023 HoH 1-child EITC 3445.29 matches statute exactly,
    i.e. PE does NOT use EITC-table rounding; 2021 RRC in `cares`).
  * `idtl=2` output columns (41): taxsimid year state fiitax siitax fica
    tfica v10 v11 v12 v13 v14 v17 qbid niit addmed v18 v19 v22 v24 v25
    v26 v27 v28 v29 v32 v34 v35 v36 srebate v37 v38 v39 v40 v42 v43 v44
    actc cares frate srate.  Notes: no `v23`; refundable CTC is in
    `actc`.  `fica` = employee+employer payroll tax incl. SECA; `tfica`
    = employee half (= v29).  `addmed` is NOT in fiitax (README).
    `niit` IS in fiitax.  v17 reports itemized deductions even when the
    unit takes the standard deduction.  `frate` = federal marginal rate.
    v44 nonzero for wage earners (meaning TBD in Phase 2).
    v32-v43, siitax, srate, srebate are state items (all 0; ignore).
  * Timing: 1,000-unit `c23` sample (old taxsim_input.py) ran in 10.4 s
    wall (cached env; first uvx env build ~25 s).  PE speed is not a
    constraint: N=10,000 takes ~2 min, so Phase 1 can set N=10,000 (or
    larger if repo size allows).
  * Input handling found in PE-taxsim source (`config/variable_mappings.yaml`,
    `core/utils.py:convert_taxsim32_dependents`) and verified by probe runs:
    - `dep13/dep17/dep18` are honored only when no `ageN` columns are
      present; converted to ages 10 (<13), 15 (13-16), 17 (17), and 21
      (depx-dep18 extra dependents, treated as non-student adult
      dependents: ODC $500, HoH status, no EITC).  So with dep13-style
      input no child is ever under 6 (2021 CTC $3,600 never applies).
    - Any `ageN == 0` (or NaN) is silently changed to 10 (verified: 2021
      CTC for age1=0 is $3,000, for age1=3 is $3,600).  Generator must
      use ages >= 1 for infants.
    - `nonprop` is IGNORED by the PolicyEngine runner (verified: +$10,000
      nonprop changes nothing).  Generator should set nonprop=0 (or the
      comparison must drop it from TC input).
    - `otherprop` -> rental_income; `pui`+`sui` -> unemployment_compensation;
      `transfers` -> general_assistance (non-taxable); `rentpaid` -> rent.
    - `psemp/ssemp` and `pbusinc/sbusinc` all -> self_employment_income
      (SECA + non-SSTB QBI, per person); `pprofinc/sprofinc` ->
      sstb_self_employment_income (SECA + SSTB-phased QBI);
      `scorp` -> partnership_s_corp_income (QBI, no SECA).
    - `dividends` are treated as QUALIFIED dividends.
    - `mortgage` + `otheritem` are summed into deductible_mortgage_interest:
      fully deductible, no floor, outside the SALT cap, no AMT add-back.
    - `childcare` -> tax_unit_childcare_expenses.
  * `--disable-salt`: zeroes state income/sales tax in the SALT deduction.
    With `state=0`, PE already does this automatically for every row, so
    the flag is redundant for us: do not use it.
  * `--scorp-treatment passive|active` (NIIT only): default `passive` with
    PE-US >= 2.10.1.  Tax-Calculator's NetInvIncTax excludes e26270 from
    NII by default (i.e., active) unless `NIIT_PT_taxed` is True.
  * DECISIONS PENDING (ask user at start of next session, then record in
    the Decisions table):
    (1) Dependent ages: switch the generator from dep13/17/18 to explicit
        `age1..ageN` (ages >= 1), recommended, so under-6, 17-year-old,
        and adult-dependent cases are all exercised and TC's nu06/nu13/
        nu18/n24/EIC/f2441 can be derived exactly.
    (2) S-corp NIIT: run PE with `--scorp-treatment active` (matches TC
        current law, recommended), or keep PE default `passive` and add
        `NIIT_PT_taxed: true` to pe_emulation.json.
  * Old-generator quirk noticed: in `c23`, psemp/ssemp max is only 350
    (looks like a units bug; the business-income vars reach 350,000).
    Re-examine in Phase 3.
  * Next step: get the two decisions above, then start Phase 1.
- 2026-10-07: Phase 1 session.
  * User decisions (now in the Decisions table): explicit `age1..ageN`
    dependent ages; PE runs with `--scorp-treatment active` (added as
    `pe_cli_options` to `pe_pin.json`); `CSV_INPUT_VARS.md` and
    `CSV_OUTPUT_VARS.md` removed.
  * `git mv` into `pe_taxsim/` (content unchanged): taxsim_input.py ->
    generate_sample.py, prepare_taxcalc_input.py -> taxsim_to_tc.py,
    process_taxcalc_output.py -> run_tc.py, main_comparison.py ->
    compare.py, taxsim_emulation.json -> pe_emulation.json,
    Differences_Explained.md.  `git rm` of the rest of `taxsim35/`
    (incl. old 2017-2021 expected_differences) and `tests_35.sh`.
  * Removing `CSV_INPUT_VARS.md` broke `test_records.py::
    test_csv_input_vars_md_contents`, which was vacuous (the file had
    no variable table, so it checked an empty set).  With user approval
    the test was deleted.  `test_records.py` + `test_calcfunctions.py`
    pass (418) and `make cstest` is clean; full `make pytest` not run.
  * Added `pe_taxsim/.gitignore` (ignores `work/`); removed the obsolete
    `taxsim35/actual_differences/` line from the top-level `.gitignore`.
  * Rewrote `taxcalc/validation/README.md`; stubbed `pe_taxsim/README.md`
    (five steps, uv setup, pinned uvx command).  Updated the validation
    link in `docs/index.md`, which pointed at the deleted taxsim35 README.
  * Not touched: `taxcalc.egg-info/SOURCES.txt` is tracked and still
    lists the removed files; it is regenerated by packaging, so it was
    left alone (mention to user at PR time).
  * Next step: Phase 2, write `VARIABLES.md` (input table first),
    using the PE input-handling facts from the Phase 0 log.
