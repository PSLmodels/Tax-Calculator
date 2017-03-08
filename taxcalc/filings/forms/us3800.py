from tax_form import TaxForm


class US3800(TaxForm):
    _DESCRIPTIVE_NAME = 'General Business Credit'
    _EVAR_MAP = {
        'line17': 'e07400',  # General business credit
    }
    _NUMERIC_NAME = 'Form 3800'
    _SUPPORTED_YEARS = [2013, 2014, 2015]
