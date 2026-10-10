TAXSIM / Tax-Calculator variable correspondence
==============================================

This document specifies how the TAXSIM-format sample (step 1) is
translated into Tax-Calculator input (step 3, `taxsim_to_tc.py`) and
how Tax-Calculator output is converted into TAXSIM-format output
(step 4, `run_tc.py`) so that it can be compared with the
policyengine-taxsim output (step 5, `compare.py`).

All statements about policyengine-taxsim ("PE") describe the pinned
version in [`pe_pin.json`](pe_pin.json) (policyengine-taxsim
`3e2a7589`, policyengine-us 2.30.1), as read from its source code
(`config/variable_mappings.yaml`, `core/input_mapper.py`,
`runners/policyengine_runner.py`) and checked by probe runs.  They
must be rechecked whenever the pin changes.

Notation: `p`/`s` suffixes denote the primary taxpayer and spouse;
"deps" means the `depx` dependents, whose ages are `age1..age{depx}`.


Input variables
---------------

Every sample row has `state=0` and `idtl=2`, and `mstat` is 1 or 2.
PE simulates a `state=0` row in Texas but pins the state and local
income/sales tax deduction to zero, so no state tax affects the
federal results.

### Identification and demographics

| TAXSIM | PE treatment | Tax-Calculator | Transformation |
|---|---|---|---|
| `taxsimid` | record id | `RECID` | copy |
| `year` | tax year | `FLPDYR` | copy |
| `state` | always 0 | (none) | dropped |
| `idtl` | always 2 | (none) | dropped |
| `mstat` | 1: head only; 2: head + spouse (joint) | `MARS` | `2` if `mstat==2`; else `4` (head of household) if `depx>0`; else `1` |
| `page` | head age | `age_head` | copy |
| `sage` | spouse age (joint only) | `age_spouse` | copy if `mstat==2`, else 0 |
| `depx` | number of dependents | `XTOT` | `XTOT = depx + (2 if mstat==2 else 1)` |
| `age1..ageN` | each dependent's age; 0 or missing is silently changed to 10 | child-count variables | see next table |
| `dep13/dep17/dep18` | used only when no `ageN` is given | (none) | not written by the generator |

`MARS=4` for every single filer with a dependent is correct for PE
because PE treats every TAXSIM dependent as a qualifying child (age
< 19) or a qualifying relative (age >= 19, no gross income), both of
which make the filer eligible for head-of-household status.

### Dependent counts derived from `age1..age{depx}`

PE has no full-time-student, disability, or support information, so
it treats every dependent as a non-student who is not disabled.  The
derived counts below follow PE's rules for those dependents.

| Tax-Calculator | Definition (count over deps unless noted) | Used by |
|---|---|---|
| `nu06` | age < 6 | 2021 ARPA CTC under-6 amount (`CTC_new_c_under6_bonus`) |
| `nu13` | age < 13 | dependent-care ALD (reform only) |
| `f2441` | age < 13 | CDCC qualifying persons |
| `n24` | age < 17 | CTC qualifying children (2022-2025) |
| `nu18` | age < 18, **plus** head if `page<18` and spouse if `sage<18` | 2021 CTC child count (`CTC_include17`), which subtracts head/spouse under 18 |
| `EIC` | `min(3, count of age < 19)` | EITC qualifying children |
| `elderly_dependents` | age >= 65 | dependent-care ALD (reform only) |

Under these definitions the Credit for Other Dependents count that
Tax-Calculator computes, `XTOT - childnum - num`, equals the number of
dependents who are not CTC-qualifying children, which is PE's
"adult dependent" ($500) count.  `n1820` and `n21` (used only by the
UBI reform) are not written.

### Income

| TAXSIM | PE treatment | Tax-Calculator | Transformation |
|---|---|---|---|
| `pwages`, `swages` | per-person `employment_income` | `e00200p`, `e00200s`, `e00200` | copy; `e00200 = e00200p + e00200s` |
| `psemp`+`pbusinc`, `ssemp`+`sbusinc` | per-person `self_employment_income`: SECA and non-SSTB QBI | `e00900p`, `e00900s`, `e00900` | `e00900p = psemp + pbusinc`; `e00900s = ssemp + sbusinc`; `e00900 = e00900p + e00900s` |
| `pprofinc`, `sprofinc` | per-person `sstb_self_employment_income`: SECA and SSTB-phased QBI | (none) | generator must write 0 (Tax-Calculator's `PT_SSTB_income` is a unit-level flag, so a per-person SSTB split cannot be represented); `PT_SSTB_income = 0` |
| `scorp` | `partnership_s_corp_income`: QBI, no SECA; with `--scorp-treatment active` not in NIIT base | `e26270`, and included in `e02000` | `e26270 = scorp`; `k1bx14p = k1bx14s = 0` |
| `otherprop` | `rental_income`: in AGI, NII, and EITC investment income, but **not QBI** (see below) | `e02000` | `e02000 = otherprop + scorp`; not written to `e27200` |
| `dividends` | `qualified_dividend_income` (all dividends qualified) | `e00600`, `e00650` | `e00600 = e00650 = dividends` |
| `intrec` | `taxable_interest_income` | `e00300` | copy |
| `stcg` | `short_term_capital_gains` | `p22250` | copy |
| `ltcg` | `long_term_capital_gains` | `p23250` | copy |
| `pensions` | `taxable_private_pension_income` | `e01500`, `e01700` | `e01500 = e01700 = pensions` |
| `gssi` | `social_security_retirement` | `e02400` | copy |
| `pui`+`sui` | per-person `unemployment_compensation` | `e02300` | `e02300 = pui + sui` (the per-person split mattered only for the 2020 exclusion) |
| `nonprop` | **ignored** by PE (verified) | (none) | generator must write 0; old `e00800`/`AlimonyReceived_frac_in_AGI` handling dropped |
| `transfers` | `general_assistance` (non-taxable) | (none) | generator writes 0; dropped |
| `rentpaid` | `rent` (state use only) | (none) | generator writes 0; dropped |

PE splits interest, dividends, capital gains, S-corp income, pensions,
and Social Security between spouses on joint returns.  None of these
splits affects a federal tax amount, so Tax-Calculator's unit-level
variables suffice.

Neither model counts `otherprop` as qualified business income.
policyengine-us includes `rental_income` in QBI by default
(`rental_income_would_be_qualified` defaults to True), but the PE-taxsim
runner (`runners/policyengine_runner.py`) pins that variable to False
for every row, as TAXSIM does; Tax-Calculator's QBI includes rental
income only through `e27200`, which is left at zero (decision D1).
Both models reduce QBI by the deductible part of self-employment tax
(TC `c03260`; PE `qbi.deduction_definition`).  Neither model gets any W-2 wages or UBIA of the
business (`PT_binc_w2_wages = PT_ubia_property = 0`; PE's
`w2_wages_from_qualified_business` is left unset), so both limit the
deduction the same way above the QBID taxable-income threshold.

### Itemized deductions and child care

| TAXSIM | PE treatment | Tax-Calculator | Transformation |
|---|---|---|---|
| `proptax` | `real_estate_taxes`: SALT, subject to the SALT cap and AMT add-back | `e18500` | copy |
| (none) | state/local income or sales tax pinned to 0 | `e18400` | 0 |
| `mortgage`+`otheritem` | both summed into `deductible_mortgage_interest`: fully deductible, no AGI floor, outside the SALT cap, no AMT add-back | `e19200` | `e19200 = mortgage + otheritem` (the old `otheritem -> e18400` mapping is wrong for PE) |
| `childcare` | `tax_unit_childcare_expenses` | `e32800` | copy; the generator writes 0 unless some dependent is under 13 |

### Tax-Calculator inputs set to constants

`DSI = 0`, `blind_head = blind_spouse = 0`, `PT_SSTB_income = 0`,
`k1bx14p = k1bx14s = 0`.  All other Tax-Calculator input variables
take their default value of zero.

### Consequences for the generator (Phase 3)

- Write `age1..age{depx}` with every age >= 1; cover ages under 6,
  6-12, 13-16, 17, 18, and 19-23 so every child-count boundary is
  exercised.  Dependents need not be younger than the head: PE
  applies no relative-age test.
- Write `nonprop = transfers = rentpaid = pprofinc = sprofinc = 0`.
- Write `sage = ssemp = swages = sui = sbusinc = 0` when `mstat == 1`.
- Write `childcare = 0` when no dependent is under 13.
- Fix the old units bug: `psemp`/`ssemp` must be in dollars
  (thousands times 1000), like the other income amounts.
- In sets b and c, make each of `psemp`, `ssemp`, `pbusinc`,
  `sbusinc`, and `scorp` nonzero for only a fraction (25%) of units,
  so that those sets include units with incomes low enough to get
  the income-tested credits.


Output variables
----------------

PE emits 41 columns at `idtl=2` (Phase 0 log).  The table below maps
each federal column to a Tax-Calculator expression that `run_tc.py`
computes from the `--dumpdb` output.  "Compare" says whether `compare.py`
checks the variable (tolerance $1 unless noted).

Tax-Calculator facts that the expressions rely on:
`soi_iitax` is false under current law, so `iitax` excludes, and
`payrolltax` includes, the self-employment tax `setax` and the
Additional Medicare Tax `ptax_amc`; `payrolltax = ptax_was + setax +
ptax_amc` (no `e09800` in these samples).

| TAXSIM | PE variable | Tax-Calculator expression | Compare | Notes |
|---|---|---|---|---|
| `taxsimid` | id | `RECID` | key | |
| `year` | year | `FLPDYR` | key | |
| `fiitax` | `income_tax` (incl. NIIT; excl. Additional Medicare Tax and SECA) | `iitax` | yes | includes refundable credits, incl. the 2021 RRC |
| `fica` | `taxsim_fica`: employee + employer OASDI and HI, SECA, Additional Medicare Tax | `payrolltax` | yes | |
| `tfica` | `taxsim_tfica`: employee OASDI and HI, Additional Medicare Tax, full SECA | `payrolltax - ptax_er_p - ptax_er_s` | yes | |
| `v29` | same as `tfica` | same as `tfica` | no | duplicate of `tfica` |
| `addmed` | `additional_medicare_tax` | `ptax_amc` | yes | |
| `v44` | `employee_medicare_tax + additional_medicare_tax` | `FICA_mc_trt_employee * e00200 + ptax_amc` | yes | rate taken from the `Policy` object for the year (0.0145 in 2021-2025) |
| `v10` | `adjusted_gross_income` | `c00100` | yes | |
| `v11` | `tax_unit_taxable_unemployment_compensation` | `e02300` | yes | no UI exclusion after 2020 (`UI_em = 0`) |
| `v12` | `tax_unit_taxable_social_security` | `c02500` | yes | |
| `v13` | `standard_deduction` (reported whether or not the unit itemizes) | `standard` | only where TC does not itemize (`c04470 == 0`) | TC zeroes `standard` for itemizers; an itemizing-choice difference shows up in `v18` |
| `v14` | `exemptions` | `c04600` | yes | zero in 2021-2025 in both models |
| `v17` | `itemized_taxable_income_deductions` (reported whether or not the unit itemizes) | `c04470` | only where TC itemizes (`standard == 0`) | TC zeroes `c04470` for non-itemizers |
| `qbid` | `qualified_business_income_deduction` | `qbided` | yes | `otherprop` is not QBI in either model (decision D1) |
| `v18` | `taxable_income` | `c04800` | yes | includes the 2025 senior deduction in both models |
| `v19` | `income_tax_main_rates`: ordinary rates on taxable income less adjusted net capital gain | `c05200` | only where `dwks10 == 0` (`run_tc.py` writes `dwks10` as column `tc_dwks10`) | when there is no preferential income both equal the Schedule X/Y/Z tax on all taxable income; otherwise TC has no matching output, and `v28` is the meaningful check |
| `v28` | `income_tax_main_rates + capital_gains_tax`: regular tax before credits, excl. AMT | `taxbc` | yes | |
| `v26` | `amt_income` | `c62100` | yes | |
| `v27` | `alternative_minimum_tax` (excess over regular tax) | `c09600` | yes | |
| `niit` | `net_investment_income_tax` | `niit` | yes | |
| `v22` | 2022-2025: `min(ctc, ctc_limiting_tax_liability)`, where PE's `ctc` includes the $500 credit for other dependents; 2021: `ctc_value = min(ctc, limiting tax + refundable_ctc)` | 2022-2025: `c07220 + odc`; 2021: `c07220 + odc + ctc_new` | yes | TC models the 2021 ARPA increase as `ctc_new`; see watch item W1 |
| `actc` | `refundable_ctc` | 2022-2025: `c11070`; 2021: `c07220 + ctc_new` | yes | in 2021 TC's `c11070` is 0 because the whole CTC is refundable |
| `v24` | `cdcc` (2021: full refundable credit; otherwise capped at tax) | `c07180 + CDCC_refund` | yes | |
| `v25` | `eitc` | `eitc` | yes | requires full take-up in TC; see `pe_emulation.json` below |
| `cares` | `recovery_rebate_credit` | `recovery_rebate_credit` | yes | nonzero only in 2021 |
| `frate` | `income_tax` change from a $100 wage increase split by wage shares | (none) | no | TC's CLI `mtr_itax` uses a $0.01 increase in `e00200p` only; the methods differ, so `frate` is excluded (could be revisited with a custom TC computation) |

### Excluded PE columns

| TAXSIM | Reason |
|---|---|
| `siitax`, `srate`, `srebate`, `v32`, `v34`-`v40` | state items; always 0 with `state=0` |
| `v42`, `v43` | mapped to `na_pe`, so always 0 |
| `v29` | duplicate of `tfica` |
| `frate` | different marginal-rate methods (see above) |

`v15`, `v16`, `v20`, `v21`, and `v23` are marked unimplemented in PE
and are not emitted.  The old pipeline's `v15`/`v16`/`v20`/`v21`
placeholders (`phased_out_pe`, `c21040`, zeros) are dropped.

### Year-specific notes

- **2021 (ARPA)**: CTC fully refundable, age-17 children qualify,
  $3,600/$3,000 per child with the increase phased out from
  $75,000 (single), $112,500 (head of household), and $150,000
  (joint) (TC: `CTC_include17`, `CTC_is_refundable`, and the
  `CTC_new_*` parameters); CDCC refundable (TC: `CDCC_refundable`);
  childless EITC ages 19 and up with no upper limit (TC:
  `EITC_MinEligAge = 19`, `EITC_MaxEligAge = 125`); RRC of $1,400 per
  person including every dependent (TC: `RRC_c * XTOT`).
- **2025 (OBBBA)**: CTC $2,200; senior deduction of $6,000 per
  person 65+ phased out above $75,000/$150,000 (TC: `SeniorDed_*`,
  output `senior_deduction`, part of `c04800`); SALT cap raised to
  $40,000 with an income phase-down.  The tips, overtime, and car-loan
  interest deductions have no TAXSIM input and are zero in both models.


`pe_emulation.json` contents
----------------------------

The three entries carried over from the TAXSIM-35 emulation are
dropped:

| Old entry | Why it is dropped |
|---|---|
| `AMT_child_em_c_age: 24` | PE's age limit is 19, not 24 |
| `EITC_excess_InvestIncome_rt: 1.0` | PE applies the statutory investment-income cliff (`eitc_investment_income_eligible`), as TC does by default |
| `AlimonyReceived_frac_in_AGI: 1.0` | `nonprop` is ignored by PE and always 0 in the samples |

Two new entries were adopted (2026-10-07), because PE computes credit
entitlement with full take-up (`takes_up_eitc` defaults to True),
whereas TC's default `eitc_claim_prob_scale = 1.03` (minimum
probability 0.4) and `actc_claim_prob_scale = 1.1` (minimum 0.0)
randomly zero some EITC and ACTC amounts using `credit_claim_urn`.

```
"eitc_claim_prob_scale": {"2013": 9e99},
"actc_claim_prob_scale": {"2013": 9e99}
```

A third entry, `AMT_child_em_c_age: 19`, was adopted and then dropped
(2026-10-07): PE applies the IRC section 59(j) kiddie-AMT exemption
limit (`amt_kiddie_tax_applies`) to non-student filers younger than 19
(the section 152(c)(3) non-student age limit), and TC's current-law
value of `AMT_child_em_c_age` was corrected on master from 18 to 19,
so no emulation is needed.  PE also applies the limit to a joint return
when both spouses are under 19; TC no longer does (bug B3, fixed on
master 2026-10-09), because section 1(g)(2)(C) excludes a child who
files a joint return.  This is a PE bug, so it is not emulated (see
`Differences_Explained.md`).


Open decisions and watch items
------------------------------

- **D1 (decided 2026-10-07): rental income in QBI.**  `otherprop` is
  written only to `e02000`, not to `e27200`, because the PE-taxsim
  runner forces `rental_income_would_be_qualified` to False (an
  earlier draft of this document wrongly said PE counts it as QBI).
- **W1 (confirmed 2026-10-07 as a TC bug): 2021 credit for other
  dependents.**  TC sets `ODC_is_refundable = true` for 2021, but
  under ARPA only the child credit became refundable; PE keeps the
  $500 credit nonrefundable in 2021.  The a21 data confirm it (see
  `Differences_Explained.md`); it is to be fixed on a branch off
  `master`, together with a second 2021 TC bug (the uncapped ARPA
  phase-out in `CTC_new`).
- **W2 (resolved 2026-10-07): QBI reduction for SECA.**  PE, like TC,
  reduces QBI by the deductible part of self-employment tax
  (`qbi.deduction_definition` includes `self_employment_tax_ald_person`).
