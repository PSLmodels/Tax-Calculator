from tax_form import TaxForm


class US4137(TaxForm):
    _DESCRIPTIVE_NAME = ('Social Security and Medicare Tax on Unreported Tip '
                         'Income')
    _EVAR_MAP = {
        'line13': 'e09800',  # Social security tax on tip income
    }
    _NUMERIC_NAME = 'Form 4137'
    _SUPPORTED_YEARS = [2013, 2014, 2015]
