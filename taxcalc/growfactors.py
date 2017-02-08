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
from records import Records  # TODO: why can't use .records ?


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
        if first_year < self.first_year:
            msg = 'first_year={} < Growfactors.first_year={}'
            raise ValueError(msg.format(first_year, self.first_year))
        if last_year > self.last_year:
            msg = 'last_year={} > Growfactors.last_year={}'
            raise ValueError(msg.format(last_year, self.last_year))
        rates = [round((self.gfdf['AWAGE'][cyr] - 1.0), 4)
                 for cyr in range(first_year, last_year + 1)]
        return rates

    """
    def blowup(self, year):
        # Applies gfdf to variables for specified calendar year
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-locals
        AWAGE = self.gfdf['AWAGE'][year]
        AINTS = self.gfdf['AINTS'][year]
        ADIVS = self.gfdf['ADIVS'][year]
        ATXPY = self.gfdf['ATXPY'][year]
        ASCHCI = self.gfdf['ASCHCI'][year]
        ASCHCL = self.gfdf['ASCHCL'][year]
        ACGNS = self.gfdf['ACGNS'][year]
        ASCHEI = self.gfdf['ASCHEI'][year]
        ASCHEL = self.gfdf['ASCHEL'][year]
        ASCHF = self.gfdf['ASCHF'][year]
        AUCOMP = self.gfdf['AUCOMP'][year]
        ASOCSEC = self.gfdf['ASOCSEC'][year]
        ACPIM = self.gfdf['ACPIM'][year]
        AGDPN = self.gfdf['AGDPN'][year]
        ABOOK = self.gfdf['ABOOK'][year]
        AIPD = self.gfdf['AIPD'][year]
        self.e00200 *= AWAGE
        self.e00200p *= AWAGE
        self.e00200s *= AWAGE
        self.e00300 *= AINTS
        self.e00400 *= AINTS
        self.e00600 *= ADIVS
        self.e00650 *= ADIVS
        self.e00700 *= ATXPY
        self.e00800 *= ATXPY
        self.e00900[:] = np.where(self.e00900 >= 0,
                                  self.e00900 * ASCHCI,
                                  self.e00900 * ASCHCL)
        self.e00900s[:] = np.where(self.e00900s >= 0,
                                   self.e00900s * ASCHCI,
                                   self.e00900s * ASCHCL)
        self.e00900p[:] = np.where(self.e00900p >= 0,
                                   self.e00900p * ASCHCI,
                                   self.e00900p * ASCHCL)
        self.e01100 *= ACGNS
        self.e01200 *= ACGNS
        self.e01400 *= ATXPY
        self.e01500 *= ATXPY
        self.e01700 *= ATXPY
        self.e02000[:] = np.where(self.e02000 >= 0,
                                  self.e02000 * ASCHEI,
                                  self.e02000 * ASCHEL)
        self.e02100 *= ASCHF
        self.e02100p *= ASCHF
        self.e02100s *= ASCHF
        self.e02300 *= AUCOMP
        self.e02400 *= ASOCSEC
        self.e03150 *= ATXPY
        self.e03210 *= ATXPY
        self.e03220 *= ATXPY
        self.e03230 *= ATXPY
        self.e03270 *= ACPIM
        self.e03240 *= AGDPN
        self.e03290 *= ACPIM
        self.e03300 *= ATXPY
        self.e03400 *= ATXPY
        self.e03500 *= ATXPY
        self.e07240 *= ATXPY
        self.e07260 *= ATXPY
        self.e07300 *= ABOOK
        self.e07400 *= ABOOK
        self.p08000 *= ATXPY
        self.e09700 *= ATXPY
        self.e09800 *= ATXPY
        self.e09900 *= ATXPY
        self.e11200 *= ATXPY
        # ITEMIZED DEDUCTIONS
        self.e17500 *= ACPIM
        self.e18400 *= ATXPY
        self.e18500 *= ATXPY
        self.e19200 *= AIPD
        self.e19800 *= ATXPY
        self.e20100 *= ATXPY
        self.e20400 *= ATXPY
        self.e20500 *= ATXPY
        # CAPITAL GAINS
        self.p22250 *= ACGNS
        self.p23250 *= ACGNS
        self.e24515 *= ACGNS
        self.e24518 *= ACGNS
        # SCHEDULE E
        self.p25470 *= ASCHEI
        self.e26270 *= ASCHEI
        self.e27200 *= ASCHEI
        # MISCELLANOUS SCHEDULES
        self.e07600 *= ATXPY
        self.e32800 *= ATXPY
        self.e58990 *= ATXPY
        self.e62900 *= ATXPY
        self.e87530 *= ATXPY
        self.p87521 *= ATXPY
        self.cmbtp *= ATXPY
    """

# TODO: drop this code
if __name__ == '__main__':
    GFACTORS = Growfactors()
    PIR = GFACTORS.price_inflation_rates(2013, 2026)
    print PIR
    WGR = GFACTORS.wage_growth_rates(2013, 2026)
    print WGR
