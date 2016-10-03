from .tax_form import TaxForm


class US5695(TaxForm):
    _DESCRIPTIVE_NAME = 'Residential Energy Credits'
    _EVAR_MAP = {
        'line15': 'e07260',  # Residential Energy Credit
    }
    _NUMERIC_NAME = 'Form 5695'
    _SUPPORTED_YEARS = [2013, 2014, 2015]
