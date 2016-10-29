from pandas import DataFrame
from taxcalc import Records
from .base import FilingCollection
from .util import create_calculator
from .us_filing import USFiling
from multiprocessing import Process


class USFilingCollection(FilingCollection):

    @classmethod
    def example(cls, year, **kwargs):
        return super(USFilingCollection, cls).example(USFiling, year, **kwargs)

    @classmethod
    def from_dir(cls, _dir, filing_cls=None, ext=None, verbose=False):
        return super(USFilingCollection, cls)\
            .from_dir(_dir, USFiling, ext=ext, verbose=verbose)

    def __init__(self, filing_class=None):
        super(USFilingCollection, self).__init__(USFiling)

    def to_records(self):
        """
        Creates a set of records indexed by year containing these filings
        """
        records = {}
        for year, filings_by_filer in self._filings.items():
            data = [
                filing.read_rvars_with_forms()
                for filing in filings_by_filer.values()
            ]
            records[year] = Records(
                blowup_factors=None,
                data=DataFrame(data),
                exact_calculations=True,
                start_year=year,
                weights=None,
            )
        return records

    def write_records(self, records_by_year):
        """
        Write the values from records to filings
        """
        for year, records in records_by_year.items():
            if year not in self._filings:
                self._filings[year] = {}

            for index, row in records.to_df().iterrows():
                filer_id = row['RECID']

                if filer_id not in self._filings[year]:
                    self._filings[year][filer_id] = \
                        self._filing_class(year, filer_id)

                self._filings[year][filer_id].write_rvars_with_forms(row)

    def calc_all(self, policy=None, econ=None, verbose=False):
        records_by_year = self.to_records()
        calculators_by_year = {
            year: create_calculator(
                records, year, policy=policy, econ=econ, sync_years=False
            )
            for year, records in records_by_year.items()
        }

        calc_processes = []
        for calculator in calculators_by_year.values():
            calc_processes.append(
                Process(target=calculator.calc_one_year())
            )
        if verbose:
            print('USFilingCollection running {} calc processes.'
                  .format(len(calc_processes)))
        for process in calc_processes:
            process.start()
        for process in calc_processes:
            process.join()
        if verbose:
            print('USFilingCollection finished {} calc processes.'
                  .format(len(calc_processes)))

        self.write_records(records_by_year)

        # Allow method chaining
        return self

    def compare_to(self, other):
        raise NotImplementedError
