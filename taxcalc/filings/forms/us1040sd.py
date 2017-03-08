from taxcalc.filings.forms.tax_form import TaxForm


class US1040SD(TaxForm):
    _DESCRIPTIVE_NAME = 'Capital Gains and Losses'
    _EVAR_MAP = {
        'line7': 'p22250',  # Net short-term gain or loss
        'line15': 'p23250',  # Net Long Term Gain or Loss
        'line18': 'e24518',  # 28% Rate Gain or Loss New 2003
        'line19': 'e24515',  # Un-Recaptured Section 1250 Gain
    }
    _NUMERIC_NAME = 'Form 1040 Schedule D'
    _SUPPORTED_YEARS = [2013, 2014, 2015]
