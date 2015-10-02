import os
import json
from .utils import expand_array


class ParametersBase(object):

    '''Inherit from this class for Parameters, Behavior,
    and other groups of parameters that need to have
    a set_year option.  Override the __init__ method
    and DEFAULTS_FILENAME.'''

    DEFAULTS_FILENAME = None

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
            setattr(self, name,
                    expand_array(values, inflate=cpi_inflated,
                                 inflation_rates=getattr(self,
                                                         '_inflation_rates',
                                                         None),
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
        """Private method used **only** by the public implement_reform method.

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
        This is a private method that helps
        the public methods work.

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
        # implement reform provisions included in the single YEAR:MODS pair
        num_years_to_expand = (self.start_year + self.num_years) - year
        if hasattr(self, '_inflation_rates'):
            inf_rates = [self._inflation_rates[(year - self.start_year) + i]
                         for i in range(0, num_years_to_expand)]
        else:
            inf_rates = None
        paramvals = self._vals
        for name, values in year_mods[year].items():
            # determine inflation indexing status of parameter with name
            if name.endswith('_cpi'):
                continue
            if name in paramvals:
                default_cpi = paramvals[name].get('cpi_inflated', False)
            else:
                default_cpi = False
            cpi_inflated = year_mods[year].get(name + '_cpi', default_cpi)
            # set post-reform values of parameter with name
            cval = getattr(self, name, None)
            if cval is None:
                continue
            nval = expand_array(values,
                                inflate=cpi_inflated,
                                inflation_rates=inf_rates,
                                num_years=num_years_to_expand)
            cval[(self.current_year - self.start_year):] = nval
        self.set_year(self._current_year)
