"""
Tax-Calculator federal tax policy Policy class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 policy.py
# pylint --disable=locally-disabled policy.py

import six
import numpy as np
from taxcalc.parameters import ParametersBase
from taxcalc.growfactors import Growfactors


class Policy(ParametersBase):

    """
    Policy is a subclass of the abstract ParametersBase class, and
    therefore, inherits its methods (none of which are shown here).

    Constructor for the federal tax policy class.

    Parameters
    ----------
    gfactors: Growfactors class instance
        containing price inflation rates and wage growth rates

    parameter_dict: dictionary of PARAM:DESCRIPTION pairs
        dictionary of policy parameters; if None, default policy
        parameters are read from the current_law_policy.json file.

    start_year: integer
        first calendar year for historical policy parameters.

    num_years: integer
        number of calendar years for which to specify policy parameter
        values beginning with start_year.

    Raises
    ------
    ValueError:
        if gfactors is not a Growfactors class instance.
        if parameter_dict is neither None nor a dictionary.
        if num_years is less than one.

    Returns
    -------
    class instance: Policy
    """

    DEFAULTS_FILENAME = 'current_law_policy.json'
    JSON_START_YEAR = 2013  # remains the same unless earlier data added
    LAST_KNOWN_YEAR = 2017  # last year for which indexed param vals are known
    LAST_BUDGET_YEAR = 2026  # increases by one every calendar year
    DEFAULT_NUM_YEARS = LAST_BUDGET_YEAR - JSON_START_YEAR + 1

    def __init__(self,
                 gfactors=Growfactors(),
                 parameter_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS):
        super(Policy, self).__init__()

        if not isinstance(gfactors, Growfactors):
            raise ValueError('gfactors is not a Growfactors instance')
        self._gfactors = gfactors

        if parameter_dict is None:  # read default parameters
            self._vals = self._params_dict_from_json_file()
        elif isinstance(parameter_dict, dict):
            self._vals = parameter_dict
        else:
            raise ValueError('parameter_dict is not None or a dictionary')

        if num_years < 1:
            raise ValueError('num_years cannot be less than one')

        syr = start_year
        lyr = start_year + num_years - 1
        self._inflation_rates = gfactors.price_inflation_rates(syr, lyr)
        self._wage_growth_rates = gfactors.wage_growth_rates(syr, lyr)

        self.initialize(start_year, num_years)

        self.reform_range_warnings = ''
        self.reform_range_errors = ''

    def inflation_rates(self):
        """
        Returns list of price inflation rates starting with JSON_START_YEAR.
        """
        return self._inflation_rates

    def wage_growth_rates(self):
        """
        Returns list of wage growth rates starting with JSON_START_YEAR.
        """
        return self._wage_growth_rates

    def implement_reform(self, reform):
        """
        Implement multi-year policy reform and leave current_year unchanged.

        Parameters
        ----------
        reform: dictionary of one or more YEAR:MODS pairs
            see Notes to Parameters _update method for info on MODS structure

        Raises
        ------
        ValueError:
            if reform is not a dictionary.
            if each YEAR in reform is not an integer.
            if minimum YEAR in the YEAR:MODS pairs is less than start_year.
            if minimum YEAR in the YEAR:MODS pairs is less than current_year.
            if maximum YEAR in the YEAR:MODS pairs is greater than end_year.

        Returns
        -------
        nothing: void

        Notes
        -----
        Given a reform dictionary, typical usage of the Policy class
        is as follows::

            policy = Policy()
            policy.implement_reform(reform)

        In the above statements, the Policy() call instantiates a
        policy object (policy) containing current-law policy parameters,
        and the implement_reform(reform) call applies the (possibly
        multi-year) reform specified in reform and then sets the
        current_year to the value of current_year when implement_reform
        was called with parameters set for that pre-call year.

        An example of a multi-year, multi-parameter reform is as follows::

            reform = {
                2016: {
                    '_EITC_c': [[900, 5000, 8000, 9000]],
                    '_II_em': [7000],
                    '_SS_Earnings_c': [300000]
                },
                2017: {
                    '_SS_Earnings_c': [500000], '_SS_Earnings_c_cpi': False
                },
                2019: {
                    '_EITC_c': [[1200, 7000, 10000, 12000]],
                    '_II_em': [9000],
                    '_SS_Earnings_c': [700000], '_SS_Earnings_c_cpi': True
                }
            }

        Notice that each of the four YEAR:MODS pairs is specified as
        required by the private _update method, whose documentation
        provides several MODS dictionary examples.

        IMPORTANT NOTICE: when specifying a reform dictionary always group
        all reform provisions for a specified year into one YEAR:MODS pair.
        If you make the mistake of specifying two or more YEAR:MODS pairs
        with the same YEAR value, all but the last one will be overwritten,
        and therefore, not part of the reform.  This is because Python
        expects unique (not multiple) dictionary keys.  There is no way to
        catch this error, so be careful to specify reform dictionaries
        correctly.
        """
        # check that all reform dictionary keys are integers
        if not isinstance(reform, dict):
            raise ValueError('reform is not a dictionary')
        if len(reform) == 0:
            return  # no reform to implement
        reform_years = sorted(list(reform.keys()))
        for year in reform_years:
            if not isinstance(year, int):
                msg = 'key={} in reform is not an integer calendar year'
                raise ValueError(msg.format(year))
        # check range of remaining reform_years
        first_reform_year = min(reform_years)
        if first_reform_year < self.start_year:
            msg = 'reform provision in year={} < start_year={}'
            raise ValueError(msg.format(first_reform_year, self.start_year))
        if first_reform_year < self.current_year:
            msg = 'reform provision in year={} < current_year={}'
            raise ValueError(msg.format(first_reform_year, self.current_year))
        last_reform_year = max(reform_years)
        if last_reform_year > self.end_year:
            msg = 'reform provision in year={} > end_year={}'
            raise ValueError(msg.format(last_reform_year, self.end_year))
        # implement the reform year by year
        precall_current_year = self.current_year
        for year in reform_years:
            self.set_year(year)
            self._update({year: reform[year]})
        self.set_year(precall_current_year)
        self._validate_parameter_values()

    def current_law_version(self):
        """
        Return Policy object same as self except with current-law policy.
        """
        startyear = self.start_year
        numyears = self.num_years
        clv = Policy(self._gfactors,
                     parameter_dict=None,
                     start_year=startyear,
                     num_years=numyears)
        clv.set_year(self.current_year)
        return clv

    JSON_REFORM_SUFFIXES = {
        # MARS-indexed suffixes and list index numbers
        'single': 0,
        'joint': 1,
        'separate': 2,
        'headhousehold': 3,
        'widow': 4,
        # EIC-indexed suffixes and list index numbers
        '0kids': 0,
        '1kid': 1,
        '2kids': 2,
        '3+kids': 3,
        # idedtype-indexed suffixes and list index numbers
        'medical': 0,
        'statelocal': 1,
        'realestate': 2,
        'casualty': 3,
        'misc': 4,
        'interest': 5,
        'charity': 6
    }

    @staticmethod
    def translate_json_reform_suffixes(indict):
        """
        Replace any array parameters with suffixes in the specified
        JSON-derived "policy" dictionary, indict, and
        return a JSON-equivalent dictionary containing constructed array
        parameters and containing no parameters with suffixes, odict.
        """

        # define no_suffix function used only in this method
        def no_suffix(idict):
            """
            Return param_base:year dictionary having only no-suffix parameters.
            """
            odict = dict()
            suffixes = Policy.JSON_REFORM_SUFFIXES.keys()
            for param in idict.keys():
                param_pieces = param.split('_')
                suffix = param_pieces[-1]
                if suffix not in suffixes:
                    odict[param] = idict[param]
            return odict

        # define group_dict function used only in this method
        def suffix_group_dict(idict):
            """
            Return param_base:year:suffix dictionary with each idict value.
            """
            gdict = dict()
            suffixes = Policy.JSON_REFORM_SUFFIXES.keys()
            for param in idict.keys():
                param_pieces = param.split('_')
                suffix = param_pieces[-1]
                if suffix in suffixes:
                    del param_pieces[-1]
                    param_base = '_'.join(param_pieces)
                    if param_base not in gdict:
                        gdict[param_base] = dict()
                    for year in sorted(idict[param].keys()):
                        if year not in gdict[param_base]:
                            gdict[param_base][year] = dict()
                        gdict[param_base][year][suffix] = idict[param][year][0]
            return gdict

        # define with_suffix function used only in this method
        def with_suffix(gdict):
            """
            Return param_base:year dictionary having only suffix parameters.
            """
            pol = Policy()
            odict = dict()
            for param in gdict.keys():
                odict[param] = dict()
                for year in sorted(gdict[param].keys()):
                    odict[param][year] = dict()
                    for suffix in gdict[param][year].keys():
                        plist = getattr(pol, param).tolist()
                        dvals = plist[int(year) - Policy.JSON_START_YEAR]
                        odict[param][year] = [dvals]
                        idx = Policy.JSON_REFORM_SUFFIXES[suffix]
                        odict[param][year][0][idx] = gdict[param][year][suffix]
                        udict = {int(year): {param: odict[param][year]}}
                        pol.implement_reform(udict)
            return odict

        # high-level logic of translate_json_reform_suffixes method:
        # - construct odict containing just parameters without a suffix
        odict = no_suffix(indict)
        # - group params with suffix into param_base:year:suffix dictionary
        gdict = suffix_group_dict(indict)
        # - add to odict the consolidated values for parameters with a suffix
        if len(gdict) > 0:
            odict.update(with_suffix(gdict))
        # - return policy dictionary containing constructed parameter arrays
        return odict

    # ----- begin private methods of Policy class -----

    def _validate_parameter_values(self):
        """
        Check policy parameter values using range information from
        the current_law_policy.json file.
        """
        # pylint: disable=too-many-branches
        clp = self.current_law_version()
        parameters = sorted(self._vals.keys())
        syr = Policy.JSON_START_YEAR
        for pname in parameters:
            pvalue = getattr(self, pname)
            for vop, vval in self._vals[pname]['range'].items():
                if isinstance(vval, six.string_types):
                    if vval == 'default':
                        vvalue = getattr(clp, pname)
                    else:
                        vvalue = getattr(self, vval)
                else:
                    vvalue = np.full(pvalue.shape, vval)
                assert pvalue.shape == vvalue.shape
                for idx in np.ndindex(pvalue.shape):
                    out_of_range = False
                    if vop == 'min' and pvalue[idx] < vvalue[idx]:
                        out_of_range = True
                        msg = '{} {} value {} < min value {}'
                        extra = self._vals[pname]['out_of_range_minmsg']
                        if len(extra) > 0:
                            msg += ' {}'.format(extra)
                    if vop == 'max' and pvalue[idx] > vvalue[idx]:
                        out_of_range = True
                        msg = '{} {} value {} > max value {}'
                        extra = self._vals[pname]['out_of_range_maxmsg']
                        if len(extra) > 0:
                            msg += ' {}'.format(extra)
                    if out_of_range:
                        action = self._vals[pname]['out_of_range_action']
                        if action == 'warn':
                            self.reform_range_warnings += (
                                'WARNING: ' + msg.format(idx[0] + syr, pname,
                                                         pvalue[idx],
                                                         vvalue[idx]) + '\n'
                            )
                        if action == 'stop':
                            self.reform_range_errors += (
                                'ERROR: ' + msg.format(idx[0] + syr, pname,
                                                       pvalue[idx],
                                                       vvalue[idx]) + '\n'
                            )
