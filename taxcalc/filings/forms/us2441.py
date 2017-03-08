from taxcalc.filings.forms.tax_form import TaxForm


class US2441(TaxForm):
    _DESCRIPTIVE_NAME = 'Child and Dependent Care Expenses'
    _EVAR_MAP = {
        'line3': 'e32800',  # Child/dep care qualifying individual expenses
    }
    _NUMERIC_NAME = 'Form 2441'
    _SUPPORTED_YEARS = [2013, 2014, 2015]

    def to_evars_indirect(self):
        results = {}
        fields = self._fields

        # f2441 -  Number of Child Care Credit qualified individuals
        # @todo Parse from attached statements if more than 2
        child_ssns = ['line2b_1', 'line2b_2']
        results['f2441'] = sum(1 if fields.get(key) else 0
                               for key in child_ssns)

        return results
