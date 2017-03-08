from taxcalc.filings.forms.tax_form import TaxForm


class US8863(TaxForm):
    _DESCRIPTIVE_NAME = 'Education Credits'
    _EVAR_MAP = {
        'line4': 'e87530',  # Lifetime Learning Total Qualified Exp.s
        'line7': 'p87521',  # Tentative American Opportunity Credit
        'line30': 'P87482',  # AOC qualified expenses per student
    }
    _NUMERIC_NAME = 'Form 8863'
    _SUPPORTED_YEARS = [2013, 2014, 2015]
