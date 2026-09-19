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
If you get a startup error saying the previously installed TCA is
not up to date with your Tax-Calculator version, then re-install
TCA into the existing TCA-work folder as described in the next
paragraph.

If you have not already created such a TCA-work folder, move to the
`agents/tca` folder in the Tax-Calculator repository tree and execute
the following command (where, for illustration, we assume your new
TCA-work folder name is `~/TCA/project1`):
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
numerical results should be the same across sessions (apart from
differences caused by bug fixes since the Tax-Calculator 6.8.3 version,
which was used in these examples).

**Prompt 1:**

```
Estimate the aggregate ten-year tax revenue effects of a reform that
raises in 2026 the maximum earned income tax credit for childless tax
filing units by $300, leaving the EITC amount unchanged for those with
children, using CPS input data.
```

Response:

```
⏺ Current-law EITC_c for childless filers (KIDS=0) in 2026 is $664; raising it
  by $300 gives $964. Creating the 10-year run now.

⏺ Aggregate revenue effect, 2026–2035 (run 3)

  Reform: raise the maximum EITC for childless filers from $664 to $964 in 2026
  (a $300 increase), leaving EITC amounts for filers with children unchanged.
  Input: CPS.

  ┌────────────────────┬─────────────────┬─────────────────┬───────────────┐
  │        Tax         │    Baseline     │     Reform      │  Difference   │
  ├────────────────────┼─────────────────┼─────────────────┼───────────────┤
  │ Individual income  │ $25,220.6       │ $25,209.8       │ -$10.8        │
  │ tax                │ billion         │ billion         │ billion       │
  ├────────────────────┼─────────────────┼─────────────────┼───────────────┤
  │ Payroll tax        │ $21,114.5       │ $21,114.5       │ $0.0 billion  │
  │                    │ billion         │ billion         │               │
  └────────────────────┴─────────────────┴─────────────────┴───────────────┘

  The reform reduces individual income tax revenue by about $10.8 billion over
  the ten years (2026–2035), a 0.04% decrease; it has no effect on payroll tax
  revenue, as expected since EITC doesn't touch payroll taxes.
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
⏺ All required variables are already in the dumpdb by default (no --dumpvars
  file needed). Creating the compound reform run now.

⏺ Run finished with no execution errors. Now checking the dumpdb schema to
  confirm column names before building the custom SQL table.

⏺ Reform

  Run 4 (2026, CPS input, custom baseline = current law): compound reform
  combining
  - EITC max credit for childless filers (EITC_c, KIDS=0): $664 → $964 (+$300)
  - Standard deduction (STD), all filing statuses, reduced 0.25% (rounded to
    nearest dollar):

  ┌───────────────────────┬─────────────┬───────────────────────────┐
  │         MARS          │ Current law │ Reform (×0.9975, rounded) │
  ├───────────────────────┼─────────────┼───────────────────────────┤
  │ 1 (single)            │ $16,100     │ $16,060                   │
  ├───────────────────────┼─────────────┼───────────────────────────┤
  │ 2 (joint)             │ $32,200     │ $32,120                   │
  ├───────────────────────┼─────────────┼───────────────────────────┤
  │ 3 (sep)               │ $16,100     │ $16,060                   │
  ├───────────────────────┼─────────────┼───────────────────────────┤
  │ 4 (head of household) │ $24,150     │ $24,090                   │
  ├───────────────────────┼─────────────┼───────────────────────────┤
  │ 5 (widow)             │ $32,200     │ $32,120                   │
  └───────────────────────┴─────────────┴───────────────────────────┘

  SQL used (run4-26.dumpdb)

  WITH t AS (
    SELECT b.RECID, b.s006, b.expanded_income,
           bl.iitax AS iitax_base, rf.iitax AS iitax_reform
    FROM base b
    JOIN baseline bl ON b.RECID = bl.RECID
    JOIN reform rf ON b.RECID = rf.RECID
  ),
  g AS (
    SELECT *,
      CASE
        WHEN expanded_income < 100000 THEN '1: Under $100K'
        WHEN expanded_income < 250000 THEN '2: $100K-$250K'
        WHEN expanded_income < 500000 THEN '3: $250K-$500K'
        WHEN expanded_income < 1000000 THEN '4: $500K-$1M'
        ELSE '5: Over $1M'
      END AS income_group
    FROM t
  )
  SELECT income_group,
         SUM(s006)/1e6 AS num_units_M,
         SUM(s006*(iitax_reform-iitax_base))/1e9 AS rev_change_B,
         100.0*SUM(s006*(iitax_reform-iitax_base))/SUM(s006*iitax_base) AS
  pct_change
  FROM g GROUP BY income_group
  UNION ALL
  SELECT 'ALL baseline incomes',
         SUM(s006)/1e6,
         SUM(s006*(iitax_reform-iitax_base))/1e9,
         100.0*SUM(s006*(iitax_reform-iitax_base))/SUM(s006*iitax_base)
  FROM g
  ORDER BY income_group;

  (Custom income groups were used instead of the dumpdb's built-in
  income_group_definition table, since the requested breakpoint at $100K —
  combining negative through $100K into one group — differs from the built-in
  $50K/$100K split.)

  Distributional effects, 2026 (CPS)

  ┌───────────────────────────┬──────────────┬───────────────┬──────────────┐
  │   Baseline income group   │ Filing units │ Δ Income tax  │ Δ Income tax │
  │                           │      (M)     │     ($B)      │      (%)     │
  ├───────────────────────────┼──────────────┼───────────────┼──────────────┤
  │ Under $100K (incl.        │        147.5 │         -0.65 │       -0.76% │
  │ negative income)          │              │               │              │
  ├───────────────────────────┼──────────────┼───────────────┼──────────────┤
  │ $100K – $250K             │         57.6 │          0.40 │        0.07% │
  ├───────────────────────────┼──────────────┼───────────────┼──────────────┤
  │ $250K – $500K             │         11.8 │          0.08 │        0.02% │
  ├───────────────────────────┼──────────────┼───────────────┼──────────────┤
  │ $500K – $1M               │          2.3 │          0.02 │        0.01% │
  ├───────────────────────────┼──────────────┼───────────────┼──────────────┤
  │ Over $1M                  │          0.9 │          0.02 │        0.00% │
  ├───────────────────────────┼──────────────┼───────────────┼──────────────┤
  │ ALL baseline incomes      │        220.1 │         -0.14 │       -0.01% │
  └───────────────────────────┴──────────────┴───────────────┴──────────────┘

  Filers under $100K see a net income tax cut (larger EITC gain outweighs the
  smaller standard deduction), while every group above $100K sees a small net
  tax increase (the standard deduction cut dominates there, since they don't
  benefit from the childless EITC increase). The total revenue loss of $0.14
  billion matches the -$0.1 billion reported by execute_run_and_report (rounded
  to the nearest $0.1B).
```
