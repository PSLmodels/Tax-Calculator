"""
Tax-Calculator tax-filing-unit Records class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 records.py
# pylint --disable=locally-disabled records.py

import os
import six
import numpy as np
import pandas as pd

from .growfactors import Growfactors
from .utils import read_egg_csv, read_json_from_file


PUFCSV_YEAR = 2009


class Records(object):
    """
    Constructor for the tax-filing-unit records class.

    Parameters
    ----------
    data: string or Pandas DataFrame
        string describes CSV file in which records data reside;
        DataFrame already contains records data;
        default value is the string 'puf.csv'
        For details on how to use your own data with the Tax-Calculator,
        look at the test_Calculator_using_nonstd_input() function in the
        tests/test_calculate.py file.

    exact_calculations: boolean
        specifies whether or not exact tax calculations are done without
        any smoothing of "stair-step" provisions in income tax law;
        default value is false.

    gfactors: Growfactors class instance or None
        containing record data extrapolation (or "blowup") factors

    adjust_ratios: string or Pandas DataFrame or None
        string describes CSV file in which adjustment ratios reside;
        DataFrame already contains adjustment ratios;
        None creates empty adjustment-ratios DataFrame;
        default value is filename of the default adjustment ratios.

    weights: string or Pandas DataFrame or None
        string describes CSV file in which weights reside;
        DataFrame already contains weights;
        None creates empty sample-weights DataFrame;
        default value is filename of the default weights.

    start_year: integer
        specifies calendar year of the data;
        default value is PUFCSV_YEAR.
        NOTE: if specifying your own data (see above) as being a custom
              data set, be sure to explicitly set start_year to the
              custom data's calendar year.  For details on how to
              use your own data with the Tax-Calculator, read the
              DATAPREP.md file in the top-level directory and then
              look at the test_Calculator_using_nonstd_input()
              function in the taxcalc/tests/test_calculate.py file.

    Raises
    ------
    ValueError:
        if data is not the appropriate type.
        if taxpayer and spouse variables do not add up to filing-unit total.
        if dividends is less than qualified dividends.
        if gfactors is not None or a Growfactors class instance.
        if start_year is not an integer.
        if files cannot be found.

    Returns
    -------
    class instance: Records

    Notes
    -----
    Typical usage is "recs = Records()", which uses all the default
    parameters of the constructor, and therefore, imputed variables
    are generated to augment the data and initial-year grow factors
    are applied to the data.  There are situations in which you need
    to specify the values of the Record constructor's arguments, but
    be sure you know exactly what you are doing when attempting this.
    """
    # suppress pylint warnings about unrecognized Records variables:
    # pylint: disable=no-member
    # suppress pylint warnings about uppercase variable names:
    # pylint: disable=invalid-name
    # suppress pylint warnings about too many class instance attributes:
    # pylint: disable=too-many-instance-attributes

    PUF_YEAR = PUFCSV_YEAR
    CUR_PATH = os.path.abspath(os.path.dirname(__file__))
    WEIGHTS_FILENAME = 'puf_weights.csv'
    WEIGHTS_PATH = os.path.join(CUR_PATH, WEIGHTS_FILENAME)
    ADJUST_RATIOS_FILENAME = 'puf_ratios.csv'
    ADJUST_RATIOS_PATH = os.path.join(CUR_PATH, ADJUST_RATIOS_FILENAME)
    EVARS_PATH = os.path.join(CUR_PATH, 'evars.json')

    # Load metadata about all Records variables
    EVAR_INFO = read_json_from_file(EVARS_PATH)

    # Read variables
    INTEGER_READ_VARS = set(
        k for k, v in EVAR_INFO['in'].items() if v['format'] == 'int'
    )
    FLOAT_READ_VARS = set(
        k for k, v in EVAR_INFO['in'].items() if v['format'] == 'float'
    )
    MUST_READ_VARS = set(
        k for k, v in EVAR_INFO['in'].items() if v.get('required')
    )
    USABLE_READ_VARS = INTEGER_READ_VARS | FLOAT_READ_VARS

    # Calculated variables
    BINARY_CALCULATED_VARS = set(
        k for k, v in EVAR_INFO['out'].items() if v['format'] == 'binary'
    )
    INTEGER_CALCULATED_VARS = set(
        k for k, v in EVAR_INFO['out'].items() if v['format'] == 'int'
    )
    FLOAT_CALCULATED_VARS = set(
        k for k, v in EVAR_INFO['out'].items() if v['format'] == 'float'
    )
    CALCULATED_VARS = \
        BINARY_CALCULATED_VARS | \
        INTEGER_CALCULATED_VARS | \
        FLOAT_CALCULATED_VARS

    CHANGING_CALCULATED_VARS = FLOAT_CALCULATED_VARS

    def __init__(self,
                 data='puf.csv',
                 exact_calculations=False,
                 gfactors=Growfactors(),
                 weights=WEIGHTS_PATH,
                 adjust_ratios=ADJUST_RATIOS_PATH,
                 start_year=PUFCSV_YEAR):
        """
        Records class constructor
        """
        # pylint: disable=too-many-arguments
        # read specified data
        self._read_data(data, exact_calculations)
        # check that three sets of split-earnings variables have valid values
        msg = 'expression "{0} == {0}p + {0}s" is not true for every record'
        if not np.allclose(self.e00200, (self.e00200p + self.e00200s),
                           rtol=0.0, atol=0.001):
            raise ValueError(msg.format('e00200'))
        if not np.allclose(self.e00900, (self.e00900p + self.e00900s),
                           rtol=0.0, atol=0.001):
            raise ValueError(msg.format('e00900'))
        if not np.allclose(self.e02100, (self.e02100p + self.e02100s),
                           rtol=0.0, atol=0.001):
            raise ValueError(msg.format('e02100'))
        # check that ordinary dividends are no less than qualified dividends
        other_dividends = np.maximum(0., self.e00600 - self.e00650)
        if not np.allclose(self.e00600, self.e00650 + other_dividends,
                           rtol=0.0, atol=0.001):
            msg = 'expression "e00600 >= e00650" is not true for every record'
            raise ValueError(msg)
        # handle grow factors
        is_correct_type = isinstance(gfactors, Growfactors)
        if gfactors is not None and not is_correct_type:
            msg = 'gfactors is neither None nor a Growfactors instance'
            raise ValueError(msg)
        self.gfactors = gfactors
        # read sample weights
        self.WT = None
        self._read_weights(weights)
        self.ADJ = None
        self._read_adjust(adjust_ratios)
        # weights must be same size as tax record data
        if not self.WT.empty and self.dim != len(self.WT):
            frac = float(self.dim) / len(self.WT)
            self.WT = self.WT.iloc[self.index]
            self.WT = self.WT / frac
        # specify current_year and FLPDYR values
        if isinstance(start_year, int):
            self._current_year = start_year
            self.FLPDYR.fill(start_year)
        else:
            msg = 'start_year is not an integer'
            raise ValueError(msg)
        # consider applying initial-year grow factors
        if gfactors is not None and start_year == Records.PUF_YEAR:
            self._blowup(start_year)
        # construct sample weights for current_year
        wt_colname = 'WT{}'.format(self.current_year)
        if wt_colname in self.WT.columns:
            self.s006 = self.WT[wt_colname] * 0.01

    @property
    def current_year(self):
        """
        Return current calendar year of Records.
        """
        return self._current_year

    def increment_year(self):
        """
        Adds one to current year.
        Also, does blowup and reweighting for the new current year.
        """
        self._current_year += 1
        # apply variable extrapolation growfactors
        if self.gfactors is not None:
            self._blowup(self.current_year)
        # apply variable adjustment ratios
        self._adjust(self.current_year)
        # specify current-year sample weights
        if self.WT is not None:
            wt_colname = 'WT{}'.format(self.current_year)
            if wt_colname in self.WT.columns:
                self.s006 = self.WT[wt_colname] * 0.01

    def set_current_year(self, new_current_year):
        """
        Sets current year to specified value and updates FLPDYR variable.
        Unlike increment_year method, extrapolation & reweighting are skipped.
        """
        self._current_year = new_current_year
        self.FLPDYR.fill(new_current_year)

    # --- begin private methods of Records class --- #

    def _blowup(self, year):
        """
        Applies to variables the grow factors for specified calendar year.
        """
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-locals
        # pylint: disable=unsubscriptable-object
        AWAGE = self.gfactors.factor_value('AWAGE', year)
        AINTS = self.gfactors.factor_value('AINTS', year)
        ADIVS = self.gfactors.factor_value('ADIVS', year)
        ATXPY = self.gfactors.factor_value('ATXPY', year)
        ASCHCI = self.gfactors.factor_value('ASCHCI', year)
        ASCHCL = self.gfactors.factor_value('ASCHCL', year)
        ACGNS = self.gfactors.factor_value('ACGNS', year)
        ASCHEI = self.gfactors.factor_value('ASCHEI', year)
        ASCHEL = self.gfactors.factor_value('ASCHEL', year)
        ASCHF = self.gfactors.factor_value('ASCHF', year)
        AUCOMP = self.gfactors.factor_value('AUCOMP', year)
        ASOCSEC = self.gfactors.factor_value('ASOCSEC', year)
        ACPIM = self.gfactors.factor_value('ACPIM', year)
        AGDPN = self.gfactors.factor_value('AGDPN', year)
        ABOOK = self.gfactors.factor_value('ABOOK', year)
        AIPD = self.gfactors.factor_value('AIPD', year)
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

    def _adjust(self, year):
        """
        Adjust value of income variables to match SOI distributions
        """
        if len(self.ADJ) != 0:
            # Interest income
            self.e00300 *= self.ADJ['INT{}'.format(year)][self.agi_bin]

    def _read_data(self, data, exact_calcs):
        """
        Read Records data from file or use specified DataFrame as data.
        Specifies _exact array depending on boolean value of exact_calcs.
        """
        # pylint: disable=too-many-branches
        if isinstance(data, pd.DataFrame):
            taxdf = data
        elif isinstance(data, six.string_types):
            if data.endswith('gz'):
                taxdf = pd.read_csv(data, compression='gzip')
            else:
                taxdf = pd.read_csv(data)
        else:
            msg = 'data is neither a string nor a Pandas DataFrame'
            raise ValueError(msg)
        self.dim = len(taxdf)
        self.index = taxdf.index
        # create class variables using taxdf column names
        READ_VARS = set()
        self.IGNORED_VARS = set()
        for varname in list(taxdf.columns.values):
            if varname in Records.USABLE_READ_VARS:
                READ_VARS.add(varname)
                if varname in Records.INTEGER_READ_VARS:
                    setattr(self, varname,
                            taxdf[varname].astype(np.int64).values)
                else:
                    setattr(self, varname,
                            taxdf[varname].astype(np.float64).values)
            else:
                self.IGNORED_VARS.add(varname)
        # check that MUST_READ_VARS are all present in taxdf
        if not Records.MUST_READ_VARS.issubset(READ_VARS):
            msg = 'Records data missing one or more MUST_READ_VARS'
            raise ValueError(msg)
        # create other class variables that are set to all zeros
        UNREAD_VARS = Records.USABLE_READ_VARS - READ_VARS
        ZEROED_VARS = Records.CALCULATED_VARS | UNREAD_VARS
        INT_VARS = Records.INTEGER_READ_VARS | Records.INTEGER_CALCULATED_VARS
        for varname in ZEROED_VARS:
            if varname in INT_VARS:
                setattr(self, varname,
                        np.zeros(self.dim, dtype=np.int64))
            else:
                setattr(self, varname,
                        np.zeros(self.dim, dtype=np.float64))
        # create variables derived from MARS, which is in MUST_READ_VARS
        self._num[:] = np.where(self.MARS == 2,
                                2, 1)
        self._sep[:] = np.where(np.logical_or(self.MARS == 3, self.MARS == 6),
                                2, 1)
        # specify value of _exact array
        self._exact[:] = np.where(exact_calcs is True, 1, 0)
        # specify value of ID_Casualty_frt_in_pufcsv_year array
        ryear = 9999  # specify reform year if ID_Casualty_frt changes
        rvalue = 0.0  # specify value of ID_Casualty_frt beginning in ryear
        self.ID_Casualty_frt_in_pufcsv_year[:] = np.where(PUFCSV_YEAR < ryear,
                                                          0.10, rvalue)

    def zero_out_changing_calculated_vars(self):
        """
        Set all CHANGING_CALCULATED_VARS to zero.
        """
        for varname in Records.CHANGING_CALCULATED_VARS:
            var = getattr(self, varname)
            var.fill(0.)

    def _read_weights(self, weights):
        """
        Read Records weights from file or
        use specified DataFrame as data or
        create empty DataFrame if None.
        """
        if weights is None:
            WT = pd.DataFrame({'nothing': []})
            setattr(self, 'WT', WT)
            return
        if isinstance(weights, pd.DataFrame):
            WT = weights
        elif isinstance(weights, six.string_types):
            if os.path.isfile(weights):
                WT = pd.read_csv(weights)
            else:
                WT = read_egg_csv('weights', Records.WEIGHTS_FILENAME)
        else:
            msg = 'weights is not None or a string or a Pandas DataFrame'
            raise ValueError(msg)
        setattr(self, 'WT', WT)

    def _read_adjust(self, adjust_ratios):
        """
        Read Records adjustment ratios from file or uses specified DataFrame
        as data or creates empty DataFrame if None
        """
        if adjust_ratios is None:
            ADJ = pd.DataFrame({'nothing': []})
            setattr(self, 'ADJ', ADJ)
            return
        if isinstance(adjust_ratios, pd.DataFrame):
            ADJ = adjust_ratios
        elif isinstance(adjust_ratios, six.string_types):
            if os.path.isfile(adjust_ratios):
                ADJ = pd.read_csv(adjust_ratios, index_col=0)
            else:
                ADJ = Records._read_egg_csv('adjust_ratios',
                                            Records.ADJUST_RATIOS_FILENAME)
            ADJ = ADJ.transpose()
        else:
            msg = ('adjust_ratios is not None or a string'
                   'or a Pandas DataFrame')
            raise ValueError(msg)
        if ADJ.index.name != 'agi_bin':
            ADJ.index.name = 'agi_bin'
        self.ADJ = ADJ
