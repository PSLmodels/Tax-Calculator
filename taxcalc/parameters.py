import copy
import os
import re
from collections import defaultdict

import marshmallow as ma
import paramtools
import numpy as np
import requests

import taxcalc
from taxcalc.utils import json_to_dict


def lt_func(x, y) -> bool:
    return all(x < item for item in y)


def select_lt(value_objects, exact_match, labels, tree=None):
    return paramtools.select(value_objects, exact_match, lt_func, labels, tree)


class CompatibleDataSchema(ma.Schema):
    """
    Schema for Compatible data object
    {
        "compatible_data": {"data1": bool, "data2": bool, ...}
    }
    """

    puf = ma.fields.Boolean()
    cps = ma.fields.Boolean()


class Parameters(paramtools.Parameters):
    """
    Base Parameters class that wraps ParamTools,
    providing parameter indexing for tax policy in the
    adjust method and backwards-compatible preserving
    layer that supports Tax-Calculator's conventional
    reform formatting style as well as convenience
    methods like set_Year for classes operating on
    this one.

    The defaults file path may be set through the
    defaults class attribute variable or through
    the old DEFAULTS_FILE_NAME/DEFAULTS_FILE_PATH
    work flow.

    A custom getter method is implemented so that
    the value of a parameter over all allowed years
    can conveniently be retrieved by adding an
    underscore before the variable name (e.g.
    EITC_c vs _EITC_c).

    Note: Like all paramtools.Parameters classes
    the values of attributes corresponding to a
    parameter value on this class are ephemeral
    and the only way to make permanent changes
    to this class'sstate is through the set_state
    or adjust methods.

    """
    field_map = {"compatible_data": ma.fields.Nested(CompatibleDataSchema())}

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

    def __init__(self, *args, **kwargs):
        pass

    def adjust(self, params_or_path, **kwargs):
        """
        Custom adjust method that handles special indexing logic. The logic
        is:

        1. If "CPI_offset" is adjusted, revert all values of indexed parameters
            to the 'known' values:
            a. The current values of parameters that are being adjusted are
                deleted after the first year in which CPI_offset is adjusted.
            b. The current values of parameters that are not being adjusted
                (i.e. are not in params) are deleted after the last known year.
            After the 'unknown' values have been deleted, the last known value
            is extrapolated through the budget window. If there are indexed
            parameters in the adjustment, they will be included in the final
            adjustment call (unless their indexed status is changed).
        2. If the "indexed" status is updated for any parameter:
            a. if a parameter has values that are being adjusted before
                the indexed status is adjusted, update those parameters fist.
            b. extend the values of that parameter to the year in which
                the status is changed.
            c. change the the indexed status for the parameter.
            d. update parameter values in adjustment that are adjusted after
                the year in which the indexed status changes.
            e. using the new "-indexed" status, extend the values of that
                parameter through the remaining years or until the -indexed
                status changes again.
        3. Update all parameters that are not indexing related, i.e. they are
            not "CPI_offset" or do not end with "-indexed".
        4. Return parsed adjustment with all adjustments, including "-indexed"
            parameters.

        Notable side-effects:
            - All values of indexed parameters, including default values, are
                wiped out after the first year in which the "CPI_offset" is
                changed. This is only necessary because Tax-Calculator
                hard-codes inflated values. If Tax-Calculator only hard-coded
                values that were changed for non-inflation related reasons,
                then this would not be necessary for default values.
            - All values of a parameter whose indexed status is adjusted are
              wiped out after the year in which the value is adjusted for the
              same hard-coding reason.
        """
        min_year = min(self._stateless_label_grid["year"])

        # turn off extra ops during the intermediary adjustments so that
        # expensive and unnecessary operations are not changed.
        label_to_extend = self.label_to_extend
        array_first = self.array_first
        self.array_first = False

        params = self.read_params(params_or_path)

        # Check if CPI_offset is adjusted. If so, reset values of all indexed
        # parameters after year where CPI_offset is changed. If CPI_offset is
        # changed multiple times, then the reset year is the year in which the
        # CPI_offset is first changed.
        needs_reset = []
        if params.get("CPI_offset") is not None:
            # get first year CPI_offset is adjusted
            cpi_adj = super().adjust(
                {
                    "CPI_offset": params["CPI_offset"]
                },
                **kwargs
            )
            # turn off extend now that CPI_offset has been updated.
            self.label_to_extend = None
            cpi_min_year = min(
                cpi_adj["CPI_offset"],
                key=lambda vo: vo["year"]
            )
            # apply new CPI_offset values to inflation rates
            rate_adjustment_vals = filter(
                lambda vo: vo["year"] >= cpi_min_year["year"],
                self._data["CPI_offset"]["value"]
            )
            for cpi_vo in rate_adjustment_vals:
                self._inflation_rates[cpi_vo["year"] - self.start_year] += \
                    cpi_vo["value"]
            # 1. delete all unknown values.
            # 1.a for revision these are years specified after cpi_min_year
            to_delete = {}
            to_adjust = {}
            for param in params:
                if param == "CPI_offset" or param in self._wage_indexed:
                    continue
                if param.endswith("-indexed"):
                    param = param.split("-indexed")[0]
                # TODO: disting. btw wage and price?
                if self._data[param].get("indexed", False):
                    gt = self.select_gt(param, True, year=cpi_min_year["year"])
                    to_delete[param] = list(
                        [dict(vo, **{"value": None}) for vo in gt]
                    )
                    to_adjust[param] = select_lt(
                        self._init_values[param],
                        True,
                        {"year": cpi_min_year["year"] + 1},
                    )
                    needs_reset.append(param)
            super().adjust(to_delete, **kwargs)
            super().adjust(to_adjust, **kwargs)

            # 1.b for all others these are years after last_known_year
            to_delete = {}
            to_adjust = {}
            last_known_year = max(cpi_min_year["year"], self._last_known_year)
            for param in self._data:
                if (
                    param in params or
                    param == "CPI_offset" or
                    param in self.WAGE_INDEXED_PARAMS
                ):
                    continue
                if self._data[param].get("indexed", False):  # TODO: see above
                    gt = self.select_gt(param, True, year=last_known_year)
                    to_delete[param] = list(
                        [dict(vo, **{"value": None}) for vo in gt]
                    )
                    to_adjust[param] = select_lt(
                        self._init_values[param],
                        True,
                        {"year": last_known_year + 1}
                    )
                    needs_reset.append(param)

            super().adjust(to_delete, **kwargs)
            super().adjust(to_adjust, **kwargs)

            self.extend(label_to_extend="year")

        # 2. handle -indexed parameters
        self.label_to_extend = None
        index_affected = set([])
        for param, values in params.items():
            if param.endswith("-indexed"):
                base_param = param.split("-indexed")[0]
                if not self._data[base_param].get("indexable", None):
                    msg = f"Parameter {base_param} is not indexable."
                    raise paramtools.ValidationError(
                        {"errors": {base_param: msg}},
                        labels=None
                    )
                index_affected = index_affected | {param, base_param}
                to_index = {}
                if isinstance(values, bool):
                    to_index[min_year] = values
                elif isinstance(values, list):
                    for vo in values:
                        to_index[vo.get("year", min_year)] = vo["value"]
                else:
                    raise Exception(
                        "Index adjustment parameter must be a boolean or list."
                    )
                # 2.a adjust values less than first year in which index status
                # was changed
                if base_param in params:
                    min_index_change_year = min(to_index.keys())
                    vos = select_lt(
                        params[base_param],
                        False,
                        {"year": min_index_change_year}
                    )
                    if vos:
                        min_adj_year = min(
                            vos,
                            key=lambda vo: vo["year"]
                        )["year"]
                        gt = self.select_gt(
                            base_param,
                            True,
                            year=min_adj_year
                        )
                        super().adjust(
                            {
                                base_param: list(
                                    [
                                        dict(vo, **{"value": None})
                                        for vo in gt
                                    ]
                                )
                            }
                        )
                        super().adjust({base_param: vos}, **kwargs)
                        self.extend(
                            params=[base_param],
                            label_to_extend="year",
                            label_to_extend_values=list(
                                range(min_year, min_index_change_year)
                            ),
                        )

                for year in sorted(to_index):
                    indexed_val = to_index[year]
                    # get and delete all default values after year where
                    # indexed status changed.
                    gte = self.select_gt(base_param, True, year=year)
                    super().adjust(
                        {
                            base_param: list(
                                [
                                    dict(vo, **{"value": None})
                                    for vo in gte
                                ]
                            )
                        }
                    )

                    # 2.b extend values for this parameter to the year where
                    # the indexed status changes.
                    if year > min_year:
                        self.extend(
                            params=[base_param],
                            label_to_extend="year",
                            label_to_extend_values=list(
                                range(min_year, year + 1)
                            ),
                        )

                    # 2.c set indexed status.
                    self._data[base_param]["indexed"] = indexed_val

                    # 2.d adjust with values greater than or equal to current
                    # year in params
                    if base_param in params:
                        vos = paramtools.select_gt(
                            params[base_param], False, {"year": year - 1}
                        )
                        super().adjust({base_param: vos}, **kwargs)

                    # 2.e extend values throuh remaining years.
                    self.extend(params=[base_param], label_to_extend="year")

                needs_reset.append(base_param)
        # re-instate actions.
        self.label_to_extend = label_to_extend
        self.array_first = array_first

        # filter out "-indexed" params
        nonindexed_params = {
            param: val for param, val in params.items()
            if param not in index_affected
        }

        needs_reset = set(needs_reset) - set(nonindexed_params.keys())
        if needs_reset:
            self._set_state(params=needs_reset)

        # 3. Do adjustment for all non-indexing related parameters.
        adj = super().adjust(nonindexed_params, **kwargs)

        # 4. Add indexing params back for return to user.
        adj.update(
            {
                param: val for param, val in params.items()
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
        if param in self.WAGE_INDEXED_PARAMS:
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
                   removed=None, redefined=None, wage_indexed=None):
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

        if start_year or self.JSON_START_YEAR:
            initial_state = {"year": start_year or self.JSON_START_YEAR}
        else:
            initial_state = None
        super().__init__(initial_state=initial_state)
        self._init_values = {
            param: data["value"]
            for param, data in self.read_params(self.defaults).items()
            if param != "schema"
        }

    def _update(self, revision, ignore_warnings, raise_errors):
        """
        A translation layer on top of Parameters.adjust. Projects
        that have historically used the `_update` method with
        Tax-Calculator styled adjustments can continue to do so
        without making any changes to how they handle adjustments.

        Converts reforms that are compatible with Tax-Calculator:

        adjustment = {
            "standard_deduction": {2024: [10000.0, 10000.0]},
            "ss_rate": {2024: 0.2}
        }

        into reforms that are compatible with ParamTools:

        {
            'standard_deduction': [
                {'year': 2024, 'marital_status': 'single', 'value': 10000.0},
                {'year': 2024, 'marital_status': 'joint', 'value': 10000.0}
            ],
            'ss_rate': [{'value': 0.2}]}
        }

        """
        if not isinstance(revision, dict):
            raise paramtools.ValidationError(
                {"errors": {"schema": "Revision must be a dictionary."}},
                None
            )
        new_params = defaultdict(list)
        # save shallow copy of current instance state
        cur_state = dict(self.view_state())
        for param, val in revision.items():
            if not isinstance(param, str):
                msg = f"Parameter {param} is not a string."
                raise paramtools.ValidationError(
                    {"errors": {"schema": msg}},
                    None
                )
            if (
                param not in self._data and
                param.split("-indexed")[0] not in self._data
            ):
                if self.REMOVED_PARAMS and param in self.REMOVED_PARAMS:
                    msg = self.REMOVED_PARAMS[param]
                elif self.REDEFINED_PARAMS and param in self.REDEFINED_PARAMS:
                    msg = self.REDEFINED_PARAMS[param]
                else:
                    msg = f"Parameter {param} does not exist."
                raise paramtools.ValidationError(
                    {"errors": {"schema": msg}},
                    None
                )
            if param.endswith("-indexed"):
                for year, yearval in val.items():
                    new_params[param] += [{"year": year, "value": yearval}]
            elif isinstance(val, dict):
                for year, yearval in val.items():
                    val = getattr(self, param)
                    if isinstance(val, np.ndarray):
                        ndims = val.ndim
                    else:
                        ndims = 0
                    yearval = np.array(yearval)
                    short_dims = ndims - yearval.ndim
                    yearval = yearval.reshape(
                        (*(1, ) * short_dims, *yearval.shape)
                    )
                    self.set_state(year=year)
                    try:
                        yearval = self.from_array(param, yearval)
                    except IndexError:
                        msg = (
                            f"Pameter {param} does not have the correct "
                            f"array dimensions for year {year}."
                        )
                        raise paramtools.ValidationError(
                            {"errors": {"schema": msg}},
                            None
                        )
                    new_params[param] += yearval
            else:
                msg = (
                    f"Parameter {param} must be a year:value dictionary "
                    f"if you are not using the new adjust method."
                )
                raise paramtools.ValidationError(
                    {"errors": {"schema": msg}},
                    None
                )
        self.set_state(**cur_state)
        return self.adjust(
            new_params,
            ignore_warnings=ignore_warnings,
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
        # TODO: taxcalc expects string errors when empty.
        # TODO: paramtools doesn't do errors.
        return self.errors or ""

    @property
    def parameter_errors(self):
        # TODO: taxcalc expects string errors when empty.
        return self.errors or ""

    @staticmethod
    def _read_json_revision(obj, topkey):
        """
        Read JSON revision specified by obj and topkey
        returning a single revision dictionary suitable for
        use with the Parameters._update method.
        The obj function argument can be None or a string, where the
        string contains a local filename, a URL beginning with 'http'
        pointing to a valid JSON file hosted online, or valid JSON
        text.
        The topkey argument must be a string containing the top-level
        key in a compound-revision JSON text for which a revision
        dictionary is returned.  If the specified topkey is not among
        the top-level JSON keys, the obj is assumed to be a
        non-compound-revision JSON text for the specified topkey.
        """
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
        if not isinstance(obj, str):
            raise ValueError('obj is neither None nor a string')
        if not isinstance(topkey, str):
            raise ValueError('topkey={} is not a string'.format(topkey))
        if os.path.isfile(obj):
            if not obj.endswith('.json'):
                msg = 'obj does not end with ".json": {}'
                raise ValueError(msg.format(obj))
            txt = open(obj, 'r').read()
        elif obj.startswith('http'):
            if not obj.endswith('.json'):
                msg = 'obj does not end with ".json": {}'
                raise ValueError(msg.format(obj))
            req = requests.get(obj)
            req.raise_for_status()
            txt = req.text
        else:
            txt = obj
        # strip out //-comments without changing line numbers
        json_txt = re.sub('//.*', ' ', txt)
        # convert JSON text into a Python dictionary
        full_dict = json_to_dict(json_txt)
        # check top-level key contents of dictionary
        if topkey in full_dict.keys():
            single_dict = full_dict[topkey]
        else:
            single_dict = full_dict
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
        Allows the user to get the value of a parameter over all years,
        not just the ones that are active.
        """
        if (
            attr.startswith("_") and
            attr[1:] in super().__getattribute__("_data")
        ):
            state = dict(self.view_state())
            self.clear_state()
            value = getattr(self, attr[1:])
            self.set_state(**state)
            return value
        else:
            raise AttributeError(f"{attr} not definied.")
