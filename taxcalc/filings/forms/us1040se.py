from .tax_form import TaxForm
from taxcalc.utils import string_to_number


class US1040SE(TaxForm):
    _DESCRIPTIVE_NAME = 'Supplemental Income and Loss'
    _EVAR_MAP = {
        'line32': 'e26270',  # Combined partnership and S corp net income/loss
        'line40': 'e27200',  # Farm rent net income or loss
    }
    _NUMERIC_NAME = 'Form 1040 Schedule E'
    _SUPPORTED_YEARS = [2013, 2014, 2015]

    def to_evars_indirect(self):
        results = {}
        fields = self._fields

        # p25470 - Royalty depletion
        p25470_fields = ['line18a', 'line18b', 'line18c']
        if any(key in fields for key in p25470_fields):
            results['p25470'] = sum(string_to_number(fields.get(key, 0))
                                    for key in p25470_fields)

        return results
