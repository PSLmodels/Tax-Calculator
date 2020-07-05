Policy parameter naming and placing conventions
===============================================

Policy parameter names have two components; the first component is an
abbreviation for the parameter's tax category and the second component
is an abbreviation for the role the parameter plays in those tax
category rules. In some cases, parameter names have a subcategory that
conveys additional information about the role the parameter plays (see
Examples below).

## Tax categories

Tax categories are uppercase:

   **`ACTC`**: Additional Child Tax Credit

   **`ALD`**: Above-the-Line Deduction

   **`AMEDT`**: Additional Medicare Tax

   **`AMT`**: Alternative Minimum Tax

   **`CDCC`**: Child and Dependent Care Credit

   **`CG`**: Capital Gain

   **`CTC`**: Child Tax Credit

   **`EITC`**: Earned Income Tax Credit

   **`ETC`**: Education Tax Credit

   **`FICA`**: Federal Income Contributions Act

   **`ID`**: Itemized Deduction

   **`II`**: Individual Income (including personal exemptions and tax brackets)

   **`KT`**: Kiddie Tax

   **`LLC`**: Lifetime Learning Credit

   **`NIIT`**: Net Investment Income Tax

   **`PT`**: Pass-Through Income

   **`SS`**: Social Security

   **`STD`**: Standard Deduction

## Parameter role

Abbreviates for the role the parameter plays in the tax rules are
usually lowercase:

   **`c`**: ceiling (or use **`Max`** especially for integer variables)

   **`e`**: end

   **`ec`**: exclusion

   **`em`**: exemption

   **`f`**: floor (or use **`Min`** especially for integer variables)

   **`hc`**: haircut

   **`p`**: phaseout

   **`rt`**: rate (always expressed as a decimal, rather than a percentage, rate)

   **`s`**: start

   **`t`**: tax

   **`thd`**: threshold

Combine abbreviations to create more complex roles: frt = floor rate.

## Examples

   **`AMT_em`**: Alternative Minimum Tax exemption amount

   **`ID_ps`**: Itemized Deduction phaseout Adjusted Gross Income start (Pease)

   **`AMT_brk1`**: Alternative Minimum Tax first rate bracket top

   **`SS_Earnings_c`**: Maximum taxable earnings for Social Security

   **`AMT_child_em`**: Child Alternative Minimum Tax exemption
   additional income base

   **`ETC_pe_Married`**: Education Tax Credit phaseout ends (Married)

   **`EITC_MinEligAge`**: Earned Income Tax Credit minimum eligibility
   age for those with no EITC-eligible children

## Placing new parameters in `policy_current_law.json`

All new policy parameters should be added to the
`policy_current_law.json` file in a location that is near conceptually
similar parameters.
Be sure to specify the `section_1` and `section_2` values of each new parameter so that it appears in an appropriate place on the [Tax-Brain
webapp](https://www.compute.studio/PSLmodels/Tax-Brain/) input page.
If the new parameter is not supposed to appear on the input page of
the Tax-Brain webapp, set the value of `section_1` and `section_2` to
an empty string.