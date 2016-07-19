"""
Tax-Calculator tax-filing-unit Records class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 records.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy records.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)


import pandas as pd
import numpy as np
import os
import six
from pkg_resources import resource_stream, Requirement, DistributionNotFound


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

    schR_calculations: boolean
        specifies whether or not Schedule R calculations are done or
        whether the Schedule R credit is set to value of input variable;
        default value is true.

    blowup_factors: string or Pandas DataFrame or None
        string describes CSV file in which blowup factors reside;
        DataFrame already contains blowup factors;
        None creates empty blowup-factors DataFrame;
        default value is filename of the default blowup factors.

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
        if parameters are not the appropriate type.
        if files cannot be found.

    Returns
    -------
    class instance: Records

    Notes
    -----
    Typical usage is "recs = Records()", which uses all the default
    parameters of the constructor, and therefore, imputed variables
    are generated to augment the data and initial-year blowup factors
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
    WEIGHTS_FILENAME = 'WEIGHTS.csv'
    WEIGHTS_PATH = os.path.join(CUR_PATH, WEIGHTS_FILENAME)
    BLOWUP_FACTORS_FILENAME = 'StageIFactors.csv'
    BLOWUP_FACTORS_PATH = os.path.join(CUR_PATH, BLOWUP_FACTORS_FILENAME)

    # specify set of all Record variables that MAY be read by Tax-Calculator:
    VALID_READ_VARS = set([
        'DSI', 'EIC', 'FDED', 'FLPDYR',
        'f2441', 'f6251', 'n24', 'XTOT',
        'e00200', 'e00300', 'e00400', 'e00600', 'e00650', 'e00700', 'e00800',
        'e00200p', 'e00200s',
        'e00900', 'e01100', 'e01200', 'e01400', 'e01500', 'e01700',
        'e00900p', 'e00900s',
        'e02000', 'e02100', 'e02300', 'e02400', 'e03150', 'e03210',
        'e02100p', 'e02100s',
        'e03220', 'e03230', 'e03270', 'e03240', 'e03290',
        'e03400', 'e03500',
        'e07240', 'e07260', 'e07300',
        'e07400', 'e07600', 'p08000',
        'e09700', 'e09800', 'e09900',
        'e11550', 'e11070', 'e11200',
        'e11580',
        'e17500', 'e18400', 'e18500',
        'e19200', 'e19800', 'e20100',
        'e20400', 'e20500', 'p22250',
        'p23250', 'e24515', 'e24518',
        'p25470',
        'e26270',
        'e27200', 'e32800', 'e03300',
        'e58990',
        'e62900',
        'p87482', 'e87487', 'e87492', 'e87497', 'p87521',
        'e87530',
        'MARS', 'MIDR', 'RECID',
        'cmbtp_standard', 'cmbtp_itemizer',
        'age_head', 'age_spouse', 'blind_head', 'blind_spouse',
        's006', 'filer'])

    # specify set of all Record variables that MUST be read by Tax-Calculator:
    MUST_READ_VARS = set(['RECID', 'MARS'])

    # specify which VALID_READ_VARS should be int64 (rather than float64):
    INTEGER_READ_VARS = set([
        'DSI', 'EIC', 'FDED', 'FLPDYR',
        'f2441', 'f6251',
        'n24', 'XTOT',
        'MARS', 'MIDR', 'RECID',
        'age_head', 'age_spouse', 'blind_head', 'blind_spouse'])

    # specify set of all Record variables that cannot be read in:
    CALCULATED_VARS = set([
        'f2555',
        '_exact',
        '_calc_schR', 'c07200',
        'c00650', 'c00100',
        'c04470', 'c04600', 'c21060', 'c21040', 'c17000',
        'c18300', 'c20800', 'c02900', 'c02700', 'c23650',
        'c01000', 'c02500',
        'c11580',
        '_sey', '_earned', '_earned_p', '_earned_s',
        'c09400', '_feided', 'ymod', 'ymod1', '_posagi',
        '_xyztax', '_avail',
        '_taxinc', 'c04800', '_feitax', 'c24517',
        '_taxbc', 'c60000', '_standard', 'c24516',
        'c05700', 'c32880', 'c32890', 'c32800',
        'c05800', 'c59560',
        'c87521', 'c87550', 'c07180',
        'c07230', '_precrd', 'c07220', 'c59660',
        'c09200', 'c07100', '_eitc',
        'c02650',
        '_prexmp',
        '_fica', '_fica_was', 'c03260',
        '_sep', '_num',
        'c04500', 'c05200',
        'c24505', 'c24520',
        'c62720', 'c60260', 'c63100',
        'c60200', 'c60240', 'c60220', 'c60130', 'c62730',
        'c62100', '_cmbtp', '_amtsepadd',
        'c62600', 'c62700', '_alminc', 'c62760',
        '_amtfei', 'c62780', 'c62900', 'c63000', 'c62740',
        '_ngamty', 'c62745', '_tamt2', '_amt5pc',
        '_amt15pc', '_amt25pc', 'c62747', 'c62755', 'c62770',
        '_amt20pc', 'c62800', 'c09600',
        'c33200',
        '_extrastd', 'ID_Casualty_frt_in_pufcsv_year',
        'c11070', 'c87482',
        'c87487', 'c87492', 'c87497', 'c87483', 'c87488',
        'c87493', 'c87498', 'c87654',
        'c87656', 'c87658', 'c87660', 'c87662',
        'c10960', 'c87668',
        'c82925', 'c82930', 'c82935',
        'c82880', 'c82885', 'c82890', 'c82900',
        'c82905', 'c82910', 'c82915', 'c82920', 'c82937',
        'c82940', 'c08800',
        '_othertax', 'NIIT',
        '_iitax', '_refund', '_amed',
        '_expanded_income', 'c07300',
        'c07600', 'c07240',
        '_surtax', '_combined', 'personal_credit'])

    INTEGER_CALCULATED_VARS = set([
        '_num', '_sep', '_exact', '_calc_schR', 'f2555'])

    def __init__(self,
                 data='puf.csv',
                 exact_calculations=False,
                 schR_calculations=True,
                 blowup_factors=BLOWUP_FACTORS_PATH,
                 weights=WEIGHTS_PATH,
                 start_year=PUFCSV_YEAR):
        """
        Records class constructor
        """
        # pylint: disable=too-many-arguments
        # read specified data
        self._read_data(data, exact_calculations, schR_calculations)
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
        # read extrapolation blowup factors and sample weights
        self._read_blowup(blowup_factors)
        self._read_weights(weights)
        # specify current_year and FLPDYR values
        if isinstance(start_year, int):
            self._current_year = start_year
            self.FLPDYR.fill(start_year)
        else:
            msg = 'start_year is not an integer'
            raise ValueError(msg)
        # consider applying initial-year blowup factors
        if self.BF.empty is False and self.current_year == Records.PUF_YEAR:
            self._extrapolate_in_puf_year()
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
        Also, does variable blowup and reweighting for the new current year.
        """
        self._current_year += 1
        # apply Stage 1 Extrapolation blowup factors
        self._blowup(self.current_year)
        # specify Stage 2 Extrapolation sample weights
        wt_colname = 'WT{}'.format(self.current_year)
        if wt_colname in self.WT.columns:
            self.s006 = self.WT[wt_colname] * 0.01

    def set_current_year(self, new_current_year):
        """
        Sets current year to specified value and updates FLPDYR variable.
        Unlike increment_year method, blowup and reweighting are skipped.
        """
        self._current_year = new_current_year
        self.FLPDYR.fill(new_current_year)

    # --- begin private methods of Records class --- #

    def _blowup(self, year):
        """
        Applies blowup factors (BF) to variables for specified calendar year.
        """
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-locals
        AWAGE = self.BF.AWAGE[year]
        AINTS = self.BF.AINTS[year]
        ADIVS = self.BF.ADIVS[year]
        ATXPY = self.BF.ATXPY[year]
        ASCHCI = self.BF.ASCHCI[year]
        ASCHCL = self.BF.ASCHCL[year]
        ACGNS = self.BF.ACGNS[year]
        ASCHEI = self.BF.ASCHEI[year]
        ASCHEL = self.BF.ASCHEL[year]
        ASCHF = self.BF.ASCHF[year]
        AUCOMP = self.BF.AUCOMP[year]
        ASOCSEC = self.BF.ASOCSEC[year]
        ACPIM = self.BF.ACPIM[year]
        AGDPN = self.BF.AGDPN[year]
        ABOOK = self.BF.ABOOK[year]
        AIPD = self.BF.AIPD[year]
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
        self.e11580 *= ATXPY
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
        self.p87482 *= ATXPY
        self.e87487 *= ATXPY
        self.e87492 *= ATXPY
        self.e87497 *= ATXPY
        self.cmbtp_itemizer *= ATXPY
        self.cmbtp_standard *= ATXPY

    def _read_data(self, data, exact_calcs, schR_calcs):
        """
        Read Records data from file or use specified DataFrame as data.
        Specifies _exact array depending on boolean value of exact_calcs.
        Specifies _calc_schR array depending on boolean value of schR_calcs.
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
        # create class variables using taxdf column names
        READ_VARS = set()
        for varname in list(taxdf.columns.values):
            if varname not in Records.VALID_READ_VARS:
                msg = 'Records data variable name {} not in VALID_READ_VARS'
                raise ValueError(msg.format(varname))
            READ_VARS.add(varname)
            if varname in Records.INTEGER_READ_VARS:
                setattr(self, varname,
                        taxdf[varname].astype(np.int64).values)
            else:
                setattr(self, varname,
                        taxdf[varname].astype(np.float64).values)
        # check that MUST_READ_VARS are all present in taxdf
        if not Records.MUST_READ_VARS.issubset(READ_VARS):
            msg = 'Records data missing one or more MUST_READ_VARS'
            raise ValueError(msg)
        # create other class variables that are set to all zeros
        UNREAD_VARS = Records.VALID_READ_VARS - READ_VARS
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
        # specify value of _calc_schR array
        self._calc_schR[:] = np.where(schR_calcs is True, 1, 0)
        # specify value of ID_Casualty_frt_in_pufcsv_year array
        ryear = 9999  # specify reform year if ID_Casualty_frt changes
        rvalue = 0.0  # specify value of ID_Casualty_frt beginning in ryear
        self.ID_Casualty_frt_in_pufcsv_year[:] = np.where(PUFCSV_YEAR < ryear,
                                                          0.10, rvalue)

    @staticmethod
    def _read_egg_csv(vname, fpath, **kwargs):
        """
        Read csv file with fpath containing vname data from EGG;
        return dict of vname data
        """
        try:
            # grab vname data from EGG distribution
            path_in_egg = os.path.join('taxcalc', fpath)
            vname_fname = resource_stream(
                Requirement.parse('taxcalc'), path_in_egg)
            vname_dict = pd.read_csv(vname_fname, **kwargs)
        except (DistributionNotFound, IOError):
            msg = 'could not read {} file from EGG'
            raise ValueError(msg.format(vname))
        return vname_dict

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
                WT = Records._read_egg_csv('weights',
                                           Records.WEIGHTS_FILENAME)
        else:
            msg = 'weights is not None or a string or a Pandas DataFrame'
            raise ValueError(msg)
        setattr(self, 'WT', WT)

    def _read_blowup(self, blowup_factors):
        """
        Read Records blowup factors from file or
        use specified DataFrame as data or
        creates empty DataFrame if None.
        """
        if blowup_factors is None:
            BF = pd.DataFrame({'nothing': []})
            setattr(self, 'BF', BF)
            return
        if isinstance(blowup_factors, pd.DataFrame):
            BF = blowup_factors
        elif isinstance(blowup_factors, six.string_types):
            if os.path.isfile(blowup_factors):
                BF = pd.read_csv(blowup_factors, index_col='YEAR')
            else:
                BF = Records._read_egg_csv('blowup_factors',
                                           Records.BLOWUP_FACTORS_FILENAME,
                                           index_col='YEAR')
        else:
            msg = ('blowup_factors is not None or a string '
                   'or a Pandas DataFrame')
            raise ValueError(msg)
        BF.AGDPN = BF.AGDPN / BF.APOPN
        BF.ATXPY = BF. ATXPY / BF. APOPN
        BF.AWAGE = BF.AWAGE / BF.APOPN
        BF.ASCHCI = BF.ASCHCI / BF.APOPN
        BF.ASCHCL = BF.ASCHCL / BF.APOPN
        BF.ASCHF = BF.ASCHF / BF.APOPN
        BF.AINTS = BF.AINTS / BF.APOPN
        BF.ADIVS = BF.ADIVS / BF.APOPN
        BF.ASCHEI = BF.ASCHEI / BF.APOPN
        BF.ASCHEL = BF.ASCHEL / BF.APOPN
        BF.ACGNS = BF.ACGNS / BF.APOPN
        BF.ABOOK = BF.ABOOK / BF.APOPN
        BF.ASOCSEC = BF.ASOCSEC / BF.APOPSNR
        BF = 1.0 + BF.pct_change()
        setattr(self, 'BF', BF)

    def _extrapolate_in_puf_year(self):
        """
        Calls appropriate current_year extrapolation method.
        """
        if self.current_year == 2009:
            self._extrapolate_2009_puf()

    def _extrapolate_2009_puf(self):
        """
        Initial year blowup factors for 2009 IRS-PUF/Census-CPS merged data.
        """
        year = 2009
        self.BF.AGDPN[year] = 1.0
        self.BF.ATXPY[year] = 1.0
        self.BF.AWAGE[year] = 1.0053
        self.BF.ASCHCI[year] = 1.0041
        self.BF.ASCHCL[year] = 1.1629
        self.BF.ASCHF[year] = 1.0
        self.BF.AINTS[year] = 1.0357
        self.BF.ADIVS[year] = 1.0606
        self.BF.ASCHEI[year] = 1.1089
        self.BF.ASCHEL[year] = 1.2953
        self.BF.ACGNS[year] = 1.1781
        self.BF.ABOOK[year] = 1.0
        self.BF.ARETS[year] = 1.0026
        self.BF.APOPN[year] = 1.0
        self.BF.ACPIU[year] = 1.0
        self.BF.APOPDEP[year] = 1.0
        self.BF.ASOCSEC[year] = 0.9941
        self.BF.ACPIM[year] = 1.0
        self.BF.AUCOMP[year] = 1.0034
        self.BF.APOPSNR[year] = 1.0
        self.BF.AIPD[year] = 1.0
        self._blowup(year)
