from taxcalc.filings.forms.tax_form import TaxForm


class US1040SB(TaxForm):
    """
    Taxcalc doesn't currently use any fields directly from this form.
    It is provided for PDF writing and later further use.
    """
    _DESCRIPTIVE_NAME = 'Interest and Ordinary Dividends'
    _NUMERIC_NAME = 'Form 1040/1040A Schedule B'
