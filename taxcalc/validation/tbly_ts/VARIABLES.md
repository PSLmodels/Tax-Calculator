TAXSIM / tax-simulator-gpu variable correspondence
==================================================

The tables below describe what `run_ts.py` and `ts_batch.py` do; they
were confirmed by reading tax-simulator-gpu ("TS") source code and
running `run_ts.py` on the samples.  Differences between TS and
Tax-Calculator results are triaged in `SUMMARY.md`.

This document specifies how the TAXSIM-formatted sample (step 1) is
translated into TS tax units and how TS output is converted into
TAXSIM-formatted output (step 2, `run_ts.py`), so that it can be
compared with Tax-Calculator output (steps 3-5).

The translation of the TAXSIM-formatted sample into Tax-Calculator
input, and of Tax-Calculator output into TAXSIM-formatted output, is
the same as in the `pe_taxsim` workflow, so it is not repeated here:
see [`../pe_taxsim/VARIABLES.md`](../pe_taxsim/VARIABLES.md).

All statements about TS describe the pinned version in
[`ts_pin.json`](ts_pin.json), as read from its source code
(`src/taxmodel/run/batch.py`, `src/taxmodel/frame/`,
`src/taxmodel/taxes/`, and the default tax law in
`config/scenarios/tax_law/default/`).  They must be rechecked whenever
the pin changes.

Notation: `p`/`s` suffixes denote the primary taxpayer and spouse;
"deps" means the `depx` dependents, whose ages are `age1..age{depx}`.
The `tbly_ts` samples have `depx <= 3`, because TS records only three
dependent ages.


How TS is run
-------------

`run_ts.py` writes the TS tax units to a CSV file, and `ts_batch.py`,
running in the TS environment, converts it to the parquet file read by
TS's batch command (`python -m taxmodel.run.batch`), runs that command,
and converts its parquet output back to CSV.  The batch command:

1. checks that the tax units have every column that the TS frame steps
   and tax calculation read (`run_ts.py` checks, using the command's
   manifest, that every column it supplies is read);
2. splits each earner's wages into base pay, tips, and overtime (the
   samples have no tips or overtime) and attaches the random draws;
3. compiles the year's default law;
4. runs the TS frame steps (the law join, the state SALT-cap
   workaround, the capital gain price ratio, and net worth) and the
   whole income and payroll tax calculation under that law.  The
   estate tax is left out, and the wealth tax, which is zero under the
   default law, is computed separately from the income tax and is not
   used here.

`ts_batch.py` gives the batch command two options:

- `--zero-draws` sets every TS random draw to zero, which means full
  child and dependent care credit take-up (`r.cdctc_takeup`) and that
  the excess business loss limit applies to every unit
  (`r.bus_loss`).  The other draws have no effect on the samples: the
  EITC pre-certification check (`r.eitc_precert`) is off in the
  default law, there is no auto loan interest (`r.new_car`), and there
  are no state income or sales taxes for the SALT-cap workaround
  (`r.salt_workaround`).
- `--bundled-macro` reads the price and wage indexes the TS law
  compiler uses from the copy of the pinned Macro-Projections
  publication in the TS repository (`resources/macro_projections/`).

The law is the TS default law, unchanged (see the "Tax law" section of
`README.md`).


Input variables
---------------

Every sample row has `state=0` and `idtl=2`, and `mstat` is 1, 2, or 6.
TS columns not listed below are zero-filled (see `ZERO_COLUMNS` in
`run_ts.py`).

### Identification and demographics

| TAXSIM | TS | Transformation |
|---|---|---|
| `taxsimid` | `id` | copy |
| `year` | (none) | selects the law year of the batch command |
| `state`, `idtl` | (none) | dropped |
| `mstat` | `filing_status` | `2` if `mstat==2`; else `3` if `mstat==6`; else `4` (head of household) if `depx>0`; else `1` (same rule as TC's `MARS`) |
| `page` | `age1` | copy |
| `sage` | `age2` | copy if `mstat==2`, else **NaN** |
| (none) | `blind1`, `blind2` | `0`; `blind2` is NaN when there is no spouse |
| `depx` | `n_dep` | copy |
| `age1..age3` | `dep_age1..dep_age3` | copy for present deps, ordered youngest first; **NaN** for absent deps |
| (none) | `dep_ctc1..3`, `dep_ssn1..3` | `1` for present deps, NaN otherwise (`dep_ctc` encodes only the non-age tests; TS applies the CTC age limits itself, and deps that are not CTC children get the $500 credit for other dependents) |
| (none) | `n_dep_eitc` | count of deps with age < 19 (TS applies no age test of its own, so this matches TC's `EIC`) |
| (none) | `dep_status` | `0` (not a dependent filer) |
| (none) | `filer` | `1` |
| (none) | `weight` | `1` |

### Income

| TAXSIM | TS | Transformation |
|---|---|---|
| `pwages`, `swages` | `wages1`, `wages2`, `wages` | copy; `wages = wages1 + wages2`; tips and overtime (`tips1`, `tips2`, `ot1`, `ot2`) are zero |
| `psemp`+`pbusinc`, `ssemp`+`sbusinc` | `sole_prop1`, `sole_prop2`, `sole_prop` | sums per person; `sole_prop = sole_prop1 + sole_prop2`; `sstb_sole_prop = 0` |
| `pprofinc`, `sprofinc` | (none) | always 0 in the samples |
| `scorp` | `scorp_active` | copy; `sstb_scorp = 0` |
| `otherprop` | `rent` | copy; not QBI in TS (its QBI deduction uses only sole proprietorship, partnership, S corporation, and farm income), as in `pe_taxsim` decision D1; included in NIIT investment income through `sch_e` |
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
| `mortgage`+`otheritem` | `other_item_exp` | sum; `first_mort_int` is not used, so TS's mortgage-balance limit, which needs mortgage balances the samples do not have, plays no role; `other_item_exp` is fully deductible, not subject to the SALT cap or an AGI floor, and not added back for the AMT |
| `childcare` | `care_exp` | copy |

### TS inputs set to zero

All other TS tax unit inputs are zero, including the balance-sheet
(`value.*`, `basis.*`) and mortality (`q_death1`, `q_death2`) columns
that only the estate and wealth taxes and the net worth frame step
use, and `divorce_year`, `male1`, `kg_lt_basis`, and
`kg_lt_years_held`, which do not affect income or payroll taxes under
the default law.


Output variables
----------------

`run_ts.py` writes `taxsimid`, `year`, and the TAXSIM output variables
that `../common/compare.py` compares, in its `COMPARED_VARIABLES`
order (not in the column layout of `../pe_taxsim/pe_output`).  All of
them have a TS equivalent.  "Compare" restrictions are those of
`../pe_taxsim/VARIABLES.md`.

| TAXSIM | TS expression | Notes |
|---|---|---|
| `taxsimid` | `id` | key |
| `year` | (sample `year`) | key |
| `fiitax` | `liab_iit_net` | income tax after all credits, incl. NIIT; excl. Additional Medicare Tax, estate tax, and wealth tax |
| `fica` | `liab_pr` | employee + employer OASDI and HI, SECA, Additional Medicare Tax |
| `tfica` | `liab_pr - liab_fica_er1 - liab_fica_er2` | employee OASDI and HI, full SECA, Additional Medicare Tax |
| `addmed` | `liab_add_med` | |
| `v44` | employee HI rate `* wages + liab_add_med` | `ts_batch.py` reads the employee HI rate from the year's TS law (`payroll.hi_ee_rates`), after checking that it is a single rate |
| `v10` | `agi` | |
| `v11` | `ui` | input |
| `v12` | `txbl_ss` | |
| `v13` | `std_ded` | |
| `v14` | `pe_ded` | zero in 2023-2025 |
| `v17` | `item_ded` | |
| `qbid` | `qbi_ded` | |
| `v18` | `txbl_inc` | |
| `v19` | `liab_ord` | tax at ordinary rates on taxable income less preferential income |
| `v28` | `liab` | regular tax before credits, excl. AMT |
| `v26` | `amt_gross_inc` | AMT income before the exemption |
| `v27` | `liab_amt` | |
| `niit` | `liab_niit` | TS multiplies net investment income by 0.7 (a calibration factor in `niit.py`), so NIIT differs from TC's (see `SUMMARY.md`) |
| `v22` | `ctc_nonref` | nonrefundable CTC incl. the $500 credit for other dependents |
| `actc` | `ctc_ref` | |
| `v24` | `cdctc_nonref + cdctc_ref` | |
| `v25` | `eitc` | |
| `cares` | `rebate` | zero in 2023-2025 |
