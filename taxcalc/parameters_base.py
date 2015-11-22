"""
Tax-Calculator abstract base parameters class.
"""
import os
import json
import numpy as np
from abc import ABCMeta


class ParametersBase(object):
    """
    Inherit from this class for Parameters, Behavior, Growth, and
    other groups of parameters that need to have a set_year method.
    Override this __init__ method and DEFAULTS_FILENAME.
    """
    __metaclass__ = ABCMeta

    DEFAULTS_FILENAME = None

    @classmethod
    def default_data(cls, metadata=False, start_year=None):
        """
        Return parameter data read from the subclass's json file.

        Parameters
        ----------
        metadata: boolean

        start_year: int

        Returns
        -------
        params: dictionary of data
        """
        # extract different data from DEFAULT_FILENAME depending on start_year
        if start_year:  # if start_year is not None
            nyrs = start_year - cls.JSON_START_YEAR + 1
            ppo = cls(num_years=nyrs)
            ppo.set_year(start_year)
            params = getattr(ppo, '_vals')
            params = ParametersBase._revised_default_data(params, start_year,
                                                          nyrs, ppo)
        else:  # if start_year is None
            params = cls._params_dict_from_json_file()
        # return different data from params dict depending on metadata value
        if metadata:
            return params
        else:
            return {name: data['value'] for name, data in params.items()}

    def __init__(self, *args, **kwargs):
        msg = 'Override __init__ and call self.initialize from it.'
        raise NotImplementedError(msg)

    def initialize(self, start_year, num_years):
        self._current_year = start_year
        self._start_year = start_year
        self._num_years = num_years
        self._end_year = start_year + num_years - 1
        self.set_default_vals()

    def set_default_vals(self):
        for name, data in self._vals.items():
            cpi_inflated = data.get('cpi_inflated', False)
            values = data['value']
            index_rates = self.indexing_rates(name)
            setattr(self, name,
                    self.expand_array(values, inflate=cpi_inflated,
                                      inflation_rates=index_rates,
                                      num_years=self._num_years))
        self.set_year(self._start_year)

    @property
    def num_years(self):
        return self._num_years

    @property
    def current_year(self):
        return self._current_year

    @property
    def end_year(self):
        return self._end_year

    @property
    def start_year(self):
        return self._start_year

    def inflation_rates(self):
        """
        Override this method in subclass when appropriate.
        """
        return None

    def wage_growth_rates(self):
        """
        Override this method in subclass when appropriate.
        """
        return None

    def indexing_rates(self, param_name):
        if param_name == '_SS_Earnings_c':
            return self.wage_growth_rates()
        else:
            return self.inflation_rates()

    def indexing_rates_for_update(self, param_name,
                                  calyear, num_years_to_expand):
        if param_name == '_SS_Earnings_c':
            rates = self.wage_growth_rates()
        else:
            rates = self.inflation_rates()
        if rates:
            expand_rates = [rates[(calyear - self.start_year) + i]
                            for i in range(0, num_years_to_expand)]
            return expand_rates
        else:
            return None

    def set_year(self, year):
        """
        Set parameters to values for specified calendar year.

        Parameters
        ----------
        year: int
            calendar year for which to current_year and parameter values

        Raises
        ------
        ValueError:
            if year is not in [start_year, end_year] range.

        Returns
        -------
        nothing: void

        Notes
        -----
        To increment the current year, use the following statement::

            behavior.set_year(behavior.current_year + 1)

        where behavior is a policy Behavior object.
        """
        if year < self.start_year or year > self.end_year:
            msg = 'year passed to set_year() must be in [{},{}] range.'
            raise ValueError(msg.format(self.start_year, self.end_year))
        self._current_year = year
        year_zero_indexed = year - self._start_year
        for name in self._vals:
            arr = getattr(self, name)
            setattr(self, name[1:], arr[year_zero_indexed])

    # ----- begin private methods of ParametersBase class -----

    @staticmethod
    def _revised_default_data(params, start_year, nyrs, ppo):
        """
        Return revised default parameter data.

        Parameters
        ----------
        params: dictionary of NAME:DATA pairs for each parameter
            as defined in calling default_data staticmethod.

        start_year: int
            as defined in calling default_data staticmethod.

        nyrs: int
            as defined in calling default_data staticmethod.

        ppo: Policy object
            as defined in calling default_data staticmethod.

        Returns
        -------
        params: dictionary of revised parameter data

        Notes
        -----
        This staticmethod is called from default_data staticmethod in
        order to reduce the complexity of the default_data staticmethod.
        """
        start_year_str = '{}'.format(start_year)
        for name, data in params.items():
            data['start_year'] = start_year
            values = data['value']
            num_values = len(values)
            if num_values <= nyrs:
                # val should be the single start_year value
                rawval = getattr(ppo, name[1:])
                if isinstance(rawval, np.ndarray):
                    val = rawval.tolist()
                else:
                    val = rawval
                data['value'] = [val]
                data['row_label'] = [start_year_str]
            else:  # if num_values > nyrs
                # val should extend beyond the start_year value
                data['value'] = data['value'][(nyrs - 1):]
                data['row_label'] = data['row_label'][(nyrs - 1):]
        return params

    @classmethod
    def _params_dict_from_json_file(cls):
        """
        Read DEFAULTS_FILENAME file and return complete dictionary.

        Parameters
        ----------
        nothing: void

        Returns
        -------
        params: dictionary
            containing complete contents of DEFAULTS_FILENAME file.
        """
        if cls.DEFAULTS_FILENAME is None:
            msg = 'DEFAULTS_FILENAME must be overrriden by inheriting class'
            raise NotImplementedError(msg)
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            cls.DEFAULTS_FILENAME)
        if os.path.exists(path):
            with open(path) as pfile:
                params_dict = json.load(pfile)
        else:
            from pkg_resources import resource_stream, Requirement
            path_in_egg = os.path.join('taxcalc', cls.DEFAULTS_FILENAME)
            buf = resource_stream(Requirement.parse('taxcalc'), path_in_egg)
            as_bytes = buf.read()
            as_string = as_bytes.decode("utf-8")
            params_dict = json.loads(as_string)
        return params_dict

    def _update(self, year_mods):
        """
        Private method used by public implement_reform and update_* methods
        in inheriting classes.

        Parameters
        ----------
        year_mods: dictionary containing a single YEAR:MODS pair
            see Notes below for details on dictionary structure.

        Raises
        ------
        ValueError:
            if year_mods is not a dictionary of the expected structure.

        Returns
        -------
        nothing: void

        Notes
        -----
        This is a private method that should **never** be used by clients
        of the inheriting classes.  Instead, always use the public
        implement_reform or update_behavior methods.
        This is a private method that helps the public methods work.

        This method implements a policy reform or behavior modification,
        the provisions of which are specified in the year_mods dictionary,
        that changes the values of some policy parameters in objects of
        inheriting classes.  This year_mods dictionary contains exactly one
        YEAR:MODS pair, where the integer YEAR key indicates the
        calendar year for which the reform provisions in the MODS
        dictionary are implemented.  The MODS dictionary contains
        PARAM:VALUE pairs in which the PARAM is a string specifying
        the policy parameter (as used in the DEFAULTS_FILENAME default
        parameter file) and the VALUE is a Python list of post-reform
        values for that PARAM in that YEAR.  Beginning in the year
        following the implementation of a reform provision, the
        parameter whose value has been changed by the reform continues
        to be inflation indexed, if relevant, or not be inflation indexed
        according to that parameter's cpi_inflated value loaded from
        DEFAULTS_FILENAME.  For a cpi-related parameter, a reform can change
        the indexing status of a parameter by including in the MODS dictionary
        a term that is a PARAM_cpi:BOOLEAN pair specifying the post-reform
        indexing status of the parameter.

        So, for example, to raise the OASDI (i.e., Old-Age, Survivors,
        and Disability Insurance) maximum taxable earnings beginning
        in 2018 to $500,000 and to continue indexing it in subsequent
        years as in current-law policy, the YEAR:MODS dictionary would
        be as follows::

            {2018: {"_SS_Earnings_c":[500000]}}

        But to raise the maximum taxable earnings in 2018 to $500,000
        without any indexing in subsequent years, the YEAR:MODS
        dictionary would be as follows::

            {2018: {"_SS_Earnings_c":[500000], "_SS_Earnings_c_cpi":False}}

        And to raise in 2019 the starting AGI for EITC phaseout for
        married filing jointly filing status (which is a two-dimensional
        policy parameter that varies by the number of children from zero
        to three or more and is inflation indexed), the YEAR:MODS dictionary
        would be as follows::

            {2019: {"_EITC_ps_MarriedJ":[[8000, 8500, 9000, 9500]]}}

        Notice the pair of double square brackets around the four values
        for 2019.  The one-dimensional parameters above require only a pair
        of single square brackets.

        To model a change in behavior substitution effect, a year_mods dict
        example would be {2014: {'_BE_inc': [0.2, 0.3]}}
        """
        # check YEAR value in the single YEAR:MODS dictionary parameter
        if not isinstance(year_mods, dict):
            msg = 'year_mods is not a dictionary'
            raise ValueError(msg)
        if len(year_mods.keys()) != 1:
            msg = 'year_mods dictionary must contain a single YEAR:MODS pair'
            raise ValueError(msg)
        year = list(year_mods.keys())[0]
        if year != self.current_year:
            msg = 'YEAR={} in year_mods is not equal to current_year={}'
            raise ValueError(msg.format(year, self.current_year))
        # check that MODS is a dictionary
        if not isinstance(year_mods[year], dict):
            msg = 'mods in year_mods is not a dictionary'
            raise ValueError(msg)
        # implement reform provisions included in the single YEAR:MODS pair
        num_years_to_expand = (self.start_year + self.num_years) - year
        all_names = set(year_mods[year].keys())  # no duplicate keys in a dict
        used_names = set()  # set of used parameter names in MODS dict
        for name, values in year_mods[year].items():
            # determine indexing status of parameter with name for year
            if name.endswith('_cpi'):
                continue  # handle elsewhere in this method
            if name in self._vals:
                vals_indexed = self._vals[name].get('cpi_inflated', False)
            else:
                msg = 'parameter name {} not in parameter values dictionary'
                raise ValueError(msg.format(name))
            name_plus_cpi = name + '_cpi'
            if name_plus_cpi in year_mods[year].keys():
                used_names.add(name_plus_cpi)
                indexed = year_mods[year].get(name_plus_cpi)
                self._vals[name]['cpi_inflated'] = indexed  # remember status
            else:
                indexed = vals_indexed
            # set post-reform values of parameter with name
            used_names.add(name)
            cval = getattr(self, name, None)
            if cval is None:
                msg = 'parameter {} in year_mods for year [] is unknown'
                raise ValueError(msg.format(name, year))
            index_rates = self.indexing_rates_for_update(name, year,
                                                         num_years_to_expand)
            nval = self.expand_array(values,
                                     inflate=indexed,
                                     inflation_rates=index_rates,
                                     num_years=num_years_to_expand)
            cval[(year - self.start_year):] = nval
        # handle unused parameter names, all of which end in _cpi, but some
        # parameter names ending in _cpi were handled above
        unused_names = all_names - used_names
        for name in unused_names:
            used_names.add(name)
            pname = name[:-4]  # root parameter name
            if pname not in self._vals:
                msg = 'root parameter name {} not in values dictionary'
                raise ValueError(msg.format(pname))
            pindexed = year_mods[year][name]
            self._vals[pname]['cpi_inflated'] = pindexed  # remember status
            cval = getattr(self, pname, None)
            if cval is None:
                msg = 'parameter {} in year_mods for year [] is unknown'
                raise ValueError(msg.format(pname, year))
            pvalues = [cval[year - self.start_year]]
            index_rates = self.indexing_rates_for_update(name, year,
                                                         num_years_to_expand)
            nval = self.expand_array(pvalues,
                                     inflate=pindexed,
                                     inflation_rates=index_rates,
                                     num_years=num_years_to_expand)
            cval[(year - self.start_year):] = nval
        # confirm that all names have been used
        assert len(used_names) == len(all_names)
        # implement updated parameters for year
        self.set_year(year)

    @staticmethod
    def expand_1D(x, inflate, inflation_rates, num_years):
        """
        Expand the given data to account for the given number of budget years.
        If necessary, pad out additional years by increasing the last given
        year using the given inflation_rates list.
        """
        if isinstance(x, np.ndarray):
            if len(x) >= num_years:
                return x
            else:
                ans = np.zeros(num_years, dtype='f8')
                ans[:len(x)] = x
                if inflate:
                    extra = []
                    cur = x[-1]
                    for i in range(0, num_years - len(x)):
                        inf_idx = i + len(x) - 1
                        cur *= (1. + inflation_rates[inf_idx])
                        extra.append(cur)
                else:
                    extra = [float(x[-1]) for i in
                             range(1, num_years - len(x) + 1)]

                ans[len(x):] = extra
                return ans.astype(x.dtype, casting='unsafe')
        return ParametersBase.expand_1D(np.array([x]),
                                        inflate,
                                        inflation_rates,
                                        num_years)

    @staticmethod
    def expand_2D(x, inflate, inflation_rates, num_years):
        """
        Expand the given data to account for the given number of budget years.
        For 2D arrays, we expand out the number of rows until we have num_years
        number of rows. For each expanded row, we inflate using the given
        inflation rates list.
        """
        if isinstance(x, np.ndarray):
            # Look for -1s and create masks if present
            last_good_row = -1
            keep_user_data_mask = []
            keep_calc_data_mask = []
            has_nones = False
            for row in x:
                keep_user_data_mask.append([1 if i != -1 else 0 for i in row])
                keep_calc_data_mask.append([0 if i != -1 else 1 for i in row])
                if not np.any(row == -1):
                    last_good_row += 1
                else:
                    has_nones = True
            if x.shape[0] >= num_years and not has_nones:
                return x
            else:
                if has_nones:
                    c = x[:last_good_row + 1]
                    keep_user_data_mask = np.array(keep_user_data_mask)
                    keep_calc_data_mask = np.array(keep_calc_data_mask)

                else:
                    c = x
                ans = np.zeros((num_years, c.shape[1]))
                ans[:len(c), :] = c
                if inflate:
                    extra = []
                    cur = c[-1]
                    for i in range(0, num_years - len(c)):
                        inf_idx = i + len(c) - 1
                        cur = np.array(cur * (1. + inflation_rates[inf_idx]))
                        extra.append(cur)
                else:
                    extra = [c[-1, :] for i in
                             range(1, num_years - len(c) + 1)]
                ans[len(c):, :] = extra
                if has_nones:
                    # Use masks to "mask in" provided data and "mask out"
                    # data we don't need (produced in rows with a None value)
                    ans = ans * keep_calc_data_mask
                    user_vals = x * keep_user_data_mask
                    ans = ans + user_vals
                return ans.astype(c.dtype, casting='unsafe')
        return ParametersBase.expand_2D(np.array(x), inflate,
                                        inflation_rates, num_years)

    @staticmethod
    def strip_Nones(x):
        """
        Takes a list of scalar values or a list of lists.
        If it is a list of scalar values, when None is encountered, we
        return everything encountered before. If a list of lists, we
        replace None with -1 and return

        Parameters
        ----------
        x: list

        Returns
        -------
        list
        """
        accum = []
        for val in x:
            if val is None:
                return accum
            if not isinstance(val, list):
                accum.append(val)
            else:
                for i, v in enumerate(val):
                    if v is None:
                        val[i] = -1
                accum.append(val)

        return accum

    @staticmethod
    def expand_array(x, inflate, inflation_rates, num_years):
        """
        Dispatch to either expand_1D or expand_2D
        depending on the dimension of x

        Parameters
        ----------
        x : value to expand

        inflate: Boolean
            As we expand, inflate values if this is True, otherwise, just copy

        inflation_rates: list of inflation rates
            Annual decimal inflation rates

        num_years: int
            Number of budget years to expand

        Returns
        -------
        expanded numpy array
        """
        x = np.array(ParametersBase.strip_Nones(x))
        try:
            if len(x.shape) == 1:
                return ParametersBase.expand_1D(x, inflate, inflation_rates,
                                                num_years)
            elif len(x.shape) == 2:
                return ParametersBase.expand_2D(x, inflate, inflation_rates,
                                                num_years)
            else:
                raise ValueError("Need a 1D or 2D array")
        except AttributeError:
            raise ValueError("Must pass a numpy array")
