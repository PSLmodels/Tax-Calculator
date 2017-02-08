"""
Tax-Calculator Growfactors class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 growfactors.py
# pylint --disable=locally-disabled growfactors.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)


import os
import six
import pandas as pd
from .records import Records


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
    # suppress pylint warnings about unrecognized Records variables:
    # pylintx: disable=...

    CUR_PATH = os.path.abspath(os.path.dirname(__file__))
    FILENAME = 'growfactors.csv'
    FILE_PATH = os.path.join(CUR_PATH, FILENAME)

    VALID_NAMES = set(['ABOOK', 'ACGNS', 'ACPIM', 'ACPIU',
                       'ADIVS', 'AGDPN', 'AINTS',
                       'APOPN',  # TODO: drop this name eventually
                       'AIPD', 'ASCHCI', 'ASCHCL',
                       'ASCHEI', 'ASCHEL', 'ASCHF',
                       'ASOCSEC', 'ATXPY', 'AUCOMP', 'AWAGE'])

    def __init__(self, growfactors_filename=FILE_PATH):
        """
        Growfactors class constructor
        """
        # read grow factors from specified growfactors_filename
        if isinstance(growfactors_filename, six.string_types):
            if os.path.isfile(growfactors_filename):
                gfdf = pd.read_csv(growfactors_filename, index_col='YEAR')
            else:
                gfdf = Records.read_egg_csv('blowup_factors',
                                            Growfactors.FILENAME,
                                            index_col='YEAR')
        else:
            raise ValueError('growfactors_filename is not a string')
        # check validity of gfdf column names
        gfdf_names = set(list(gfdf))
        if gfdf_names < Growfactors.VALID_NAMES:
            msg = 'missing growfactors names are: {}'
            missing = Growfactors.VALID_NAMES - gfdf_names
            raise ValueError(msg.format(missing))
        if gfdf_names > Growfactors.VALID_NAMES:
            msg = 'invalid growfactors names are: {}'
            invalid = gfdf_names - Growfactors.VALID_NAMES
            raise ValueError(msg.format(invalid))
        # determine first_year and last_year from gfdf
        self.first_year = min(gfdf.index)
        self.last_year = max(gfdf.index)
        # set gfdf as attribute of class
        setattr(self, 'gfdf', gfdf)
        # specify factors as being unused (that is, not yet accessed)
        self.used = False

    def price_inflation_rates(self, first_year, last_year):
        """
        Return list of price inflation rates rounded to four decimal digits
        """
        # pylint: disable=no-member
        self.used = True
        if first_year > last_year:
            msg = 'first_year={} > last_year={}'
            raise ValueError(msg.format(first_year, last_year))
        if first_year < self.first_year:
            msg = 'first_year={} < Growfactors.first_year={}'
            raise ValueError(msg.format(first_year, self.first_year))
        if last_year > self.last_year:
            msg = 'last_year={} > Growfactors.last_year={}'
            raise ValueError(msg.format(last_year, self.last_year))
        rates = [round((self.gfdf['ACPIU'][cyr] - 1.0), 4)
                 for cyr in range(first_year, last_year + 1)]
        return rates

    def wage_growth_rates(self, first_year, last_year):
        """
        Return list of wage growth rates rounded to four decimal digits
        """
        # pylint: disable=no-member
        self.used = True
        if first_year > last_year:
            msg = 'first_year={} > last_year={}'
            raise ValueError(msg.format(first_year, last_year))
        if first_year < self.first_year:
            msg = 'first_year={} < Growfactors.first_year={}'
            raise ValueError(msg.format(first_year, self.first_year))
        if last_year > self.last_year:
            msg = 'last_year={} > Growfactors.last_year={}'
            raise ValueError(msg.format(last_year, self.last_year))
        rates = [round((self.gfdf['AWAGE'][cyr] - 1.0), 4)
                 for cyr in range(first_year, last_year + 1)]
        return rates

    def factor_value(self, name, year):
        """
        Return value of factor with specified name for specified year
        """
        # pylint: disable=no-member
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
