"""
Tax-Calculator abstract base data class.
"""
# CODING-STYLE CHECKS:
# pycodestyle data.py
# pylint --disable=locally-disabled data.py

import os
import abc
import numpy as np
import pandas as pd
from taxcalc.growfactors import GrowFactors
from taxcalc.utils import read_egg_csv, read_egg_json, json_to_dict


class Data():
    """
    Inherit from this class for Records, and other collections of
    cross-sectional data that need to have growth factors and weights
    to extrapolate the data to years after the start_year.

    Parameters
    ----------
    data: string or Pandas DataFrame
        string describes CSV file in which records data reside;
        DataFrame already contains cross-sectional data.

    start_year: integer
        specifies calendar year of the input data.

    gfactors: GrowFactors class instance or None
        containing data growth (or extrapolation) factors.
        NOTE: the constructor should never call the _extrapolate() method.

    weights: string or Pandas DataFrame or None
        string describes CSV file in which weights reside;
        DataFrame already contains weights;
        None creates empty sample-weights DataFrame.

    Raises
    ------
    ValueError:
        if data is not a string or a DataFrame instance.
        if start_year is not an integer.
        if gfactors is not a GrowFactors class instance or None.
        if weights is not a string or a DataFrame instance or None.
        if files cannot be found.

    Returns
    -------
    class instance: Data
    """
    # suppress pylint warnings about unrecognized Data variables:
    # pylint: disable=no-member
    # suppress pylint warnings about uppercase variable names:
    # pylint: disable=invalid-name
    # suppress pylint warnings about too many class instance attributes:
    # pylint: disable=too-many-instance-attributes

    __metaclass__ = abc.ABCMeta
        
    VAR_INFO_FILE_NAME = None
    VAR_INFO_FILE_PATH = None

    def __init__(self, data, start_year, gfactors, weights):
        # pylixx: disable=too-many-statements,too-many-branches,too-many-locals
        self.__data_year = start_year
        # read specified data
        self._read_data(data)
        # handle growth factors
        is_correct_type = isinstance(gfactors, GrowFactors)
        if gfactors is not None and not is_correct_type:
            msg = 'gfactors is neither None nor a GrowFactors instance'
            raise ValueError(msg)
        self.gfactors = gfactors
        # read sample weights
        self.WT = None
        self._read_weights(weights)
        # weights must be same size as data
        if self.WT.size > 0 and self.array_length != len(self.WT.index):
            # scale-up sub-sample weights by year-specific factor
            sum_full_weights = self.WT.sum()
            self.WT = self.WT.iloc[self.__index]
            sum_sub_weights = self.WT.sum()
            factor = sum_full_weights / sum_sub_weights
            self.WT *= factor
        # specify current_year and FLPDYR values
        if isinstance(start_year, int):
            self.__current_year = start_year
        else:
            msg = 'start_year is not an integer'
            raise ValueError(msg)
        # construct sample weights for current_year
        if self.WT.size > 0:
            wt_colname = 'WT{}'.format(self.current_year)
            if wt_colname in self.WT.columns:
                self.s006 = self.WT[wt_colname] * 0.01

    @property
    def data_year(self):
        """
        Data class original data year property.
        """
        return self.__data_year

    @property
    def current_year(self):
        """
        Data class current calendar year property.
        """
        return self.__current_year

    @property
    def array_length(self):
        """
        Length of arrays in Data class's DataFrame.
        """
        return self.__dim

    def increment_year(self):
        """
        Add one to current year.
        Also, does extrapolation & reweighting for new current year.
        """
        # move to next year
        self.__current_year += 1
        # apply variable extrapolation grow factors
        if self.gfactors is not None:
            self._extrapolate(self.__current_year)
        # specify current-year sample weights
        if self.WT.size > 0:
            wt_colname = 'WT{}'.format(self.__current_year)
            self.s006 = self.WT[wt_colname] * 0.01

    def set_current_year(self, new_current_year):
        """
        Set current year to specified value.
        Unlike increment_year method, extrapolation & reweighting are skipped.
        """
        self.__current_year = new_current_year

    @staticmethod
    def read_var_info():
        """
        Read Data variables metadata from JSON file;
        returns dictionary and specifies static varname sets listed below.
        """
        assert Data.VAR_INFO_FILE_NAME is not None
        assert Data.VAR_INFOR_FILE_PATH is not None
        file_path = os.path.join(Data.VAR_INFO_FILE_PATH,
                                 Data.VAR_INFO_FILE_NAME)
        if os.path.isfile(file_path):
            with open(file_path) as pfile:
                json_text = pfile.read()
            vardict = json_to_dict(json_text)
        else:  # find file in conda package
            vardict = read_egg_json(
                self.DEFAULTS_FILE_NAME)  # pragma: no cover
        Data.INTEGER_READ_VARS = set(k for k, v in vardict['read'].items()
                                     if v['type'] == 'int')
        FLOAT_READ_VARS = set(k for k, v in vardict['read'].items()
                              if v['type'] == 'float')
        Data.MUST_READ_VARS = set(k for k, v in vardict['read'].items()
                                  if v.get('required'))
        Data.USABLE_READ_VARS = Data.INTEGER_READ_VARS | FLOAT_READ_VARS
        INT_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                  if v['type'] == 'int')
        FLOAT_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                    if v['type'] == 'float')
        FIXED_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                    if v['type'] == 'unchanging_float')
        Data.CALCULATED_VARS = (INT_CALCULATED_VARS |
                                FLOAT_CALCULATED_VARS |
                                FIXED_CALCULATED_VARS)
        Data.CHANGING_CALCULATED_VARS = FLOAT_CALCULATED_VARS
        Data.INTEGER_VARS = Data.INTEGER_READ_VARS | INT_CALCULATED_VARS
        return vardict

    # specify various sets of variable names
    INTEGER_READ_VARS = set()
    MUST_READ_VARS = set()
    USABLE_READ_VARS = set()
    CALCULATED_VARS = set()
    CHANGING_CALCULATED_VARS = set()
    INTEGER_VARS = set()

    # ----- begin private methods of Data class -----

    def _read_data(self, data):
        """
        Read data from file or use specified DataFrame as data.
        """
        # pylint: disable=too-many-statements,too-many-branches
        if Data.INTEGER_VARS == set():
            Data.read_var_info()
        # read specified data
        if isinstance(data, pd.DataFrame):
            taxdf = data
        elif isinstance(data, str):
            if os.path.isfile(data):
                taxdf = pd.read_csv(data)
            else:  # find file in conda package
                taxdf = read_egg_csv(data)  # pragma: no cover
        else:
            msg = 'data is neither a string nor a Pandas DataFrame'
            raise ValueError(msg)
        self.__dim = len(taxdf.index)
        self.__index = taxdf.index
        # create class variables using taxdf column names
        READ_VARS = set()
        self.IGNORED_VARS = set()
        for varname in list(taxdf.columns.values):
            if varname in Data.USABLE_READ_VARS:
                READ_VARS.add(varname)
                if varname in Data.INTEGER_READ_VARS:
                    setattr(self, varname,
                            taxdf[varname].astype(np.int32).values)
                else:
                    setattr(self, varname,
                            taxdf[varname].astype(np.float64).values)
            else:
                self.IGNORED_VARS.add(varname)
        # check that MUST_READ_VARS are all present in taxdf
        if not Data.MUST_READ_VARS.issubset(READ_VARS):
            msg = 'Records data missing one or more MUST_READ_VARS'
            raise ValueError(msg)
        # delete intermediate taxdf object
        del taxdf
        # create other class variables that are set to all zeros
        UNREAD_VARS = Data.USABLE_READ_VARS - READ_VARS
        ZEROED_VARS = Data.CALCULATED_VARS | UNREAD_VARS
        for varname in ZEROED_VARS:
            if varname in Data.INTEGER_VARS:
                setattr(self, varname,
                        np.zeros(self.array_length, dtype=np.int32))
            else:
                setattr(self, varname,
                        np.zeros(self.array_length, dtype=np.float64))
        # delete intermediate variables
        del READ_VARS
        del UNREAD_VARS
        del ZEROED_VARS

    def zero_out_changing_calculated_vars(self):
        """
        Set to zero all variables in the Data.CHANGING_CALCULATED_VARS set.
        """
        for varname in Data.CHANGING_CALCULATED_VARS:
            var = getattr(self, varname)
            var.fill(0.)
        del var

    def _read_weights(self, weights):
        """
        Read Records weights from file or
        use specified DataFrame as data or
        create empty DataFrame if None.
        Assumes weights are integers equal to 100 times the real weight.
        """
        if weights is None:
            setattr(self, 'WT', pd.DataFrame({'nothing': []}))
            return
        if isinstance(weights, pd.DataFrame):
            WT = weights
        elif isinstance(weights, str):
            if os.path.isfile(weights):
                WT = pd.read_csv(weights)
            else:  # find file in conda package
                WT = read_egg_csv(
                    os.path.basename(weights))  # pragma: no cover
        else:
            msg = 'weights is not None or a string or a Pandas DataFrame'
            raise ValueError(msg)
        assert isinstance(WT, pd.DataFrame)
        setattr(self, 'WT', WT.astype(np.int32))
        del WT

    def _extrapolate(self, year):
        """
        Apply to dats variables the growth factor values for specified year.
        """
        # Override this empty method in subclass
