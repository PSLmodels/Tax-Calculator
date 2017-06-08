"""
Tax-Calculator Growfactors class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 growfactors.py
# pylint --disable=locally-disabled growfactors.py

import os
import six
import pandas as pd
from taxcalc.utils import read_egg_csv


class Growfactors(object):
    """
    Constructor for the Growfactors class.

    Parameters
    ----------
    growfactors_filename: string
        string is name of CSV file in which grow factors reside;
        default value is name of file containing baseline grow factors.

    Raises
    ------
    ValueError:
        if growfactors_filename is not a string.

    Returns
    -------
    class instance: Growfactors

    Notes
    -----
    Typical usage is "gfactor = Growfactors()", which produces an object
    containing the default grow factors in the Growfactors.FILENAME file.
    """

    CUR_PATH = os.path.abspath(os.path.dirname(__file__))
    FILENAME = 'growfactors.csv'
    FILE_PATH = os.path.join(CUR_PATH, FILENAME)

    VALID_NAMES = set(['ABOOK', 'ACGNS', 'ACPIM', 'ACPIU',
                       'ADIVS', 'AINTS',
                       'AIPD', 'ASCHCI', 'ASCHCL',
                       'ASCHEI', 'ASCHEL', 'ASCHF',
                       'ASOCSEC', 'ATXPY', 'AUCOMP', 'AWAGE'])

    def __init__(self, growfactors_filename=FILE_PATH):
        """
        Growfactors class constructor
        """
        # read grow factors from specified growfactors_filename
        gfdf = pd.DataFrame()
        if isinstance(growfactors_filename, six.string_types):
            # pylint: disable=redefined-variable-type
            # (above because pylint mistakenly thinks gfdf is not a DataFrame)
            if os.path.isfile(growfactors_filename):
                gfdf = pd.read_csv(growfactors_filename, index_col='YEAR')
            else:
                gfdf = read_egg_csv(Growfactors.FILENAME, index_col='YEAR')
        else:
            raise ValueError('growfactors_filename is not a string')
        assert isinstance(gfdf, pd.DataFrame)
        # check validity of gfdf column names
        gfdf_names = set(list(gfdf))
        if gfdf_names != Growfactors.VALID_NAMES:
            msg = ('missing names are: {} and invalid names are: {}')
            missing = Growfactors.VALID_NAMES - gfdf_names
            invalid = gfdf_names - Growfactors.VALID_NAMES
            raise ValueError(msg.format(missing, invalid))
        # determine first_year and last_year from gfdf
        self._first_year = min(gfdf.index)
        self._last_year = max(gfdf.index)
        # set gfdf as attribute of class
        self.gfdf = pd.DataFrame()
        setattr(self, 'gfdf', gfdf)
        # specify factors as being unused (that is, not yet accessed)
        self.used = False

    @property
    def first_year(self):
        """
        Growfactors class start_year property.
        """
        return self._first_year

    @property
    def last_year(self):
        """
        Growfactors class last_year property.
        """
        return self._last_year

    def price_inflation_rates(self, firstyear, lastyear):
        """
        Return list of price inflation rates rounded to four decimal digits.
        """
        self.used = True
        if firstyear > lastyear:
            msg = 'first_year={} > last_year={}'
            raise ValueError(msg.format(firstyear, lastyear))
        if firstyear < self.first_year:
            msg = 'firstyear={} < Growfactors.first_year={}'
            raise ValueError(msg.format(firstyear, self.first_year))
        if lastyear > self.last_year:
            msg = 'last_year={} > Growfactors.last_year={}'
            raise ValueError(msg.format(lastyear, self.last_year))
        # pylint: disable=no-member
        rates = [round((self.gfdf['ACPIU'][cyr] - 1.0), 4)
                 for cyr in range(firstyear, lastyear + 1)]
        return rates

    def wage_growth_rates(self, firstyear, lastyear):
        """
        Return list of wage growth rates rounded to four decimal digits.
        """
        self.used = True
        if firstyear > lastyear:
            msg = 'firstyear={} > lastyear={}'
            raise ValueError(msg.format(firstyear, lastyear))
        if firstyear < self.first_year:
            msg = 'firstyear={} < Growfactors.first_year={}'
            raise ValueError(msg.format(firstyear, self.first_year))
        if lastyear > self.last_year:
            msg = 'lastyear={} > Growfactors.last_year={}'
            raise ValueError(msg.format(lastyear, self.last_year))
        # pylint: disable=no-member
        rates = [round((self.gfdf['AWAGE'][cyr] - 1.0), 4)
                 for cyr in range(firstyear, lastyear + 1)]
        return rates

    def factor_value(self, name, year):
        """
        Return value of factor with specified name for specified year.
        """
        self.used = True
        if name not in Growfactors.VALID_NAMES:
            msg = 'name={} not in Growfactors.VALID_NAMES'
            raise ValueError(msg.format(year, name))
        if year < self.first_year:
            msg = 'year={} < Growfactors.first_year={}'
            raise ValueError(msg.format(year, self.first_year))
        if year > self.last_year:
            msg = 'year={} > Growfactors.last_year={}'
            raise ValueError(msg.format(year, self.last_year))
        return self.gfdf[name][year]

    def update(self, name, year, diff):
        """
        Add to self.gfdf[name][year] the specified diff amount.
        """
        if self.used:
            msg = 'cannot update growfactors after they have been used'
            raise ValueError(msg)
        self.gfdf[name][year] += diff
