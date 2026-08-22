# Tax-Calculator Assistant, TCA

TCA is an AI agent that enables conversational use of Tax-Calculator's CLI.

A useful question to ask TCA at first-use is: What can you do?

For additional TCA prompts, see the Examples section below.

TCA currently requires Claude Code and an Anthropic subscription to its
LLMs (like Sonnet and Opus).  The cheapest Pro subscription is likely
to be sufficient for most needs.  There are plans to experiment with
using Claude Code with free LLMs, but that work is in the future.

In order to use TCA, you must be running MacOS or Linux, and have
cloned the Tax-Calculator repository.  If on Windows, you can use
Microsoft's free [Windows Subsystem for
Linux](https://learn.microsoft.com/en-us/windows/wsl/) to install the
free Ubuntu Linux operating system, within which you can clone the
Tax-Calculator repository.

TCA is used from the terminal prompt.  Every time a terminal window is
opened for TCA work, execute the "conda activate taxcalc-dev" command
in order to get access to the CLI tool, `tc`.  You can check that `tc`
is available by executing the "tc --version" command.  If the `tc`
command is not found, move to the top-level folder of the
Tax-Calculator repository code tree (the one containng `Makefile`) and
execute the "make package" command to create the `tc` command.

TCA is used in a folder **outside** the Tax-Calculator repository
tree.  If you have already installed TCA in such a TCA-work folder,
move to that TCA-work folder and execute the "./tca-exec" command.

If you have not already created such a TCA-work folder, move to the
`agents/tca` folder in the Tax-Calculator repository tree and execute
the following command (where, for illustration, we assume your new
TCA-work folder name is `~/TCA/project1` where the `~/TCA` folder
already exists):
```
(taxcalc-dev) tca> ./install.sh ~/TCA/project1
```

Then follow the instructions written to the terminal screen.

If the install test fails or you have other problems using TCA, please
raise an issue [here](https://github.com/PSLmodels/Tax-Calculator/issues).

### Examples

An assignment you give TCA is called a prompt.

Here are a couple of prompts that are used in TCA testing.  Note that
LLMs produce different response wording in each session, but the
numrical results should be the same across sessions (apart from
differences caused by bug fixes since Tax-Calculator 6.8.1 was
released).

**Prompt 1:**

```
Estimate the aggregate ten-year tax revenue effects of a reform that
raises in 2026 the maximum earned income tax credit for childless tax
filing units by $300, leaving the EITC amount unchanged for those with
children, using CPS input data.
```

Response:

```
⏺ Reform: raise childless EITC maximum by $300 (2026–2035)

  Parameter change: EITC_c (maximum EITC amount), KIDS=0 index, tax
  year 2026: $664 → $964 current law. Amounts for filers with 1, 2, or
  3+ children are unchanged.

  Aggregate 10-year revenue effect (2026–2035, $ billions):

  ┌───────────────────────┬──────────┬──────────┬────────────┐
  │          Tax          │ Baseline │  Reform  │ Difference │
  ├───────────────────────┼──────────┼──────────┼────────────┤
  │ Individual income tax │ 25,220.6 │ 25,209.8 │ -10.8      |
  ├───────────────────────┼──────────┼──────────┼────────────┤
  │ Payroll tax           │ 21,114.5 │ 21,114.5 │ 0.0        │
  └───────────────────────┴──────────┴──────────┴────────────┘

  The reform reduces individual income tax revenue by about $10.8
  billion over 10 years (a 0.04% reduction), with no effect on payroll
  tax revenue, as expected since EITC only affects income tax
  liability.
```

**Prompt 2:**

```
Create a 2026 custom table, using CPS data, showing the distributional
effects of a 2026 compound tax reform that increases the maximum EITC
for childless tax units by $300 and reduces the standard deduction
amounts for all filing units by 0.25 percent (rounding each standard
deduction value to the nearest whole dollar).
The custom table has these columns:
  * income group description
  * number of tax filing units (M) expressed in millions
  * dollar change in income tax revenue ($B) expressed in billions
  * percentage change in income tax revenue (%)
and these rows:
  * baseline income under $100K (including those with negative income)
  * baseline income between $100K and $250K
  * baseline income between $250K and $500K
  * baseline income between $500K and $1M
  * baseline income over $1M
  * ALL baseline incomes
Always show the SQL code used to produce this custom table.
```

Response: The custom table looks like this:

```
⏺ Reform (2026, CPS data)

  - EITC_c (max EITC), KIDS=0: $664 → $964 (+$300)
  - STD (standard deduction), reduced 0.25%, rounded to nearest dollar:
    - MARS=1 (single): $16,100 → $16,060
    - MARS=2 (joint): $32,200 → $32,120
    - MARS=3 (separate): $16,100 → $16,060
    - MARS=4 (head of household): $24,150 → $24,090
    - MARS=5 (widow): $32,200 → $32,120

  Custom distributional table — income tax revenue effect, 2026

  ┌───────────────────────┬──────────────────┬───────────────────┬──────────────────┐
  │ Baseline income group │ Filing units (M) │ Δ income tax ($B) │ Δ income tax (%) │
  ├───────────────────────┼──────────────────┼───────────────────┼──────────────────┤
  │ income under $100K    │           147.47 │            -0.647 │          -0.759% │
  ├───────────────────────┼──────────────────┼───────────────────┼──────────────────┤
  │ income $100K–$250K    │            57.64 │             0.396 │           0.071% │
  ├───────────────────────┼──────────────────┼───────────────────┼──────────────────┤
  │ income $250K–$500K    │            11.82 │             0.079 │           0.015% │
  ├───────────────────────┼──────────────────┼───────────────────┼──────────────────┤
  │ income $500K–$1M      │             2.28 │             0.015 │           0.005% │
  ├───────────────────────┼──────────────────┼───────────────────┼──────────────────┤
  │ income over $1M       │             0.93 │             0.017 │           0.003% │
  ├───────────────────────┼──────────────────┼───────────────────┼──────────────────┤
  │ ALL incomes           │           220.13 │            -0.139 │          -0.007% │
  └───────────────────────┴──────────────────┴───────────────────┴──────────────────┘
  
  Sub-$100K units see a net tax cut (larger EITC benefit outweighs the
  smaller standard deduction), while higher-income groups see a small
  net tax increase (reduced standard deduction only, no EITC
  eligibility).

  SQL used

  WITH joined AS (
    SELECT b.RECID,
           b.s006,
           b.expanded_income,
           bl.iitax AS iitax_base,
           rf.iitax AS iitax_reform
    FROM base b
    JOIN baseline bl ON b.RECID = bl.RECID
    JOIN reform rf ON b.RECID = rf.RECID
  ),
  grouped AS (
    SELECT
      CASE
        WHEN expanded_income < 100000 THEN 1
        WHEN expanded_income < 250000 THEN 2
        WHEN expanded_income < 500000 THEN 3
        WHEN expanded_income < 1000000 THEN 4
        ELSE 5
      END AS grp,
      s006, iitax_base, iitax_reform
    FROM joined
  ),
  summary AS (
    SELECT grp,
           SUM(s006) AS wsum,
           SUM(s006*(iitax_reform-iitax_base)) AS chg,
           SUM(s006*iitax_base) AS base_tax
    FROM grouped GROUP BY grp
    UNION ALL
    SELECT 6, SUM(s006),
           SUM(s006*(iitax_reform-iitax_base)),
           SUM(s006*iitax_base)
    FROM grouped
  )
  SELECT
    CASE grp
      WHEN 1 THEN 'Baseline income under $100K'
      WHEN 2 THEN 'Baseline income $100K-$250K'
      WHEN 3 THEN 'Baseline income $250K-$500K'
      WHEN 4 THEN 'Baseline income $500K-$1M'
      WHEN 5 THEN 'Baseline income over $1M'
      WHEN 6 THEN 'ALL baseline incomes'
    END AS income_group_description,
    wsum/1e6 AS num_filing_units_M,
    chg/1e9 AS iitax_change_B,
    100.0*chg/base_tax AS iitax_pct_change
  FROM summary
  ORDER BY grp;

  (Run against run4-26.dumpdb; base holds RECID/s006/expanded_income,
  baseline/reform hold each RECID's iitax under the two policies.)
```
