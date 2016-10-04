import six

from .errors import UnsupportedFormYearError
from taxcalc.utils import string_to_number


class TaxForm(object):
    """
    Represents a particular tax form for a given year and filer.
    Provides a bridge between tax record data in tax form and evar formats:
        Can be populated using actual form line data or output evars.
        Can be read as actual form line data or as input evars.
    Could also hold form-specific tax calculation logic, if deemed useful.

    We provide a child class for each unique form the IRS provides.
    Each child class implements direct and indirect evar mapping.
    This should simplify maintenance while providing flexibility in mapping.

    Form field keys are strings with a standardized naming convention:
        all lowercase
        always numerals for numbers
        no spaces & exact matches to labeled lines - 'line1', 'line59a'
        underscores & contextual keys for unlabeled fields -
            'line3_spouse_ssn', 'line21_income_type', 'line6c_dependent1_name'

    Form field values can be passed in as any format and will be cast upon
    calls to to_evars(). We generally expect strings.
    """

    # Each child class should override these basic constants:
    _DESCRIPTIVE_NAME = 'TaxForm Base'  # e.g. 'Individual Income Tax Return'
    _EVAR_MAP = None                    # e.g. {'line8a': 'e00300'}
    _EVAR_MAP_BY_YEAR = None            # e.g. {2013: {'line52': 'e00047'}}
    _NUMERIC_NAME = 'TaxForm Base'      # e.g. 'Form 1040'
    _SUPPORTED_YEARS = None             # an array of years to restrict to
    _TAX_UNIT_ID_FIELD = 'ssn'          # e.g. 'ssn' or 'identifying_number'
    _VALID_FIELDS = None                # a list of valid field names

    # _VALID_FIELDS would allow us to ensure that any data being stored as a
    # form field is actually valid for that form, which could help catch some
    # input errors. It would also be a great point of reference when creating
    # form fields. But defining it for every form/year is a lot of work. @todo

    @classmethod
    def check_year_support(cls, year):
        """
        Raises an error if this class cannot be used for the given filing year.
        Incompatibility is likely the result of a form revision we haven't
        coded for yet.
        """
        if not isinstance(year, int):
            raise ValueError('Expected year "{}" to be an int'.format(year))
        if cls._SUPPORTED_YEARS and year not in cls._SUPPORTED_YEARS:
            raise UnsupportedFormYearError('{} not supported.'.format(year))

    @classmethod
    def form_id(cls):
        """
        Short alphanumeric form identifier. Useful when creating from strings.
        """
        return cls.__name__.lower()

    @classmethod
    def form_name(cls):
        """
        Full descriptive name for the form. For display purposes.
        """
        return '{0} : {1}'.format(cls._NUMERIC_NAME, cls._DESCRIPTIVE_NAME)

    def __init__(self, year, fields={}):
        """
        Completes the basic construction for its derived classes.
        """
        self.check_year_support(year)
        self._year = year
        self._fields = {}
        self.set_fields(fields)

    @property
    def year(self):
        """
        Form filing year. Static and necessary when mapping fields to evars.
        """
        return self._year

    @property
    def tax_unit_id(self):
        """
        Gets the tax unit id specified by a form's __TAX_UNIT_ID_FIELD.
        If not specified defaults to zero.
        """
        return self._fields.get(self.__class__._TAX_UNIT_ID_FIELD) or '0'

    def set_field(self, name, value):
        """
        Helper method for setting a single field.
        """
        self.set_fields({name: value})

    def set_fields(self, data):
        """
        Set given fields if they pass validation.
        """
        if not isinstance(data, dict):
            raise ValueError('Expected a dict of field data')
        valid_fields = self.__class__._VALID_FIELDS
        for key, value in data.items():
            if valid_fields and key not in valid_fields:
                print('Unknown field {0} for form {2}'.
                      format(key, self.form_name()))
            else:
                self._fields[key] = value

    def to_evars(self):
        """
        Get stored data as a dict of evars.
        Raises an error on conflicting calculations.
        Converts field values (stored as strings) to floats
        """
        direct = self.to_evars_direct()
        indirect = self.to_evars_indirect() or {}

        # Check for conflicts
        for key in direct:
            if key in indirect and direct[key] != indirect[key]:
                raise ValueError('Different calc for same evar.')
        for key in indirect:
            if key in direct and direct[key] != indirect[key]:
                raise ValueError('Different calc for same evar.')

        direct.update(indirect)
        return direct

    def to_evars_direct(self):
        """
        Get stored data as a dict of evars following defined evar maps.
        Raises an error on conflicting calculations.
        Converts field values stored as strings to int/float.
        """
        results = {}

        if self._EVAR_MAP_BY_YEAR and self.year in self._EVAR_MAP_BY_YEAR:
            year_evar_map = self._EVAR_MAP_BY_YEAR[self.year]
        else:
            year_evar_map = None

        for key, value in self._fields.items():
            if self._EVAR_MAP and key in self._EVAR_MAP:
                # print('(a) key, value = {} : {}'.format(key, value))
                evar = self._EVAR_MAP[key]
            elif year_evar_map and key in year_evar_map:
                # print('(b) key, value = {} : {}'.format(key, value))
                evar = year_evar_map[key]
            else:
                # print('(c) key, value = {} : {}'.format(key, value))
                continue
            if evar in results and results[evar] != value:
                raise ValueError('Different calc for same evar.')
            results[evar] = value

        # convert results to value types
        for key, value in results.items():
            if isinstance(value, six.string_types):
                results[key] = string_to_number(value)

        return results

    def to_evars_indirect(self):
        """
        Get any evars that can't be determined with a simple 1-1 mapping,
        e.g. if an evar depends on multiple lines.
        To be extended by child classes.
        Should convert values to their expected types.
        """

    def to_pdf(self):
        """
        Each class will need to prepare a specific file and write its fields.
        Probably need attributes for file template name, fields_to_write, etc,
        then can generalize some of it here.
        """
        raise NotImplementedError
