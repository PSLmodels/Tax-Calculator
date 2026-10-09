# Tax-Calculator Behavioral Responses

Documentation of the `taxcalc.behresp` module.

## employer_ptax_on_wages

```python
def employer_ptax_on_wages(ss_rate, mc_rate, cap, thd, gross_ws)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/behresp.py#L61)

```text
Returns array of employer payroll tax liability on the specified
array of one earner's gross wages (wages plus employer pension
contributions), where ss_rate and mc_rate are the employer OASDI and
HI payroll tax rates, cap is the SS_Earnings_c value, and thd is the
SS_Earnings_thd value.  Liability is increasing in gross wages and is
piecewise linear with breakpoints at cap and thd.

Note: this restates the ptax_er_p and ptax_er_s logic in the
EI_PayrollTax function, which cannot be read from those output
variables by the response function because it needs liability at
trial wages that neither Calculator object has computed.  The two
statements of the rule must be kept in agreement; see the response
function docstring.
```

## bisect

```python
def bisect(residual, low, high, steps=ESF_BISECTION_STEPS)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/behresp.py#L82)

```text
Returns array containing the zero of the specified residual function
on each of the brackets given by the low and high arrays, which must
contain the zero: the residual must be increasing, nonpositive at
low, and nonnegative at high.  Each of the specified number of steps
halves every bracket, so the returned arrays are accurate to the
initial bracket width divided by two raised to the steps power.

Note: this function knows nothing about taxes; it is pure numerical
solution logic that operates on whatever residual function its caller
supplies.
```

## response

```python
def response(calc_1, calc_2, elasticities, dump=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/behresp.py#L103)

```text
Implements conventional analysis (that is, static reform analysis
plus partial-equilibrium behavior responses to a reform),
returning results as a tuple of Pandas DataFrame objects (df1, df2)
where df1 is extracted from a baseline-policy calc_1 copy, and df2 is
extracted from a reform-policy calc_2 copy that incorporates the
behavioral responses given by the nature of the baseline-to-reform
change in policy and elasticities in the specified behavior dictionary.

This function internally modifies a copy of the calc_2 records to
account for behavioral responses that arise from the policy reform that
involves moving from calc_1 policy to calc_2 policy.  Neither calc_1 nor
calc_2 need to have had calc_all() executed before calling the response
function.  And neither calc_1 nor calc_2 are affected by this response
function.

Parameters
----------
calc_1: Calculator object
    represents baseline policy; must be advanced to the analysis year.

calc_2: Calculator object
    represents reform policy; must be advanced to the same analysis
    year as calc_1 and must contain the same number of filing units.

elasticities: dictionary
    contains the assumed response parameters/elasticities.  Omitting a
    key:value pair implies the omitted parameter/elasticity is
    assumed to be zero.  (Note that the tc CLI --behavior option is
    stricter: a JSON behavior file must contain all the keys.)
    Here is the full dictionary content and each parameter/elasticity's
    internal name:

    be_esf = elasticities['esf']
      Earnings shift factor.
      Defined as the fraction of the reform-induced change in employer
      payroll tax liability that is shifted to wages rather than to
      nontaxable employee fringe benefits such as employer-provided
      health insurance.  The shift is sign-symmetric: an increase in
      employer payroll tax liability decreases wages and a decrease
      increases them, although the two shifts are not equal in size
      because the employer tax rate that feeds back into the shifted
      wage differs between the two reforms.  It is calculated per
      earner, and it is applied before the elasticities below are
      evaluated.
      Must be in the [0,1] range.

    be_sub = elasticities['sub']
      Substitution elasticity of taxable income.
      Defined as proportional change in taxable income divided by
      proportional change in marginal net-of-tax rate (1-MTR) on
      taxpayer earnings caused by the reform.
      Must be zero or positive.

    be_inc = elasticities['inc']
      Income elasticity of taxable income.
      Defined as dollar change in taxable income divided by dollar
      change in after-tax income caused by the reform.
      Must be zero or negative.

    be_cg = elasticities['cg']
      Semi-elasticity of long-term capital gains.
      Defined as change in logarithm of long-term capital gains
      divided by change in marginal tax rate (MTR) on long-term
      capital gains caused by the reform.
      Must be zero or negative.
      See the capital-gains note below for a discussion of
      appropriate values; be_cg is NOT the tax-rate elasticity
      usually reported in the literature.

dump: boolean
    controls the number of variables included in the two returned
    DataFrame objects.  When dump=False (its default value), the
    variables in the two returned DataFrame objects include just the
    variables in the Tax-Calculator DIST_VARIABLES list, which is
    sufficient for constructing the standard Tax-Calculator tables.
    When dump=True, the variables in the two returned DataFrame
    objects include all the Tax-Calculator input and calculated
    output variables, which is the same output as produced by the
    Tax-Calculator tc --dumpdb option except for one difference: the
    tc dump output provides two calculated variables, mtr_inctax and
    mtr_paytax, that are replaced in the dump output of this response
    function by mtr_combined, which is the sum of mtr_inctax and
    mtr_paytax.  Two cautions about the mtr_combined column: it is
    expressed in percentage points (that is, it is 100 times the
    rates returned by the Calculator.mtr method), and it contains all
    zeros when both be_sub and be_inc are zero, because in that case
    no earnings marginal tax rates are computed.

Returns
-------
(df1, df2): tuple of two Pandas DataFrame objects
    df1 contains baseline-policy results extracted from a copy of
    calc_1, and df2 contains reform-policy results, incorporating
    the behavioral responses, extracted from a copy of calc_2.
    Both have one row per filing unit, in input-data order, and
    contain the columns described in the dump argument documentation.

Notes
-----
Response equations:

  The earnings shift is computed first, and separately for the
  taxpayer and the spouse, because the OASDI cap (SS_Earnings_c) and
  the reform-only extra OASDI threshold (SS_Earnings_thd) apply per
  person rather than per filing unit, so a couple with two earners
  just below the cap and a couple with one earner well above it have
  different employer payroll tax exposure at the same filing-unit
  earnings.  Writing ptax_er(wage) for an earner's employer payroll
  tax liability on wages under reform policy as a function of that
  earner's wages, ptax_er_1 for the same earner's baseline employer
  payroll tax liability on wages, and wage2 for the earner's
  pre-shift reform wages, the shifted wage is the solution of

    wage = wage2 - be_esf * (ptax_er(wage) - ptax_er_1)

  This holds the be_esf fraction of the earner's gross compensation
  --- wages plus employer payroll tax --- fixed, and it is
  sign-symmetric: an increase in employer payroll tax liability
  lowers wages and a decrease raises them.  The remaining
  (1 - be_esf) fraction is absorbed by nontaxable fringe benefits,
  which are not represented in the input data.

  The equation is implicit in wage because ptax_er is a function of
  the wage being solved for, and it has no single closed-form
  solution because that function is piecewise linear.  Writing s0 and
  s1 for the baseline and reform employer OASDI rates, h for the
  employer HI rate, and cap for SS_Earnings_c, the two interior
  regimes are:

    wages below the cap under both policies, where the employer
    payroll tax is proportional to the wage in both its OASDI and its
    HI part, so the shift is proportional:

      wage = wage2 * (1 + be_esf * (s0 + h)) / (1 + be_esf * (s1 + h))

    wages above the cap under both policies, where the OASDI part is
    the flat amount s * cap and only the uncapped HI part varies with
    the wage, so the OASDI portion of the shift is a lump sum:

      wage = wage2 - be_esf * (s1 - s0) * cap / (1 + be_esf * h)

  In the second regime the earner's marginal wage is unchanged by an
  OASDI rate reform, so the shift is a pure income effect there,
  whereas in the first regime the marginal wage falls as well.  An
  earner whose wage cut carries them from above the cap to below it
  is in neither regime; such an earner is on the kink, where the
  wage cut shrinks their own employer OASDI liability, which in turn
  feeds back into the wage.  Because of these earners --- and of the
  band between the old and new caps under a reform to SS_Earnings_c
  itself --- the shift cannot be computed as a single average rate
  applied to all earners.  The implementation therefore solves the
  fixed-point equation numerically, by bisection on a bracket that is
  guaranteed to contain the solution, which covers all three regimes
  above without special-casing any of them.  The bracket follows from
  the residual of the equation being increasing in the wage with a
  slope of at least one, which puts the solution no farther from the
  pre-shift wage than the residual evaluated there.  The numerical
  solution logic is the module-level bisect function, which knows
  nothing about payroll taxes, and the payroll tax rule is the
  module-level employer_ptax_on_wages function, which knows nothing
  about the equation being solved; a change in the payroll tax rule
  therefore leaves the solution logic untouched.

  The ptax_er function used here is the employer payroll tax on
  wages: the employer share of the OASDI tax on wages up to the
  SS_Earnings_c cap, plus the employer share of the reform-only extra
  OASDI tax on wages above the SS_Earnings_thd threshold, plus the
  employer share of the uncapped HI tax on wages, all of them
  evaluated on gross wages, which are wages plus employer pension
  contributions.  This is exactly the rule that the EI_PayrollTax
  function applies to produce the ptax_er_p and ptax_er_s output
  variables, both of which are functions of gross wages alone; that
  is what makes an employer-payroll-tax incidence assumption
  expressible as a shift of wages.  The baseline anchor ptax_er_1 is
  therefore read from those output variables rather than recomputed.
  The reform-policy function must still be stated here, as the
  module-level employer_ptax_on_wages function, because the bisection
  evaluates it at trial wages that neither Calculator object has
  computed, which no output variable can supply; the employer payroll
  tax rules are consequently stated in this module as well as in the
  EI_PayrollTax function, and the two statements must be kept in
  agreement.  The test_behresp.py module tests that agreement
  directly.

  The substitution and income effects on taxable income are computed,
  in dollars per filing unit, as follows, where mtr1 and mtr2 are the
  baseline and reform combined (income plus payroll) marginal tax
  rates on the taxpayer's earnings (e00200p) computed with respect to
  full compensation (and not capped in any way), where c04800 is
  baseline taxable income, and where combined1 and combined2 are the
  baseline and reform combined income and payroll tax liabilities:

    sub = be_sub * (((1 - mtr2) / (1 - mtr1)) - 1) * c04800

    inc = be_inc * (combined1 - combined2)

  The long-term capital gains response is computed, in dollars per
  filing unit, as follows, where ltcg_mtr1 and ltcg_mtr2 are the
  baseline and reform income-tax marginal tax rates on long-term
  capital gains (p23250):

    new_p23250 = p23250 * exp(be_cg * (ltcg_mtr2 - ltcg_mtr1))

    ltcg_chg = new_p23250 - p23250

  Note that the substitution effect is scaled by taxable income,
  which includes long-term capital gains, so its magnitude is not
  independent of the filing unit's LTCG amount.

How responses are applied to input variables:

  The earnings shift is applied directly to the earnings variables of
  the two earners it is computed for: the taxpayer part is added to
  e00200p and the spouse part to e00200s, with e00200 incremented by
  their sum.  Nothing else is adjusted.  In particular, the pension
  contribution variables, pencon_p and pencon_s, are held fixed even
  though they are part of the employer payroll tax base, because
  nontaxable benefits are what the (1 - be_esf) fraction of the shift
  is defined to absorb.

  The shift is applied to a copy of calc_2 before the elasticities
  below are evaluated, and that copy is recalculated, so the reform
  marginal tax rates and tax liabilities that enter the substitution,
  income, and capital-gains responses are all measured at post-shift
  earnings.  The ordering matters because the shift is an accounting
  adjustment that defines the reform being analyzed --- it holds gross
  compensation fixed --- rather than a behavioral response to it, so
  the elasticity-driven responses are layered on top of it.  There is
  no double counting of the employer payroll tax: the substitution
  effect prices earnings using marginal tax rates computed with
  respect to full compensation, which is a different concept from the
  wage shift itself.

  The sum of the substitution and income effects is a change in
  taxable income that must be mapped back onto the input variables
  used in the tax calculation.  The dollar change is allocated in
  proportion to three components --- wage and salary income (e00200),
  other AGI (c00100 minus e00200), and itemized deductions --- and
  the three parts are added to these input variables:

    - the wage part is added to both e00200 and e00200p
    - the other-income part is added to e00300 (taxable interest)
    - the deduction part is added to e19200 (interest paid deduction)

  Two consequences are worth noting.  First, the spouse's earnings
  variable, e00200s, is not adjusted by this part of the response,
  so the substitution and income effects adjust e00200 and e00200p by
  the same amount.  (The earnings shift, in contrast, is calculated
  per earner and does adjust e00200s.)  Second, a
  response shows up in dump output as changes in e00300 and e19200 even
  for filing units whose actual behavior would involve other income or
  deduction items.  The capital-gains response, by contrast, is applied
  directly to p23250.

  The denominator used to form the three allocation shares, called
  alloc_base in the code, is AGI minus itemized deductions, where
  itemized deductions (c04470) are counted only for filing units that
  actually itemize (that is, only when c04470 is no less than the
  standard deduction).  This is NOT an approximation of taxable
  income, and it must not be replaced by the calculated taxable
  income variable, c04800.  Because other AGI is defined as AGI minus
  wages, the three components sum to alloc_base by construction, so
  the three shares sum to one and the allocated parts sum to the
  intended dollar change.  Dividing by any other quantity --- c04800
  included --- would scale the delivered change by the ratio of
  alloc_base to that quantity.  Taxable income is used where taxable
  income is the concept called for: c04800 scales the substitution
  effect, as described in the response equations above.

  The mapping does assume that a dollar added to e00200, e00300, or
  e19200 moves taxable income by a dollar.  That is exact for a
  filing unit in the interior of the rate schedule, but not for one
  whose AGI change also moves an AGI-linked provision (taxable Social
  Security benefits, phase-outs such as the EITC, the qualified
  business income deduction, or the itemized deduction limitation).
  The realized change in aggregate taxable income therefore differs
  somewhat from the intended change: for a top-bracket rate reform
  applied to CPS data for 2026, with be_sub of 0.25 and be_inc of
  -0.1, the realized change exceeded the intended change by about
  four percent, with under one percent of responding filing units
  differing by more than ten dollars.

Filing units excluded from the response:

  The earnings shift is skipped entirely when be_esf is zero or when
  the reform alters none of the four parameters of the employer
  payroll tax on wages: the four ESF_PARAMS parameters, which are
  FICA_ss_trt_employer, FICA_mc_trt_employer, SS_Earnings_c, and
  SS_Earnings_thd.  Those four are the only parameters that the
  employer payroll tax on wages depends on; in particular the
  employee-share rates are not among them.  That test is on the
  parameters themselves rather than on calculated tax amounts, so it
  is exact for the documented use of this function, in which calc_1
  and calc_2 differ only in policy.  A caller that passes two
  Calculator objects containing different input data would get no
  earnings shift when the two policies are the same, even though the
  two employer payroll tax liabilities would differ.

  Within a reform that does change one of the four parameters, the
  shift is applied only to earners with positive wages.  That
  excludes the self-employed, who have no employer to shift a payroll
  tax to.  It also excludes an earner whose gross wages are entirely
  employer pension contributions: such an earner does generate an
  employer payroll tax liability, but has no wages to shift it onto,
  and shifting it onto an e00200p or e00200s of zero would make that
  variable negative.  Note that the employer payroll tax used for an
  included earner is nevertheless computed on gross wages, so it
  includes the part generated by that earner's pension
  contributions.

  The shifted wage is floored at zero.  The shift is bounded by
  be_esf times the employer payroll tax rate times the gross wage,
  so under any plausible reform it is a small fraction of the wage
  and the floor never binds, but a reform that sets an extreme
  employer rate, or an earner whose gross wages are mostly pension
  contributions, could otherwise drive a wage negative.  Where the
  floor does bind, the earner's gross compensation is not held
  fixed, because there is not enough wage income to absorb the
  be_esf fraction of the employer payroll tax change.

  The substitution and income effects are applied only to filing
  units with positive alloc_base; all other filing units are assumed
  to have no ordinary-income response.  That condition is a guard on
  the allocation arithmetic rather than an economic screen: it keeps
  the denominator away from zero and prevents the negative shares
  that a negative alloc_base would produce.  It excludes no filing
  unit that has positive taxable income, because c04800 is positive
  only when alloc_base is positive.  Note that the converse does not
  hold: a filing unit with positive alloc_base and zero taxable
  income does respond, which is intended, because such a unit can
  still owe payroll tax and therefore can still have an income
  effect.  For that reason the condition must not be tightened to
  require positive c04800.  Within the responding group, filing
  units that do not itemize receive no change in e19200.  Aside from
  this positive alloc_base condition, the response function applies
  no adhoc limits: earnings marginal tax rates are used exactly as
  computed, with no cap, so a marginal tax rate at or above one
  generates a zero or negative baseline net-of-tax rate and hence an
  extreme substitution effect for that filing unit.  Likewise, there
  is no limit on the capital-gains response, whose exponential form
  can generate large proportional changes when the change in the
  capital-gains marginal tax rate is large.

What is not modeled:

  Each analysis year is handled independently: this function contains
  no logic that carries a response in one year over into another
  year, so retiming behavior --- most notably the realization timing
  of capital gains --- is not modeled.  There are no response margins
  for the spouse's earnings, for short-term capital gains, for
  deduction items other than the mechanical e19200 adjustment
  described above, or for any margin not represented by the
  elasticities.  The earnings shift assumes full backward shifting of
  the be_esf fraction onto the individual earner who generated the
  employer payroll tax liability, so it models neither shifting across
  workers within an employer nor any forward shifting to consumers or
  to capital.  Being a partial-equilibrium calculation, the
  analysis holds constant all prices, wages, and macroeconomic
  aggregates.

Note: the use here of a dollar-change income elasticity (rather than
  a proportional-change elasticity) is consistent with Feldstein and
  Feenberg, "The Taxation of Two Earner Families", NBER Working Paper
  No. 5155 (June 1995).  A proportional-change elasticity was used by
  Gruber and Saez, "The elasticity of taxable income: evidence and
  implications", Journal of Public Economics 84:1-32 (2002) [see
  equation 2 on page 10].

Note: the nature of the capital-gains elasticity used here is similar
  to that used in Joint Committee on Taxation, "New Evidence on the
  Tax Elasticity of Capital Gains: A Joint Working Paper of the Staff
  of the Joint Committee on Taxation and the Congressional Budget
  Office", (JCX-56-12), June 2012.  In particular, the elasticity
  use here is equivalent to the term inside the square brackets on
  the right-hand side of equation (4) on page 11 --- not the epsilon
  variable on the left-hand side of equation (4), which is equal to
  the elasticity used here times the weighted average marginal tax
  rate on long-term capital gains.  So, the JCT-CBO estimate of
  -0.792 for the epsilon elasticity (see JCT-CBO, Table 5) translates
  into a much larger absolute value for the be_cg semi-elasticity
  used by Tax-Calculator.
  To calculate the elasticity from a semi-elasticity, we multiply by
  MTRs from T-C and weight by shares of taxable gains. To avoid those
  with zero MTRs, we restrict this to the top 40% of tax units by AGI.
  Using this function, a semi-elasticity of -3.45 corresponds to a tax
  rate elasticity of -0.792.
  Specifying be_cg equal to a published tax-rate elasticity such as
  -0.792 is therefore a common mistake that generates a much smaller
  capital-gains response than intended.
```

## pch_response

```python
def pch_response(elasticity=np.zeros(1), val1=np.zeros(1), val2=np.zeros(1))
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/behresp.py#L737)

```text
Calculate the percentage change response, given an elasticity and
original/new values. Can be used to calculate substitution or
income effects.

This is a helper function for the quantity_response function; it is
not part of the public API of this module (it is not in __all__) and
it is not used by the response function.

A val1 element equal to zero implies an undefined proportional
change, so this function returns a zero response for such elements
rather than generating a divide-by-zero warning.

Parameters
----------
elasticity: value or numpy array representing elasticity(ies).
    Defaults to zero.

val1: value or numpy array representing original value(s).
    Defaults to zero.

val2: value or numpy array representing new value(s).
    Defaults to zero.

Returns
-------
pch_response: numpy array
    Percentage change in the response, calculated essentially as:
    elasticity * (val2 / val1 - 1).
```

## quantity_response

```python
def quantity_response(quantity=np.array([1]), price_elasticity=np.zeros(1), aftertax_price1=np.zeros(1), aftertax_price2=np.zeros(1), income_elasticity=np.zeros(1), aftertax_income1=np.zeros(1), aftertax_income2=np.zeros(1))
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/behresp.py#L775)

```text
Calculate dollar change in quantity using a log-log response equation,
which assumes that the proportional change in the quantity is equal to
the sum of two terms:

(1) the proportional change in the quantity's marginal aftertax price
    times an assumed price elasticity, and

(2) the proportional change in aftertax income
    times an assumed income elasticity.

Not all inputs are required, so it's possible to calculate only the price
or income effects by providing a subset of arguments. Accepts arrays.

Parameters
----------
quantity: numpy array
    pre-response quantity whose response is being calculated.
    Defaults to 1.

price_elasticity: float
    coefficient of the percentage change in aftertax price of
    the quantity in the log-log response equation. Defaults to 0.

aftertax_price1: numpy array
    marginal aftertax price of the quantity under baseline policy.

    Note that this function forces prices to be in [0.01, inf] range,
    but the caller of this function may want to constrain negative
    or very small prices to be somewhat larger in order to avoid extreme
    proportional changes in price. Defaults to 0.

    Note this is NOT an array of marginal tax rates (MTR), but rather
    usually 1-MTR (or in the case of quantities, like charitable
    giving, whose MTR values are non-positive, 1+MTR).

aftertax_price2: numpy array
    marginal aftertax price of the quantity under reform policy.

    Note that this function forces prices to be in [0.01, inf] range,
    but the caller of this function may want to constrain negative
    or very small prices to be somewhat larger in order to avoid extreme
    proportional changes in price. Defaults to 0.

    Note this is NOT an array of marginal tax rates (MTR), but rather
    usually 1-MTR (or in the case of quantities, like charitable
    giving, whose MTR values are non-positive, 1+MTR).

income_elasticity: float
    coefficient of the percentage change in aftertax income in the
    log-log response equation. Defaults to 0.

aftertax_income1: numpy array
    aftertax income under baseline policy.

    Note that this function forces income to be in [1, inf] range,
    but the caller of this function may want to constrain negative
    or small incomes to be somewhat larger in order to avoid extreme
    proportional changes in aftertax income. Defaults to 0.

aftertax_income2: numpy array
    aftertax income under reform policy.

    Note that this function forces income to be in [1, inf] range,
    but the caller of this function may want to constrain negative
    or small incomes to be somewhat larger in order to avoid extreme
    proportional changes in aftertax income. Defaults to 0.

Returns
-------
response: numpy array
    dollar change in quantity calculated from log-log response equation
```

## labor_response

```python
def labor_response(earnings=np.array([1]), substitution_eti=np.zeros(1), mtr1=np.zeros(1), mtr2=np.zeros(1), income_elasticity=np.zeros(1), aftertax_income1=np.zeros(1), aftertax_income2=np.zeros(1))
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/behresp.py#L867)

```text
Calculate labor response given earnings, substitution elasticity of taxable
income, initial and new marginal tax rates, income elasticity, and initial
and new after-tax income. Accepts arrays.

Parameters
----------
earnings: numpy array
    pre-response earnings whose response is being calculated.
    Defaults to 1.

substitution_eti: float or numpy array
    coefficient of the substitution elasticity of taxable income.
    Defaults to 0.

mtr1: numpy array
    marginal tax rate of earnings under baseline policy.

    Note that this function forces MTRs to be in [-inf, 0.99] range,
    but the caller of this function may want to constrain large MTRs
    to be somewhat smaller in order to avoid extreme
    proportional changes in earnings. Defaults to 0.

mtr2: numpy array
    marginal tax rate of earnings under reform policy.

    Note that this function forces MTRs to be in [-inf, 0.99] range,
    but the caller of this function may want to constrain large MTRs
    to be somewhat smaller in order to avoid extreme
    proportional changes in earnings. Defaults to 0.

income_elasticity: float
    coefficient of the percentage change in aftertax income in the
    log-log response equation. Defaults to 0.

aftertax_income1: numpy array
    aftertax income under baseline policy.

    Note that this function forces income to be in [1, inf] range,
    but the caller of this function may want to constrain negative
    or small incomes to be somewhat larger in order to avoid extreme
    proportional changes in aftertax income. Defaults to 0.

aftertax_income2: numpy array
    aftertax income under reform policy.

    Note that this function forces income to be in [1, inf] range,
    but the caller of this function may want to constrain negative
    or small incomes to be somewhat larger in order to avoid extreme
    proportional changes in aftertax income. Defaults to 0.

Returns
-------
response: numpy array
    dollar change in earnings calculated from log-log response equation
```
