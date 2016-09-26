from .tax_form import TaxForm


class US8801(TaxForm):
    _DESCRIPTIVE_NAME = ('Credit for Prior Year Minimum Tax - Individuals, '
                         'Estates, and Trusts')
    _EVAR_MAP = {
        'line25': 'e07600',  # Prior year minimum tax credit
    }
    _NUMERIC_NAME = 'Form 8801'
    _SUPPORTED_YEARS = [2013, 2014, 2015]
