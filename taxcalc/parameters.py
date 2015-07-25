""" OSPC Tax-Calculator taxcalc Parameters class.
"""
# PYLINT USAGE: pylint --disable=locally-disabled parameters.py

from .utils import expand_array
import os
import json


DEFAULT_START_YEAR = 2013


class Parameters(object):
    """ Constructor for class that contains federal income tax parameters.

    If both **inflation_rate** and **inflation_rates** are None, the
    built-in default inflation rates are used.

    Parameters
    ----------
    start_year: integer
        first calendar year for policy parameters.

    budget_years: integer
        number of calendar years for which to specify policy parameter
        values beginning with start_year.

    inflation_rate: float
        constant inflation rate used to project future policy parameter
        values.

    inflation_rates: dictionary of YEAR:RATE pairs
        variable inflation rates used to project future policy parameter
        values.

    data: dictionary
        dictionary of policy parameters; if data=None, policy parameters
        are read from the params.json file.

    Raises
    ------
    ValueError:
        if **inflation_rate** is not None and **inflation_rates** is not None.

    Returns
    -------
    class instance: Parameters
    """

    CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
    PARAMS_FILENAME = "params.json"
    params_path = os.path.join(CURRENT_PATH, PARAMS_FILENAME)

    # default inflation rates by year
    __rates = {2013:0.015, 2014:0.020, 2015:0.022, 2016:0.020, 2017:0.021,
               2018:0.022, 2019:0.023, 2020:0.024, 2021:0.024, 2022:0.024,
               2023:0.024, 2024:0.024}


    @classmethod
    def default_inflation_rate(cls, calyear):
        """ Return default inflation rate for specified calendar year.

        Parameters
        ----------
        calyear: integer
            calendar year (for example, 2013).

        Returns
        -------
        default inflation rate: float
            decimal (not percentage) annual inflation rate for calyear.
        """
        return cls.__rates[calyear]


    @classmethod
    def from_file(cls, file_name, **kwargs):
        """ Read policy parameters from JSON file with specified file_name.
        """
        if file_name:
            with open(file_name) as pfile:
                params = json.loads(pfile.read())
        else:
            params = None
        return cls(data=params, **kwargs)


    def __init__(self, start_year=DEFAULT_START_YEAR, budget_years=12,
                 inflation_rate=None, inflation_rates=None, data=None):
        """ Parameters class constructor.
        """
        #pylint: disable=too-many-arguments

        if inflation_rate and inflation_rates:
            raise ValueError("Can only specify either one constant inflation"
                             " rate or a list of inflation rates")

        self._inflation_rates = None

        if inflation_rate:
            self._inflation_rates = [inflation_rate] * budget_years

        if inflation_rates:
            assert len(inflation_rates) == budget_years
            self._inflation_rates = [inflation_rates[start_year + i]
                                     for i in range(0, budget_years)]

        if not self._inflation_rates:
            self._inflation_rates = [self.__rates[start_year + i]
                                     for i in range(0, budget_years)]

        self._current_year = start_year
        self._start_year = start_year
        self._budget_years = budget_years

        if data:
            self._vals = data
        else:
            self._vals = default_data(metadata=True)

        # initialize parameter values
        for name, data in self._vals.items():
            cpi_inflated = data.get('cpi_inflated', False)
            values = data['value']
            setattr(self, name,
                    expand_array(values, inflate=cpi_inflated,
                                 inflation_rates=self._inflation_rates,
                                 num_years=budget_years))
        self.set_year(start_year)


    def update(self, year_mods):
        """ Apply year_mods policy-parameter-reform dictionary to parameters.

        Notes
        -----
        This method implements a policy reform, the provisions of
        which are specified in the year_mods dictionary, that changes
        the values of some policy parameters in this Parameters
        object.  This year_modes dictionary contains exactly one
        YEAR:MODS pair, where the integer YEAR key indicates the
        calendar year for which the reform provisions in the MODS
        dictionary are implemented.  The MODS dictionary contains
        PARAM:VALUE pairs in which the PARAM is a string specifying
        the policy parameter (as used in the params.json default
        parameter file) and the VALUE is a Python list of post-reform
        values for that PARAM in that YEAR.  Beginning in the year
        following the implementation of a reform provision, the
        parameter whose value has been changed by the reform continues
        to be inflation indexed or not be inflation indexed according
        to that parameter's cpi_inflated value in the params.json
        file.  But a reform can change the indexing status of a
        parameter by including in the MODS dictionary a term that is a
        PARAM_cpi:BOOLEAN pair specifying the post-reform indexing
        status of the parameter.

        So, for example, to raise the OASDI (i.e., Old-Age, Survivors,
        and Disability Insurance) maximum taxable earnings beginning
        in 2018 to $500,000 and to continue indexing it in subsequent
        years as in current-law policy, the YEAR:MODS dictionary would
        be as follows:
        {2018: {"_SS_Earnings_c":[500000]}}.

        But to raise the maximum taxable earnings in 2018 to $500,000
        without any indexing in subsequent years, the YEAR:MODS
        dictionary would be as follows:
        {2018: {"_SS_Earnings_c":[500000], "_SS_Earnings_c_cpi":False}}.

        And to raise in 2018 the starting AGI for EITC phaseout for
        married filing jointly filing status (which varies by the
        number of children from zero to three or more and is inflation
        indexed), the YEAR:MODS dictionary would be as follows:
        {2018: {"_EITC_ps_MarriedJ":[8000, 8500, 9000, 9500]}}.

        Parameters
        ----------
        year_mods: dictionary of a single YEAR:MODS pair
            see Notes above for details on dictionary structure.

        Returns
        -------
        nothing: void
        """
        # check YEAR value in the single YEAR:MODS dictionary parameter
        if not isinstance(year_mods, dict):
            msg = ('Parameters.update method requires year_mods dictionary '
                   'as its only parameter.')
            raise ValueError(msg)
        if len(year_mods.keys()) != 1:
            msg = ('Parameters.update method requires year_mods dictionary '
                   'with a single YEAR:MODS pair --- not {} pairs.')
            raise ValueError(msg.format(len(year_mods.keys())))
        year = year_mods.keys()[0]
        if not isinstance(year, int):
            msg = ('Parameters.update method requires year_mods dictionary '
                   'with a single YEAR:MODS pair where YEAR is an integer '
                   '--- not this [{}] value.')
            raise ValueError(msg.format(year))
        if year != self.current_year:
            msg = ('Parameters.update method requires year_mods dictionary '
                   'with a single YEAR:MODS pair where YEAR is equal to '
                   'current_year={} --- not {} year.')
            raise ValueError(msg.format(self.current_year, year))
        if year < self.start_year:
            msg = ('Parameters.update method requires year_mods dictionary '
                   'with a single YEAR:MODS pair where YEAR is not less '
                   'than start__year={} --- not {} year.')
            raise ValueError(msg.format(self.start_year, year))

        # implement reform provisions included in the single YEAR:MODS pair
        num_years_to_expand = (self.start_year + self.budget_years) - year
        paramvals = self._vals #TODO: requires __init__(...,data=None)
        for name, values in year_mods[year].items():
            # determine indexing status of parameter with name
            if name.endswith('_cpi'):
                continue
            if name in paramvals:
                default_cpi = paramvals[name].get('cpi_inflated', False)
            else:
                default_cpi = False
            cpi_inflated = year_mods[year].get(name + '_cpi', default_cpi)
            # set post-reform values of parameter with name
            inf_rates = [self._inflation_rates[(year - self.start_year) + i]
                         for i in range(0, num_years_to_expand)]
            nval = expand_array(values,
                                inflate=cpi_inflated,
                                inflation_rates=inf_rates,
                                num_years=num_years_to_expand)
            if self.current_year > self.start_year:
                cur_val = getattr(self, name)
                cur_val[(self.current_year - self.start_year):] = nval
            else:
                setattr(self, name, nval)
        self.set_year(self._current_year)


    @property
    def current_year(self):
        """ Current policy parameter year property.
        """
        return self._current_year


    @property
    def start_year(self):
        """ First policy parameter year property.
        """
        return self._start_year


    @property
    def budget_years(self):
        """ Number of policy parameter years property.
        """
        return self._budget_years


    def increment_year(self):
        """ Increase current_year by one and set parameters for that year.
        """
        self._current_year += 1
        self.set_year(self._current_year)


    def set_year(self, year):
        """ Set policy parameters to values for specified year.
        """
        for name in self._vals:
            arr = getattr(self, name)
            setattr(self, name[1:], arr[year-self._start_year])


def default_data(metadata=False, start_year=None):
    """ Retrieve current-law policy parameters from params.json file.
    """
    #pylint: disable=too-many-locals,too-many-branches

    if not os.path.exists(Parameters.params_path):
        from pkg_resources import resource_stream, Requirement
        path_in_egg = os.path.join("taxcalc", Parameters.PARAMS_FILENAME)
        buf = resource_stream(Requirement.parse("taxcalc"), path_in_egg)
        _bytes = buf.read()
        as_string = _bytes.decode("utf-8")
        params = json.loads(as_string)
    else:
        with open(Parameters.params_path) as pfile:
            params = json.load(pfile)

    if start_year:
        for pdv in params.values(): # pdv = parameter dictionary value
            first_year = pdv.get('start_year', DEFAULT_START_YEAR)
            assert isinstance(first_year, int)

            if start_year < first_year:
                msg = "Can't set a start year of {0}, because it is before {1}"
                raise ValueError(msg.format(start_year, first_year))

            # set the new start year:
            pdv['start_year'] = start_year

            # work with the values
            vals = pdv['value']
            last_year_for_data = first_year + len(vals) - 1

            if last_year_for_data < start_year:
                if pdv['row_label']:
                    pdv['row_label'] = ["2015"]
                # need to produce new values
                new_val = vals[-1]
                if pdv['cpi_inflated'] is True:
                    for cyr in range(last_year_for_data, start_year):
                        ifactor = 1.0 + Parameters.default_inflation_rate(cyr)
                        if isinstance(new_val, list):
                            new_val = [x * ifactor for x in new_val]
                        else:
                            new_val *= ifactor
                # set the new values
                pdv['value'] = [new_val]

            else:
                # need to get rid of [first_year, ..., start_year-1] values
                years_to_chop = start_year - first_year
                if pdv['row_label']:
                    pdv['row_label'] = pdv['row_label'][years_to_chop:]
                pdv['value'] = pdv['value'][years_to_chop:]

    if metadata:
        return params
    else:
        return {key: val['value'] for key, val in params.items()}
