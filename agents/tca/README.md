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

The question you pose to TCA is called a prompt.

Here are a couple of prompt examples that are used in the testing of TCA.

**Prompt 1:**

```
Estimate the aggregate ten-year tax revenue effects of a reform that
raises in 2026 the maximum earned income tax credit for childless tax
filing units by $300, leaving the EITC amount unchanged for those with
children, using CPS input data.
```

Response:

```
⏺ Reform: EITC_c (max EITC), KIDS=0 (childless filers), 2026:
          $664 → $964 (+$300), indexed thereafter; children-based
          amounts (KIDS=1,2,3) unchanged.
          Run 4 created (cps.csv, current-law baseline, 2026–2035).
          Executing now.

⏺ Ten-Year Revenue Estimate (2026–2035): EITC Expansion for Childless Filers

  Reform: Increase the maximum EITC by $300 for childless tax filing units
          (KIDS=0: $664 → $964 in 2026, indexed for inflation thereafter);
          EITC amounts for filers with children are unchanged.
          CPS input data, current-law baseline.

  ┌─────────────────────────────┬──────────┬──────────┬────────────┐
  │                             │ Baseline │  Reform  │ Difference │
  ├─────────────────────────────┼──────────┼──────────┼────────────┤
  │ Income tax ($B, 2026–2035)  │ 25,221.0 │ 25,210.2 │      -10.8 │
  ├─────────────────────────────┼──────────┼──────────┼────────────┤
  │ Payroll tax ($B, 2026–2035) │ 21,114.5 │ 21,114.5 │        0.0 │
  └─────────────────────────────┴──────────┴──────────┴────────────┘

  The reform reduces cumulative income tax revenue by about $10.8 billion
  over 2026–2035 (a 0.04% decrease), with no effect on payroll tax revenue
  since it only changes an income tax credit.
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
⏺ Reform confirmed:
  - EITC_c (max EITC), KIDS=0 (childless): $664 → $964 (+$300), effective 2026
  - STD (standard deduction), all MARS statuses reduced by 0.25%, effective 2026:
    Single $16,100→$16,060, MFJ $32,200→$32,120, MFS $16,100→$16,060,
    HOH $24,150→$24,090, Widow $32,200→$32,120

⏺ Run created (run_id=3). Executing it now.

⏺ Run finished with no errors. Now checking the dumpdb schema for run 3,
  year 2026 to write the tabulation SQL.

⏺ Distributional Effects: 2026 Compound Reform (Run 3)

  Reform: EITC max credit for childless filers +$300 (KIDS=0: $664→$964);
  standard deduction reduced 0.25% for all filing statuses (rounded to nearest dollar).
  CPS data, tax year 2026.

  ┌───────────────────────┬───────────────┬───────────────────┬──────────────────┐
  │ Baseline Income Group │ Tax Units (M) │ Δ Income Tax ($B) │ Δ Income Tax (%) │
  ├───────────────────────┼───────────────┼───────────────────┼──────────────────┤
  │ Under $100K           │        147.47 │            -0.647 │          -0.759% │
  ├───────────────────────┼───────────────┼───────────────────┼──────────────────┤
  │ $100K – $250K         │         57.64 │            +0.396 │          +0.071% │
  ├───────────────────────┼───────────────┼───────────────────┼──────────────────┤
  │ $250K – $500K         │         11.82 │            +0.079 │          +0.015% │
  ├───────────────────────┼───────────────┼───────────────────┼──────────────────┤
  │ $500K – $1M           │          2.28 │            +0.015 │          +0.005% │
  ├───────────────────────┼───────────────┼───────────────────┼──────────────────┤
  │ Over $1M              │          0.93 │            +0.017 │          +0.003% │
  ├───────────────────────┼───────────────┼───────────────────┼──────────────────┤
  │ ALL                   │        220.13 │            -0.139 │          -0.007% │
  └───────────────────────┴───────────────┴───────────────────┴──────────────────┘

  The EITC expansion cuts taxes for lower-income (mostly under-$100K) filers,
  while the smaller standard deduction raises taxes slightly across all
  groups — net effect: a modest $0.14B income tax cut, concentrated below $100K.
```

And the SQL looks like this (although different TCA runs might use
somewhat different SQL code):

```
  WITH joined AS (
    SELECT b.RECID, b.s006, b.expanded_income, bl.iitax AS iitax_base, rf.iitax AS iitax_reform
    FROM base b
    JOIN baseline bl ON b.RECID = bl.RECID
    JOIN reform rf ON b.RECID = rf.RECID
  ),
  grouped AS (
    SELECT
      CASE
        WHEN expanded_income < 100000 THEN '1_Under $100K'
        WHEN expanded_income < 250000 THEN '2_$100K-$250K'
        WHEN expanded_income < 500000 THEN '3_$250K-$500K'
        WHEN expanded_income < 1000000 THEN '4_$500K-$1M'
        ELSE '5_Over $1M'
      END AS income_group,
      s006, iitax_base, iitax_reform
    FROM joined
  ) 
  SELECT income_group,
         SUM(s006)/1e6 AS tax_units_millions,
         SUM(s006*(iitax_reform-iitax_base))/1e9 AS revenue_change_billions,
         100.0*SUM(s006*(iitax_reform-iitax_base))/SUM(s006*iitax_base) AS pct_change
  FROM grouped
  GROUP BY income_group
  UNION ALL
  SELECT 'ALL', SUM(s006)/1e6,
         SUM(s006*(iitax_reform-iitax_base))/1e9,
         100.0*SUM(s006*(iitax_reform-iitax_base))/SUM(s006*iitax_base)
  FROM grouped
  ORDER BY income_group
```

