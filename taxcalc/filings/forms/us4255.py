from .tax_form import TaxForm


class US4255(TaxForm):
    _DESCRIPTIVE_NAME = 'Recapture of Investment Credit'
    _EVAR_MAP = {
        'line15': 'e09700',  # Recapture tax
    }
    _NUMERIC_NAME = 'Form 4255'
    _SUPPORTED_YEARS = [2012, 2013, 2014, 2015]  # Last revision 2012
