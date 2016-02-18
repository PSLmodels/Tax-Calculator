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
from numba import vectorize, float64
from pkg_resources import resource_stream, Requirement


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

    blowup_factors: string or Pandas DataFrame
        string describes CSV file in which blowup factors reside;
        DataFrame already contains blowup factors;
        default value is filename of the default blowup factors

    weights: string or Pandas DataFrame
        string describes CSV file in which weights reside;
        DataFrame already contains weights;
        default value is filename of the default weights

    start_year: None or integer
        None implies current_year is set to PUF_YEAR (see below);
        integer implies current_year is set to start_year;
        default value is None
        NOTE: if specifying data (see above) as being a custom
              data set, be sure to explicitly set start_year to the
              custom data's calendar year.  For details on how to
              use your own data with the Tax-Calculator, look at the
              test_Calculator_using_nonstd_input() function in the
              tests/test_calculate.py file.

    consider_imputations: boolean
        True implies that if current_year (see start_year above) equals
        PUF_YEAR (see below), then call _impute_variables() method;
        False implies never call _impute_variables() method;
        default value is True
        For details on how to use your own data with the Tax-Calculator,
        look at the test_Calculator_using_nonstd_input() function in the
        tests/test_calculate.py file.

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
    are applied to the data. Explicitly setting consider_imputation to
    False and/or the start_year to something other than Records.PUF_YEAR
    will cause this variable-imputation and initial-year-blowup logic to
    be skipped.  There are situations in which this is exactly what is
    desired, but more often than not, skipping the imputation and blowup
    logic would be a mistake.  In other words, do not explicitly specify
    consider_imputations=False or specify the start_year in the Records
    class constructor unless you know exactly what you are doing.
    """
    # suppress pylint warnings about unrecognized Records variables:
    # pylint: disable=no-member
    # suppress pylint warnings about uppercase variable names:
    # pylint: disable=invalid-name
    # suppress pylint warnings about too many class instance attributes:
    # pylint: disable=too-many-instance-attributes

    PUF_YEAR = 2009

    CUR_PATH = os.path.abspath(os.path.dirname(__file__))
    WEIGHTS_FILENAME = "WEIGHTS.csv"
    WEIGHTS_PATH = os.path.join(CUR_PATH, WEIGHTS_FILENAME)
    BLOWUP_FACTORS_FILENAME = "StageIFactors.csv"
    BLOWUP_FACTORS_PATH = os.path.join(CUR_PATH, BLOWUP_FACTORS_FILENAME)

    # specify set of all Record variables that MAY be read by Tax-Calculator:
    VALID_READ_VARS = set([
        'AGIR1', 'DSI', 'EFI', 'EIC', 'ELECT', 'FDED', 'FLPDYR', 'FLPDMO',
        'f2441', 'f3800', 'f6251', 'f8582', 'f8606', 'f8829', 'f8910', 'f8936',
        'n20', 'n24', 'n25', 'n30', 'PREP', 'SCHB', 'SCHCF', 'SCHE',
        'TFORM', 'IE', 'TXST', 'XFPT', 'XFST',
        'XOCAH', 'XOCAWH', 'XOODEP', 'XOPAR', 'XTOT',
        'e00200', 'e00300', 'e00400', 'e00600', 'e00650', 'e00700', 'e00800',
        'e00200p', 'e00200s',
        'e00900', 'e01000', 'e01100', 'e01200', 'e01400', 'e01500', 'e01700',
        'e00900p', 'e00900s',
        'e02000', 'e02100', 'e02300', 'e02400', 'e02500', 'e03150', 'e03210',
        'e02100p', 'e02100s',
        'e03220', 'e03230', 'e03260', 'e03270', 'e03240', 'e03290', 'e03300',
        'e03400', 'e03500', 'e00100', 'p04470', 'e04250', 'e04600', 'e04800',
        'e05100', 'e05200', 'e05800', 'e06000', 'e06200', 'e06300', 'e09600',
        'e07180', 'e07200', 'e07220', 'e07230', 'e07240', 'e07260', 'e07300',
        'e07400', 'e07600', 'p08000', 'e07150', 'e06500', 'e08800', 'e09400',
        'e09700', 'e09800', 'e09900', 'e10300', 'e10700', 'e10900', 'e10950',
        'e10960', 'e15100', 'e15210', 'e15250', 'e15360', 'e18600', 'e59560',
        'e59680', 'e59700', 'e59720', 'e11550', 'e11070', 'e11100', 'e11200',
        'e11300', 'e11400', 'e11570', 'e11580', 'e11581', 'e11582', 'e11583',
        'e10605', 'e11900', 'e12000', 'e12200', 'e17500', 'e18400', 'e18500',
        'e19200', 'e19550', 'e19800', 'e20100', 'e19700', 'e20550', 'e20600',
        'e20400', 'e20800', 'e20500', 'e21040', 'p22250', 'e22320', 'e22370',
        'p23250', 'e24515', 'e24516', 'e24518', 'e24535', 'e24560', 'e24598',
        'e24615', 'e24570', 'p25350', 'p25380', 'p25470', 'p25700', 'e25820',
        'e25850', 'e25860', 'e25940', 'e25980', 'e25920', 'e25960', 'e26110',
        'e26170', 'e26190', 'e26160', 'e26180', 'e26270', 'e26100', 'e26390',
        'e26400', 'e27200', 'e30400', 'e30500', 'e32800', 'e33000', 'e53240',
        'e53280', 'e53410', 'e53300', 'e53317', 'e53458', 'e58950', 'e58990',
        'p60100', 'p61850', 'e60000', 'e62100', 'e62900', 'e62720', 'e62730',
        'e62740', 'p65300', 'p65400', 'p87482', 'p87521', 'e68000', 'e82200',
        't27800', 's27860', 'p27895', 'e87530', 'e87550', 'e87870', 'e87875',
        'e87880', 'MARS', 'MIDR', 'RECID', 'gender',
        'wage_head', 'wage_spouse', 'earnsplit',
        'age', 'agedp1', 'agedp2', 'agedp3', 'AGERANGE',
        's006', 's008', 's009', 'WSAMP', 'TXRT', 'filer', 'matched_weight'])

    # specify set of all Record variables that MUST be read by Tax-Calculator:
    MUST_READ_VARS = set(['RECID', 'MARS'])

    # specify subset of VALID_READ_VARS that are not e-code variables and
    # that are unused by Tax-Calculator:
    UNUSED_READ_VARS = set([
        'AGIR1', 'EFI', 'ELECT', 'FLPDMO',
        'f3800', 'f8582', 'f8606', 'f8829', 'f8910', 'f8936',
        'n20', 'n25', 'n30', 'PREP', 'SCHB', 'SCHCF', 'SCHE',
        'TFORM', 'IE', 'TXST', 'XFPT', 'XFST',
        'XOCAH', 'XOCAWH', 'XOODEP', 'XOPAR',
        'gender',
        'earnsplit',
        'agedp1', 'agedp2', 'agedp3',
        's008', 's009', 'WSAMP', 'TXRT', 'filer', 'matched_weight'])
    # TODO: the long-term objective is to remove these UNUSED_READ_VARS
    #       from the puf.csv input file so that this set can be removed
    #       from the Records class code.
    # Each removal from UNUSED_READ_VARS set requires removal of same
    # variable from VALID_READ_VARS set.

    # specify which VALID_READ_VARS should be int64 (rather than float64):
    INTEGER_READ_VARS = set([
        'DSI', 'EIC', 'FDED', 'FLPDYR',
        'f2441', 'f6251',
        'n24',
        'XTOT',
        'MARS', 'MIDR', 'RECID',
        'age', 'AGERANGE'])

    # specify set of all Record variables that cannot be read in:
    CALCULATED_VARS = set([
        'e35300_0', 'e35600_0', 'e35910_0', 'x03150', 'e03600',
        'e03280', 'e03900', 'e04000', 'e03700', 'c23250',
        'e23660', 'f2555', 'e02800', 'e02610', 'e02540',
        'e02615', 'SSIND', 'e18800', 'e18900',
        'e20950', 'e19500', 'e19570', 'e19400', 'c20400',
        'e20200', 'e20900', 'e21000', 'e21010', 'e02600',
        '_exact', 'e11055', 'e00250', 'e30100',
        'e04200', 'e37717', 'e04805', 'AGEP', 'AGES', 'PBI',
        'SBI', 't04470', 'e58980', 'c00650', 'c00100',
        'c04470', 'c04600', 'c21060', 'c21040', 'c17000',
        'c18300', 'c20800', 'c02900', 'c02700', 'c23650',
        'c01000', 'c02500', 'e24583', '_cmp',
        'e59440', 'e59470', 'e59400', 'e10105', 'e83200_0',
        'e59410', 'e59420', 'e74400', 'x62720', 'x60260',
        'x60240', 'x60220', 'x60130', 'x62730', 'e60290',
        'DOBYR', 'SDOBYR', 'DOBMD', 'SDOBMD', 'e62600',
        'x62740', '_fixeic', 'e32880', 'e32890', 'CDOB1',
        'CDOB2', 'e32750', 'e32775', 'e33420', 'e33430',
        'e33450', 'e33460', 'e33465', 'e33470', 'x59560',
        'EICYB1', 'EICYB2', 'EICYB3', 'e83080', 'e25360',
        'e25430', 'e25400', 'e25500', 'e26210', 'e26340',
        'e26205', 'e26320', 'e87487', 'e87492', 'e07170',
        'e87497', 'e87526', 'e87522', 'e87524', 'e87528',
        'e07960', 'e07700', 'e07250', 't07950',
        'e82882', 'e82880', 'e07500', 'e08001', 'e07970',
        'e07980', 'e10000', 'e10100', 'e10050', 'e10075',
        'e09805', 'e09710', 'e09720', 'e87900', 'e87905',
        'e87681', 'e87682', 'e11451', 'e11452', 'e11601',
        'e11602', 'e60300', 'e60860', 'e60840', 'e60630',
        'e60550', 'e60720', 'e60430', 'e60500', 'e60340',
        'e60680', 'e60600', 'e60405', 'e60440', 'e60420',
        'e60410', 'e61400', 'e60660', 'e60480', 'e62000',
        'e60250', 'e40223', '_earned', '_sey',
        'c09400', '_feided', '_ymod', '_ymod1', '_posagi',
        'xtxcr1xtxcr10', '_xyztax', '_avail', 'e85070',
        '_taxinc', 'c04800', '_feitax', 'c05750', 'c24517',
        '_taxbc', 'c60000', '_standard', 'c24516', 'c25420',
        'c05700', 'c32880', 'c32890', '_dclim', 'c32800',
        'c33000', 'c05800', '_othtax', 'c59560', '_agep',
        '_ages', 'c87521', 'c87550', 'c07180',
        'c07230', '_precrd', 'c07220', 'c59660', 'c07970',
        'c08795', 'c09200', 'c07100', '_eitc', 'c59700',
        'c10950', '_ymod2', '_ymod3', 'c02650', '_agierr',
        '_ywossbe', '_ywossbc', '_prexmp', 'c17750',
        '_statax', 'c37703', 'c20500', 'c20750', 'c19200',
        'c19700', '_nonlimited', '_limitratio', '_phase2_i',
        '_fica', '_fica_was', 'c03260', 'c11055', 'c15100', '_numextra',
        '_num', '_txpyers', 'c15200', '_othded', 'c04100', 'c04200',
        'c04500', '_amtstd', '_oldfei', 'c05200', '_cglong',
        '_noncg', '_hasgain', '_dwks9', '_dwks5', '_dwks12',
        '_dwks16', '_dwks17', '_dwks21', '_dwks25', '_dwks26',
        '_dwks28', '_dwks31', 'c24505', 'c24510', 'c24520',
        'c24530', 'c24540', 'c24534', 'c24597', 'c24598',
        'c24610', 'c24615', 'c24550', 'c24570', '_addtax',
        'c24560', '_taxspecial', 'c24580', 'c05100',
        'c59430', 'c59450', 'c59460', '_line17', '_line19',
        '_line22', '_line30', '_line31', '_line32', '_line36',
        '_line33', '_line34', '_line35', 'c59485', 'c59490',
        '_s1291', '_parents', 'c62720', 'c60260', 'c63100',
        'c60200', 'c60240', 'c60220', 'c60130', 'c62730',
        '_addamt', 'c62100', '_cmbtp', '_edical', '_amtsepadd',
        'c62600', 'c62700', '_alminc', 'c62760',
        '_amtfei', 'c62780', 'c62900', 'c63000', 'c62740',
        '_ngamty', 'c62745', 'y62745', '_tamt2', '_amt5pc',
        '_amt15pc', '_amt25pc', 'c62747', 'c62755', 'c62770',
        '_amt20pc', 'c62800', 'c09600', '_ncu13',
        '_seywage', 'c33465', 'c33470', 'c33475', 'c33480',
        'c32840', '_tratio', 'c33200', 'c33400',
        '_ieic', '_modagi',
        '_val_ymax', '_preeitc', '_val_rtbase', '_val_rtless',
        '_dy', 'c11070', '_nctcr', '_ctcagi', 'c87482',
        'c87487', 'c87492', 'c87497', 'c87483', 'c87488',
        'c87493', 'c87498', 'c87540', 'c87530', 'c87654',
        'c87656', 'c87658', 'c87660', 'c87662', 'c87664',
        'c87666', 'c10960', 'c87668', 'c87681', 'c87560',
        'c87570', 'c87580', 'c87590', 'c87600', 'c87610',
        'c87620', '_ctc1', '_ctc2', '_regcrd', '_exocrd',
        '_ctctax', 'c82925', 'c82930', 'c82935',
        'c82880', 'c82885', 'c82890', 'c82900',
        'c82905', 'c82910', 'c82915', 'c82920', 'c82937',
        'c82940', 'e59660', '_othadd', 'y07100',
        'x07100', 'c08800', 'e08795', 'x07400', 'c59680',
        '_othertax', 'e82915', 'e82940', 'SFOBYR', 'NIIT',
        'c59720', '_comb', 'c07150', 'c10300', '_iitax',
        '_refund', 'c11600', 'e11450', 'e82040', 'e11500',
        '_amed', '_xlin3', '_xlin6', '_cmbtp_itemizer',
        '_cmbtp_standard', '_expanded_income', 'c07300',
        'c07600', 'c07240', 'c62100_everyone',
        '_surtax', '_combined', 'x04500', '_personal_credit'])

    def __init__(self,
                 data="puf.csv",
                 blowup_factors=BLOWUP_FACTORS_PATH,
                 weights=WEIGHTS_PATH,
                 start_year=None,
                 consider_imputations=True):
        """
        Records class constructor
        """
        # pylint: disable=unused-argument,too-many-arguments
        self._read_data(data)
        self._read_blowup(blowup_factors)
        self._read_weights(weights)
        if start_year is None:
            self._current_year = Records.PUF_YEAR
            self.FLPDYR.fill(Records.PUF_YEAR)
        elif isinstance(start_year, int):
            self._current_year = start_year
            self.FLPDYR.fill(start_year)
        else:
            msg = ('Records.constructor start_year is neither None nor '
                   'an integer')
            raise ValueError(msg)
        if consider_imputations and self.current_year == Records.PUF_YEAR:
            self._impute_variables()
            self._extrapolate_2009_puf()

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
        # Implement Stage 1 Extrapolation blowup factors
        self._blowup(self.current_year)
        # Implement Stage 2 Extrapolation reweighting
        # pylint: disable=attribute-defined-outside-init
        self.s006 = self.WT["WT" + str(self.current_year)] * 0.01

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
        # pylint: disable=attribute-defined-outside-init
        # pylint: disable=too-many-locals
        # local copies of blowup factors for specified year:
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
        # apply blowup factors to variables:
        self.e00200 = self.e00200 * AWAGE
        self.e00200p = self.e00200p * AWAGE
        self.e00200s = self.e00200s * AWAGE
        self.e00300 = self.e00300 * AINTS
        self.e00400 = self.e00400 * AINTS
        self.e00600 = self.e00600 * ADIVS
        self.e00650 = self.e00650 * ADIVS
        self.e00700 = self.e00700 * ATXPY
        self.e00800 = self.e00800 * ATXPY
        self.e00900 = np.where(self.e00900 >= 0,
                               self.e00900 * ASCHCI, self.e00900 * ASCHCL)
        self.e00900s = np.where(self.e00900s >= 0,
                                self.e00900s * ASCHCI, self.e00900s * ASCHCL)
        self.e00900p = np.where(self.e00900p >= 0,
                                self.e00900p * ASCHCI, self.e00900p * ASCHCL)
        self.e01000 = np.where(self.e01000 >= 0,
                               self.e01000 * ACGNS, self.e01000)
        self.e01100 = self.e01100 * ACGNS
        self.e01200 = self.e01200 * ACGNS
        self.e01400 = self.e01400 * ATXPY
        self.e01500 = self.e01500 * ATXPY
        self.e01700 = self.e01700 * ATXPY
        self.e02000 = np.where(self.e02000 >= 0,
                               self.e02000 * ASCHEI, self.e02000 * ASCHEL)
        self.e02100 = self.e02100 * ASCHF
        self.e02100p = self.e02100p * ASCHF
        self.e02100s = self.e02100s * ASCHF
        self.e02300 = self.e02300 * AUCOMP
        self.e02400 = self.e02400 * ASOCSEC
        self.e02500 = self.e02500 * ASOCSEC
        self.e03150 = self.e03150 * ATXPY
        self.e03210 = self.e03210 * ATXPY
        self.e03220 = self.e03220 * ATXPY
        self.e03230 = self.e03230 * ATXPY
        self.e03260 = self.e03260 * ASCHCI
        self.e03270 = self.e03270 * ACPIM
        self.e03240 = self.e03240 * AGDPN
        self.e03290 = self.e03290 * ACPIM
        self.e03300 = self.e03300 * ATXPY
        self.e03400 = self.e03400 * ATXPY
        self.e03500 = self.e03500 * ATXPY
        self.e07230 = self.e07230 * ATXPY
        self.e07240 = self.e07240 * ATXPY
        self.e07260 = self.e07260 * ATXPY
        self.e07300 = self.e07300 * ABOOK
        self.e07400 = self.e07400 * ABOOK
        self.p08000 = self.p08000 * ATXPY
        self.e09700 = self.e09700 * ATXPY
        self.e09800 = self.e09800 * ATXPY
        self.e09900 = self.e09900 * ATXPY
        self.e10700 = self.e10700 * ATXPY
        self.e10900 = self.e10900 * ATXPY
        self.e59560 = self.e59560 * ATXPY
        self.e59680 = self.e59680 * ATXPY
        self.e59700 = self.e59700 * ATXPY
        self.e59720 = self.e59720 * ATXPY
        self.e11550 = self.e11550 * ATXPY
        self.e11070 = self.e11070 * ATXPY
        self.e11100 = self.e11100 * ATXPY
        self.e11200 = self.e11200 * ATXPY
        self.e11300 = self.e11300 * ATXPY
        self.e11400 = self.e11400 * ATXPY
        self.e11570 = self.e11570 * ATXPY
        self.e11580 = self.e11580 * ATXPY
        self.e11581 = self.e11581 * ATXPY
        self.e11582 = self.e11582 * ATXPY
        self.e11583 = self.e11583 * ATXPY
        self.e10605 = self.e10605 * ATXPY
        # ITEMIZED DEDUCTIONS
        self.e17500 = self.e17500 * ACPIM
        self.e18400 = self.e18400 * ATXPY
        self.e18500 = self.e18500 * ATXPY
        self.e19200 = self.e19200 * AIPD
        self.e19550 = self.e19550 * ATXPY
        self.e19800 = self.e19800 * ATXPY
        self.e20100 = self.e20100 * ATXPY
        self.e19700 = self.e19700 * ATXPY
        self.e20550 = self.e20550 * ATXPY
        self.e20600 = self.e20600 * ATXPY
        self.e20400 = self.e20400 * ATXPY
        self.e20800 = self.e20800 * ATXPY
        self.e20500 = self.e20500 * ATXPY
        self.e21040 = self.e21040 * ATXPY
        # CAPITAL GAINS
        self.p22250 = self.p22250 * ACGNS
        self.e22320 = self.e22320 * ACGNS
        self.e22370 = self.e22370 * ACGNS
        self.p23250 = self.p23250 * ACGNS
        self.e24515 = self.e24515 * ACGNS
        self.e24516 = self.e24516 * ACGNS
        self.e24518 = self.e24518 * ACGNS
        self.e24535 = self.e24535 * ACGNS
        self.e24560 = self.e24560 * ACGNS
        self.e24598 = self.e24598 * ACGNS
        self.e24615 = self.e24615 * ACGNS
        self.e24570 = self.e24570 * ACGNS
        # SCHEDULE E
        self.p25350 = self.p25350 * ASCHEI
        self.p25380 = self.p25380 * ASCHEI
        self.p25470 = self.p25470 * ASCHEI
        self.p25700 = self.p25700 * ASCHEI
        self.e25820 = self.e25820 * ASCHEI
        self.e25850 = self.e25850 * ASCHEI
        self.e25860 = self.e25860 * ASCHEI
        self.e25940 = self.e25940 * ASCHEI
        self.e25980 = self.e25980 * ASCHEI
        self.e25920 = self.e25920 * ASCHEI
        self.e25960 = self.e25960 * ASCHEI
        self.e26110 = self.e26110 * ASCHEI
        self.e26170 = self.e26170 * ASCHEI
        self.e26190 = self.e26190 * ASCHEI
        self.e26160 = self.e26160 * ASCHEI
        self.e26180 = self.e26180 * ASCHEI
        self.e26270 = self.e26270 * ASCHEI
        self.e26100 = self.e26100 * ASCHEI
        self.e26390 = self.e26390 * ASCHEI
        self.e26400 = self.e26400 * ASCHEI
        self.e27200 = self.e27200 * ASCHEI
        # MISCELLANOUS SCHEDULES
        self.e30400 = self.e30400 * ASCHCI
        self.e30500 = self.e30500 * ASCHCI
        self.e32800 = self.e32800 * ATXPY
        self.e33000 = self.e33000 * ATXPY
        self.e53240 = self.e53240 * ATXPY
        self.e53280 = self.e53280 * ATXPY
        self.e53410 = self.e53410 * ATXPY
        self.e53300 = self.e53300 * ATXPY
        self.e53317 = self.e53317 * ATXPY
        self.e53458 = self.e53458 * ATXPY
        self.e58950 = self.e58950 * ATXPY
        self.e58990 = self.e58990 * ATXPY
        self.p60100 = self.p60100 * ATXPY
        self.p61850 = self.p61850 * ATXPY
        self.e60000 = self.e60000 * ATXPY
        self.e62100 = self.e62100 * ATXPY
        self.e62900 = self.e62900 * ATXPY
        self.e62720 = self.e62720 * ATXPY
        self.e62730 = self.e62730 * ATXPY
        self.e62740 = self.e62740 * ATXPY
        self.p65300 = self.p65300 * ATXPY
        self.p65400 = self.p65400 * ATXPY
        self.e68000 = self.e68000 * ATXPY
        self.e82200 = self.e82200 * ATXPY
        self.t27800 = self.t27800 * ATXPY
        self.s27860 = self.s27860 * ATXPY
        self.p27895 = self.p27895 * ATXPY
        self.e87530 = self.e87530 * ATXPY
        self.e87550 = self.e87550 * ATXPY
        self.p87521 = self.p87521 * ATXPY
        self._cmbtp_itemizer = self._cmbtp_itemizer * ATXPY
        self._cmbtp_standard = self._cmbtp_standard * ATXPY

    def _read_data(self, data):
        """
        Read Records data from file or use specified DataFrame as data.
        """
        # pylint: disable=too-many-branches
        if isinstance(data, pd.DataFrame):
            taxdf = data
        elif isinstance(data, six.string_types):
            if data.endswith("gz"):
                taxdf = pd.read_csv(data, compression='gzip')
            else:
                taxdf = pd.read_csv(data)
        else:
            msg = ('Records.constructor data is neither a string nor '
                   'a Pandas DataFrame')
            raise ValueError(msg)
        self.dim = len(taxdf)
        # create class variables using taxdf column names
        READ_VARS = set()
        for varname in list(taxdf.columns.values):
            if varname not in Records.VALID_READ_VARS:
                msg = 'Records data variable name {} not in VALID_READ_VARS'
                raise ValueError(msg.format(varname))
            READ_VARS.add(varname)
            if varname not in Records.UNUSED_READ_VARS:
                if varname in Records.INTEGER_READ_VARS:
                    setattr(self, varname,
                            taxdf[varname].astype(np.int64).values)
                else:
                    setattr(self, varname,
                            taxdf[varname].astype(np.float64).values)
        # check that MUST_READ_VARS are all present in taxdf
        UNREAD_MUST_VARS = Records.MUST_READ_VARS - READ_VARS
        if len(UNREAD_MUST_VARS) > 0:
            msg = 'Records data missing {} MUST_READ_VARS'
            raise ValueError(msg.format(len(UNREAD_MUST_VARS)))
        # create other class variables that are set to all zeros
        UNREAD_VARS = Records.VALID_READ_VARS - READ_VARS
        ZEROED_VARS = Records.CALCULATED_VARS | UNREAD_VARS
        for varname in ZEROED_VARS:
            if varname not in Records.UNUSED_READ_VARS:
                setattr(self, varname, np.zeros(self.dim, dtype=np.float64))
        # create variables derived from MARS, which is in MUST_READ_VARS
        self._num = np.where(self.MARS == 2,
                             2., 1.)
        self._sep = np.where(np.logical_or(self.MARS == 3, self.MARS == 6),
                             2., 1.)

    def _read_weights(self, weights):
        """
        Read Records weights from file or use specified DataFrame as data.
        """
        if isinstance(weights, pd.DataFrame):
            WT = weights
        elif isinstance(weights, six.string_types):
            try:
                if not os.path.exists(weights):
                    # grab weights out of EGG distribution
                    path_in_egg = os.path.join("taxcalc",
                                               self.WEIGHTS_FILENAME)
                    weights = resource_stream(Requirement.parse("taxcalc"),
                                              path_in_egg)
                WT = pd.read_csv(weights)
            except IOError:
                msg = 'could not find weights file'
                ValueError(msg)
        else:
            msg = ('Records.constructor blowup_factors is neither a string '
                   'nor a Pandas DataFrame')
            raise ValueError(msg)
        setattr(self, 'WT', WT)

    def _read_blowup(self, blowup_factors):
        """
        Read Records blowup factors from file or
        use specified DataFrame as data.
        """
        if isinstance(blowup_factors, pd.DataFrame):
            BF = blowup_factors
        elif isinstance(blowup_factors, six.string_types):
            try:
                if not os.path.exists(blowup_factors):
                    # grab blowup factors out of EGG distribution
                    path_in_egg = os.path.join("taxcalc",
                                               self.BLOWUP_FACTORS_FILENAME)
                    blowup_factors = resource_stream(
                        Requirement.parse("taxcalc"), path_in_egg)
                BF = pd.read_csv(blowup_factors, index_col='YEAR')
            except IOError:
                msg = 'could not find blowup_factors file'
                ValueError(msg)
        else:
            msg = ('Records.constructor blowup_factors is neither a string '
                   'nor a Pandas DataFrame')
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

    def _impute_variables(self):
        """
        Impute variables in 2009 PUF Records data
        """
        self._cmbtp_itemizer = self._imputed_cmbtp_itemizer()
        self._cmbtp_standard = self.e62100 - self.e00100 + self.e00700
        # impute number of taxpayers
        self._txpyers = np.where(np.logical_or(self.MARS == 2,
                                               np.logical_or(self.MARS == 3,
                                                             self.MARS == 6)),
                                 2., 1.)
        # impute number of extra standard deductions for aged
        self._numextra = np.where(
            np.logical_or(self.AGERANGE >= 6,
                          np.logical_and(self.age >= 65, self.AGERANGE == 0)),
            self._txpyers, 0.)
        # impute the ratio of household head in total household income
        total = np.where(self.MARS == 2,
                         self.wage_head + self.wage_spouse, 0)
        earnings_split = np.where(total != 0,
                                  self.wage_head / total, 1.)
        one_minus_earnings_split = 1.0 - earnings_split
        self.e00200p = earnings_split * self.e00200
        self.e00200s = one_minus_earnings_split * self.e00200
        self.e00900p = earnings_split * self.e00900
        self.e00900s = one_minus_earnings_split * self.e00900
        self.e02100p = earnings_split * self.e02100
        self.e02100s = one_minus_earnings_split * self.e02100

    def _imputed_cmbtp_itemizer(self):
        """
        Private class method calls global function defined below.
        """
        return imputed_cmbtp_itemizer(self.e17500, self.e00100, self.e18400,
                                      self.e62100, self.e00700,
                                      self.p04470, self.e21040,
                                      self.e18500, self.e20800)

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
        self.s006 = self.WT["WT" + str(year)] * 0.01


@vectorize([float64(float64, float64, float64,
                    float64, float64,
                    float64, float64,
                    float64, float64)])
def imputed_cmbtp_itemizer(e17500, e00100, e18400,
                           e62100, e00700,
                           p04470, e21040,
                           e18500, e20800):
    """
    Global function that calculates _cmbtp_itemizer values
    (uses vectorize decorator to speed up calculations with NumPy arrays)
    """
    # pylint: disable=too-many-arguments
    medical_limited = max(0., e17500 - max(0., e00100) * 0.075)
    medical_adjustment = min(medical_limited, 0.025 * max(0., e00100))
    state_adjustment = max(0, e18400)
    return (e62100 - medical_adjustment + e00700 + p04470 + e21040 -
            state_adjustment - e00100 - e18500 - e20800)
