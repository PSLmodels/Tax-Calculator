"""
Tax-Calculator tax-filing-unit Records class.
"""
# CODING-STYLE CHECKS:
# pycodestyle records.py
# pylint --disable=locally-disabled records.py

import os
import numpy as np
import pandas as pd
from taxcalc.data import Data
from taxcalc.growfactors import GrowFactors
from taxcalc.utils import read_egg_csv


class Records(Data):
    """
    Records is a subclass of the abstract Data class, and therefore,
    inherits its methods (none of which are shown here).

    Constructor for the tax-filing-unit Records class.

    Parameters
    ----------
    data: string or Pandas DataFrame
        string describes CSV file in which records data reside;
        DataFrame already contains records data;
        default value is the string 'puf.csv'
        NOTE: when using custom data, set this argument to a DataFrame.
        NOTE: to use your own data for a specific year with Tax-Calculator,
        be sure to read the documentation on creating your own data file and
        then construct a Records object like this:
        mydata = pd.read_csv(<mydata.csv>)
        myrec = Records(data=mydata, start_year=<mydata_year>,
                        gfactors=None, weights=None)
        NOTE: data=None is allowed but the returned instance contains only
              the data variable information in the specified VARINFO file.

    start_year: integer
        specifies calendar year of the input data;
        default value is PUFCSV_YEAR.
        Note that if specifying your own data (see above NOTE) as being
        a custom data set, be sure to explicitly set start_year to the
        custom data's calendar year.

    gfactors: GrowFactors class instance or None
        containing record data growth (or extrapolation) factors.

    weights: string or Pandas DataFrame or None
        string describes CSV file in which weights reside;
        DataFrame already contains weights;
        None creates empty sample-weights DataFrame;
        default value is filename of the PUF weights.
        NOTE: when using custom weights, set this argument to a DataFrame.
        NOTE: assumes weights are integers that are 100 times the real weights.

    adjust_ratios: string or Pandas DataFrame or None
        string describes CSV file in which adjustment ratios reside;
        DataFrame already contains transposed/no-index adjustment ratios;
        None creates empty adjustment-ratios DataFrame;
        default value is filename of the PUF adjustment ratios.
        NOTE: when using custom ratios, set this argument to a DataFrame.
        NOTE: if specifying a DataFrame, set adjust_ratios to my_df defined as:
              my_df = pd.read_csv('<my_ratios.csv>', index_col=0).transpose()

    exact_calculations: boolean
        specifies whether or not exact tax calculations are done without
        any smoothing of stair-step provisions in income tax law;
        default value is false.

    Raises
    ------
    ValueError:
        if data is not the appropriate type.
        if taxpayer and spouse variables do not add up to filing-unit total.
        if dividends is less than qualified dividends.
        if gfactors is not None or a GrowFactors class instance.
        if start_year is not an integer.
        if files cannot be found.

    Returns
    -------
    class instance: Records

    Notes
    -----
    Typical usage when using PUF input data is as follows::

        recs = Records()

    which uses all the default parameters of the constructor, and
    therefore, imputed variables are generated to augment the data and
    initial-year grow factors are applied to the data.  There are
    situations in which you need to specify the values of the Record
    constructor's arguments, but be sure you know exactly what you are
    doing when attempting this.

    Use Records.cps_constructor() to get a Records object instantiated
    with CPS input data.
    """
    # suppress pylint warning about constructor having too many arguments:
    # pylint: disable=too-many-arguments
    # suppress pylint warnings about uppercase variable names:
    # pylint: disable=invalid-name
    # suppress pylint warnings about too many class instance attributes:
    # pylint: disable=too-many-instance-attributes

    PUFCSV_YEAR = 2011
    CPSCSV_YEAR = 2014

    PUF_WEIGHTS_FILENAME = 'puf_weights.csv.gz'
    PUF_RATIOS_FILENAME = 'puf_ratios.csv'
    CPS_WEIGHTS_FILENAME = 'cps_weights.csv.gz'
    CPS_RATIOS_FILENAME = None
    CODE_PATH = os.path.abspath(os.path.dirname(__file__))
    VARINFO_FILE_NAME = 'records_variables.json'
    VARINFO_FILE_PATH = CODE_PATH

    def __init__(self,
                 data='puf.csv',
                 start_year=PUFCSV_YEAR,
                 gfactors=GrowFactors(),
                 weights=PUF_WEIGHTS_FILENAME,
                 adjust_ratios=PUF_RATIOS_FILENAME,
                 exact_calculations=False):
        # pylint: disable=no-member,too-many-branches
        if isinstance(weights, str):
            weights = os.path.join(Records.CODE_PATH, weights)
        super().__init__(data, start_year, gfactors, weights)
        if data is None:
            return  # because there are no data
        # read adjustment ratios
        self.ADJ = None
        self._read_ratios(adjust_ratios)
        # specify exact value based on exact_calculations
        self.exact = np.where(exact_calculations is True, 1, 0)
        # specify FLPDYR value based on start_year
        self.FLPDYR = start_year
        # check for valid MARS values
        if not np.all(np.logical_and(np.greater_equal(self.MARS, 1),
                                     np.less_equal(self.MARS, 5))):
            raise ValueError('not all MARS values in [1,5] range')
        # create variables derived from MARS, which is in MUST_READ_VARS
        self.num = np.where(self.MARS == 2, 2, 1)
        self.sep = np.where(self.MARS == 3, 2, 1)
        # check for valid EIC values
        if not np.all(np.logical_and(np.greater_equal(self.EIC, 0),
                                     np.less_equal(self.EIC, 3))):
            raise ValueError('not all EIC values in [0,3] range')
        # check that three sets of split-earnings variables have valid values
        msg = 'expression "{0} == {0}p + {0}s" is not true for every record'
        tol = 0.020001  # handles "%.2f" rounding errors
        if not np.allclose(self.e00200, (self.e00200p + self.e00200s),
                           rtol=0.0, atol=tol):
            raise ValueError(msg.format('e00200'))
        if not np.allclose(self.e00900, (self.e00900p + self.e00900s),
                           rtol=0.0, atol=tol):
            raise ValueError(msg.format('e00900'))
        if not np.allclose(self.e02100, (self.e02100p + self.e02100s),
                           rtol=0.0, atol=tol):
            raise ValueError(msg.format('e02100'))
        # check that spouse income variables have valid values
        nospouse = self.MARS != 2
        zeros = np.zeros_like(self.MARS[nospouse])
        msg = '{} is not always zero for non-married filing unit'
        if not np.allclose(self.e00200s[nospouse], zeros):
            raise ValueError(msg.format('e00200s'))
        if not np.allclose(self.e00900s[nospouse], zeros):
            raise ValueError(msg.format('e00900s'))
        if not np.allclose(self.e02100s[nospouse], zeros):
            raise ValueError(msg.format('e02100s'))
        if not np.allclose(self.k1bx14s[nospouse], zeros):
            raise ValueError(msg.format('k1bx14s'))
        # check that ordinary dividends are no less than qualified dividends
        other_dividends = np.maximum(0., self.e00600 - self.e00650)
        if not np.allclose(self.e00600, self.e00650 + other_dividends,
                           rtol=0.0, atol=tol):
            msg = 'expression "e00600 >= e00650" is not true for every record'
            raise ValueError(msg)
        del other_dividends
        # check that total pension income is no less than taxable pension inc
        nontaxable_pensions = np.maximum(0., self.e01500 - self.e01700)
        if not np.allclose(self.e01500, self.e01700 + nontaxable_pensions,
                           rtol=0.0, atol=tol):
            msg = 'expression "e01500 >= e01700" is not true for every record'
            raise ValueError(msg)
        del nontaxable_pensions
        # check that PT_SSTB_income has valid value
        if not np.all(np.logical_and(np.greater_equal(self.PT_SSTB_income, 0),
                                     np.less_equal(self.PT_SSTB_income, 1))):
            raise ValueError('not all PT_SSTB_income values are 0 or 1')

    @staticmethod
    def cps_constructor(data=None,
                        gfactors=GrowFactors(),
                        exact_calculations=False):
        """
        Static method returns a Records object instantiated with CPS
        input data.  This works in a analogous way to Records(), which
        returns a Records object instantiated with PUF input data.
        This is a convenience method that eliminates the need to
        specify all the details of the CPS input data just as the
        default values of the arguments of the Records class constructor
        eliminate the need to specify all the details of the PUF input
        data.
        """
        if data is None:
            data = os.path.join(Records.CODE_PATH, 'cps.csv.gz')
        if gfactors is None:
            weights = None
        else:
            weights = os.path.join(Records.CODE_PATH,
                                   Records.CPS_WEIGHTS_FILENAME)
        return Records(data=data,
                       start_year=Records.CPSCSV_YEAR,
                       gfactors=gfactors,
                       weights=weights,
                       adjust_ratios=Records.CPS_RATIOS_FILENAME,
                       exact_calculations=exact_calculations)

    def increment_year(self):
        """
        Add one to current year, and also does
        extrapolation, reweighting, adjusting for new current year.
        """
        super().increment_year()
        self.FLPDYR = self.current_year  # pylint: disable=no-member
        # apply variable adjustment ratios
        self._adjust(self.current_year)

    @staticmethod
    def read_cps_data():
        """
        Return data in cps.csv.gz as a Pandas DataFrame.
        """
        fname = os.path.join(Records.CODE_PATH, 'cps.csv.gz')
        if os.path.isfile(fname):
            cpsdf = pd.read_csv(fname)
        else:  # find file in conda package
            cpsdf = read_egg_csv(fname)  # pragma: no cover
        return cpsdf

    # ----- begin private methods of Records class -----

    def _extrapolate(self, year):
        """
        Apply to variables the grow factor values for specified calendar year.
        """
        # pylint: disable=too-many-statements,no-member
        # put values in local dictionary
        gfv = dict()
        for name in GrowFactors.VALID_NAMES:
            gfv[name] = self.gfactors.factor_value(name, year)
        # apply values to Records variables
        self.e00200 *= gfv['AWAGE']
        self.e00200p *= gfv['AWAGE']
        self.e00200s *= gfv['AWAGE']
        self.pencon_p *= gfv['AWAGE']
        self.pencon_s *= gfv['AWAGE']
        self.e00300 *= gfv['AINTS']
        self.e00400 *= gfv['AINTS']
        self.e00600 *= gfv['ADIVS']
        self.e00650 *= gfv['ADIVS']
        self.e00700 *= gfv['ATXPY']
        self.e00800 *= gfv['ATXPY']
        self.e00900s = np.where(self.e00900s >= 0,
                                   self.e00900s * gfv['ASCHCI'],
                                   self.e00900s * gfv['ASCHCL'])
        self.e00900p = np.where(self.e00900p >= 0,
                                   self.e00900p * gfv['ASCHCI'],
                                   self.e00900p * gfv['ASCHCL'])
        self.e00900 = self.e00900p + self.e00900s
        self.e01100 *= gfv['ACGNS']
        self.e01200 *= gfv['ACGNS']
        self.e01400 *= gfv['ATXPY']
        self.e01500 *= gfv['ATXPY']
        self.e01700 *= gfv['ATXPY']
        self.e02000 = np.where(self.e02000 >= 0,
                                  self.e02000 * gfv['ASCHEI'],
                                  self.e02000 * gfv['ASCHEL'])
        self.e02100 *= gfv['ASCHF']
        self.e02100p *= gfv['ASCHF']
        self.e02100s *= gfv['ASCHF']
        self.e02300 *= gfv['AUCOMP']
        self.e02400 *= gfv['ASOCSEC']
        self.e03150 *= gfv['ATXPY']
        self.e03210 *= gfv['ATXPY']
        self.e03220 *= gfv['ATXPY']
        self.e03230 *= gfv['ATXPY']
        self.e03270 *= gfv['ACPIM']
        self.e03240 *= gfv['ATXPY']
        self.e03290 *= gfv['ACPIM']
        self.e03300 *= gfv['ATXPY']
        self.e03400 *= gfv['ATXPY']
        self.e03500 *= gfv['ATXPY']
        self.e07240 *= gfv['ATXPY']
        self.e07260 *= gfv['ATXPY']
        self.e07300 *= gfv['ABOOK']
        self.e07400 *= gfv['ABOOK']
        self.p08000 *= gfv['ATXPY']
        self.e09700 *= gfv['ATXPY']
        self.e09800 *= gfv['ATXPY']
        self.e09900 *= gfv['ATXPY']
        self.e11200 *= gfv['ATXPY']
        # ITEMIZED DEDUCTIONS
        self.e17500 *= gfv['ACPIM']
        self.e18400 *= gfv['ATXPY']
        self.e18500 *= gfv['ATXPY']
        self.e19200 *= gfv['AIPD']
        self.e19800 *= gfv['ATXPY']
        self.e20100 *= gfv['ATXPY']
        self.e20400 *= gfv['ATXPY']
        self.g20500 *= gfv['ATXPY']
        # CAPITAL GAINS
        self.p22250 *= gfv['ACGNS']
        self.p23250 *= gfv['ACGNS']
        self.e24515 *= gfv['ACGNS']
        self.e24518 *= gfv['ACGNS']
        # SCHEDULE E
        self.e26270 *= gfv['ASCHEI']
        self.e27200 *= gfv['ASCHEI']
        self.k1bx14p *= gfv['ASCHEI']
        self.k1bx14s *= gfv['ASCHEI']
        # MISCELLANOUS SCHEDULES
        self.e07600 *= gfv['ATXPY']
        self.e32800 *= gfv['ATXPY']
        self.e58990 *= gfv['ATXPY']
        self.e62900 *= gfv['ATXPY']
        self.e87530 *= gfv['ATXPY']
        self.e87521 *= gfv['ATXPY']
        self.cmbtp *= gfv['ATXPY']
        # BENEFITS
        self.other_ben *= gfv['ABENOTHER']
        self.mcare_ben *= gfv['ABENMCARE']
        self.mcaid_ben *= gfv['ABENMCAID']
        self.ssi_ben *= gfv['ABENSSI']
        self.snap_ben *= gfv['ABENSNAP']
        self.wic_ben *= gfv['ABENWIC']
        self.housing_ben *= gfv['ABENHOUSING']
        self.tanf_ben *= gfv['ABENTANF']
        self.vet_ben *= gfv['ABENVET']
        # remove local dictionary
        del gfv

    def _adjust(self, year):
        """
        Adjust value of income variables to match SOI distributions
        Note: adjustment must leave variables as numpy.ndarray type
        """
        # pylint: disable=no-member
        if self.ADJ.size > 0:
            # Interest income
            self.e00300 *= self.ADJ['INT{}'.format(year)][self.agi_bin].values

    def _read_ratios(self, ratios):
        """
        Read Records adjustment ratios from file or
        use specified transposed/no-index DataFrame as ratios or
        create empty DataFrame if None
        """
        if ratios is None:
            setattr(self, 'ADJ', pd.DataFrame({'nothing': []}))
            return
        if isinstance(ratios, pd.DataFrame):
            assert 'INT2013' in ratios.columns  # check for transposed
            assert ratios.index.name is None  # check for no-index
            ADJ = ratios
        elif isinstance(ratios, str):
            ratios_path = os.path.join(Records.CODE_PATH, ratios)
            if os.path.isfile(ratios_path):
                ADJ = pd.read_csv(ratios_path,
                                  index_col=0)
            else:  # find file in conda package
                ADJ = read_egg_csv(os.path.basename(ratios_path),
                                   index_col=0)  # pragma: no cover
            ADJ = ADJ.transpose()
        else:
            msg = 'ratios is neither None nor a Pandas DataFrame nor a string'
            raise ValueError(msg)
        assert isinstance(ADJ, pd.DataFrame)
        if ADJ.index.name != 'agi_bin':
            ADJ.index.name = 'agi_bin'
        self.ADJ = pd.DataFrame()
        setattr(self, 'ADJ', ADJ.astype(np.float32))
        del ADJ
