from .tax_form import TaxForm


class US1040SR(TaxForm):
    """
    Taxcalc doesn't currently use any fields directly from this form.
    It is provided for PDF writing and later further use.
    """
    _DESCRIPTIVE_NAME = 'Credit for the Elderly or the Disabled'
    _NUMERIC_NAME = 'Form 1040/1040A Schedule R'
