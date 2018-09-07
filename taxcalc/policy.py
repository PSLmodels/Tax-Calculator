"""
Tax-Calculator federal tax policy Policy class.
"""
# CODING-STYLE CHECKS:
# pycodestyle policy.py
# pylint --disable=locally-disabled policy.py

import numpy as np
from taxcalc.parameters import ParametersBase
from taxcalc.growfactors import GrowFactors
from taxcalc.growdiff import GrowDiff


class Policy(ParametersBase):
    """
    Policy is a subclass of the abstract ParametersBase class, and
    therefore, inherits its methods (none of which are shown here).

    Constructor for the federal tax policy class.

    Parameters
    ----------
    gfactors: GrowFactors class instance
        containing price inflation rates and wage growth rates

    start_year: integer
        first calendar year for historical policy parameters.

    num_years: integer
        number of calendar years for which to specify policy parameter
        values beginning with start_year.

    Raises
    ------
    ValueError:
        if gfactors is not a GrowFactors class instance.
        if start_year is less than JSON_START_YEAR.
        if num_years is less than one.

    Returns
    -------
    class instance: Policy
    """

    DEFAULTS_FILENAME = 'current_law_policy.json'
    JSON_START_YEAR = 2013  # remains the same unless earlier data added
    LAST_KNOWN_YEAR = 2017  # last year for which indexed param vals are known
    LAST_BUDGET_YEAR = 2027  # increases by one every calendar year
    DEFAULT_NUM_YEARS = LAST_BUDGET_YEAR - JSON_START_YEAR + 1

    def __init__(self,
                 gfactors=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS):
        super(Policy, self).__init__()

        if gfactors is None:
            self._gfactors = GrowFactors()
        elif isinstance(gfactors, GrowFactors):
            self._gfactors = gfactors
        else:
            raise ValueError('gfactors is not None or a GrowFactors instance')

        # read default parameters
        self._vals = self._params_dict_from_json_file()

        if start_year < Policy.JSON_START_YEAR:
            raise ValueError('start_year cannot be less than JSON_START_YEAR')
        if num_years < 1:
            raise ValueError('num_years cannot be less than one')

        syr = start_year
        lyr = start_year + num_years - 1
        self._inflation_rates = self._gfactors.price_inflation_rates(syr, lyr)
        self._apply_clp_cpi_offset(self._vals['_cpi_offset'], num_years)
        self._wage_growth_rates = self._gfactors.wage_growth_rates(syr, lyr)

        self.initialize(start_year, num_years)

        self.parameter_warnings = ''
        self.parameter_errors = ''
        self._ignore_errors = False

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

    def implement_reform(self, reform,
                         print_warnings=False, raise_errors=True):
        """
        Implement multi-year policy reform and leave current_year unchanged.

        Parameters
        ----------
        reform: dictionary of one or more YEAR:MODS pairs
            see Notes to Parameters _update method for info on MODS structure

        print_warnings: boolean
            if True, prints warnings when parameter_warnings exists;
            if False, does not print warnings when parameter_warnings exists
                    and leaves warning handling to caller of implement_reform.

        raise_errors: boolean
            if True, raises ValueError when parameter_errors exists;
            if False, does not raise ValueError when parameter_errors exists
                    and leaves error handling to caller of implement_reform.

        Raises
        ------
        ValueError:
            if reform is not a dictionary.
            if each YEAR in reform is not an integer.
            if minimum YEAR in the YEAR:MODS pairs is less than start_year.
            if minimum YEAR in the YEAR:MODS pairs is less than current_year.
            if maximum YEAR in the YEAR:MODS pairs is greater than end_year.
            if raise_errors is True AND
              _validate_parameter_names_types generates errors OR
              _validate_parameter_values generates errors.

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
            raise ValueError('ERROR: YYYY PARAM reform is not a dictionary')
        if not reform:
            return  # no reform to implement
        reform_years = sorted(list(reform.keys()))
        for year in reform_years:
            if not isinstance(year, int):
                msg = 'ERROR: {} KEY {}'
                details = 'KEY in reform is not an integer calendar year'
                raise ValueError(msg.format(year, details))
        # check range of remaining reform_years
        first_reform_year = min(reform_years)
        if first_reform_year < self.start_year:
            msg = 'ERROR: {} YEAR reform provision in YEAR < start_year={}'
            raise ValueError(msg.format(first_reform_year, self.start_year))
        if first_reform_year < self.current_year:
            msg = 'ERROR: {} YEAR reform provision in YEAR < current_year={}'
            raise ValueError(msg.format(first_reform_year, self.current_year))
        last_reform_year = max(reform_years)
        if last_reform_year > self.end_year:
            msg = 'ERROR: {} YEAR reform provision in YEAR > end_year={}'
            raise ValueError(msg.format(last_reform_year, self.end_year))
        # validate reform parameter names and types
        self.parameter_warnings = ''
        self.parameter_errors = ''
        self._validate_parameter_names_types(reform)
        if not self._ignore_errors and self.parameter_errors:
            raise ValueError(self.parameter_errors)
        # optionally apply cpi_offset to inflation_rates and re-initialize
        if Policy._cpi_offset_in_reform(reform):
            known_years = self._apply_reform_cpi_offset(reform)
            self.set_default_vals(known_years=known_years)
        # implement the reform year by year
        precall_current_year = self.current_year
        reform_parameters = set()
        for year in reform_years:
            self.set_year(year)
            reform_parameters.update(reform[year].keys())
            self._update({year: reform[year]})
        self.set_year(precall_current_year)
        # validate reform parameter values
        self._validate_parameter_values(reform_parameters)
        if self.parameter_warnings and print_warnings:
            print(self.parameter_warnings)
        if self.parameter_errors and raise_errors:
            raise ValueError('\n' + self.parameter_errors)

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
    def translate_json_reform_suffixes(indict,
                                       growdiff_baseline_dict,
                                       growdiff_response_dict):
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
        def with_suffix(gdict, growdiff_baseline_dict, growdiff_response_dict):
            """
            Return param_base:year dictionary having only suffix parameters.
            """
            if bool(growdiff_baseline_dict) or bool(growdiff_response_dict):
                gdiff_baseline = GrowDiff()
                gdiff_baseline.update_growdiff(growdiff_baseline_dict)
                gdiff_response = GrowDiff()
                gdiff_response.update_growdiff(growdiff_response_dict)
                growfactors = GrowFactors()
                gdiff_baseline.apply_to(growfactors)
                gdiff_response.apply_to(growfactors)
            else:
                gdiff_baseline = None
                gdiff_response = None
                growfactors = None
            pol = Policy(gfactors=growfactors)
            pol.ignore_reform_errors()
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
                        pol.implement_reform(udict,
                                             print_warnings=False,
                                             raise_errors=False)
            del gdiff_baseline
            del gdiff_response
            del growfactors
            del pol
            return odict

        # high-level logic of translate_json_reform_suffixes method:
        # - construct odict containing just parameters without a suffix
        odict = no_suffix(indict)
        # - group params with suffix into param_base:year:suffix dictionary
        gdict = suffix_group_dict(indict)
        # - add to odict the consolidated values for parameters with a suffix
        if gdict:
            odict.update(with_suffix(gdict,
                                     growdiff_baseline_dict,
                                     growdiff_response_dict))
        # - return policy dictionary containing constructed parameter arrays
        return odict

    def ignore_reform_errors(self):
        """
        Sets self._ignore_errors to True.
        """
        self._ignore_errors = True

    # ----- begin private methods of Policy class -----

    def _apply_clp_cpi_offset(self, cpi_offset_clp_data, num_years):
        """
        Call this method from Policy constructor
        after self._inflation_rates has been set and
        before base class initialize method is called.
        (num_years is number of years for which inflation rates are specified)
        """
        ovalues = cpi_offset_clp_data['value']
        if len(ovalues) < num_years:  # extrapolate last known value
            ovalues = ovalues + ovalues[-1:] * (num_years - len(ovalues))
        for idx in range(0, num_years):
            infrate = round(self._inflation_rates[idx] + ovalues[idx], 6)
            self._inflation_rates[idx] = infrate

    @staticmethod
    def _cpi_offset_in_reform(reform):
        """
        Return true if cpi_offset is in reform; otherwise return false.
        """
        for year in reform:
            for name in reform[year]:
                if name == '_cpi_offset':
                    return True
        return False

    def _apply_reform_cpi_offset(self, reform):
        """
        Call this method ONLY if _cpi_offset_in_reform returns True.
        Apply CPI offset to inflation rates and
        revert indexed parameter values in preparation for re-indexing.
        Also, return known_years which is
        (first cpi_offset year - start year + 1).
        """
        # extrapolate cpi_offset reform
        self.set_year(self.start_year)
        first_cpi_offset_year = 0
        for year in sorted(reform.keys()):
            self.set_year(year)
            if '_cpi_offset' in reform[year]:
                if first_cpi_offset_year == 0:
                    first_cpi_offset_year = year
                oreform = {'_cpi_offset': reform[year]['_cpi_offset']}
                self._update({year: oreform})
        self.set_year(self.start_year)
        assert first_cpi_offset_year > 0
        # adjust inflation rates
        cpi_offset = getattr(self, '_cpi_offset')
        for idx in range(0, self.num_years):
            infrate = round(self._inflation_rates[idx] + cpi_offset[idx], 6)
            self._inflation_rates[idx] = infrate
        # revert CPI-indexed parameter values to current_law_policy.json values
        for name in self._vals.keys():
            if self._vals[name]['cpi_inflated']:
                setattr(self, name, self._vals[name]['value'])
        # return known_years
        return first_cpi_offset_year - self.start_year + 1

    def _validate_parameter_names_types(self, reform):
        """
        Check validity of parameter names and parameter types used
        in the specified reform dictionary.
        """
        # pylint: disable=too-many-branches,too-many-nested-blocks
        # pylint: disable=too-many-locals
        param_names = set(self._vals.keys())
        for year in sorted(reform.keys()):
            for name in reform[year]:
                if name.endswith('_cpi'):
                    if isinstance(reform[year][name], bool):
                        pname = name[:-4]  # root parameter name
                        if pname not in param_names:
                            msg = '{} {} unknown parameter name'
                            self.parameter_errors += (
                                'ERROR: ' + msg.format(year, name) + '\n'
                            )
                        else:
                            # check if root parameter is cpi inflatable
                            if not self._vals[pname]['cpi_inflatable']:
                                msg = '{} {} parameter is not cpi inflatable'
                                self.parameter_errors += (
                                    'ERROR: ' + msg.format(year, pname) + '\n'
                                )
                    else:
                        msg = '{} {} parameter is not true or false'
                        self.parameter_errors += (
                            'ERROR: ' + msg.format(year, name) + '\n'
                        )
                else:  # if name does not end with '_cpi'
                    if name not in param_names:
                        msg = '{} {} unknown parameter name'
                        self.parameter_errors += (
                            'ERROR: ' + msg.format(year, name) + '\n'
                        )
                    else:
                        # check parameter value type avoiding use of isinstance
                        # because isinstance(True, (int,float)) is True, which
                        # makes it impossible to check float parameters
                        bool_param_type = self._vals[name]['boolean_value']
                        int_param_type = self._vals[name]['integer_value']
                        assert isinstance(reform[year][name], list)
                        pvalue = reform[year][name][0]
                        if isinstance(pvalue, list):
                            scalar = False  # parameter value is a list
                        else:
                            scalar = True  # parameter value is a scalar
                            pvalue = [pvalue]  # make scalar a single-item list
                        # pylint: disable=consider-using-enumerate
                        for idx in range(0, len(pvalue)):
                            if scalar:
                                pname = name
                            else:
                                pname = '{}_{}'.format(name, idx)
                            pval = pvalue[idx]
                            # pylint: disable=unidiomatic-typecheck
                            pval_is_bool = type(pval) == bool
                            pval_is_int = type(pval) == int
                            pval_is_float = type(pval) == float
                            if bool_param_type:
                                if not pval_is_bool:
                                    msg = '{} {} value {} is not boolean'
                                    self.parameter_errors += (
                                        'ERROR: ' +
                                        msg.format(year, pname, pval) +
                                        '\n'
                                    )
                            elif int_param_type:
                                if not pval_is_int:
                                    msg = '{} {} value {} is not integer'
                                    self.parameter_errors += (
                                        'ERROR: ' +
                                        msg.format(year, pname, pval) +
                                        '\n'
                                    )
                            else:  # param is float type
                                if not (pval_is_int or pval_is_float):
                                    msg = '{} {} value {} is not a number'
                                    self.parameter_errors += (
                                        'ERROR: ' +
                                        msg.format(year, pname, pval) +
                                        '\n'
                                    )
        del param_names

    def _validate_parameter_values(self, parameters_set):
        """
        Check values of parameters in specified parameter_set using
        range information from the current_law_policy.json file.
        """
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-nested-blocks
        parameters = sorted(parameters_set)
        syr = Policy.JSON_START_YEAR
        for pname in parameters:
            if pname.endswith('_cpi'):
                continue  # *_cpi parameter values validated elsewhere
            pvalue = getattr(self, pname)
            for vop, vval in self._vals[pname]['range'].items():
                if isinstance(vval, str):
                    vvalue = getattr(self, vval)
                else:
                    vvalue = np.full(pvalue.shape, vval)
                assert pvalue.shape == vvalue.shape
                assert len(pvalue.shape) <= 2
                if len(pvalue.shape) == 2:
                    scalar = False  # parameter value is a list
                else:
                    scalar = True  # parameter value is a scalar
                for idx in np.ndindex(pvalue.shape):
                    out_of_range = False
                    if vop == 'min' and pvalue[idx] < vvalue[idx]:
                        out_of_range = True
                        msg = '{} {} value {} < min value {}'
                        extra = self._vals[pname]['out_of_range_minmsg']
                        if extra:
                            msg += ' {}'.format(extra)
                    if vop == 'max' and pvalue[idx] > vvalue[idx]:
                        out_of_range = True
                        msg = '{} {} value {} > max value {}'
                        extra = self._vals[pname]['out_of_range_maxmsg']
                        if extra:
                            msg += ' {}'.format(extra)
                    if out_of_range:
                        action = self._vals[pname]['out_of_range_action']
                        if scalar:
                            name = pname
                        else:
                            name = '{}_{}'.format(pname, idx[1])
                            if extra:
                                msg += '_{}'.format(idx[1])
                        if action == 'warn':
                            self.parameter_warnings += (
                                'WARNING: ' + msg.format(idx[0] + syr, name,
                                                         pvalue[idx],
                                                         vvalue[idx]) + '\n'
                            )
                        if action == 'stop':
                            self.parameter_errors += (
                                'ERROR: ' + msg.format(idx[0] + syr, name,
                                                       pvalue[idx],
                                                       vvalue[idx]) + '\n'
                            )
        del parameters
