TAXSIM / Tax-Simulator variable correspondence
=============================================

The tables below describe what `run_ts.R` does; they were
confirmed by reading Tax-Simulator ("TS") source code and running
`run_ts.R` on the samples.  Differences between TS and
Tax-Calculator results are triaged in `SUMMARY.md`.

This document specifies how the TAXSIM-formatted sample (step 1) is
translated into TS tax units and how TS output is converted into
TAXSIM-formatted output (step 2, `run_ts.R`), so that it can be
compared with Tax-Calculator output (steps 3-5).

The translation of the TAXSIM-formatted sample into Tax-Calculator
input, and of Tax-Calculator output into TAXSIM-formatted output, is
the same as in the `pe_taxsim` workflow, so it is not repeated here:
see [`../pe_taxsim/VARIABLES.md`](../pe_taxsim/VARIABLES.md).

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
| (none) | `dep_ctc1..3`, `dep_ssn1..3` | `1` for present deps, NA otherwise (`dep_ctc` encodes only the non-age tests; TS applies the CTC age limits itself, and deps that are not CTC children get the $500 credit for other dependents) |
| (none) | `n_dep_eitc` | count of deps with age < 19 (TS applies no age test of its own, so this matches TC's `EIC`) |
| (none) | `dep_status` | `0` (not a dependent filer) |
| (none) | `filer` | `1` |

### Income

| TAXSIM | TS | Transformation |
|---|---|---|
| `pwages`, `swages` | `wages1`, `wages2`, `wages` | copy; `wages = wages1 + wages2` |
| `psemp`+`pbusinc`, `ssemp`+`sbusinc` | `sole_prop1`, `sole_prop2`, `sole_prop` | sums per person; `sole_prop = sole_prop1 + sole_prop2`; `sstb_sole_prop = 0` |
| `pprofinc`, `sprofinc` | (none) | always 0 in the samples |
| `scorp` | `scorp_active` | copy; `sstb_scorp = 0` |
| `otherprop` | `rent` | copy; not QBI in TS (its QBI deduction uses only `sole_prop`, `part`, `scorp`, `farm`), as in `pe_taxsim` decision D1; included in NIIT investment income through `sch_e` |
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
| `mortgage`+`otheritem` | `other_item_exp` | sum; `first_mort_int` is not used, because TS's mortgage-balance limit divides by the mortgage balance (0/0 when the balance is zero); `other_item_exp` is fully deductible, not subject to the SALT cap or an AGI floor, and not added back for the AMT |
| `childcare` | `care_exp` | copy |

### TS inputs set to constants

- `r.bus_loss = r.new_car = r.cdctc_takeup = r.eitc_precert = 0`
  (random draws: zero means full CDCTC take-up and the EITC
  pre-certification check off; set explicitly, not by zero-fill).
- `salt_workaround_part = salt_workaround_scorp = 0`.
- All other exogenous TS inputs are zero-filled.

### Tax law

The 2023-2025 baseline law is built by
`build_tax_law_from_id('default', years, indexes)` with `indexes`
read from the committed `ts_indexes.csv` (IRS-style Sept-Aug averages
of CPI-U from 1986 and chained CPI-U, plus SSA AWI), then adjusted by
the committed `ts_law_overrides.csv` (year, filing status, TS column,
IRS/SSA published value, TS value) where TS's indexation gives a value
that differs from the published one.  `build_overrides.py` generates
that file by comparing the TS law with Tax-Calculator's policy
parameters (see the "Building the overrides file" section of
`README.md`).  `run_ts.R` checks
that each TS value equals the `ts_value` recorded in the overrides
file, so a change in the pin or in `ts_indexes.csv` cannot silently
change the overrides.  The overrides cover ordinary and
capital-gains brackets, AMT exemption, phase-out threshold, and 28%
bracket, EITC phase-in amounts, phase-out thresholds, and investment
income limit, QBI thresholds, and the 2024-2025 OASDI maximum taxable
earnings.  A TS parameter value that is wrong in the TS YAML files
themselves (not because of indexation) would **not** be overridden, so
that it shows up as a difference and can be reported to the Budget
Lab; the pinned TS has no such errors.

`ts_indexes.csv` was made by `build_indexes.py` from the FRED series
`CPIAUCNS` (CPI-U) and `SUUR0000SA0` (chained CPI-U), averaged over
September of the previous year through August, and SSA national
average wage index values for 2020-2025; the series must start no
later than 1986.


Output variables
----------------

`run_ts.R` writes `taxsimid`, `year`, and the TAXSIM output variables
that `../common/compare.py` compares, in its `COMPARED_VARIABLES`
order (not in the column layout of `../pe_taxsim/pe_output`).  All of
them have a TS equivalent.  "Compare" restrictions are those of
`../pe_taxsim/VARIABLES.md`.

| TAXSIM | TS expression | Notes |
|---|---|---|
| `taxsimid` | `id` | key |
| `year` | `year` | key |
| `fiitax` | `liab_iit_net` | income tax after all credits, incl. NIIT; excl. Additional Medicare Tax |
| `fica` | `liab_pr` | employee + employer OASDI and HI, SECA, Additional Medicare Tax |
| `tfica` | `liab_pr - liab_fica_er1 - liab_fica_er2` | employee OASDI and HI, full SECA, Additional Medicare Tax |
| `addmed` | `liab_add_med` | |
| `v44` | `pr.hi_ee_rates * wages + liab_add_med` | HI rate from the TS law row |
| `v10` | `agi` | |
| `v11` | `ui` | input |
| `v12` | `txbl_ss` | |
| `v13` | `std_ded` | |
| `v14` | `pe_ded` | zero in 2023-2025 |
| `v17` | `item_ded` | |
| `qbid` | `qbi_ded` | |
| `v18` | `txbl_inc` | |
| `v19` | `liab_ord` | tax at ordinary rates on taxable income less preferential income |
| `v28` | `liab` | regular tax before credits, excl. AMT (TS's `liab_bc` includes `liab_amt`, so it is not used) |
| `v26` | `amt_gross_inc` | AMT income before the exemption |
| `v27` | `liab_amt` | |
| `niit` | `liab_niit` | TS multiplies net investment income by 0.7 (a calibration factor in `niit.R`), so NIIT differs from TC's (see `SUMMARY.md`) |
| `v22` | `ctc_nonref` | nonrefundable CTC incl. the $500 credit for other dependents |
| `actc` | `ctc_ref` | |
| `v24` | `cdctc_nonref + cdctc_ref` | |
| `v25` | `eitc` | |
| `cares` | `rebate` | zero in 2023-2025 |
