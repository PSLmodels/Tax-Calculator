TAXSIM / Tax-Simulator variable correspondence
=============================================

**Draft (Phase 2).**  Entries marked *(to confirm)* are taken from a
static reading of Tax-Simulator ("TS") source code and the Phase 1
spike, and must be confirmed when `run_ts.R` is written (Phase 3).

This document specifies how the TAXSIM-format sample (step 1) is
translated into TS tax units and how TS output is converted into
TAXSIM-format output (step 2, `run_ts.R`), so that it can be compared
with Tax-Calculator output (steps 3-5).

The translation of the TAXSIM-format sample into Tax-Calculator
input, and of Tax-Calculator output into TAXSIM-format output, is the
same as in the `pe_taxsim` workflow, so it is not repeated here: see
[`../pe_taxsim/VARIABLES.md`](../pe_taxsim/VARIABLES.md).

All statements about TS describe the pinned version in
[`ts_pin.json`](ts_pin.json), as read from its source code
(`src/tests/test_taxsim.R` crosswalk, `src/calc/**`,
`src/data/tax_law.R`).  They must be rechecked whenever the pin
changes.

Notation: `p`/`s` suffixes denote the primary taxpayer and spouse;
"deps" means the `depx` dependents, whose ages are `age1..age{depx}`.
The `tbly_ts` samples have `depx <= 3`, because TS records only three
dependent ages.


Input variables
---------------

Every sample row has `state=0` and `idtl=2`, and `mstat` is 1, 2, or 6.
TS columns not listed below are zero-filled.

### Identification and demographics

| TAXSIM | TS | Transformation |
|---|---|---|
| `taxsimid` | `id` | copy |
| `year` | `year` | copy; selects the tax-law row |
| `state`, `idtl` | (none) | dropped |
| `mstat` | `filing_status` | `2` if `mstat==2`; else `3` if `mstat==6`; else `4` (head of household) if `depx>0`; else `1` (same rule as TC's `MARS`) |
| `page` | `age1` | copy |
| `sage` | `age2` | copy if `mstat==2`, else **NA** |
| (none) | `blind1`, `blind2` | `0`; `blind2` is NA when there is no spouse |
| `depx` | `n_dep` | copy |
| `age1..age3` | `dep_age1..dep_age3` | copy for present deps, ordered youngest first; **NA** for absent deps |
| (none) | `dep_ctc1..3`, `dep_ssn1..3` | `1` for present deps, NA otherwise *(to confirm: whether TS applies the age < 17 test itself or `dep_ctc` must encode it)* |
| (none) | `n_dep_eitc` | count of deps with age < 19 *(to confirm against TS's EITC child test)* |
| (none) | `dep_status` | `0` (not a dependent filer) |
| (none) | `filer` | `1` |

### Income

| TAXSIM | TS | Transformation |
|---|---|---|
| `pwages`, `swages` | `wages1`, `wages2`, `wages` | copy; `wages = wages1 + wages2` |
| `psemp`+`pbusinc`, `ssemp`+`sbusinc` | `sole_prop1`, `sole_prop2`, `sole_prop` | sums per person; `sole_prop = sole_prop1 + sole_prop2`; `sstb_sole_prop = 0` |
| `pprofinc`, `sprofinc` | (none) | always 0 in the samples |
| `scorp` | `scorp_active` | copy; `sstb_scorp = 0` |
| `otherprop` | `rent` | copy *(to confirm: TS's QBI and NIIT treatment of `rent` vs. TC's `e02000`)* |
| `dividends` | `div_pref` | copy; `div_ord = 0` (all dividends qualified) |
| `intrec` | `txbl_int` | copy |
| `stcg` | `kg_st` | copy |
| `ltcg` | `kg_lt` | copy |
| `pensions` | `txbl_pens_dist`, `gross_pens_dist` | copy to both; `txbl_ira_dist = 0` |
| `gssi` | `gross_ss` | copy |
| `pui`+`sui` | `ui` | sum |
| `nonprop`, `transfers`, `rentpaid` | (none) | always 0 in the samples |

### Itemized deductions and child care

TAXSIM's `mortgage` and `otheritem` are composites that TS splits
across several inputs.  The convention below makes both models treat
the amounts the same way as `pe_taxsim` does (fully deductible, no
AGI floor, outside the SALT cap, no AMT add-back).

| TAXSIM | TS | Transformation |
|---|---|---|
| `proptax` | `salt_prop` | copy |
| (none) | `salt_inc_sales`, `salt_pers` | 0 |
| `mortgage`+`otheritem` | `first_mort_int` | sum *(to confirm: TS's mortgage-balance limit must not bind; set `first_mort_bal` = 0 or a value below the limit, and `first_mort_year` to a pre-2017 year if needed)* |
| `childcare` | `care_exp` | copy |

### TS inputs set to constants

- `r.bus_loss = r.new_car = r.cdctc_takeup = r.eitc_precert = 0`
  (random draws: zero means full CDCTC take-up and the EITC
  pre-certification check off; set explicitly, not by zero-fill).
- `salt_workaround_part = salt_workaround_scorp = 0`.
- All other exogenous TS inputs are zero-filled.

### Tax law

The 2023-2025 baseline law is built by
`build_tax_law_from_id('baseline', years, indexes)` with `indexes`
read from the committed `ts_indexes.csv` (IRS-style Sept-Aug averages
of CPI-U from 1986 and chained CPI-U, plus SSA AWI), then adjusted by
the committed `ts_law_overrides.csv` (year, filing status, TS column,
IRS/SSA published value) where TS's indexation gives a value that
differs from the published one (decision D6).  The 2025 standard
deduction is **not** overridden (see `SUMMARY.md`).


Output variables
----------------

`run_ts.R` writes the TAXSIM-35 output columns that TS can supply,
with the same names as `../pe_taxsim/pe_output/*.out-pe.csv.gz`.
"Compare" restrictions are those of `../pe_taxsim/VARIABLES.md`.

| TAXSIM | TS expression | Notes |
|---|---|---|
| `taxsimid` | `id` | key |
| `year` | `year` | key |
| `fiitax` | `liab_iit_net` | *(to confirm)* |
| `fica` | `liab_pr` | employee + employer OASDI and HI, SECA, Additional Medicare Tax *(to confirm)* |
| `addmed` | `liab_add_med` | |
| `v10` | `agi` | |
| `v11` | `ui` | input |
| `v12` | `txbl_ss` | |
| `v13` | `std_ded` | |
| `v14` | `pe` | personal exemptions; zero in 2023-2025 *(to confirm)* |
| `v17` | `item_ded` | |
| `v18` | `txbl_inc` | |
| `v27` | `liab_amt` | |
| `v28` | `liab_bc` | regular tax before credits *(to confirm: whether `liab_bc` includes `liab_amt`)* |
| `niit` | `liab_niit` | |
| `v22` | `ctc_nonref` | *(to confirm: whether it includes the $500 credit for other dependents)* |
| `actc` | `ctc_ref` | |
| `v24` | `cdctc_nonref + cdctc_ref` | |
| `v25` | `eitc` | |

TAXSIM outputs for which TS has no equivalent identified yet
(`tfica`, `v44`, `qbid`, `v19`, `v26`, `cares`, `frate`) are
left out until Phase 3 finds one; TS outputs with no TAXSIM
equivalent are left out.
