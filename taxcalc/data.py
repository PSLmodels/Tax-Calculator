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
    Inherit from this class for Records and other collections of
    cross-sectional data that need to have growth factors and sample
    weights to age the data to years after the start_year.

    Parameters
    ----------
    data: string or Pandas DataFrame
        string describes CSV file in which data reside;
        DataFrame already contains cross-sectional data for start_year.
        NOTE: data=None is allowed but the returned instance contains only
              the data variable information in the specified VARINFO file.
        NOTE: when using custom data, set this argument to a DataFrame.

    start_year: integer
        specifies calendar year of the input data.

    gfactors: None or GrowFactors class instance
        None implies empty growth factors DataFrame;
        instance contains data growth factors.

    weights: None or string or Pandas DataFrame
        None creates empty sample weights DataFrame.
        string describes CSV file in which sample weights reside;
        DataFrame already contains sample weights.
        NOTE: when using custom weights, set this argument to a DataFrame.
        NOTE: assumes weights are integers that are 100 times the real weights.

    weights_scale: float
        specifies the weights scaling factor used to convert contents
        of weights file into the s006 variable.  PUF and CPS input data
        generated in the taxdata repository use a weights_scale of 0.01,
        while TMD input data generated in the tax-microdata repository
        use a 1.0 weights_scale value.

    Raises
    ------
    ValueError:
        if data is not a string or a DataFrame instance.
        if start_year is not an integer.
        if gfactors is not None or a GrowFactors class instance
        if weights is not None or a string or a DataFrame instance.
        if gfactors and weights are not consistent.
        if files cannot be found.

    Returns
    -------
    class instance: Data
    """
    # pylint: disable=too-many-instance-attributes,invalid-name

    __metaclass__ = abc.ABCMeta

    VARINFO_FILE_NAME = None
    VARINFO_FILE_PATH = None

    def __init__(self, data, start_year, gfactors=None,
                 weights=None, weights_scale=0.01):
        # pylint: disable=too-many-arguments,too-many-positional-arguments

        # initialize data variable info sets and read variable information
        self.INTEGER_READ_VARS = set()
        self.MUST_READ_VARS = set()
        self.USABLE_READ_VARS = set()
        self.CALCULATED_VARS = set()
        self.CHANGING_CALCULATED_VARS = set()
        self.INTEGER_VARS = set()
        self._read_var_info()
        if data is not None:
            # check consistency of specified gfactors and weights
            if gfactors is None and weights is None:
                self.__aging_data = False
            elif gfactors is not None and weights is not None:
                self.__aging_data = True
            else:
                raise ValueError('gfactors and weights are inconsistent')
            # check start_year type and remember specified start_year
            if not isinstance(start_year, int):
                raise ValueError('start_year is not an integer')
            self.__data_year = start_year
            self.__current_year = start_year
            # read specified data
            self._read_data(data)
            # handle growth factors
            if self.__aging_data:
                if not isinstance(gfactors, GrowFactors):
                    raise ValueError('gfactors is not a GrowFactors instance')
            self.gfactors = gfactors
            # read sample weights
            self.WT = None
            self.weights_scale = weights_scale
            if self.__aging_data:
                self._read_weights(weights)
                # ... weights must be same size as data
                if self.array_length > len(self.WT.index):
                    raise ValueError("Data has more records than weights.")
                if self.array_length < len(self.WT.index):
                    # scale-up sub-sample weights by year-specific factor
                    sum_full_weights = self.WT.sum()
                    self.WT = self.WT.iloc[self.__index]
                    sum_sub_weights = self.WT.sum()
                    factor = sum_full_weights / sum_sub_weights
                    self.WT *= factor
                # ... construct sample weights for current_year
                wt_colname = f'WT{self.current_year}'
                assert wt_colname in self.WT.columns, (
                    f'no weights for start year {self.current_year}'
                )
                self.s006 = self.WT[wt_colname] * self.weights_scale

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
        Add one to current year; and also does extrapolation & reweighting
        of data for the new current year if self._aging_data is True.
        """
        # move to next year
        self.__current_year += 1
        if self.__aging_data:
            # ... apply variable extrapolation growth factors
            self._extrapolate(self.__current_year)
            # ... specify current-year sample weights
            wt_colname = f'WT{self.__current_year}'
            assert wt_colname in self.WT.columns, (
                f'no weights for new year {self.current_year}'
            )
            self.s006 = self.WT[wt_colname] * self.weights_scale

    # ----- begin private methods of Data class -----

    def _read_var_info(self):
        """
        Read Data variables metadata from JSON file and
        specifies static variable name sets listed above.
        """
        assert self.VARINFO_FILE_NAME is not None
        assert self.VARINFO_FILE_PATH is not None
        file_path = os.path.join(self.VARINFO_FILE_PATH,
                                 self.VARINFO_FILE_NAME)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as pfile:
                json_text = pfile.read()
            vardict = json_to_dict(json_text)
        else:  # find file in taxcalc package
            vardict = read_egg_json(  # pragma: no cover
                self.VARINFO_FILE_NAME
            )
        self.INTEGER_READ_VARS = set(k for k, v in vardict['read'].items()
                                     if v['type'] == 'int')
        FLOAT_READ_VARS = set(k for k, v in vardict['read'].items()
                              if v['type'] == 'float')
        self.MUST_READ_VARS = set(k for k, v in vardict['read'].items()
                                  if v.get('required'))
        self.USABLE_READ_VARS = self.INTEGER_READ_VARS | FLOAT_READ_VARS
        INT_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                  if v['type'] == 'int')
        FLOAT_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                    if v['type'] == 'float')
        FIXED_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                    if v['type'] == 'unchanging_float')
        self.CALCULATED_VARS = (INT_CALCULATED_VARS |
                                FLOAT_CALCULATED_VARS |
                                FIXED_CALCULATED_VARS)
        self.CHANGING_CALCULATED_VARS = FLOAT_CALCULATED_VARS
        self.INTEGER_VARS = self.INTEGER_READ_VARS | INT_CALCULATED_VARS

    def _read_data(self, data):
        """
        Read data from file or use specified DataFrame as data.
        """
        # pylint: disable=too-many-branches
        if data is None:
            return  # because there are no data to read
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
            if varname in self.USABLE_READ_VARS:
                READ_VARS.add(varname)
                if varname in self.INTEGER_READ_VARS:
                    setattr(self, varname,
                            taxdf[varname].astype(np.int32).values)
                else:
                    setattr(self, varname,
                            taxdf[varname].astype(np.float64).values)
            else:
                self.IGNORED_VARS.add(varname)
        # check that MUST_READ_VARS are all present in taxdf
        if not self.MUST_READ_VARS.issubset(READ_VARS):
            msg = 'data missing one or more MUST_READ_VARS'
            raise ValueError(msg)
        # delete intermediate taxdf object
        del taxdf
        # create other class variables that are set to all zeros
        UNREAD_VARS = self.USABLE_READ_VARS - READ_VARS
        ZEROED_VARS = self.CALCULATED_VARS | UNREAD_VARS
        for varname in ZEROED_VARS:
            if varname in self.INTEGER_VARS:
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
        Set to zero all variables in the self.CHANGING_CALCULATED_VARS set.
        """
        for varname in self.CHANGING_CALCULATED_VARS:
            var = getattr(self, varname)
            var.fill(0.)
        del var

    def _read_weights(self, weights):
        """
        Read sample weights from file or
        use specified DataFrame as weights or
        create empty DataFrame if None.
        """
        if weights is None:
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
        setattr(self, 'WT', WT.astype(np.float64))
        del WT

    def _extrapolate(self, year):
        """
        Apply to data variables the growth factor values for specified year.
        """
        # Override this empty method in subclass
