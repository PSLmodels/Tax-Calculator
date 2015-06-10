:orphan:

Parameter taxonomy
===================

Parameter names have two fixed components; the first component is the
tax category abbreviation and the second is the abbreviation for the
function of the parameter’s value. In some cases, parameter names have
a subcategory that conveys additional information about the parameter
(see examples).

Tax categories
---------------

Tax categories are uppercase:

   **ACTC**: Additional Child Tax Credit

   **ALD**: Above-the-line Deduction

   **AMED**: Additional Medicare

   **AMT**: Alternative Minimum Tax

   **CDCC**: Child and Dependent Care Credit

   **CG**: Capital Gain

   **CTC**: Child Tax Credit

   **DCC**: Dependent Care Credit

   **EITC**: Earned Income Tax Credit

   **ETC**: Education Tax Credit

   **FEI**: Foreign Earned Income

   **FICA**: Federal Income Contributions Act

   **ID**: Itemized Deduction

   **II**: Individual Income (Including personal exemptions and tax brackets)

   **KT**: Kiddie Tax

   **LLC**: Lifetime Learning Credit

   **MED**: Medicare

   **NIIT**: Net Investment Income Tax

   **SS**: Social Security

   **STD**: Standard Deduction

Functions of the parameter’s value
-----------------------------------

Functions of the parameter’s value are lowercase:

   **c**: ceiling

   **e**: end

   **ec**: exclusion

   **em**: exemption

   **f**: floor

   **HC**: haircut [1]_

   **p**: phaseout

   **rt**: rate

   **s**: start

   **t**: tax

   **thd**: threshold

Combine functions to create additional functions: frt = floor rate.

Examples
---------

   **_AMT_em**: Alternative Minimum Tax exemption amount

   **_ID_ps**: Itemized Deduction phaseout Adjusted Gross Income start (Pease)

   **_AMT_tthd**: Alternative Minimum Tax surtax threshold

   **_SS_Earnings_c**: Maximum taxable earnings for Social Security

   **_AMT_Child_em**: Child Alternative Minimum Tax exemption
   additional income base

   **_ETC_pe_Married**: Education Tax Credit phaseout ends (Married)


.. [1] Currently, the abbreviation for haircuts is uppercase in the
       Tax Calculator; we will be changing it to lowercase and will
       update this page accordingly.
