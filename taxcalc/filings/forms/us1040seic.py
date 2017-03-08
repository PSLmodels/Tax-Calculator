from taxcalc.filings.forms.tax_form import TaxForm


class US1040SEIC(TaxForm):
    _DESCRIPTIVE_NAME = 'Earned Income Credit'
    _NUMERIC_NAME = 'Form 1040/1040A Schedule EIC'
    _SUPPORTED_YEARS = [2013, 2014, 2015]

    def to_evars_indirect(self):
        results = {}
        fields = self._fields

        # EIC - Earned Income Credit code: categorical variable
        child_ssns = ['line2_child1', 'line2_child2', 'line2_child3']
        results['EIC'] = sum(1 if fields.get(key) else 0 for key in child_ssns)

        return results
