Policy Parameter Naming and Placing Conventions
===============================================

Policy parameter names have two components; the first component is an
abbreviation for the parameter's tax category and the second component
is an abbreviation for the role the parameter plays in those tax
category rules. In some cases, parameter names have a subcategory that
conveys additional information about the role the parameter plays (see
Examples below).

Tax Categories
--------------

Tax categories are uppercase:

   **ACTC**: Additional Child Tax Credit

   **ALD**: Above-the-Line Deduction

   **AMEDT**: Additional Medicare Tax

   **AMT**: Alternative Minimum Tax

   **CDCC**: Child and Dependent Care Credit

   **CG**: Capital Gain

   **CTC**: Child Tax Credit

   **EITC**: Earned Income Tax Credit

   **ETC**: Education Tax Credit

   **FICA**: Federal Income Contributions Act

   **ID**: Itemized Deduction

   **II**: Individual Income (including personal exemptions and tax brackets)

   **KT**: Kiddie Tax

   **LLC**: Lifetime Learning Credit

   **NIIT**: Net Investment Income Tax

   **PT**: Pass-Through Income

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

   **hc**: haircut

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

   **_AMT_brk1**: Alternative Minimum Tax first rate bracket top

   **_SS_Earnings_c**: Maximum taxable earnings for Social Security

   **_AMT_Child_em**: Child Alternative Minimum Tax exemption
   additional income base

   **_ETC_pe_Married**: Education Tax Credit phaseout ends (Married)

   **_EITC_MinEligAge**: Earned Income Tax Credit minimum eligibility
   age for those with no EITC-eligible children

Placing New Parameters in ``current_law_policy.json``
-----------------------------------------------------

All new policy parameters should be added to the
``current_law_policy.json`` file in a location that is near
conceptually similar parameters.  Be sure to specify the ``section_1``
and ``section_2`` values of each new parameter so that it appears in
an appropriate place on the TaxBrain input page.  If the new parameter
is not supposed to appear on the TaxBrain input page, set the value of
``section_1`` and ``section_2`` to an empty string.
