"""
Creates documentation markdown text for policy and assumption parameters.
"""

import os
import numpy as np
import pandas as pd
import taxcalc as tc


CURDIR_PATH = os.path.abspath(os.path.dirname(__file__))
TAXCALC_PATH = os.path.join(CURDIR_PATH, '../../..', 'taxcalc')
# Use TCJA to determine whether policies change in 2026.
TCJA_PATH = os.path.join(TAXCALC_PATH, 'reforms/TCJA.json')

START_YEAR = 2013
END_YEAR_SHORT = 2020
END_YEAR_LONG = 2027


def make_params(path, ptype):
    """ Make string with all parameter information.

    Args:
        path: Path to parameter file.
        ptype: Parameter type. One of 'policy', 'consumption', or 'growdiff'.

    Returns:
        Single string with all parameter information.
    """
    with open(path, 'r', encoding='utf-8') as pfile:
        json_text = pfile.read()
    params = tc.json_to_dict(json_text)
    df = pd.DataFrame(params).transpose().drop('schema')
    # Extra metadata for years and values is available for policy parameters.
    if ptype == 'policy':
        df = df.join(pd.DataFrame(reformat_params()).transpose())
    # Add parameter text for policy, consumption, and growdiff parameter types.
    df['content'] = paramtextdf(df, ptype)
    # Sort policy parameters alphabetically (ignoring case) by name.
    if ptype == 'policy':
        df = df.sort_index(key=lambda idx: idx.str.lower())
    # Return a single string.
    return '\n\n'.join(df.content)


def boolstr(b):
    """ Return a bool value or Series as 'True'/'False' strings.

    Args:
        b: Bool value or pandas Series.

    Returns:
        If b is a value, returns a single 'True'/'False' value.
        If b is a Series, returns a Series of 'True'/'False' values.
    """
    if isinstance(b, pd.Series):
        return pd.Series(np.where(b, 'True', 'False'),
                         index=b.index)
    if b:
        return 'True'
    return 'False'


def paramtextdf(df, ptype):  # pylint: disable=too-many-locals
    """ Return Series of parameter text for each parameter.

    Args:
        df: DataFrame representing parameters.
        ptype:
    """
    def title(df):
        return '####  `' + df.index + '`  \n'

    def long_name(df):
        return '_Long Name:_ ' + df.title + '  \n'

    def description(df):
        return '_Description:_ ' + df.description + '  \n'

    def notes(df):
        txt = df.get('notes', '')
        return np.where(txt == '', '', '_Notes:_ ' + txt + '  \n')

    def effect_data_one(row):
        return ('_Has An Effect When Using:_' +
                ' _PUF data:_ ' + boolstr(row.compatible_data['puf']) +
                ' _CPS data:_ ' + boolstr(row.compatible_data['cps']) +
                ' _TMD data:_ ' + boolstr(row.compatible_data['tmd']) + '  \n')

    def effect_data(df):
        return df.apply(effect_data_one, axis=1)

    def inflation_indexed(df):
        return ('_Can Be Inflation Indexed:_ ' + boolstr(df.indexable) +
                ' _Is Inflation Indexed:_ ' + boolstr(df.indexed) + '  \n')

    def value_type(df):
        return '_Value Type:_ ' + df.type + '  \n'

    def known_values_one(row):
        # Requires non-vectorizable functions.
        txt = '_Known Values:_  \n'
        nvalues = len(row['values'][0])
        if nvalues == 5:
            txt += ' for: [single, mjoint, mseparate, headhh, widow]  \n'
        elif nvalues == 4:
            txt += ' for: [0kids, 1kid, 2kids, 3+kids]  \n'
        for cyr, val in zip(row['years'], row['values']):
            if nvalues == 1:
                val = val[0]
            txt += str(cyr) + ': ' + str(val) + '  \n'
        return txt

    def known_values(df):
        return df.apply(known_values_one, axis=1)

    def default_value_one(row):
        return '_Default Value:_ ' + str(row.value[0]['value']) + '  \n'

    def default_value(df):
        return df.apply(default_value_one, axis=1)

    def valid_range_one(row):
        r = row.validators['range']
        return ('_Valid Range:_' +
                ' min = ' + str(r['min']) +
                ' and max = ' + str(r['max']) + '  \n' +
                '_Out-of-Range Action:_ ' + r.get('level', 'error') + '  \n')

    def valid_range(df):
        return df.apply(valid_range_one, axis=1)

    text = title(df)
    # Add "long name" for growdiff and consumption parameters.
    if ptype != 'policy':
        text += long_name(df)
    text += description(df)
    if ptype == 'policy':
        text += notes(df)
        text += effect_data(df)
        text += inflation_indexed(df)
    text += value_type(df)
    if ptype == 'policy':
        # Skip the newline because it's part of the loop.
        text += known_values(df)
    else:
        text += default_value(df)
    text += valid_range(df)
    return text


def reformat_params():
    """
    Translates ParamTools-style policy_current_law.json
    to a dictionary that resembles the old Tax-Calculator
    parameter schema
    """
    # Parameters that were changed by TCJA will be extended through
    # 2026 in the uguide
    tcja = tc.Policy.read_json_reform(TCJA_PATH)

    pol = tc.Policy()
    pol.clear_state()
    years_short = list(range(START_YEAR, END_YEAR_SHORT))
    years_long = list(range(START_YEAR, END_YEAR_LONG))
    pol.set_year(years_long)
    params = pol.specification(serializable=True, sort_values=True)

    # Create parameter dictionary that resembles old Tax-Calculator
    # parameter schema
    params_dict = {}
    for param in params.keys():
        if param in tcja.keys():
            years = years_long
        else:
            years = years_short
        params_dict[param] = {}
        params_dict[param]['years'] = years
        list_vals2 = []
        for year in years:
            list_vals1 = []
            for idx in range(0, len(params[param])):
                if params[param][idx]['year'] == year:
                    list_vals1.append(params[param][idx]['value'])
                    if (
                            params[param][idx]['year'] !=
                            params[param][idx - 1]['year']
                    ):
                        list_vals2.append(list_vals1)
                        params_dict[param]['values'] = list_vals2
    return params_dict
