Parameter Naming and Placing Conventions
========================================

Parameter names have two components; the first component is an
abbreviation for the parameter's tax category and the second component
is an abbreviation for the role the parameter plays in those tax
category rules. In some cases, parameter names have a subcategory that
conveys additional information about the role the parameter plays (see
Examples below).

Tax Categories
--------------

Tax categories are uppercase:

   **ACTC**: Additional Child Tax Credit

   **ALD**: Above-the-line Deduction

   **AMED**: Additional Medicare

   **AMT**: Alternative Minimum Tax

   **CDCC**: Child and Dependent Care Credit

   **CG**: Capital Gain

   **CTC**: Child Tax Credit

   **EITC**: Earned Income Tax Credit

   **ETC**: Education Tax Credit

   **FEI**: Foreign Earned Income

   **FICA**: Federal Income Contributions Act

   **ID**: Itemized Deduction

   **II**: Individual Income (including personal exemptions and tax brackets)

   **KT**: Kiddie Tax

   **LLC**: Lifetime Learning Credit

   **MED**: Medicare

   **NIIT**: Net Investment Income Tax

   **SS**: Social Security

   **STD**: Standard Deduction

Parameter Role
--------------

Abbreviates for the role the parameter plays in the tax rules are
usually lowercase:

   **c**: ceiling (or use **Max** especially for integer variables)

   **e**: end

   **ec**: exclusion

   **em**: exemption

   **f**: floor (or use **Min** especially for integer variables)

   **HC**: haircut

   **p**: phaseout

   **rt**: rate (always expressed as a decimal, rather than a percentage, rate)

   **s**: start

   **t**: tax

   **thd**: threshold

Combine abbreviations to create more complex roles: frt = floor rate.

Examples
--------

   **_AMT_em**: Alternative Minimum Tax exemption amount

   **_ID_ps**: Itemized Deduction phaseout Adjusted Gross Income start (Pease)

   **_AMT_tthd**: Alternative Minimum Tax surtax threshold

   **_SS_Earnings_c**: Maximum taxable earnings for Social Security

   **_AMT_Child_em**: Child Alternative Minimum Tax exemption
   additional income base

   **_ETC_pe_Married**: Education Tax Credit phaseout ends (Married)

   **_EITC_MinEligAge**: Earned Income Tax Credit minimum eligibility
   age for those with no EITC-eligible children

Placing New Parameters in ``current_law_policy.json``
-----------------------------------------------------

All new parameters should be added to the ``current_law_policy.json``
file in a location that maintains the convention that the policy
parameters appear in that file in the order they are first used in the
``functions.py`` file.
