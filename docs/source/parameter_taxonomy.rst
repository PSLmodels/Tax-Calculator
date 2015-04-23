Parameter taxonomy
===================

Parameter names have two fixed components; the first component is the tax category abbreviation and the second is the abbreviation for the function of the parameter’s value. In some cases, parameter names have a subcomponent that conveys additional information about the parameter.

Tax categories
---------------

Tax categories are uppercase:

   **ACTC**: Additional Child Tax Credit
   **AMED**: Additional Medicare
   **AMT**: Alternative Minimum Tax
   **CG**: Capital Gain
   **CTC**: Child Tax Credit
   **EITC**: Earned Income Tax Credit
   **ETC**: Education Tax Credit
   **FEI**: Foreign Earned Income
   **FICA**: Federal Income Contributions Act
   **ID**: Itemized Deduction
   **II**: Individual Income (Including personal exemptions and tax brackets)
   **MED**: Medicare
   **SS**: Social Security
   **STD**: Standard Deduction

Functions of the parameter’s value
-----------------------------------

Functions of the parameter’s value are lowercase:

   **c**: ceiling
   **ec**: exclusion
   **em**: exemption
   **f**: floor
   **p**: phaseout
   **rt**: rate
   **t**: tax
   **thd**: threshold

Combine functions to create additional functions: frt = floor rate.

Examples
---------

* Without a subcomponent:

   **_AMT_em**:	Alternative Minimum Tax exemption amount

   **_ID_ps**:	Itemized Deduction phaseout Adjusted Gross Income start (Pease)

   **_AMT_tthd**:	Alternative Minimum Tax surtax threshold

* With a subcomponent:

   **_SS_Earnings_c**:	Maximum taxable earnings for Social Security

   **_AMT_Child_em**:	Child Alternative Minimum Tax exemption additional income base

   **_ETC_pe_Married**:	Education Tax Credit phaseout ends (Married)
   
