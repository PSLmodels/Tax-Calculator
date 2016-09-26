from .tax_form import TaxForm


class US6251(TaxForm):
    _DESCRIPTIVE_NAME = 'Alternative Minimum Tax - Individuals'
    _EVAR_MAP = {
        'line32': 'e62900',  # Alternative minimum tax foreign tax credit
    }
    _NUMERIC_NAME = 'Form 6251'
    _SUPPORTED_YEARS = [2013, 2014, 2015]
