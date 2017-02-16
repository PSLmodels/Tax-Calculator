from taxcalc.filings import Form
from taxcalc.filings.us_forms import US_FORMS


def test_year_support():
    for form_class in US_FORMS:
        assert issubclass(form_class, Form)
        assert form_class.supported_years() == {2013, 2014, 2015}
