from .base import Filing
from .us_forms import US_FORMS_BY_ID


class USFiling(Filing):
    FORM_CLASSES_BY_ID = US_FORMS_BY_ID
    FILER_ID_RVAR = 'RECID'
    FILING_YEAR_RVAR = 'FLPDYR'
    WEIGHT_RVAR = 's006'

    # e00200p - Salaries, wages, and tips for taxpayer
    # e00200s - Salaries, wages, and tips for spouse
    # combine all W2s, see if taxpayer ID is payer or spouse

    # e00900p - Business net profit/loss (Schedule C) for taxpayer
    # e00900s - Business net profit/loss (Schedule C) for spouse
    # combine all schedule C's, see if taxpayer ID is payer or spouse,
    # use its line 30

    # e02100p - Farm net profit or loss for taxpayer
    # e02100s - Farm net profit or loss for spouse
    # combine all schedule F's, see if taxpayer ID is payer or spouse,
    # use its line 34

    # n24 - Number of children eligible for Child Tax Credit
    # Sum of all Yes checkmakrs for A-D from all attached schedule 8812

    read_funcs_all_years = ()
    read_funcs_2013 = ()
    read_funcs_2014_2015 = ()

    _READ_FUNCS_BY_YEAR = {
        2013: read_funcs_all_years + read_funcs_2013,
        2014: read_funcs_all_years + read_funcs_2014_2015,
        2015: read_funcs_all_years + read_funcs_2014_2015,
    }
