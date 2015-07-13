"""
This file reads input csv file and saves the variables
"""
import math
import copy
import pandas as pd
import numpy as np
import os.path
import os
import json
from numba import vectorize, float64
from pkg_resources import resource_stream, Requirement

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
WEIGHTS_FILENAME = "WEIGHTS.csv"
weights_path = os.path.join(CUR_PATH, WEIGHTS_FILENAME)
BLOWUP_FACTORS_FILENAME = "StageIFactors.csv"
blowup_factors_path = os.path.join(CUR_PATH, BLOWUP_FACTORS_FILENAME)


class Records(object):
    """
    This class represents the data for a collection of tax records. Typically,
    this would come from a Public Use File. Much of the current implementation
    is based on reading a PUF file, although other types of records could
    be read.
    Instances of this class hold all of the record data in memory
    to be used by the Calculator. Each pieces of member data represents
    a column of the data. Each entry in the column is the value of the data
    attribute for a particular taxpayer record.
    A federal tax year is assumed. The year can be given to the Record
    constructor.
    Advancing years is done through a member function
    """

    @classmethod
    def from_file(cls, path, **kwargs):
        return cls(path, **kwargs)

    def __init__(self, data=None, blowup_factors=blowup_factors_path,
                 weights=weights_path, start_year=None, dims=None,
                 **kwargs):

        self.BF = read_blowup(blowup_factors)
        self.WT = read_weights(weights)

        attr = ['AGIR1', 'DSI', 'EFI', 'EIC', 'ELECT', 'e04600',
                'FDED', 'FLPDYR', 'FLPDMO', 'f2441', 'e04250',
                'f3800', 'f6251', 'f8582', 'f8606', 'IE',
                'MARS', 'MIDR', 'n20', 'n24', 'n25', 'PREP',
                'SCHB', 'SCHCF', 'SCHE', 'STATE', 'TFORM',
                'TXST', 'XFPT', 'XFST', 'XOCAH', 'XOCAWH',
                'XOODEP', 'XOPAR', 'XTOT', 'e00200', 'e00300',
                'e00400', 'e00600', 'e00650', 'e00700', 'e00800',
                'e00900', 'e01000', 'e01100', 'e01200', 'e01400',
                'e01500', 'e01700', 'e02000', 'e02100', 'e02300',
                'e02400', 'e02500', 'e03150', 'e03210', 'e03220',
                'e03230', 'e03260', 'e03270', 'e03240', 'e03290',
                'e03300', 'e03400', 'e03500', 'e00100', 'p04470',
                'e04800', 'e05100', 'e05200', 'e05800', 'e06000',
                'e06200', 'e06300', 'e09600', 'e07180', 'e07200',
                'e07220', 'e07230', 'e07240', 'e07260', 'e07300',
                'e07400', 'e07600', 'p08000', 'e07150', 'e06500',
                'e08800', 'e09400', 'e09700', 'e09800', 'e09900',
                'e10300', 'e10700', 'e10900', 'e59560', 'e59680',
                'e59700', 'e59720', 'e11550', 'e11070', 'e11100',
                'e11200', 'e11300', 'e11400', 'e11570', 'e11580',
                'e11581', 'e11582', 'e11583', 'e10605', 'e11900',
                'e12000', 'e12200', 'e17500', 'e18425', 'e18450',
                'e18500', 'e19200', 'e19550', 'e19800', 'e20100',
                'e19700', 'e20550', 'e20600', 'e20400', 'e20800',
                'e20500', 'e21040', 'p22250', 'e22320', 'e22370',
                'p23250', 'e24515', 'e24516', 'e24518', 'e24535',
                'e24560', 'e24598', 'e24615', 'e24570', 'e25820',
                'p25350', 'e25370', 'e25380', 'p25470', 'p25700',
                'e25850', 'e25860', 'e25940', 'e25980', 'e25980',
                'e25920', 'e25960', 'e26110', 'e26170', 'e26190',
                'e26160', 'e26180', 'e26270', 'e26100', 'e26390',
                'e26400', 'e27200', 'e30400', 'e30500', 'e32800',
                'e33000', 'e53240', 'e53280', 'e53410', 'e53300',
                'e53317', 'e53458', 'e58950', 'e58990', 'p60100',
                'p61850', 'e60000', 'e62100', 'e62900', 'e62720',
                'e62730', 'e62740', 'p65300', 'p65400', 'e68000',
                'e82200', 't27800', 's27860', 'p27895', 'e87500',
                'e87510', 'e87520', 'e87530', 'e87540', 'e87550',
                'RECID', 's006', 's008', 's009', 'WSAMP', 'TXRT']

        zero = ['e35300_0', 'e35600_0', 'e35910_0', 'x03150', 'e03600',
                'e03280', 'e03900', 'e04000', 'e03700', 'c23250',
                'e23660', 'f2555', 'e02800', 'e02610', 'e02540',
                'e02615', 'SSIND', 'e18400', 'e18800', 'e18900',
                'e20950', 'e19500', 'e19570', 'e19400', 'c20400',
                'e20200', 'e20900', 'e21000', 'e21010', 'e02600',
                '_exact', 'e11055', 'e00250', 'e30100', 'e15360',
                'e04200', 'e37717', 'e04805', 'AGEP', 'AGES', 'PBI',
                'SBI', 't04470', 'e58980', 'c00650', 'c00100',
                'c04470', 'c04600', 'c21060', 'c21040', 'c17000',
                'c18300', 'c20800', 'c02900', 'c02700', 'c23650',
                'c01000', 'c02500', 'e24583', '_fixup', '_cmp',
                'e59440', 'e59470', 'e59400', 'e10105', 'e83200_0',
                'e59410', 'e59420', 'e74400', 'x62720', 'x60260',
                'x60240', 'x60220', 'x60130', 'x62730', 'e60290',
                'DOBYR', 'SDOBYR', 'DOBMD', 'SDOBMD', 'e62600',
                'x62740', '_fixeic', 'e32880', 'e32890', 'CDOB1',
                'CDOB2', 'e32750', 'e32775', 'e33420', 'e33430',
                'e33450', 'e33460', 'e33465', 'e33470', 'x59560',
                'EICYB1', 'EICYB2', 'EICYB3', 'e83080', 'e25360',
                'e25430', 'e25400', 'e25500', 'e26210', 'e26340',
                'e26205', 'e26320', 'e87482', 'e87487', 'e87492',
                'e87497', 'e87526', 'e87522', 'e87524', 'e87528',
                'EDCRAGE', 'e07960', 'e07700', 'e07250', 't07950',
                'e82882', 'e82880', 'e07500', 'e08001', 'e07970',
                'e07980', 'e10000', 'e10100', 'e10050', 'e10075',
                'e09805', 'e09710', 'e09720', 'e87900', 'e87905',
                'e87681', 'e87682', 'e11451', 'e11452', 'e11601',
                'e11602', 'e60300', 'e60860', 'e60840', 'e60630',
                'e60550', 'e60720', 'e60430', 'e60500', 'e60340',
                'e60680', 'e60600', 'e60405', 'e60440', 'e60420',
                'e60410', 'e61400', 'e60660', 'e60480', 'e62000',
                'e60250', 'e40223', '_sep', '_earned', '_sey',
                '_setax', '_feided', '_ymod', '_ymod1', '_posagi',
                '_sit', 'xtxcr1xtxcr10', '_earned', '_xyztax',
                '_taxinc', 'c04800', '_feitax', 'c05750', 'c24517',
                '_taxbc', 'c60000', '_standard', 'c24516', 'c25420',
                'c05700', 'c32880', 'c32890', '_dclim', 'c32800',
                'c33000', 'c05800', '_othtax', 'c59560', '_agep',
                '_ages', 'c87521', 'c87550', 'c07180',
                'c07230', '_precrd', 'c07220', 'c59660', 'c07970',
                'c08795', 'c09200', 'c07100', '_eitc', 'c59700',
                'c10950', '_ymod2', '_ymod3', 'c02650', '_agierr',
                '_ywossbe', '_ywossbc', '_prexmp', 'c17750', '_sit1',
                '_statax', 'c37703', 'c20500', 'c20750', 'c19200',
                'c19700', '_nonlimited', '_limitratio', '_phase2_i',
                '_fica', '_seyoff', 'c11055', 'c15100', '_numextra',
                '_txpyers', 'c15200', '_othded', 'c04100', 'c04200',
                'c04500', '_amtstd', '_oldfei', 'c05200', '_cglong',
                '_noncg', '_hasgain', '_dwks9', '_dwks5', '_dwks12',
                '_dwks16', '_dwks17', '_dwks21', '_dwks25', '_dwks26',
                '_dwks28', '_dwks31', 'c24505', 'c24510', 'c24520',
                'c24530', 'c24540', 'c24534', 'c24597', 'c24598',
                'c24610', 'c24615', 'c24550', 'c24570', '_addtax',
                'c24560', '_taxspecial', 'c24580', 'c05100', 'c05700',
                'c59430', 'c59450', 'c59460', '_line17', '_line19',
                '_line22', '_line30', '_line31', '_line32', '_line36',
                '_line33', '_line34', '_line35', 'c59485', 'c59490',
                '_s1291', '_parents', 'c62720', 'c60260', 'c63100',
                'c60200', 'c60240', 'c60220', 'c60130', 'c62730',
                '_addamt', 'c62100', '_cmbtp', '_edical', '_amtsepadd',
                '_agep', '_ages', 'c62600', 'c62700', '_alminc',
                '_amtfei', 'c62780', 'c62900', 'c63000', 'c62740',
                '_ngamty', 'c62745', 'y62745', '_tamt2', '_amt5pc',
                '_amt15pc', '_amt25pc', 'c62747', 'c62755', 'c62770',
                '_amt', 'c62800', 'c09600', 'c05800', '_ncu13',
                '_seywage', 'c33465', 'c33470', 'c33475', 'c33480',
                'c32840', '_tratio', 'c33200', 'c33400', 'c07180',
                '_ieic', 'EICYB1', 'EICYB2', 'EICYB3', '_modagi',
                '_val_ymax', '_preeitc', '_val_rtbase', '_val_rtless',
                '_dy', 'c11070', '_nctcr', '_ctcagi', 'c87482',
                'c87487', 'c87492', 'c87497', 'c87483', 'c87488',
                'c87493', 'c87498', 'c87540', 'c87530', 'c87654',
                'c87656', 'c87658', 'c87660', 'c87662', 'c87664',
                'c87666', 'c10960', 'c87668', 'c87681', 'c87560',
                'c87570', 'c87580', 'c87590', 'c87600', 'c87610',
                'c87620', '_ctc1', '_ctc2', '_regcrd', '_exocrd',
                '_ctctax', 'c07220', 'c82925', 'c82930', 'c82935',
                'c82880', 'h82880', 'c82885', 'c82890', 'c82900',
                'c82905', 'c82910', 'c82915',  'c82920', 'c82937',
                'c82940', 'c11070', 'e59660', '_othadd', 'y07100',
                'x07100', 'c08800', 'e08795', 'x07400', 'c59680',
                '_othertax', 'e82915', 'e82940', 'SFOBYR', 'NIIT',
                'c59720', '_comb', 'c07150', 'c10300', '_ospctax',
                '_refund', 'c11600', 'e11450', 'e82040', 'e11500',
                '_amed', '_xlin3', '_xlin6', 'share_corptax_burden',
                'expanded_income', 'agg_self_employed', 'netcapgains',
                'agg_capgains', 'total_compensation', 'dividends',
                'agg_dividends', 'bonds', 'compensation', 'agg_bonds',
                '_expanded_income']

        if data is not None:
            self.read(data)
        else:
            assert type(dims) is not None
            self.dim = dims
            for name in attr:
                setattr(self, name, np.zeros((self.dim,)))

        if (start_year):
            self._current_year = start_year
        else:
            self._current_year = self.FLPDYR[0]

        self._num = np.ones((self.dim,))

        for name in zero:
            setattr(self, name, np.zeros((self.dim,)))

        # Aliases
        self.e22250 = self.p22250
        self.e04470 = self.p04470
        self.e23250 = self.p23250
        self.e25470 = self.p25470
        self.e08000 = self.p08000
        self.e60100 = self.p60100
        self.e27860 = self.s27860
        self.SOIYR = np.repeat(2008, self.dim)

        """Imputations"""
        self._cmbtp_itemizer = None
        self._cmbtp_standard = self.e62100 - self.e00100 + self.e00700
        self.mutate_imputations()  # Updates the self._cmbtp_itemizer variable

        # Standard deduction amount in 2008
        std2008 = np.array([5450, 10900, 5450, 8000, 10900, 5450, 900])
        # Additional standard deduction for aged 2008
        STD_Aged_2008 = np.array([1350., 1050.])
        # Compulsory itemizers
        self._compitem = np.where(np.logical_and(self.FDED == 1, self.e04470
                                                 < std2008[self.MARS-1]),
                                  1, 0)
        # Number of taxpayers
        self._txpyers = np.where(np.logical_or(self.MARS == 2,
                                               np.logical_or(self.MARS == 3,
                                                             self.MARS == 6)),
                                 2., 1.)
        # Number of extra standard deductions for aged
        self._numextra = np.where(np.logical_and(self.FDED == 2, self.e04470
                                                 < std2008[self.MARS-1]),
                                  np.where(np.logical_and(self.MARS != 2,
                                                          self.MARS != 3),
                                  ((self.e04470 - std2008[self.MARS - 1])
                                   / STD_Aged_2008[0]),
                                   (self.e04470 - std2008[self.MARS - 1])
                                   / STD_Aged_2008[1]),
                                  np.where(self.e02400 > 0, self._txpyers, 0))

        """Setting Variables for Corporate Income Tax"""
        self.compensation = None
        self.dividends = None
        self.netcapgains = None
        self.bonds = None
        self.e_and_p = None
        self.share_corptax_burden = None  # get's calculated in functions.py
        # actually sets the values
        self.set_vars_for_corp_tax()

        self.agg_comp = None
        self.agg_dividends = None
        self.agg_capgains = None
        self.agg_bonds = None
        self.agg_self_employed_and_pt = None

    @property
    def current_year(self):
        return self._current_year

    def set_attr(self, name, value):
        return setattr(self, name, value)

    def increment_year(self):
        self._current_year += 1
        self.FLPDYR += 1
        # Implement Stage 1 Extrapolation blowup factors
        self.blowup()
        # Implement Stage 2 Extrapolation reweighting.
        self.s006 = self.WT["WT"+str(self.current_year)]

    def blowup(self):
        self.e00200  =   self.e00200  *   self.BF.AWAGE[self._current_year]
        self.e00300  =   self.e00300  *   self.BF.AINTS[self._current_year]
        self.e00400  =   self.e00400  *   self.BF.AINTS[self._current_year]
        self.e00600  =   self.e00600  *   self.BF.ADIVS[self._current_year]
        self.e00650  =   self.e00650  *   self.BF.ADIVS[self._current_year]
        self.e00700  =   self.e00700  *   self.BF.ATXPY[self._current_year]
        self.e00800  =   self.e00800  *   self.BF.ATXPY[self._current_year]
        self.e00900  =   np.where(self.e00900 >= 0,
                         self.e00900  *   self.BF.ASCHCI[self._current_year],
                         self.e00900  *   self.BF.ASCHCL[self._current_year]
                         )
        self.e01000  =   np.where(self.e01000 >= 0.,
                         self.e01000  *   self.BF.ACGNS[self._current_year],
                         self.e01000
                         )
        self.e01100  =   self.e01100  *   self.BF.ACGNS[self._current_year]
        self.e01200  =   self.e01200  *   self.BF.ACGNS[self._current_year]
        self.e01400  =   self.e01400  *   self.BF.ATXPY[self._current_year]
        self.e01500  =   self.e01500  *   self.BF.ATXPY[self._current_year]
        self.e01700  =   self.e01700  *   self.BF.ATXPY[self._current_year]
        self.e02000  =   np.where(self.e00200 >= 0, 
                         self.e02000  *  self.BF.ASCHEI[self._current_year], 
                         self.e02000  *  self.BF.ASCHEL[self._current_year]
                         )
        self.e02100  =   self.e02100  *   self.BF.ASCHF[self._current_year]
        self.e02300  =   self.e02300  *   self.BF.AUCOMP[self._current_year]
        self.e02400  =   self.e02400  *   self.BF.ASOCSEC[self._current_year]
        self.e02500  =   self.e02500  *   self.BF.ASOCSEC[self._current_year] # Taxable Social Security is a calculated field
        self.e03150  =   self.e03150  *   self.BF.ATXPY[self._current_year]
        self.e03210  =   self.e03210  *   self.BF.ATXPY[self._current_year]
        self.e03220  =   self.e03220  *   self.BF.ATXPY[self._current_year]
        self.e03230  =   self.e03230  *   self.BF.ATXPY[self._current_year]
        self.e03260  =   self.e03260  *   self.BF.ASCHCI[self._current_year]
        self.e03270  =   self.e03270  *   self.BF.ACPIM[self._current_year]
        self.e03240  =   self.e03240  *   self.BF.AGDPN[self._current_year]
        self.e03290  =   self.e03290  *   self.BF.ACPIM[self._current_year]
        self.e03300  =   self.e03300  *   self.BF.ATXPY[self._current_year]
        self.e03400  =   self.e03400  *   self.BF.ATXPY[self._current_year]
        self.e03500  =   self.e03500  *   self.BF.ATXPY[self._current_year]
        self.e00100  =   self.e00100  *   1. # Adjusted Gross Income is a calculated field
        self.p04470  =   self.p04470  *   1.
        self.e04250  =   self.e04250  *   1.
        self.e04600  =   self.e04600  *   1.
        self.e04800  =   self.e04800  *   1.
        self.e05100  =   self.e05100  *   1.
        self.e05200  =   self.e05200  *   1.
        self.e05800  =   self.e05800  *   1.
        self.e06000  =   self.e06000  *   1.
        self.e06200  =   self.e06200  *   1.
        self.e06300  =   self.e06300  *   1.
        self.e09600  =   self.e09600  *   1.
        self.e07180  =   self.e07180  *   1.
        self.e07200  =   self.e07200  *   1.
        self.e07220  =   self.e07220  *   1.
        self.e07230  =   self.e07230  *   self.BF.ATXPY[self._current_year]
        self.e07240  =   self.e07240  *   self.BF.ATXPY[self._current_year]
        self.e07260  =   self.e07260  *   self.BF.ATXPY[self._current_year]
        self.e07300  =   self.e07300  *   self.BF.ABOOK[self._current_year]
        self.e07400  =   self.e07400  *   self.BF.ABOOK[self._current_year]
        self.e07600  =   self.e07600  *   1.
        self.p08000  =   self.p08000  *   self.BF.ATXPY[self._current_year]
        self.e07150  =   self.e07150  *   1.
        self.e06500  =   self.e06500  *   1.
        self.e08800  =   self.e08800  *   1.
        self.e09400  =   self.e09400  *   1.
        self.e09700  =   self.e09700  *   self.BF.ATXPY[self._current_year]
        self.e09800  =   self.e09800  *   self.BF.ATXPY[self._current_year]
        self.e09900  =   self.e09900  *   self.BF.ATXPY[self._current_year]
        self.e10300  =   self.e10300  *   1.
        self.e10700  =   self.e10700  *   self.BF.ATXPY[self._current_year]
        self.e10900  =   self.e10900  *   self.BF.ATXPY[self._current_year]
        self.e59560  =   self.e59560  *   self.BF.ATXPY[self._current_year]
        self.e59680  =   self.e59680  *   self.BF.ATXPY[self._current_year]
        self.e59700  =   self.e59700  *   self.BF.ATXPY[self._current_year]
        self.e59720  =   self.e59720  *   self.BF.ATXPY[self._current_year]
        self.e11550  =   self.e11550  *   self.BF.ATXPY[self._current_year]
        self.e11070  =   self.e11070  *   self.BF.ATXPY[self._current_year]
        self.e11100  =   self.e11100  *   self.BF.ATXPY[self._current_year]
        self.e11200  =   self.e11200  *   self.BF.ATXPY[self._current_year]
        self.e11300  =   self.e11300  *   self.BF.ATXPY[self._current_year]
        self.e11400  =   self.e11400  *   self.BF.ATXPY[self._current_year]
        self.e11570  =   self.e11570  *   self.BF.ATXPY[self._current_year]
        self.e11580  =   self.e11580  *   self.BF.ATXPY[self._current_year]
        self.e11581  =   self.e11581  *   self.BF.ATXPY[self._current_year]
        self.e11582  =   self.e11582  *   self.BF.ATXPY[self._current_year]
        self.e11583  =   self.e11583  *   self.BF.ATXPY[self._current_year]
        self.e10605  =   self.e10605  *   self.BF.ATXPY[self._current_year]
        self.e11900  =   self.e11900  *   1.
        self.e12000  =   self.e12000  *   1.
        self.e12200  =   self.e12200  *   1.
        """  ITEMIZED DEDUCTIONS """
        self.e17500  =   self.e17500  *   self.BF.ACPIM[self._current_year]
        self.e18425  =   self.e18425  *   self.BF.ATXPY[self._current_year]
        self.e18450  =   self.e18450  *   self.BF.ATXPY[self._current_year]
        self.e18500  =   self.e18500  *   self.BF.ATXPY[self._current_year] 
        self.e19200  =   self.e19200  *   self.BF.AIPD[self._current_year]
        self.e19550  =   self.e19550  *   self.BF.ATXPY[self._current_year]
        self.e19800  =   self.e19800  *   self.BF.ATXPY[self._current_year]
        self.e20100  =   self.e20100  *   self.BF.ATXPY[self._current_year]
        self.e19700  =   self.e19700  *   self.BF.ATXPY[self._current_year]
        self.e20550  =   self.e20550  *   self.BF.ATXPY[self._current_year]
        self.e20600  =   self.e20600  *   self.BF.ATXPY[self._current_year]
        self.e20400  =   self.e20400  *   self.BF.ATXPY[self._current_year]
        self.e20800  =   self.e20800  *   self.BF.ATXPY[self._current_year]
        self.e20500  =   self.e20500  *   self.BF.ATXPY[self._current_year]
        self.e21040  =   self.e21040  *   self.BF.ATXPY[self._current_year]
        """  CAPITAL GAINS   """
        self.p22250  =   self.p22250  *   self.BF.ACGNS[self._current_year]
        self.e22320  =   self.e22320  *   self.BF.ACGNS[self._current_year]
        self.e22370  =   self.e22370  *   self.BF.ACGNS[self._current_year]
        self.p23250  =   self.p23250  *   self.BF.ACGNS[self._current_year]
        self.e24515  =   self.e24515  *   self.BF.ACGNS[self._current_year]
        self.e24516  =   self.e24516  *   self.BF.ACGNS[self._current_year]
        self.e24518  =   self.e24518  *   self.BF.ACGNS[self._current_year]
        self.e24535  =   self.e24535  *   self.BF.ACGNS[self._current_year]
        self.e24560  =   self.e24560  *   self.BF.ACGNS[self._current_year]
        self.e24598  =   self.e24598  *   self.BF.ACGNS[self._current_year]
        self.e24615  =   self.e24615  *   self.BF.ACGNS[self._current_year]
        self.e24570  =   self.e24570  *   self.BF.ACGNS[self._current_year]
        """  SCHEDULE E  """
        self.p25350  =   self.p25350  *   self.BF.ASCHEI[self._current_year]
        self.e25370  =   self.e25370  *   self.BF.ASCHEI[self._current_year]
        self.e25380  =   self.e25380  *   self.BF.ASCHEI[self._current_year]
        self.p25470  =   self.p25470  *   self.BF.ASCHEI[self._current_year]
        self.p25700  =   self.p25700  *   self.BF.ASCHEI[self._current_year]
        self.e25820  =   self.e25820  *   self.BF.ASCHEI[self._current_year]
        self.e25850  =   self.e25850  *   self.BF.ASCHEI[self._current_year]
        self.e25860  =   self.e25860  *   self.BF.ASCHEI[self._current_year]
        self.e25940  =   self.e25940  *   self.BF.ASCHEI[self._current_year]
        self.e25980  =   self.e25980  *   self.BF.ASCHEI[self._current_year]
        self.e25920  =   self.e25920  *   self.BF.ASCHEI[self._current_year]
        self.e25960  =   self.e25960  *   self.BF.ASCHEI[self._current_year]
        self.e26110  =   self.e26110  *   self.BF.ASCHEI[self._current_year]
        self.e26170  =   self.e26170  *   self.BF.ASCHEI[self._current_year]
        self.e26190  =   self.e26190  *   self.BF.ASCHEI[self._current_year]
        self.e26160  =   self.e26160  *   self.BF.ASCHEI[self._current_year]
        self.e26180  =   self.e26180  *   self.BF.ASCHEI[self._current_year]
        self.e26270  =   self.e26270  *   self.BF.ASCHEI[self._current_year]
        self.e26100  =   self.e26100  *   self.BF.ASCHEI[self._current_year]
        self.e26390  =   self.e26390  *   self.BF.ASCHEI[self._current_year]
        self.e26400  =   self.e26400  *   self.BF.ASCHEI[self._current_year]
        self.e27200  =   self.e27200  *   self.BF.ASCHEI[self._current_year]
        """  MISCELLANOUS SCHEDULES"""
        self.e30400  =   self.e30400  *   self.BF.ASCHCI[self._current_year]
        self.e30500  =   self.e30500  *   self.BF.ASCHCI[self._current_year]
        self.e32800  =   self.e32800  *   self.BF.ATXPY[self._current_year]
        self.e33000  =   self.e33000  *   self.BF.ATXPY[self._current_year]
        self.e53240  =   self.e53240  *   self.BF.ATXPY[self._current_year]
        self.e53280  =   self.e53280  *   self.BF.ATXPY[self._current_year]
        self.e53410  =   self.e53410  *   self.BF.ATXPY[self._current_year]
        self.e53300  =   self.e53300  *   self.BF.ATXPY[self._current_year]
        self.e53317  =   self.e53317  *   self.BF.ATXPY[self._current_year]
        self.e53458  =   self.e53458  *   self.BF.ATXPY[self._current_year]
        self.e58950  =   self.e58950  *   self.BF.ATXPY[self._current_year]
        self.e58990  =   self.e58990  *   self.BF.ATXPY[self._current_year]
        self.p60100  =   self.p60100  *   self.BF.ATXPY[self._current_year]
        self.p61850  =   self.p61850  *   self.BF.ATXPY[self._current_year]
        self.e60000  =   self.e60000  *   self.BF.ATXPY[self._current_year]
        self.e62100  =   self.e62100  *   self.BF.ATXPY[self._current_year]
        self.e62900  =   self.e62900  *   self.BF.ATXPY[self._current_year]
        self.e62720  =   self.e62720  *   self.BF.ATXPY[self._current_year]
        self.e62730  =   self.e62730  *   self.BF.ATXPY[self._current_year]
        self.e62740  =   self.e62740  *   self.BF.ATXPY[self._current_year]
        self.p65300  =   self.p65300  *   self.BF.ATXPY[self._current_year]
        self.p65400  =   self.p65400  *   self.BF.ATXPY[self._current_year]
        self.e68000  =   self.e68000  *   self.BF.ATXPY[self._current_year]
        self.e82200  =   self.e82200  *   self.BF.ATXPY[self._current_year]
        self.t27800  =   self.t27800  *   self.BF.ATXPY[self._current_year]
        self.s27860  =   self.s27860  *   self.BF.ATXPY[self._current_year]
        self.p27895  =   self.p27895  *   self.BF.ATXPY[self._current_year]
        self.e87500  =   self.e87500  *   self.BF.ATXPY[self._current_year]
        self.e87510  =   self.e87510  *   self.BF.ATXPY[self._current_year]
        self.e87520  =   self.e87520  *   self.BF.ATXPY[self._current_year]
        self.e87530  =   self.e87530  *   self.BF.ATXPY[self._current_year]
        self.e87540  =   self.e87540  *   self.BF.ATXPY[self._current_year]
        self.e87550  =   self.e87550  *   self.BF.ATXPY[self._current_year]
        self.RECID   =   self.RECID   *   1.
        self.s006    =   self.s006    *   1.
        self.s008    =   self.s008    *   1.
        self.s009    =   self.s009    *   1.
        self.WSAMP   =   self.WSAMP   *   1.
        self.TXRT    =   self.TXRT    *   1.

        """     Imputations     """
        self.mutate_imputations()
        self._cmbtp_standard = self.e62100 - self.e00100 + self.e00700

        """ Corporate Income Tax Update """
        self.set_vars_for_corp_tax()

    def read(self, data):
        if isinstance(data, pd.core.frame.DataFrame):
            tax_dta = data
        elif data.endswith("gz"):
            tax_dta = pd.read_csv(data, compression='gzip')
        else:
            tax_dta = pd.read_csv(data)

        # pairs of 'name of attribute', 'column name' - often the same
        names = [('AGIR1', 'agir1'),
                 ('DSI', 'dsi'),
                 ('EFI', 'efi'),
                 ('EIC', 'eic'),
                 ('ELECT', 'elect'),
                 ('FDED', 'fded'),
                 ('FLPDYR', 'flpdyr'),
                 ('FLPDMO', 'flpdmo'),
                 ('f2441', 'f2441'),
                 ('f3800', 'f3800'),
                 ('f6251', 'f6251'),
                 ('f8582', 'f8582'),
                 ('f8606', 'f8606'),
                 ('IE', 'ie'),
                 ('MARS', 'mars'),
                 ('MIDR', 'midr'),
                 ('n20', 'n20'),
                 ('n24', 'n24'),
                 ('n25', 'n25'),
                 ('PREP', 'prep'),
                 ('SCHB', 'schb'),
                 ('SCHCF', 'schcf'),
                 ('SCHE', 'sche'),
                 ('STATE', 'state'),
                 ('TFORM', 'tform'),
                 ('TXST', 'txst'),
                 ('XFPT', 'xfpt'),
                 ('XFST', 'xfst'),
                 ('XOCAH', 'xocah'),
                 ('XOCAWH', 'xocawh'),
                 ('XOODEP', 'xoodep'),
                 ('XOPAR', 'xopar'),
                 ('XTOT', 'xtot'),
                 ('e00200', 'e00200'),
                 ('e00300', 'e00300'),
                 ('e00400', 'e00400'),
                 ('e00600', 'e00600'),
                 ('e00650', 'e00650'),
                 ('e00700', 'e00700'),
                 ('e00800', 'e00800'),
                 ('e00900', 'e00900'),
                 ('e01000', 'e01000'),
                 ('e01100', 'e01100'),
                 ('e01200', 'e01200'),
                 ('e01400', 'e01400'),
                 ('e01500', 'e01500'),
                 ('e01700', 'e01700'),
                 ('e02000', 'e02000'),
                 ('e02100', 'e02100'),
                 ('e02300', 'e02300'),
                 ('e02400', 'e02400'),
                 ('e02500', 'e02500'),
                 ('e03150', 'e03150'),
                 ('e03210', 'e03210'),
                 ('e03220', 'e03220'),
                 ('e03230', 'e03230'),
                 ('e03260', 'e03260'),
                 ('e03270', 'e03270'),
                 ('e03240', 'e03240'),
                 ('e03290', 'e03290'),
                 ('e03300', 'e03300'),
                 ('e03400', 'e03400'),
                 ('e03500', 'e03500'),
                 ('e00100', 'e00100'),
                 ('p04470', 'p04470'),
                 ('e04250', 'e04250'),
                 ('e04600', 'e04600'),
                 ('e04800', 'e04800'),
                 ('e05100', 'e05100'),
                 ('e05200', 'e05200'),
                 ('e05800', 'e05800'),
                 ('e06000', 'e06000'),
                 ('e06200', 'e06200'),
                 ('e06300', 'e06300'),
                 ('e09600', 'e09600'),
                 ('e07180', 'e07180'),
                 ('e07200', 'e07200'),
                 ('e07220', 'e07220'),
                 ('e07230', 'e07230'),
                 ('e07240', 'e07240'),
                 ('e07260', 'e07260'),
                 ('e07300', 'e07300'),
                 ('e07400', 'e07400'),
                 ('e07600', 'e07600'),
                 ('p08000', 'p08000'),
                 ('e07150', 'e07150'),
                 ('e06500', 'e06500'),
                 ('e08800', 'e08800'),
                 ('e09400', 'e09400'),
                 ('e09700', 'e09700'),
                 ('e09800', 'e09800'),
                 ('e09900', 'e09900'),
                 ('e10300', 'e10300'),
                 ('e10700', 'e10700'),
                 ('e10900', 'e10900'),
                 ('e59560', 'e59560'),
                 ('e59680', 'e59680'),
                 ('e59700', 'e59700'),
                 ('e59720', 'e59720'),
                 ('e11550', 'e11550'),
                 ('e11070', 'e11070'),
                 ('e11100', 'e11100'),
                 ('e11200', 'e11200'),
                 ('e11300', 'e11300'),
                 ('e11400', 'e11400'),
                 ('e11570', 'e11570'),
                 ('e11580', 'e11580'),
                 ('e11581', 'e11581'),
                 ('e11582', 'e11582'),
                 ('e11583', 'e11583'),
                 ('e10605', 'e10605'),
                 ('e11900', 'e11900'),
                 ('e12000', 'e12000'),
                 ('e12200', 'e12200'),
                 ('e17500', 'e17500'),
                 ('e18425', 'e18425'),
                 ('e18450', 'e18450'),
                 ('e18500', 'e18500'),
                 ('e19200', 'e19200'),
                 ('e19550', 'e19550'),
                 ('e19800', 'e19800'),
                 ('e20100', 'e20100'),
                 ('e19700', 'e19700'),
                 ('e20550', 'e20550'),
                 ('e20600', 'e20600'),
                 ('e20400', 'e20400'),
                 ('e20800', 'e20800'),
                 ('e20500', 'e20500'),
                 ('e21040', 'e21040'),
                 ('p22250', 'p22250'),
                 ('e22320', 'e22320'),
                 ('e22370', 'e22370'),
                 ('p23250', 'p23250'),
                 ('e24515', 'e24515'),
                 ('e24516', 'e24516'),
                 ('e24518', 'e24518'),
                 ('e24535', 'e24535'),
                 ('e24560', 'e24560'),
                 ('e24598', 'e24598'),
                 ('e24615', 'e24615'),
                 ('e24570', 'e24570'),
                 ('p25350', 'p25350'),
                 ('e25370', 'e25370'),
                 ('e25380', 'e25380'),
                 ('p25470', 'p25470'),
                 ('p25700', 'p25700'),
                 ('e25820', 'e25820'),
                 ('e25850', 'e25850'),
                 ('e25860', 'e25860'),
                 ('e25940', 'e25940'),
                 ('e25980', 'e25980'),
                 ('e25920', 'e25920'),
                 ('e25960', 'e25960'),
                 ('e26110', 'e26110'),
                 ('e26170', 'e26170'),
                 ('e26190', 'e26190'),
                 ('e26160', 'e26160'),
                 ('e26180', 'e26180'),
                 ('e26270', 'e26270'),
                 ('e26100', 'e26100'),
                 ('e26390', 'e26390'),
                 ('e26400', 'e26400'),
                 ('e27200', 'e27200'),
                 ('e30400', 'e30400'),
                 ('e30500', 'e30500'),
                 ('e32800', 'e32800'),
                 ('e33000', 'e33000'),
                 ('e53240', 'e53240'),
                 ('e53280', 'e53280'),
                 ('e53410', 'e53410'),
                 ('e53300', 'e53300'),
                 ('e53317', 'e53317'),
                 ('e53458', 'e53458'),
                 ('e58950', 'e58950'),
                 ('e58990', 'e58990'),
                 ('p60100', 'p60100'),
                 ('p61850', 'p61850'),
                 ('e60000', 'e60000'),
                 ('e62100', 'e62100'),
                 ('e62900', 'e62900'),
                 ('e62720', 'e62720'),
                 ('e62730', 'e62730'),
                 ('e62740', 'e62740'),
                 ('p65300', 'p65300'),
                 ('p65400', 'p65400'),
                 ('e68000', 'e68000'),
                 ('e82200', 'e82200'),
                 ('t27800', 't27800'),
                 ('s27860', 's27860'),
                 ('p27895', 'p27895'),
                 ('e87500', 'e87500'),
                 ('e87510', 'e87510'),
                 ('e87520', 'e87520'),
                 ('e87530', 'e87530'),
                 ('e87540', 'e87540'),
                 ('e87550', 'e87550'),
                 # ('e22250', 'e22250'),
                 # ('e23250', 'e23250'),
                 # ('e04470', 'e04470'),
                 # ('e25470', 'e25470'),
                 # ('e08000', 'e08000'),
                 # ('e60100', 'e60100'),
                 ('RECID', 'recid'),
                 ('s006', 's006'),
                 ('s008', 's008'),
                 ('s009', 's009'),
                 ('WSAMP', 'wsamp'),
                 ('TXRT', 'txrt'), ]

        self.dim = len(tax_dta)

        for attrname, varname in names:
            setattr(self, attrname, tax_dta[varname].values)

        # zero'd out "nonconst" data
        zeroed_names = ['e35300_0', 'e35600_0', 'e35910_0', 'x03150', 'e03600',
                        'e03280', 'e03900', 'e04000', 'e03700', 'c23250',
                        'e23660', 'f2555', 'e02800', 'e02610', 'e02540',
                        'e02615', 'SSIND', 'e18400', 'e18800', 'e18900',
                        'e20950', 'e19500', 'e19570', 'e19400', 'c20400',
                        'e20200', 'e20900', 'e21000', 'e21010', 'e02600',
                        '_exact', 'e11055', 'e00250', 'e30100', 'e15360',
                        'e04200', 'e37717', 'e04805', 'AGEP', 'AGES', 'PBI',
                        'SBI', 't04470', 'e58980', 'c00650', 'c00100',
                        'c04470', 'c04600', 'c21060', 'c21040', 'c17000',
                        'c18300', 'c20800', 'c02900', 'c02700', 'c23650',
                        'c01000', 'c02500', 'e24583', '_fixup', '_cmp',
                        'e59440', 'e59470', 'e59400', 'e10105', 'e83200_0',
                        'e59410', 'e59420', 'e74400', 'x62720', 'x60260',
                        'x60240', 'x60220', 'x60130', 'x62730', 'e60290',
                        'DOBYR', 'SDOBYR', 'DOBMD', 'SDOBMD', 'e62600',
                        'x62740', '_fixeic', 'e32880', 'e32890', 'CDOB1',
                        'CDOB2', 'e32750', 'e32775', 'e33420', 'e33430',
                        'e33450', 'e33460', 'e33465', 'e33470', 'x59560',
                        'EICYB1', 'EICYB2', 'EICYB3', 'e83080', 'e25360',
                        'e25430', 'e25400', 'e25500', 'e26210', 'e26340',
                        'e26205', 'e26320', 'e87482', 'e87487', 'e87492',
                        'e87497', 'e87526', 'e87522', 'e87524', 'e87528',
                        'EDCRAGE', 'e07960', 'e07700', 'e07250', 't07950',
                        'e82882', 'e82880', 'e07500', 'e08001', 'e07970',
                        'e07980', 'e10000', 'e10100', 'e10050', 'e10075',
                        'e09805', 'e09710', 'e09720', 'e87900', 'e87905',
                        'e87681', 'e87682', 'e11451', 'e11452', 'e11601',
                        'e11602', 'e60300', 'e60860', 'e60840', 'e60630',
                        'e60550', 'e60720', 'e60430', 'e60500', 'e60340',
                        'e60680', 'e60600', 'e60405', 'e60440', 'e60420',
                        'e60410', 'e61400', 'e60660', 'e60480', 'e62000',
                        'e60250', 'e40223', '_sep', '_earned', '_sey',
                        '_setax', '_feided', '_ymod', '_ymod1', '_posagi',
                        '_sit', 'xtxcr1xtxcr10', '_earned', '_xyztax',
                        '_taxinc', 'c04800', '_feitax', 'c05750', 'c24517',
                        '_taxbc', 'c60000', '_standard', 'c24516', 'c25420',
                        'c05700', 'c32880', 'c32890', '_dclim', 'c32800',
                        'c33000', 'c05800', '_othtax', 'c59560', '_agep',
                        '_ages', 'c87521', 'c87550', 'c07180',
                        'c07230', '_precrd', 'c07220', 'c59660', 'c07970',
                        'c08795', 'c09200', 'c07100', '_eitc', 'c59700',
                        'c10950', '_ymod2', '_ymod3', 'c02650', '_agierr',
                        '_ywossbe', '_ywossbc', '_prexmp', 'c17750', '_sit1',
                        '_statax', 'c37703', 'c20500', 'c20750', 'c19200',
                        'c19700', '_nonlimited', '_limitratio', '_phase2_i',
                        '_fica', '_seyoff', 'c11055', 'c15100', '_numextra',
                        '_txpyers', 'c15200', '_othded', 'c04100', 'c04200',
                        'c04500', '_amtstd', '_oldfei', 'c05200', '_cglong',
                        '_noncg', '_hasgain', '_dwks9', '_dwks5', '_dwks12',
                        '_dwks16', '_dwks17', '_dwks21', '_dwks25', '_dwks26',
                        '_dwks28', '_dwks31', 'c24505', 'c24510', 'c24520',
                        'c24530', 'c24540', 'c24534', 'c24597', 'c24598',
                        'c24610', 'c24615', 'c24550', 'c24570', '_addtax',
                        'c24560', '_taxspecial', 'c24580', 'c05100', 'c05700',
                        'c59430', 'c59450', 'c59460', '_line17', '_line19',
                        '_line22', '_line30', '_line31', '_line32', '_line36',
                        '_line33', '_line34', '_line35', 'c59485', 'c59490',
                        '_s1291', '_parents', 'c62720', 'c60260', 'c63100',
                        'c60200', 'c60240', 'c60220', 'c60130', 'c62730',
                        '_addamt', 'c62100', '_cmbtp', '_edical', '_amtsepadd',
                        '_agep', '_ages', 'c62600', 'c62700', '_alminc',
                        '_amtfei', 'c62780', 'c62900', 'c63000', 'c62740',
                        '_ngamty', 'c62745', 'y62745', '_tamt2', '_amt5pc',
                        '_amt15pc', '_amt25pc', 'c62747', 'c62755', 'c62770',
                        '_amt', 'c62800', 'c09600', 'c05800', '_ncu13',
                        '_seywage', 'c33465', 'c33470', 'c33475', 'c33480',
                        'c32840', '_tratio', 'c33200', 'c33400', 'c07180',
                        '_ieic', 'EICYB1', 'EICYB2', 'EICYB3', '_modagi',
                        '_val_ymax', '_preeitc', '_val_rtbase', '_val_rtless',
                        '_dy', 'c11070', '_nctcr', '_ctcagi', 'c87482',
                        'c87487', 'c87492', 'c87497', 'c87483', 'c87488',
                        'c87493', 'c87498', 'c87540', 'c87530', 'c87654',
                        'c87656', 'c87658', 'c87660', 'c87662', 'c87664',
                        'c87666', 'c10960', 'c87668', 'c87681', 'c87560',
                        'c87570', 'c87580', 'c87590', 'c87600', 'c87610',
                        'c87620', '_ctc1', '_ctc2', '_regcrd', '_exocrd',
                        '_ctctax', 'c07220', 'c82925', 'c82930', 'c82935',
                        'c82880', 'h82880', 'c82885', 'c82890', 'c82900',
                        'c82905', 'c82910', 'c82915',  'c82920', 'c82937',
                        'c82940', 'c11070', 'e59660', '_othadd', 'y07100',
                        'x07100', 'c08800', 'e08795', 'x07400', 'c59680',
                        '_othertax', 'e82915', 'e82940', 'SFOBYR', 'NIIT',
                        'c59720', '_comb', 'c07150', 'c10300', '_ospctax',
                        '_refund', 'c11600', 'e11450', 'e82040', 'e11500',
                        '_amed', '_xlin3', '_xlin6', 'share_corptax_burden',
                        'expanded_income', 'agg_self_employed', 'netcapgains',
                        'agg_capgains', 'total_compensation', 'dividends',
                        'agg_dividends', 'bonds', 'compensation', 'agg_bonds']

        for name in zeroed_names:
            setattr(self, name, np.zeros((self.dim,)))

        self._num = np.ones((self.dim,))

        # Aliases
        self.e22250 = self.p22250
        self.e04470 = self.p04470
        self.e23250 = self.p23250
        self.e25470 = self.p25470
        self.e08000 = self.p08000
        self.e60100 = self.p60100
        self.e27860 = self.s27860
        self.SOIYR = np.repeat(2008, self.dim)

    def mutate_imputations(self):
        """
        Calculates self._cmbtp_itemizer for this record
        """
        self._cmbtp_itemizer = imputation(self.e17500, self.e00100,
                self.e18400, self.e18425, self.e62100, self.e00700,
                self.e04470, self.e21040, self.e18500, self.e20800)

    def set_vars_for_corp_tax(self):
        """
        Calculates the variables used to distribute the corporate income tax

        compensation: float
            the sum of wages, payroll tax, employer contribution to insurance,
            and untaxed voluntary contribution to retirement plans
        dividends: float
            the individual's dividends received
        netcapgains: float
            the individual's net capital gains earnings
        bonds: float
            the individual's total bonds (taxable and untaxable)
        """

        # unsure whether to use in compensation
        ss_benefits = self.e02400

        # the individual's compensation package
        # used to calculate share from labor
        # = sum of wages (e00200 + e00250),
        # payroll taxes (employer_share_fica? should I add this? how else?),
        # employer contrib's to insurance (e33420 and archer MSA, e03600),
        # and untaxed voluntary contrib's to retirement plans
        # (e07240, not sure if from employer or voluntary)

    # TODO: not sure if we have good data on insurance or retirment
    # e00250: other dependent income (not sure whether to include)
        self.compensation = (self.e00200 + self.e00250 + self.e33420 +
                             self.e03600 + self.e07240)

        # individual's share of the dividends received
        self.dividends = self.e00600

    # JTC thinks that dividends are enough to measure stock ownership,
    # but TPC thinks both capgains and dividends should be included
        # individual's share of the capital gains received
        # c23650 = long term + short term + both (calculated in CapGains fn)
        self.netcapgains = self.e23250 + self.e22250 + self.e23660

        # bonds = tax-exempt interest + taxable interest
        # indidividual's share of total bonds
        self.bonds = self.e00400 + self.e00300

        # self-employment (E09400) and pass-through income (E02000)
        self.e_and_p = self.e09400 + self.e02000


@vectorize([float64(float64, float64, float64, float64, float64, float64,
            float64, float64, float64, float64)])
def imputation(e17500, e00100, e18400, e18425, e62100, e00700, e04470,
               e21040, e18500, e20800):

    """
    Calculates _cmbtp_itemizer
    Uses vectorize decorator to speed-up calculation process
    with NumPy data structures
    """

    # temp variables to make it easier to read
    x = max(0., e17500 - max(0., e00100) * 0.075)
    medical_adjustment = min(x, 0.025 * max(0., e00100))
    state_adjustment = max(0, max(e18400, e18425))

    _cmbtp_itemizer = (e62100 - medical_adjustment + e00700 + e04470 + e21040
                       - state_adjustment - e00100 - e18500 - e20800)

    return _cmbtp_itemizer


def read_blowup(blowup_factors):
    if isinstance(blowup_factors, pd.core.frame.DataFrame):
        BF = blowup_factors
    else:
        try:
            if not os.path.exists(blowup_factors):
                # grab blowup factors out of EGG distribution
                path_in_egg = os.path.join("taxcalc",
                                           BLOWUP_FACTORS_FILENAME)
                blowup_factors = resource_stream(Requirement.parse("taxcalc"),
                                                 path_in_egg)

            BF = pd.read_csv(blowup_factors, index_col='YEAR')
        except IOError:
            print("Missing a csv file with blowup factors. Please pass "
                  "such a csv as PUF(blowup_factors='[FILENAME]').")
            raise
            # TODO, we will need to pass the csv to the Calculator once
            # we proceed with github issue #117.

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
    BF.ASOCSEC = BF.ASOCSEC / BF.APOPN

    BF = 1 + BF.pct_change()

    return BF


def read_weights(weights):
    if isinstance(weights, pd.core.frame.DataFrame):
        WT = weights
    else:
        try:
            if not os.path.exists(weights):
                # grab weights out of EGG distribution
                path_in_egg = os.path.join("taxcalc", WEIGHTS_FILENAME)
                weights = resource_stream(Requirement.parse("taxcalc"),
                                          path_in_egg)
            WT = pd.read_csv(weights)
        except IOError:
            print("Missing a csv file with weights from the second stage "
                  "data of the data extrapolation. Please pass such a "
                  "file as PUF(weights='[FILENAME]').")
            raise
            # TODO, we will need to pass the csv to the Calculator once
            # we proceed with github issue #117.

    return WT
