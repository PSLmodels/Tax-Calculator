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
| Rental income and QBI (D1) | (2026-10-07) `otherprop` goes only to `e02000`, not `e27200`: the pinned PE-taxsim runner pins `rental_income_would_be_qualified` to False, so rental income is not QBI in PE either. |
| `pe_emulation.json` | (2026-10-07) Three entries: `eitc_claim_prob_scale` and `actc_claim_prob_scale` = 9e99 (full take-up, like PE) and `AMT_child_em_c_age` = 19 (PE's non-student kiddie-AMT age limit); the three old TAXSIM-35 entries are dropped. |
| Sparse business income | (2026-10-07) In sets b/c each of `psemp`, `ssemp`, `pbusinc`, `sbusinc`, `scorp` is nonzero for only 25% of units, so b/c include moderate-income units that get credits. |

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
    pe_output/LYY.out-pe.stamp.json  versions, input/output SHA-256, run date
    expected_differences/LYY-taxdiffs-expect.csv
```

Generated working files (`*.in-tc.csv`, `*.dumpdb`, `*.out-tc.csv`,
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
- [x] Input table: each TAXSIM input variable used → Tax-Calculator
      variable(s) and transformation, including MARS from `mstat` +
      dependents, `XTOT`, child-age variables (`nu06`, `nu13`, `nu18`,
      `n24`, `f2441`, `EIC`, `elderly_dependents`), age of head/spouse,
      split wages, SE income, qualified dividends, cap gains, pensions,
      Social Security, UI, itemized deductions, child-care expenses,
      S-corp / business income and QBID inputs.
- [x] Output table: each TAXSIM `idtl=2` variable (`fiitax`, `fica`,
      `v10`..`v28`, others PE emits) → Tax-Calculator expression,
      with year-specific notes (2021 fully refundable CTC/CDCC and RRC;
      2025 OBBBA provisions such as the senior deduction).
- [x] Mark variables excluded from comparison and why.
- [x] Get user review of VARIABLES.md before coding Phases 3-6.

### Phase 3 — Step 1: `generate_sample.py`  (≈1 session)
- [x] Year range 2021-2025; `state=0`; `idtl=2`; CLI args: letter, year, N, seed offset.
- [x] Keep a/b/c assumption sets; revise only where VARIABLES.md requires
      (e.g., dependent-age inputs PE honors).
- [x] Deterministic seed per (letter, year); write `samples/LYY.in.csv.gz`.
- [x] Self-check: required columns, value ranges, no NaNs.

### Phase 4 — Step 2: `run_pe.py`  (1 session to write; runs may span days)
- [x] Reads `pe_pin.json`; builds the `uvx` command; runs via `subprocess`;
      never imports PolicyEngine.
- [x] Writes `pe_output/LYY.out-pe.csv.gz`; refuses to overwrite without `--force`.
- [x] Verifies output row count and ids match the input sample.
- [x] Generate a21..a25 first (needed for Phase 7); then b, c.

### Phase 5 — Step 3: `taxsim_to_tc.py`  (≈1 session)
- [x] Implement the input table from VARIABLES.md (replace old quirks
      where VARIABLES.md says so).
- [x] Self-checks: `e00200 == e00200p + e00200s`, `e00900` likewise,
      valid MARS, `XTOT` consistency, child counts nested
      (nu06 ≤ nu13 ≤ nu18), no unknown columns
      (verify all names exist in `records_variables.json`).

### Phase 6 — Step 4: `run_tc.py`  (1-2 sessions)
- [x] Verify how the CLI treats a custom input file for TAXYEAR (no
      extrapolation/growfactor aging, weights not needed); document the result.
- [x] Run `python -m taxcalc.cli.tc LYY.in-tc.csv 20YY --reform pe_emulation.json --dumpdb --dumpvars dumpvars.txt --silent`.
- [x] Read the SQLite dump; build TAXSIM-format output per VARIABLES.md
      (salvaging `process_taxcalc_output.py` logic, updated for 2021-2025).
- [x] `pe_emulation.json` written in Phase 5 (see Decisions table).

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
- [ ] Ask user whether to add a thin `taxcalc/validation/Makefile`
      whose targets only call `validate.py` (e.g., `make validate`,
      `make clean` of `work/`).  Con: file-dependency rules would
      silently regenerate the canonical committed samples and PE
      outputs whenever a script changes, and would duplicate
      `validate.py`; so no per-file sample/PE-output rules.
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
| 2 VARIABLES.md | done; reviewed and merged by user (2026-10-07) |
| 3 generate_sample.py | done (2026-10-07) |
| 4 run_pe.py + PE outputs | done (2026-10-07) |
| 5 taxsim_to_tc.py | done (2026-10-07) |
| 6 run_tc.py | done (2026-10-07) |
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
- 2026-10-07: Phase 2 session.
  * Wrote `pe_taxsim/VARIABLES.md` (input table, output table,
    exclusions, year notes, `pe_emulation.json` proposal, open items)
    from the pinned PE-taxsim source (in the uv git cache at
    `~/.cache/uv/git-v1/checkouts/*/3e2a758/`) and policyengine-us
    2.30.1 source (uv archive cache), plus TC `calcfunctions.py`.
  * Main findings:
    - TC default `eitc_claim_prob_scale`/`actc_claim_prob_scale`
      randomly zero some EITC/ACTC via `credit_claim_urn`; proposed
      emulation entries set both to 9e99 (full take-up, as in PE).
    - All three old emulation entries proposed for removal.
    - PE sums `mortgage`+`otheritem` into fully deductible interest:
      TC `e19200 = mortgage + otheritem` (old `otheritem->e18400` wrong).
    - PE counts rental income (`otherprop`) as QBI; TC does not.
      Open decision D1 (recommend also writing `otherprop` to `e27200`).
    - TC 2021 `ODC_is_refundable = true`, but ARPA made only the child
      credit refundable and PE keeps ODC nonrefundable: likely TC bug
      (watch item W1); confirm with data in Phase 8, then report.
    - TC `soi_iitax=false`, so `iitax`/`payrolltax` split matches PE
      `fiitax`/`fica`.  2021 ARPA CTC increase is TC `ctc_new`.
    - `v13`/`v17` compared conditionally on TC's itemizing choice;
      `v19` only when `dwks10 == 0`; `frate` excluded (method differs).
  * Next step: user reviews VARIABLES.md and decides D1 and the
    emulation proposal (record both in the Decisions table); then
    Phase 3.
- 2026-10-07: Phase 3 session.
  * User reviewed and merged VARIABLES.md; Phase 2 marked done.
    Decision D1 (rental income in QBI) and the `pe_emulation.json`
    proposal are still not recorded in the Decisions table; they are
    needed by Phases 5-6, not by Phase 3.
  * Rewrote `generate_sample.py`: CLI `python generate_sample.py
    LETTER YEAR [--size N] [--offset K] [--outdir DIR]` (YEAR is
    2021-2025, default N=10,000); writes `samples/LYY.in.csv.gz`
    (gzip mtime 0, so reruns are byte-identical).  Seed is
    `np.random.default_rng([123456789, letter index, year, offset])`.
    Columns: taxsimid year state mstat page sage depx age1..age5,
    then the old income/deduction columns and idtl (no dep13/17/18).
  * Changes from the old generator, per VARIABLES.md: dependent ages
    uniform on 1..23, sorted youngest first, 0 in unused slots (PE
    builds dependents from `depx`, so unused slots are ignored);
    `nonprop = transfers = rentpaid = pprofinc = sprofinc = 0`;
    spouse columns (incl. `sui`, which the old code missed) are 0 when
    `mstat == 1`; `childcare` is 0 unless a dependent is under 13;
    `psemp`/`ssemp` are in dollars (units bug fixed).
  * Fixing the units bug made every b/c unit's income very high (in
    a 50-row c21 PE run the minimum AGI was $471k, so no credits).  User
    chose sparse business income (Decisions table).  In 300 c21 rows
    PE then gives ACTC 76, CDCC 65, RRC 9, QBID 34, NIIT 268, but EITC
    0 and AMT 0.  EITC is zero because b/c investment income (up to
    $90k) almost always exceeds the EITC investment-income limit;
    EITC is exercised only in set a.  Revisit if b/c EITC coverage is
    wanted.
  * PE check of the new layout: in 300 a21 rows every low-income
    unit with children got ACTC exactly $3,600 per child under 6 plus
    $3,000 per other child under 18, so `age1..age5` are honored.
  * `check_sample()` enforces columns, row count, no NaNs, taxsimid
    1..N, year, idtl, mstat, zero columns, single-filer spouse zeros,
    age ranges, unused age slots 0, childcare rule, cap-gain ranges,
    non-negative amounts, and $1,000 multiples.  pycodestyle and
    pylint are clean.
  * Generated all 15 committed samples (N=10,000; 3.3 MB total).
  * Next step: Phase 4, write `run_pe.py` and generate a21..a25 PE
    outputs.  Before Phase 5, record D1 and the emulation decision.
- 2026-10-07: Phase 4 session.
  * Phase 2 review item was already checked; nothing to change there.
  * Wrote `run_pe.py`: `python run_pe.py LETTER YEAR [--force]
    [--indir DIR] [--outdir DIR]`.  Builds the uvx command from
    `pe_pin.json` (incl. `--with policyengine-us==...` and
    `pe_cli_options`); never imports PolicyEngine.  Before running,
    it asks the uv env (`uvx ... python -c`) for the resolved
    policyengine-us, policyengine-core, and Python versions and stops
    if any differs from the pin.  It gunzips the sample to a temp dir,
    runs PE, checks the output (the 41 expected columns, row count,
    taxsimid and year equal to the input, no NaNs, state 0), then
    gzips the PE output bytes unchanged (mtime 0) to
    `pe_output/LYY.out-pe.csv.gz` and writes
    `pe_output/LYY.out-pe.stamp.json` (pinned versions, input/output
    SHA-256, run date and seconds).  Refuses to overwrite without
    `--force`.  Rerunning gives a byte-identical output.
    pycodestyle and pylint are clean.  README.md updated for step 2.
  * Generated all 15 PE outputs (N=10,000): 12 s each; 7.6 MB total
    gzipped (larger than the samples because PE writes floats).
  * Nonzero counts worth remembering for triage: set a has no
    QBID/NIIT/AMT(v14), as expected; a21 RRC (`cares`) 2,969 and
    ACTC 5,130 vs about 1,700-1,800 in a22-a25.  In b/c, NIIT is
    nonzero for ~87% of units, QBID ~10-14%, EITC (v25) almost never
    (see Phase 3 log), ACTC small except in 2021.  c21 CDCC (v24)
    2,140 vs ~6,200 in c22-c25: correct, because the 2021 ARPA CDCC
    phases out completely at high AGI and the median AGI of c21 units
    with child care is ~$557k.
  * Next step: record decision D1 (rental income in QBI) and the
    `pe_emulation.json` proposal from VARIABLES.md in the Decisions
    table; then Phase 5 (`taxsim_to_tc.py`).
- 2026-10-07: Phase 5 session.
  * Decisions (now in the Decisions table), after showing the user
    options with pros and cons:
    - D1: the premise in VARIABLES.md was wrong.  policyengine-us
      counts `rental_income` as QBI by default, but the pinned PE-taxsim
      runner (`runners/policyengine_runner.py` ~line 1258) pins
      `rental_income_would_be_qualified` to False for every row, as
      TAXSIM does.  Confirmed in the PE outputs: no b23/c23 unit
      without business income has `qbid > 0`.  So `otherprop` goes
      only to `e02000`.
    - `pe_emulation.json` rewritten with three commented entries:
      EITC/ACTC take-up scale 9e99, and `AMT_child_em_c_age = 19`
      (PE `amt_kiddie_tax_applies` uses the section 152(c)(3)
      non-student age limit 19; the samples have heads aged 17-18).
      The old TAXSIM-35 entries were dropped.  Checked that `Policy`
      accepts the reform.
    - W2 resolved: PE also reduces QBI by the deductible part of SECA
      (`qbi.deduction_definition`).  PE pins
      `w2_wages_from_qualified_business` only with the unused
      `assume_w2_wages` option, so VARIABLES.md is right on W-2 wages.
  * VARIABLES.md updated (otherprop row, QBI paragraph, `qbid` note,
    emulation section, D1/W2 entries).
  * Rewrote `taxsim_to_tc.py`: `python taxsim_to_tc.py LETTER YEAR
    [--indir DIR] [--outdir DIR]` reads `samples/LYY.in.csv.gz` and
    writes `work/LYY.in-tc.csv` (38 columns, in a fixed order).
    `translate()` implements the VARIABLES.md input tables;
    `check_tc_input()` checks the Phase 5 list plus spouse-zero,
    dependent-count, dividend/pension, and e02000 >= e26270
    constraints.  Fault-injection tests confirmed the checks fire.
    pycodestyle and pylint are clean.  All 15 files translate; a21, b23,
    and c25 load in `Records(..., gfactors=None, weights=None)` and run
    through `calc_all()` with the emulation reform.
  * Next step: Phase 6, `run_tc.py` (first verify how the CLI handles
    a custom input file for TAXYEAR).
- 2026-10-07: Phase 6 session.
  * Verified (taxcalcio.py and a trial run): for an INPUT that is not
    `cps.csv` or `tmd.csv`, the CLI builds `Records(data, start_year=
    TAXYEAR, gfactors=None, weights=None)` and a Calculator with
    `sync_years=False`, so input values are used unchanged (no aging),
    `FLPDYR` is set to TAXYEAR, and `s006` is 0 (weights are not
    needed).  Output files go to the current working folder.
    Documented in README.md (step 4) and the run_tc.py docstring.
  * Rewrote `run_tc.py`: `python run_tc.py LETTER YEAR [--workdir DIR]`
    runs `python -m taxcalc.cli.tc` in `work/` with the repo root
    first on PYTHONPATH (working-tree code), the `pe_emulation.json`
    reform, and the new committed `dumpvars.txt`; renames the CLI dump
    to `work/LYY.dumpdb`; reads its `reform` table; and writes
    `work/LYY.out-tc.csv` with the 23 compared TAXSIM columns from the
    VARIABLES.md output table plus `tc_dwks10` (needed by step 5 to
    decide when `v19` is compared; VARIABLES.md notes this).  The
    `v44` HI rate comes from a `Policy` object with the emulation
    reform.  `v13`/`v17` are written unconditionally; step 5 compares
    `v13` only where TC `v17 == 0` and `v17` only where TC `v13 == 0`.
    Checks columns, row count, taxsimid, year, NaNs.  pycodestyle and
    pylint clean.  ~3.5 s per 10,000-unit file.
  * Plumbing preview (a21, a22, b23, c25 vs PE; |diff| > $1 counts):
    fica, tfica, addmed, v44, v10, v11, v12, v14, v24, v25, cares,
    niit all match exactly in a21/b23/c25.  Differences to triage:
    a21 fiitax/v22 1,195, actc 1,735 (PE 2021 `actc` seems to include
    ODC amounts; also W1-like v22 cases), v26 1,128; b23 v13/v18/v28/
    v22 ~845, qbid 52, v26 54; c25 fiitax 864, v22 860, v26 940.
  * Likely TC bug found (report to user, not yet fixed): every b23
    v13 difference is exactly -$50 for unmarried aged heads: TC
    `STD_Aged` for 2023 is $1,800 for MARS 1/4, but Rev. Proc. 2022-38
    sets $1,850.  Also noticed: TC's MARS=5 (surviving spouse)
    `STD_Aged` uses the unmarried amount in 2021-2024 but the married
    amount in 2025 (the statute gives the married amount); MARS=5 is
    not in our samples.
  * Next step: Phase 7 (`compare.py`, `validate.py`).
