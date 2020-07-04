import numpy as np
import pandas as pd
from collections import OrderedDict
import taxcalc as tc


INPUT_FILENAME = 'test_in.md'
OUTPUT_FILENAME = 'test_out.md'

# CURDIR_PATH = os.path.abspath(os.path.dirname(__file__))
CURDIR_PATH = os.path.abspath('')

TAXCALC_PATH = os.path.join(CURDIR_PATH, '..', 'taxcalc')

# INPUT_PATH = os.path.join(CURDIR_PATH, INPUT_FILENAME)
# Use TCJA to determine whether policies change in 2026.
TCJA_PATH = os.path.join(CURDIR_PATH,'../taxcalc/reforms/TCJA.json')
POLICY_PATH = os.path.join(TAXCALC_PATH, 'policy_current_law.json')
IOVARS_PATH = os.path.join(TAXCALC_PATH, 'records_variables.json')
CONSUMPTION_PATH = os.path.join(TAXCALC_PATH, 'consumption.json')
GROWDIFF_PATH = os.path.join(TAXCALC_PATH, 'growdiff.json')
INPUT_PATH = os.path.join(CURDIR_PATH, INPUT_FILENAME)
OUTPUT_PATH = os.path.join(CURDIR_PATH, OUTPUT_FILENAME)

START_YEAR = 2013
END_YEAR_SHORT = 2020
END_YEAR_LONG = 2027


SECTION_1_ORDER = ['Parameter Indexing',
                   'Payroll Taxes',
                   'Social Security Taxability',
                   'Above The Line Deductions',
                   'Personal Exemptions',
                   'Standard Deduction',
                   'Nonrefundable Credits',
                   'Child/Dependent Credits',
                   'Itemized Deductions',
                   'Capital Gains And Dividends',
                   'Personal Income',
                   'Other Taxes',
                   'Refundable Credits',
                   'Surtaxes',
                   'Universal Basic Income',
                   'Benefits',
                   'Other Parameters (not in Tax-Brain webapp)']


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


def make_policy_params():
    params_dict = reformat_params()
    text = policy_params(POLICY_PATH, '', params_dict)
    with open(POLICY_PATH) as pfile:
        json_text = pfile.read()
    params = tc.json_to_dict(json_text)
    df = pd.DataFrame(params).transpose()[1:].join(
    pd.DataFrame(params_dict).transpose())
    df['content'] = paramtextdf(df)
    df.section_1 = np.where(df.section_1 == '',
        'Other Parameters (not in Tax-Brain webapp)', df.section_1)
    section_1_order_index = dict(zip(SECTION_1_ORDER,
        range(len(SECTION_1_ORDER))))
    df['section_1_order'] = df.section_1.map(section_1_order_index)
    df.sort_values(['section_1_order', 'section_2'], inplace=True)
    # Add section titles when they change.
    df['new_section_1'] = ~df.section_1.eq(df.section_1.shift())
    df['new_section_2'] = (~df.section_2.eq(df.section_2.shift()) &
        df.section_2 > '')
    df['section_1_content'] = np.where(df.new_section_1,
        '## ' + df.section_1 + '\n\n', '')
    df['section_2_content'] = np.where(df.new_section_2,
        '### ' + df.section_2 + '\n\n', '')
    # Concatenate section titles with content for each parameter.
    df['content_all'] = df.section_1_content + df.section_2_content + df.content
    # Return a single string.
    return '\n\n'.join(df.content_all)


def paramtextdf(p):
    """ Don't include sections - do that later.
    
    Args:
        p: DataFrame representing parameters.
    """
    def title(p):
        return '####  `' + p.index + '`'
    
    def description(p):
        return '_Description:_ ' + p.description
    
    def notes(p):
        return np.where(p.notes == '', '', '_Notes:_ ' + p.notes)
    
    def effect_puf_cps_one(row):
        return ('_Has An Effect When Using:_' +
                ' _PUF data:_ ' + boolstr(row.compatible_data['puf']) +
                ' _CPS data:_ ' + boolstr(row.compatible_data['cps']))
    
    def effect_puf_cps(p):
        return p.apply(effect_puf_cps_one, axis=1)
                
    def inflation_indexed(p):
        return ('_Can Be Inflation Indexed:_ ' + boolstr(p.indexable) +
                ' _Is Inflation Indexed:_ ' + boolstr(p.indexed))
        
    def value_type(p):
        return '_Value Type:_ ' + p.type
    
    def known_values_one(row):
        # Requires non-vectorizable functions.
        txt ='_Known Values:_  \n'
        nvalues = len(row['values'][0])
        if nvalues == 5:
            txt += ' for: [single, mjoint, mseparate, headhh, widow]  \n'
        elif nvalues == 4:
            txt += ' for: [0kids, 1kid, 2kids, 3+kids]  \n'
        elif nvalues == 7:
            txt += ' for: [med, sltx, retx, cas, misc, int, char]  \n'
        for cyr, val in zip(row['years'], row['values']):
            if nvalues == 1:
                val = val[0]
            txt += str(cyr) + ': ' + str(val) + '  \n'
        return txt
                         
    def known_values(p):
        return p.apply(known_values_one, axis=1)
        
    def valid_range_one(row):
        r = row.validators['range']
        return ('_Valid Range:_' +
                ' min = ' + str(r['min']) +
                ' and max = ' + str(r['max']) + '  \n' +
                '_Out-of-Range Action:_ ' + r.get('level', 'error'))
    
    def valid_range(p):
        return p.apply(valid_range_one, axis=1)
    
    return (title(p) + '  \n' +
            description(p) + '  \n' +
            notes(p) + '  \n' +
            effect_puf_cps(p) + '  \n' +
            inflation_indexed(p) + '  \n' +
            value_type(p) + '  \n' +
            known_values(p) + '  \n' +
            valid_range(p) + '\n\n'
           )


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
                    if (params[param][idx]['year'] !=
                        params[param][idx - 1]['year']):
                        list_vals2.append(list_vals1)
                        params_dict[param]['values'] = list_vals2
    return params_dict

def policy_params(path, text, params_dict):
    """
    Read policy parameters from path, integrate them into text, and
    return the integrated text.
    """
    # pylint: disable=too-many-locals
    with open(path) as pfile:
        json_text = pfile.read()
    params = tc.json_to_dict(json_text)
    import pdb; pdb.set_trace()
    assert isinstance(params, OrderedDict)
    # construct section dict containing sec1_sec2 titles
    concat_str = ' @ '
    section = OrderedDict()
    using_other_params_section = False
    for pname in params:
        if pname == "schema":
            continue
        param = params[pname]
        sec1_sec2 = '{}{}{}'.format(param['section_1'],
                                    concat_str,
                                    param['section_2'])
        if sec1_sec2 == concat_str:
            using_other_params_section = True
        elif sec1_sec2 not in section:
            section[sec1_sec2] = 0
    if using_other_params_section:
        section[concat_str] = 0
    # construct parameter text for each sec1_sec2 in section
    for sec1_sec2 in section:
        split_list = sec1_sec2.split(concat_str)
        sec1 = split_list[0]
        sec2 = split_list[1]
        ptext = ''
        for pname in params:
            if pname == "schema":
                continue
            param = params[pname]
            if sec1 == param['section_1'] and sec2 == param['section_2']:
                ptext += policy_param_text(pname, param, params_dict)
    return ptext


def var_text(vname, iotype, variable):
    """
    Extract info from variable for vname of iotype
    and return info as HTML string.
    """
    if iotype == 'read':
        txt = '## `{}`'.format(vname)
        if 'required' in variable:
            txt += '*'
    else:
        txt = '## `{}`'.format(vname)
    txt += '_Description:_ {}  \n'.format(variable['desc'])
    if variable['type'] == 'float':
        vtype = 'real'
    elif variable['type'] == 'int':
        vtype = 'integer'
    else:
        msg = ('{} variable {} has '
               'unknown type={}  \n'.format(iotype, vname, variable['type']))
        raise ValueError(msg)
    txt += '_Datatype:_ {}  \n'.format(vtype)
    if iotype == 'read':
        txt += '_Availability:_ {}  \n'.format(variable['availability'])
    txt += '_IRS Form Location:_'
    formdict = variable['form']
    for yrange in sorted(formdict.keys()):
        txt += '{}: {}  \n'.format(yrange, formdict[yrange])
    return txt
