import copy
import os
import re
from collections import defaultdict
from typing import Union, Mapping, Any, List

import marshmallow as ma
import paramtools as pt
import numpy as np
import requests

import taxcalc
from taxcalc.growfactors import GrowFactors


class CompatibleDataSchema(ma.Schema):
    """
    Schema for Compatible data object

    .. code-block :: json

        {
            "compatible_data": {"puf": true, "cps": false}
        }

    """

    puf = ma.fields.Boolean()
    cps = ma.fields.Boolean()


pt.register_custom_type(
    "compatible_data",
    ma.fields.Nested(CompatibleDataSchema())
)


class Parameters(pt.Parameters):
    """
    Base class that wraps ParamTools, providing parameter indexing
    for tax policy in the ``adjust`` method and convenience methods
    like ``set_year`` for classes inheriting from it. It also provides
    a backwards-compatible layer for Tax-Calculator versions prior to 3.0.

    The defaults file path may be set through the defaults class attribute
    variable or through the ``DEFAULTS_FILE_NAME`` /
    ``DEFAULTS_FILE_PATH work`` flow.

    A custom getter method is implemented so that the value of a parameter
    over all allowed years can conveniently be retrieved by adding an
    underscore before the variable name (e.g. ``EITC_c`` vs ``_EITC_c``).

    This class inherits methods from ParamTools like ``items``:

        .. code-block :: python

            import taxcalc as tc
            pol = tc.Policy()

            for name, value in pol.items():
                print(name, value)

            # parameter_indexing_CPI_offset [0.]
            # FICA_ss_trt [0.124]
            # SS_Earnings_c [113700.]

    Check out the ParamTools
    `documentation <https://paramtools.dev/api/reference.html>`_
    for more information on these inherited methods.

    """
    defaults = None
    array_first = True
    label_to_extend = "year"
    uses_extend_func = True

    REMOVED_PARAMS = None
    REDEFINED_PARAMS = None
    WAGE_INDEXED_PARAMS = ()

    # Legacy class attrs
    DEFAULTS_FILE_NAME = None
    DEFAULTS_FILE_PATH = None
    JSON_START_YEAR = None
    LAST_KNOWN_YEAR = None

    def __init__(self, start_year=None, num_years=None, last_known_year=None,
                 removed=None, redefined=None, wage_indexed=None, **kwargs):
        # In case we need to wait for this to be called from the
        # initialize method for legacy reasons.
        if not start_year or not num_years:
            return
        self._wage_growth_rates = None
        self._inflation_rates = None
        if (
            self.defaults is None and
            self.DEFAULTS_FILE_PATH is not None and
            self.DEFAULTS_FILE_NAME
        ):
            self.defaults = os.path.join(
                self.DEFAULTS_FILE_PATH,
                self.DEFAULTS_FILE_NAME
            )

        if last_known_year is None:
            self._last_known_year = start_year
        else:
            assert last_known_year >= start_year
            assert last_known_year <= self.LAST_BUDGET_YEAR
            self._last_known_year = last_known_year

        self._removed_params = removed or self.REMOVED_PARAMS
        self._redefined_params = redefined or self.REDEFINED_PARAMS

        self._wage_indexed = wage_indexed or self.WAGE_INDEXED_PARAMS

        if (
            (start_year or self.JSON_START_YEAR) and
            "initial_state" not in kwargs
        ):
            kwargs["initial_state"] = {
                "year": start_year or self.JSON_START_YEAR
            }
        super().__init__(**kwargs)

    def adjust(
        self, params_or_path, print_warnings=True, raise_errors=True, **kwargs
    ):
        """
        Update parameter values using a ParamTools styled adjustment.

        Parameters
        ----------
        params_or_path : Dict, str
            New parameter values in the paramtools format. For example:

            .. code-block:: json

                {
                    "standard_deduction": [
                        {"year": 2024, "marital_status": "single", "value": 10000.0},
                        {"year": 2024, "marital_status": "joint", "value": 10000.0}
                    ],
                    "ss_rate": [{"year": 2024, "value": 0.2}]}
                }

        print_warnings : Boolean
            Print parameter warnings or not
        raise_errors: Boolean
            Raise errors as a ValidationError. If False, they will be stored
            in the errors attribute.


        Returns
        -------
        adjustment : Dict
            Parsed paremeter dictionary

        """  # noqa
        if print_warnings:
            _data = copy.deepcopy(self._data)
            kwargs["ignore_warnings"] = False
        else:
            kwargs["ignore_warnings"] = True
        self._warnings = {}
        self._errors = {}
        try:
            # Wrap all updates in adjust_with_indexing in a transaction and
            # defer related-parameter validation until all intermediate updates
            # are complete.
            with self.transaction(
                defer_validation=True,
                raise_errors=True,
                ignore_warnings=kwargs["ignore_warnings"],
            ):
                return self.adjust_with_indexing(
                    params_or_path, raise_errors=True, **kwargs
                )
        except pt.ValidationError as ve:
            if self.errors and raise_errors:
                raise ve
            elif self.errors and not raise_errors:
                return {}
            if print_warnings:
                print("WARNING:")
                print(self.warnings)
            kwargs["ignore_warnings"] = True
            self._data = _data
            _warnings = copy.deepcopy(self._warnings)
            self._warnings = {}
            self._errors = {}
            adjustment = self.adjust_with_indexing(
                params_or_path, raise_errors=True, **kwargs
            )
            self._warnings = _warnings
            return adjustment

    def adjust_with_indexing(self, params_or_path, **kwargs):
        """
        Adjust parameter values with the following indexing logic:

        1. If "parameter_indexing_CPI_offset" is adjusted, first set
           parameter_indexing_CPI_offset to zero before implementing the
           adjusted parameter_indexing_CPI_offset to avoid stacking
           adjustments. Then, revert all values of indexed parameters to
           the 'known' values:

            a. The current values of parameters that are being adjusted are
               deleted after the first year in which
               parameter_indexing_CPI_offset is adjusted.
            b. The current values of parameters that are not being adjusted
               (i.e. are not in params) are deleted after the last known year,
               with the exception of parameters that revert to their pre-TCJA
               values in 2026. Instead, these (2026) parameter values are
               recalculated using the new inflation rates.

            After the 'unknown' values have been deleted, the last known value
            is extrapolated through the budget window. If there are indexed
            parameters in the adjustment, they will be included in the final
            adjustment call (unless their indexed status is changed).

        2. If the "indexed" status is updated for any parameter:

            a. If a parameter has values that are being adjusted before
               the indexed status is adjusted, update those parameters first.
            b. Extend the values of that parameter to the year in which
               the status is changed.
            c. Change the indexed status for the parameter.
            d. Update parameter values in adjustment that are adjusted after
               the year in which the indexed status changes.
            e. Using the new "-indexed" status, extend the values of that
               parameter through the remaining years or until the -indexed
               status changes again.

        3. Update all parameters that are not indexing related, i.e. they are
           not "parameter_indexing_CPI_offset" or do not end with "-indexed".

        4. Return parsed adjustment with all adjustments, including "-indexed"
           parameters.

        Notable side-effects:

        - All values of a parameter whose indexed status is adjusted are
          wiped out after the year in which the value is adjusted for the
          same hard-coding reason.
        """
        # Temporarily turn off extra ops during the intermediary adjustments
        # so that expensive and unnecessary operations are not run.
        label_to_extend = self.label_to_extend
        array_first = self.array_first
        self.array_first = False
        self._gfactors = GrowFactors()

        params = self.read_params(params_or_path)

        # Check if parameter_indexing_CPI_offset is adjusted. If so, reset
        # values of all indexed parameters after year where
        # parameter_indexing_CPI_offset is changed. If
        # parameter_indexing_CPI_offset is changed multiple times, then
        # reset values after the first year in which the
        # parameter_indexing_CPI_offset is changed.
        needs_reset = []
        if params.get("parameter_indexing_CPI_offset") is not None:
            # Update parameter_indexing_CPI_offset with new value.
            cpi_adj = super().adjust(
                {"parameter_indexing_CPI_offset":
                 params["parameter_indexing_CPI_offset"]}, **kwargs
            )
            # turn off extend now that parameter_indexing_CPI_offset
            # has been updated.
            self.label_to_extend = None
            # Get first year in which parameter_indexing_CPI_offset
            # is changed.
            cpi_min_year = min(
                cpi_adj["parameter_indexing_CPI_offset"],
                key=lambda vo: vo["year"]
            )

            rate_adjustment_vals = (
                self.sel["parameter_indexing_CPI_offset"]["year"]
                >= cpi_min_year["year"]
            )
            # "Undo" any existing parameter_indexing_CPI_offset for
            # years after parameter_indexing_CPI_offset has
            # been updated.
            self._inflation_rates = self._inflation_rates[
                :cpi_min_year["year"] - self.start_year
            ] + self._gfactors.price_inflation_rates(
                cpi_min_year["year"], self.LAST_BUDGET_YEAR)

            # Then apply new parameter_indexing_CPI_offset values to
            # inflation rates
            for cpi_vo in rate_adjustment_vals:
                self._inflation_rates[
                    cpi_vo["year"] - self.start_year
                ] += cpi_vo["value"]
            # 1. Delete all unknown values.
            # 1.a For revision, these are years specified after cpi_min_year.
            to_delete = {}
            for param in params:
                if (
                    param == "parameter_indexing_CPI_offset" or
                    param in self._wage_indexed
                ):
                    continue
                if param.endswith("-indexed"):
                    param = param.split("-indexed")[0]
                if self._data[param].get("indexed", False):
                    to_delete[param] = (
                        self.sel[param]["year"] > cpi_min_year["year"]
                    )
                    needs_reset.append(param)
            self.delete(to_delete, **kwargs)

            # 1.b For all others, these are years after last_known_year.
            last_known_year = max(cpi_min_year["year"], self._last_known_year)
            # calculate 2026 value, using new inflation rates, for parameters
            # that revert to their pre-TCJA values.
            long_params = ['II_brk7', 'II_brk6', 'II_brk5', 'II_brk4',
                           'II_brk3', 'II_brk2', 'II_brk1',
                           'PT_brk7', 'PT_brk6', 'PT_brk5', 'PT_brk4',
                           'PT_brk3', 'PT_brk2', 'PT_brk1',
                           'PT_qbid_taxinc_thd',
                           'ALD_BusinessLosses_c',
                           'STD', 'II_em', 'II_em_ps',
                           'AMT_em', 'AMT_em_ps', 'AMT_em_pe',
                           'ID_ps', 'ID_AllTaxes_c']
            final_ifactor = 1.0
            pyear = 2017  # prior year before TCJA first implemented
            fyear = 2026  # final year in which parameter values revert to
            # pre-TCJA values
            # construct final-year inflation factor from prior year
            # NOTE: pvalue[t+1] = pvalue[t] * ( 1 + irate[t] )
            for year in range(pyear, fyear):
                final_ifactor *= 1 + \
                    self._inflation_rates[year - self.start_year]

            long_param_vals = defaultdict(list)
            # compute final year parameter value
            for param in long_params:
                # only revert param in 2026 if it's not in revision
                if params.get(param) is None:
                    # grab param values from 2017
                    vos = self.sel[param]["year"] == pyear
                    # use final_ifactor to inflate from 2017 to 2026
                    for vo in vos:
                        long_param_vals[param].append(
                            # Create new dict to avoid modifying the original
                            dict(
                                vo,
                                value=min(9e99, round(
                                    vo["value"] * final_ifactor, 0)),
                                year=fyear,
                            )
                        )
                    needs_reset.append(param)
            super().adjust(long_param_vals, **kwargs)

            to_delete = {}
            for param in self._data:
                if (
                    param in params or
                    param == "parameter_indexing_CPI_offset" or
                    param in self._wage_indexed
                ):
                    continue
                if self._data[param].get("indexed", False):
                    to_delete[param] = self.sel[param]["_auto"] == True  # noqa
                    needs_reset.append(param)

            self.delete(to_delete, **kwargs)

            self.extend(label="year")

        # 2. Handle -indexed parameters.
        self.label_to_extend = None
        index_affected = set([])
        for param, values in params.items():
            if param.endswith("-indexed"):
                base_param = param.split("-indexed")[0]
                if not self._data[base_param].get("indexable", None):
                    msg = f"Parameter {base_param} is not indexable."
                    raise pt.ValidationError(
                        {"errors": {base_param: msg}}, labels=None
                    )
                index_affected |= {param, base_param}
                indexed_changes = {}
                if isinstance(values, bool):
                    indexed_changes[self.start_year] = values
                elif isinstance(values, list):
                    for vo in values:
                        indexed_changes[vo.get("year", self.start_year)] = vo[
                            "value"
                        ]
                else:
                    msg = (
                        "Index adjustment parameter must be a boolean or "
                        "list."
                    )
                    raise pt.ValidationError(
                        {"errors": {base_param: msg}}, labels=None
                    )
                # 2.a Adjust values less than first year in which index status
                # was changed.
                if base_param in params:
                    min_index_change_year = min(indexed_changes.keys())
                    vos = self.sel[params[base_param]]["year"].lt(
                        min_index_change_year, strict=False
                    )

                    if len(list(vos)):
                        min_adj_year = min(vos, key=lambda vo: vo["year"])[
                            "year"
                        ]
                        self.delete(
                            {
                                base_param: self.sel[base_param]["year"] > min_adj_year  # noqa
                            }
                        )
                        super().adjust({base_param: vos}, **kwargs)
                        self.extend(
                            params=[base_param],
                            label="year",
                            label_values=list(
                                range(self.start_year, min_index_change_year)
                            ),
                        )

                for year in sorted(indexed_changes):
                    indexed_val = indexed_changes[year]
                    # Get and delete all default values after year where
                    # indexed status changed.
                    self.delete(
                        {base_param: self.sel[base_param]["year"] > year}
                    )

                    # 2.b Extend values for this parameter to the year where
                    # the indexed status changes.
                    if year > self.start_year:
                        self.extend(
                            params=[base_param],
                            label="year",
                            label_values=list(
                                range(self.start_year, year + 1)
                            ),
                        )

                    # 2.c Set indexed status.
                    self._data[base_param]["indexed"] = indexed_val

                    # 2.d Adjust with values greater than or equal to current
                    # year in params
                    if base_param in params:
                        vos = self.sel[params[base_param]]["year"].gte(
                            year, strict=False
                        )
                        super().adjust({base_param: vos}, **kwargs)

                    # 2.e Extend values through remaining years.
                    self.extend(params=[base_param], label="year")

                needs_reset.append(base_param)
        # Re-instate ops.
        self.label_to_extend = label_to_extend
        self.array_first = array_first
        self.set_state()

        # Filter out "-indexed" params.
        nonindexed_params = {
            param: val
            for param, val in params.items()
            if param not in index_affected
        }

        # 3. Do adjustment for all non-indexing related parameters.
        adj = super().adjust(nonindexed_params, **kwargs)

        # 4. Add indexing params back for return to user.
        adj.update(
            {
                param: val
                for param, val in params.items()
                if param in index_affected
            }
        )
        return adj

    def get_index_rate(self, param, label_to_extend_val):
        """
        Initalize indexing data and return the indexing rate value
        depending on the parameter name and label_to_extend_val, the value of
        label_to_extend.
        Returns: rate to use for indexing.
        """
        if not self._inflation_rates or not self._wage_growth_rates:
            self.set_rates()
        if param in self._wage_indexed:
            return self.wage_growth_rates(year=label_to_extend_val)
        else:
            return self.inflation_rates(year=label_to_extend_val)

    def set_rates(self):
        """
        This method is implemented by classes inheriting
        Parameters.
        """
        raise NotImplementedError()

    def wage_growth_rates(self, year=None):
        if year is not None:
            return self._wage_growth_rates[year - self.start_year]
        return self._wage_growth_rates or []

    def inflation_rates(self, year=None):
        if year is not None:
            return self._inflation_rates[year - self.start_year]
        return self._inflation_rates or []

    # alias methods below
    def initialize(self, start_year, num_years, last_known_year=None,
                   removed=None, redefined=None, wage_indexed=None,
                   **kwargs):
        """
        Legacy method for initializing a Parameters instance. Projects
        should use the __init__ method in the future.
        """
        # case where project hasn't been initialized yet.
        if getattr(self, "_data", None) is None:
            return Parameters.__init__(
                self, start_year, num_years, last_known_year=last_known_year,
                removed=removed, redefined=redefined,
                wage_indexed=wage_indexed, **kwargs
            )

    def _update(self, revision, print_warnings, raise_errors):
        """
        A translation layer on top of ``adjust``. Projects
        that have historically used the ``_update`` method with
        Tax-Calculator styled adjustments can continue to do so
        without making any changes to how they handle adjustments.

        Converts reforms that are compatible with Tax-Calculator:

        .. code-block:: python

            adjustment = {
                "standard_deduction": {2024: [10000.0, 10000.0]},
                "ss_rate": {2024: 0.2}
            }

        into reforms that are compatible with ParamTools:

        .. code-block:: python

            {
                "standard_deduction": [
                    {"year": 2024, "marital_status": "single", "value": 10000.0},
                    {"year": 2024, "marital_status": "joint", "value": 10000.0}
                ],
                "ss_rate": [{"year": 2024, "value": 0.2}]}
            }

        """  # noqa: E501
        if not isinstance(revision, dict):
            raise pt.ValidationError(
                {"errors": {"schema": "Revision must be a dictionary."}},
                None
            )
        new_params = defaultdict(list)
        for param, val in revision.items():
            if not isinstance(param, str):
                msg = f"Parameter {param} is not a string."
                raise pt.ValidationError(
                    {"errors": {"schema": msg}},
                    None
                )
            if (
                param not in self._data and
                param.split("-indexed")[0] not in self._data
            ):
                if self._removed_params and param in self._removed_params:
                    msg = f"{param} {self._removed_params[param]}"
                elif (
                    self._redefined_params and param in self._redefined_params
                ):
                    msg = self._redefined_params[param]
                else:
                    msg = f"Parameter {param} does not exist."
                raise pt.ValidationError(
                    {"errors": {"schema": msg}},
                    None
                )
            if param.endswith("-indexed"):
                for year, yearval in val.items():
                    new_params[param] += [{"year": year, "value": yearval}]
            elif isinstance(val, dict):
                for year, yearval in val.items():
                    val = getattr(self, param)
                    if (
                        self._data[param].get("type", None) == "str" and
                        isinstance(yearval, str)
                    ):
                        new_params[param] += [{"value": yearval}]
                        continue

                    yearval = np.array(yearval)
                    if (
                        getattr(val, "shape", None) and
                        yearval.shape != val[0].shape
                    ):
                        exp_dims = val[0].shape
                        if exp_dims == tuple():
                            msg = (
                                f"{param} is not an array "
                                f"parameter."
                            )
                        elif yearval.shape:
                            msg = (
                                f"{param} has {yearval.shape[0]} elements "
                                f"but should only have {exp_dims[0]} "
                                f"elements."
                            )
                        else:
                            msg = (
                                f"{param} is an array parameter with "
                                f"{exp_dims[0]} elements."
                            )
                        raise pt.ValidationError(
                            {"errors": {"schema": msg}},
                            None
                        )

                    value_objects = self.from_array(
                        param,
                        yearval.reshape((1, *yearval.shape)),
                        year=year
                    )
                    new_params[param] += value_objects
            else:
                msg = (
                    f"{param} must be a year:value dictionary "
                    f"if you are not using the new adjust method."
                )
                raise pt.ValidationError(
                    {"errors": {"schema": msg}},
                    None
                )
        return self.adjust(
            new_params,
            print_warnings=print_warnings,
            raise_errors=raise_errors
        )

    def set_year(self, year):
        self.set_state(year=year)

    @property
    def current_year(self):
        return self.label_grid["year"][0]

    @property
    def start_year(self):
        return self._stateless_label_grid["year"][0]

    @property
    def end_year(self):
        return self._stateless_label_grid["year"][-1]

    @property
    def num_years(self):
        return self.end_year - self.start_year + 1

    @property
    def parameter_warnings(self):
        return self.errors or {}

    @property
    def parameter_errors(self):
        return self.errors or {}

    @staticmethod
    def _read_json_revision(obj, topkey):
        """
        Read JSON revision specified by ``obj`` and ``topkey``
        returning a single revision dictionary suitable for
        use with the ``Parameters._update`` or ``Parameters.adjust`` methods.
        The obj function argument can be ``None`` or a string, where the
        string can be:

          - Path for a local file
          - Link pointing to a valid JSON file
          - Valid JSON text

        The ``topkey`` argument must be a string containing the top-level
        key in a compound-revision JSON text for which a revision
        dictionary is returned.  If the specified ``topkey`` is not among
        the top-level JSON keys, the ``obj`` is assumed to be a
        non-compound-revision JSON text for the specified ``topkey``.

        Some examples of valid links are:

        - HTTP: ``https://raw.githubusercontent.com/PSLmodels/Tax-Calculator/master/taxcalc/reforms/2017_law.json``

        - Github API: ``github://PSLmodels:Tax-Calculator@master/taxcalc/reforms/2017_law.json``

        Checkout the ParamTools
        `docs <https://paramtools.dev/_modules/paramtools/parameters.html#Parameters.read_params>`_
        for more information on valid file URLs.
        """  # noqa
        # embedded function used only in _read_json_revision staticmethod
        def convert_year_to_int(syr_dict):
            """
            Converts specified syr_dict, which has string years as secondary
            keys, into a dictionary with the same structure but having integer
            years as secondary keys.
            """
            iyr_dict = dict()
            for pkey, sdict in syr_dict.items():
                assert isinstance(pkey, str)
                iyr_dict[pkey] = dict()
                assert isinstance(sdict, dict)
                for skey, val in sdict.items():
                    assert isinstance(skey, str)
                    year = int(skey)
                    iyr_dict[pkey][year] = val
            return iyr_dict
        # end of embedded function
        # process the main function arguments
        if obj is None:
            return dict()

        full_dict = pt.read_json(obj)

        # check top-level key contents of dictionary
        if topkey in full_dict.keys():
            single_dict = full_dict[topkey]
        else:
            single_dict = full_dict

        if is_paramtools_format(single_dict):
            return single_dict

        # convert string year to integer year in dictionary and return
        return convert_year_to_int(single_dict)

    def metadata(self):
        return self.specification(meta_data=True, use_state=False)

    @staticmethod
    def years_in_revision(revision):
        """
        Return list of years in specified revision dictionary, which is
        assumed to have a param:year:value format.
        """
        assert isinstance(revision, dict)
        years = list()
        for _, paramdata in revision.items():
            assert isinstance(paramdata, dict)
            for year, _ in paramdata.items():
                assert isinstance(year, int)
                if year not in years:
                    years.append(year)
        return years

    def __getattr__(self, attr):
        """
        Get the value of a parameter over all years by accessing it
        with an underscore in front of its name: ``pol._EITC_c`` instead of
        ``pol.EITC_c``.
        """
        if (
            attr.startswith("_") and
            attr[1:] in super().__getattribute__("_data")
        ):
            return self.to_array(
                attr[1:], year=list(range(self.start_year, self.end_year + 1))
            )
        else:
            raise AttributeError(f"{attr} not definied.")


TaxcalcReform = Union[str, Mapping[int, Any]]
ParamToolsAdjustment = Union[str, List[pt.ValueObject]]


def is_paramtools_format(params: Union[TaxcalcReform, ParamToolsAdjustment]):
    """
    Check first item in ``params`` to determine if it is using the ParamTools
    adjustment or the Tax-Calculator reform format.
    If first item is a ``dict``, then it is likely be a Tax-Calculator reform.
    Otherwise, it is likely to be a ParamTools format.

    Parameters
    ----------
    params: dict
        Either a ParamTools or Tax-Calculator styled parameters ``dict``.

        .. code-block:: python

            # ParamTools style format:
            {
                "ss_rate": {2024: 0.2}
            }

            # Tax-Calculator style format:
            {
                "ss_rate": [{"year": 2024, "value": 0.2}]}
            }

    Returns
    -------
    bool:
        Whether ``params`` is likely to be a ParamTools formatted adjustment or
        not.
    """
    for data in params.values():
        if isinstance(data, dict):
            return False  # taxcalc reform
        else:
            # Not doing a specific check to see if the value is a list
            # since it could be a list or just a scalar value.
            return True
