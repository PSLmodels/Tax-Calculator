from tax_form import TaxForm
from taxcalc.utils import string_to_number


class US1040SA(TaxForm):
    _DESCRIPTIVE_NAME = 'Itemized Deductions'
    _EVAR_MAP = {
        'line1': 'e17500',  # Medical and Dental Expenses
        'line6': 'e18500',  # Real estate taxes
        'line15': 'e19200',  # Total interest deduction
        'line16': 'e19800',  # Gifts to Charity by cash or check
        'line17': 'e20100',  # Gifts to Charity other than cash
        'line20': 'e20500',  # Casualty or theft losses
        'line24': 'e20400',  # Total misc deductions subject to 2% AGI limit
    }
    _NUMERIC_NAME = 'Form 1040 Schedule A'
    _SUPPORTED_YEARS = [2013, 2014, 2015]

    def to_evars_indirect(self):
        results = {}
        fields = self._fields

        # e18400 - State and local income taxes
        if (fields.get('line5') and fields.get('line5a') and
                not fields.get('line5b')):
            results['e18400'] = string_to_number(fields['line5'])

        return results
