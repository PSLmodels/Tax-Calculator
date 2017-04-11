from taxcalc.filings.forms.tax_form import TaxForm


class US4952(TaxForm):
    _DESCRIPTIVE_NAME = 'Investment Interest Expense Deduction'
    _EVAR_MAP = {
        'line4g': 'e58990',  # Investment Income Amount
    }
    _NUMERIC_NAME = 'Form 4952'
    _SUPPORTED_YEARS = [2013, 2014, 2015]
