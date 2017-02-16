import os
from taxcalc.utils import update_dict_ex
from .errors import UnsupportedFormError
from .form import Form
from .filing import Filing


class FilingCollection(object):
    """
    Represents a collection of Filings indexed by year and filer_id.
    Provides helper methods to work with the Filings.
    """

    @classmethod
    def example(cls, filing_class, year, **kwargs):
        """
        Creates an example filing collection with a single example filing.
        """
        example = cls(filing_class)
        example.add_filing(
            filing_class.example(year, **kwargs)
        )
        return example

    @classmethod
    def from_dir(cls, _dir, filing_cls, ext=None, verbose=False):
        """
        Creates a FilingCollection from a directory.
        Optionally restricts to files ending in _ext.
        Optionally prints success/failure message for each file in path
        """
        if not (_dir and os.path.isdir(_dir)):
            raise ValueError("{} is not a directory.".format(_dir))

        collection = cls(filing_cls)
        for dir_path, sub_dirs, files in os.walk(_dir):
            for filename in files:
                file_path = os.path.join(dir_path, filename)
                try:
                    form = Form.parse(
                        file_path, filing_cls.FORM_CLASSES_BY_ID, ext=ext
                    )
                    collection.add_form(form)
                    if verbose:
                        print("{} loaded.".format(file_path))
                except UnsupportedFormError:
                    if verbose:
                        print("{} skipped, invalid format.".format(file_path))

        return collection

    def __init__(self, filing_class):
        """
        Create a new FilingCollection and set up internal data.
        """
        if not (filing_class and issubclass(filing_class, Filing)):
            raise ValueError("filing_class must extend Filing.")
        self._filing_class = filing_class
        self._filings = {}

    @property
    def filings(self):
        return self._filings.copy()

    def add_form(self, form):
        """
        Adds a form to the matching filing in the collection.
        """
        if not isinstance(form, Form):
            raise ValueError("Expected a Form.")

        year = form.year
        filer_id = form.filer_id

        if year not in self._filings:
            self._filings[year] = {}

        if filer_id not in self._filings[year]:
            self._filings[year][filer_id] = self._filing_class(year, filer_id)

        self._filings[year][filer_id].add_form(form)

    def add_filing(self, filing):
        """
        Add a filing to the collection.
        """
        if not isinstance(filing, self._filing_class):
            raise ValueError("Expected a {}".format(self._filing_class))

        if filing.year not in self._filings:
            self._filings[filing.year] = {}

        update_dict_ex(self._filings[filing.year], filing.filer_id, filing)

    def to_dir(self, path):
        """
        Writes all filings and their forms to dir/year/filer_id/form.format
        Creates missing directories recursively.
        """
        for year, filings_by_id in self._filings.items():
            year_path = os.path.join(path, str(year))
            for filer_id, filing in filings_by_id.items():
                filing_path = os.path.join(year_path, str(filer_id))
                filing.to_dir(filing_path)
