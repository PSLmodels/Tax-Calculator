from .tax_form import TaxForm


class US1040SSE(TaxForm):
    """
    Taxcalc doesn't currently use any fields directly from this form.
    It is provided for PDF writing and later further use.
    """
    _DESCRIPTIVE_NAME = 'Self-Employment Tax'
    _NUMERIC_NAME = 'Form 1040 Schedule SE'
