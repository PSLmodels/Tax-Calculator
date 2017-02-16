import six
from taxcalc.utils import write_json_to_file, read_json_from_file
from taxcalc.filings.util import FormMapper
from .errors import UnsupportedFormError, UnsupportedFormYearError


class Form(FormMapper):
    """
    Represents a particular tax form for a given year and filer.

    Provides a bridge between tax record data in tax form and taxcalc formats:
        Can be populated with form data and generate input rvars.
        Can be filled with output rvars and write them back to the fields.

    Field keys are strings with a standard naming convention:
        all lowercase
        numerals for numbers
        underscores for spaces
        avoid spaces if the meaning remains clear
        use the simplest clearly identifiable name for unlabeled fields

    See valid_fields() for a list of all fields for a particular form.
    """

    # Each child class should override this basic info:
    _TITLE = 'Form'                 # e.g. 'Form 1040'
    _DESCRIPTION = 'A Basic Form'   # e.g. 'Individual Income Tax Return'
    _FILER_ID_FIELD = ''            # e.g. 'ssn' or 'identifying_number'
    _VALID_FIELDS_BY_YEAR = {}      # e.g. {2013: ['line1', 'line2']}

    #
    # Class data getters
    #

    @classmethod
    def form_id(cls):
        """
        Short alphanumeric form identifier. Useful when creating from strings.
        """
        return cls.__name__.lower()

    @classmethod
    def full_name(cls):
        """
        Full descriptive name for the form. For display purposes.
        """
        return '{0} : {1}'.format(cls._TITLE, cls._DESCRIPTION)

    @classmethod
    def supported_years(cls):
        """
        A list of years with which the form can be used.
        """
        return set(cls._VALID_FIELDS_BY_YEAR.keys())

    @classmethod
    def ensure_year_supported(cls, year):
        """
        Raise an error if year isn't supported.
        """
        if year not in cls.supported_years():
            raise UnsupportedFormYearError('{} not supported.'.format(year))

    @classmethod
    def valid_fields(cls, year):
        """
        All recognized field keys for the given year.
        """
        cls.ensure_year_supported(year)
        return cls._VALID_FIELDS_BY_YEAR[year].copy()

    #
    # Class translation helpers
    #

    @classmethod
    def from_registry(cls, form_id, year, registry, fields=None):
        """
        Create a form instance from a registry of form classes
        """
        if not (registry and isinstance(registry, dict)):
            raise ValueError("Registry must be a dict.")
        if form_id not in registry:
            raise UnsupportedFormError('Unknown form id "{}".'.format(form_id))
        return registry[form_id](year, fields=fields)

    @classmethod
    def from_dict(cls, data, registry):
        """
        Create a new form instance and fill it with data given a dict.
        """
        if any(k not in data for k in ['form_id', 'filing_year', 'fields']):
            raise UnsupportedFormError("Invalid json data")

        return cls.from_registry(
            data['form_id'], data['filing_year'], registry,
            fields=data['fields']
        )

    @classmethod
    def from_pdf(cls, data, registry):
        """
        Read in a form instance from a PDF file.
        Should read data from pdf and then use from_registry().
        """
        raise NotImplementedError

    @classmethod
    def parse(cls, data, registry, ext=None):
        """
        Returns a form from generic data.
        Optionally restricts to a files ending in ext.
        """
        if isinstance(data, Form):
            return data
        if isinstance(data, dict):
            return cls.from_dict(data, registry)
        elif isinstance(data, six.string_types):
            if not ext or data.endswith(ext):
                if data.endswith('.pdf'):
                    return cls.from_pdf(data, registry)
                elif data.endswith('.json'):
                    return cls.from_dict(read_json_from_file(data), registry)

        raise UnsupportedFormError("Unrecognized data.")

    @classmethod
    def example(cls, year, all_inputs=False, all_valid=False, filer_id='0'):
        """
        Returns a new form for an example filer and year.
        Optionally fills all valid fields or just the input fields.
        """
        form = cls(year)
        if all_valid:
            for field_key in form._valid_fields:
                form.set_field(field_key, '0')
        elif all_inputs:
            for field_key in form._read_map.input_keys():
                form.set_field(field_key, '0')
        form.set_field(form._FILER_ID_FIELD, filer_id)
        return form

    #
    # Instance
    #

    def __init__(self, year, fields=None, filer_id=None):
        """
        Creates a new Form.
        """
        super(Form, self).__init__(year)
        self.ensure_year_supported(year)
        self._year = year
        self._fields = {}
        self._valid_fields = self.__class__.valid_fields(self.year)
        if fields:
            self.set_fields(fields)
        if filer_id:
            self.set_field(self._FILER_ID_FIELD, filer_id)

    @property
    def year(self):
        """
        Form filing year. Static and necessary when mapping fields to rvars.
        """
        return self._year

    @property
    def filer_id(self):
        """
        Gets the filer ids specified by a form's _FILER_ID_FIELD.
        """
        return self._fields.get(self._FILER_ID_FIELD)

    @property
    def fields(self):
        """
        Return a copy of fields for public consumption
        """
        return self._fields.copy()

    @property
    def is_empty(self):
        return len(set(self._fields.keys()) - {self._FILER_ID_FIELD}) < 1

    def set_field(self, key, value):
        """
        Store value in fields at key if key is a valid
        """
        if key not in self._valid_fields:
            raise ValueError('Unknown field {} for form {}'
                             .format(key, self.full_name()))
        self._fields[key] = value

    def set_fields(self, data):
        """
        Store data in fields
        """
        for key, value in data.items():
            self.set_field(key, value)

    def _read_store(self):
        """
        Read our fields when computing rvars.
        """
        return self._fields

    def _write_store(self, data):
        """
        Store fields computed from rvars.
        """
        self.set_fields(data)

    #
    # Instance translation
    #

    def to_dict(self):
        """
        Returns a dict representing the form's data
        """
        return {
            'form_id': self.form_id(),
            'filing_year': self.year,
            'fields': self._fields,
        }

    def to_json_file(self, full_path):
        """
        Writes to a JSON file at full_path
        """
        write_json_to_file(self.to_dict(), full_path, sort_keys=True)

    def to_pdf_file(self, full_path):
        """
        Writes to a pdf using a template and filled with field values.
        Probably will need a class-level attribute for file template path.
        """
        raise NotImplementedError
