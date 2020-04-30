"""
Reads skeletal uguide.htmx file and writes fleshed-out uguide.html file
containing information from several JSON files.
"""
# CODING-STYLE CHECKS:
# pycodestyle make_uguide.py
# pylint --disable=locally-disabled make_uguide.py

import os
import sys
from collections import OrderedDict
from taxcalc import *


INPUT_FILENAME = 'uguide.htmx'
OUTPUT_FILENAME = 'uguide.html'

CURDIR_PATH = os.path.abspath(os.path.dirname(__file__))

TAXCALC_PATH = os.path.join(CURDIR_PATH, '..', 'taxcalc')

INPUT_PATH = os.path.join(CURDIR_PATH, INPUT_FILENAME)
TCJA_PATH = os.path.join(CURDIR_PATH,'../taxcalc/reforms/TCJA.json')
POLICY_PATH = os.path.join(TAXCALC_PATH, 'policy_current_law.json')
IOVARS_PATH = os.path.join(TAXCALC_PATH, 'records_variables.json')
CONSUMPTION_PATH = os.path.join(TAXCALC_PATH, 'consumption.json')
GROWDIFF_PATH = os.path.join(TAXCALC_PATH, 'growdiff.json')
OUTPUT_PATH = os.path.join(CURDIR_PATH, OUTPUT_FILENAME)


def main():
    """
    Contains high-level logic of the script.
    """
    # read INPUT file into text variable
    with open(INPUT_PATH, 'r') as ifile:
        text = ifile.read()

    # augment text variable with do-not-edit warning
    old = '<!-- #WARN# -->'
    new = ('<!-- *** NEVER EDIT THIS FILE BY HAND *** -->\n'
           '<!-- *** INSTEAD EDIT uguide.htmx FILE *** -->')
    text = text.replace(old, new)

    # augment text variable with top button code
    topbtn_filename = os.path.join(CURDIR_PATH, 'topbtn.htmx')
    with open(topbtn_filename, 'r') as topbtn_file:
        topbtn = topbtn_file.read()
    old = '<!-- #TOP# -->'
    text = text.replace(old, topbtn)

    params_dict = reformat_params()
    # augment text variable with information from JSON files
    text = policy_params(POLICY_PATH, text, params_dict)
    text = io_variables('read', IOVARS_PATH, text)
    text = io_variables('calc', IOVARS_PATH, text)
    text = assumption_params('consumption', CONSUMPTION_PATH, text)
    text = assumption_params('growdiff', GROWDIFF_PATH, text)

    # write text variable to OUTPUT file
    with open(OUTPUT_PATH, 'w') as ofile:
        ofile.write(text)

    # normal return code
    return 0
# end of main function code


def reformat_params():
    """
    Translates ParamTools-style policy_current_law.json
    to a dictionary that resembles the old Tax-Calculator
    parameter schema
    """
    # Parameters that were changed by TCJA will be extended through
    # 2026 in the uguide
    tcja = Policy.read_json_reform(TCJA_PATH)

    pol = Policy()
    pol.clear_state()
    years_short = list(range(2013, 2020))
    years_long = list(range(2013, 2027))
    pol.set_year(years_long)
    params = pol.specification(serializable=True, sort_values=True)

    # Create parameter dictionary that resembles old Tax-Calculator
    # paramter schema
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
                    if params[param][idx]['year'] != params[param][idx - 1]['year']:
                        list_vals2.append(list_vals1)
                        params_dict[param]['values'] = list_vals2
    return params_dict


def policy_param_text(pname, param, params_dict):
    """
    Extract info from param for pname and return as HTML string.
    """
    # pylint: disable=too-many-statements,too-many-branches

    sec1 = param['section_1']
    if sec1:
        txt = '<p><b>{} &mdash; {}</b>'.format(sec1, param['section_2'])
    else:
        txt = '<p><b>{} &mdash; {}</b>'.format('Other Parameters',
                                               'Not in Tax-Brain webapp')
    txt += '<br><i>tc Name:</i> {}'.format(pname)
    txt += '<br><i>Title:</i> {}'.format(param['title'])
    txt += '<br><i>Description:</i> {}'.format(param['description'])
    if param.get('notes', ''):
        txt += '<br><i>Notes:</i> {}'.format(param['notes'])
    txt += '<br><i>Has An Effect When Using:</i>'
    txt += '&nbsp;&nbsp; <i>PUF data:</i> '
    if param['compatible_data']['puf']:
        txt += 'True'
    else:
        txt += 'False'
    txt += '&nbsp;&nbsp; <i>CPS data:</i> '
    if param['compatible_data']['cps']:
        txt += 'True'
    else:
        txt += 'False'
    txt += '<br><i>Can Be Inflation Indexed:</i> '
    if param['indexable']:
        txt += 'True'
    else:
        txt += 'False'
    txt += '&nbsp;&nbsp;&nbsp;&nbsp; <i>Is Inflation Indexed:</i> '
    if param['indexed']:
        txt += 'True'
    else:
        txt += 'False'
    txt += '<br><i>Value Type:</i> {}'.format(param['type'])
    txt += '<br><i>Known Values:</i>'
    if len(params_dict[pname]['values'][0]) == 5:
        txt += '<br>&nbsp;&nbsp; for: [single, mjoint, mseparate, headhh, widow]'
    elif len(params_dict[pname]['values'][0]) == 4:
        txt += '<br>&nbsp;&nbsp; for: [0kids, 1kid, 2kids, 3+kids]'
    elif len(params_dict[pname]['values'][0]) == 7:
        txt += '<br>&nbsp;&nbsp; for: [med, sltx, retx, cas, misc, int, char]' 
    for cyr, val in zip(params_dict[pname]['years'], params_dict[pname]['values']):
        if len(params_dict[pname]['values'][0]) == 1:
            txt += '<br>{}: {}'.format(cyr, val[0])
        else:
            txt += '<br>{}: {}'.format(cyr, val)       
    txt += '<br><i>Valid Range:</i>'
    validators = param.get("validators", None)
    if validators:
        minval = validators['range']['min']
        maxval = validators['range']['max']
        txt += ' min = {} and max = {}'.format(minval, maxval)
        invalid_action = validators["range"].get('level', 'error')
        txt += '<br><i>Out-of-Range Action:</i> {}'.format(invalid_action)
    txt += '</p>'
    return txt


def policy_params(path, text, params_dict):
    """
    Read policy parameters from path, integrate them into text, and
    return the integrated text.
    """
    # pylint: disable=too-many-locals
    with open(path) as pfile:
        json_text = pfile.read()
    params = json_to_dict(json_text)
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
        # integrate parameter text into text
        old = '<!-- {} -->'.format(sec1_sec2)
        text = text.replace(old, ptext)
    return text


def var_text(vname, iotype, variable):
    """
    Extract info from variable for vname of iotype
    and return info as HTML string.
    """
    if iotype == 'read':
        txt = '<p><i>Input Variable Name:</i> <b>{}</b>'.format(vname)
        if 'required' in variable:
            txt += '<br><b><i>Required Input Variable</i></b>'
    else:
        txt = '<p><i>Output Variable Name:</i> <b>{}</b>'.format(vname)
    txt += '<br><i>Description:</i> {}'.format(variable['desc'])
    if variable['type'] == 'float':
        vtype = 'real'
    elif variable['type'] == 'int':
        vtype = 'integer'
    else:
        msg = ('{} variable {} has '
               'unknown type={}'.format(iotype, vname, variable['type']))
        raise ValueError(msg)
    txt += '<br><i>Datatype:</i> {}'.format(vtype)
    if iotype == 'read':
        txt += '<br><i>Availability:</i> {}'.format(variable['availability'])
    txt += '<br><i>IRS Form Location:</i>'
    formdict = variable['form']
    for yrange in sorted(formdict.keys()):
        txt += '<br>{}: {}'.format(yrange, formdict[yrange])
    txt += '</p>'
    return txt


def io_variables(iotype, path, text):
    """
    Read variables for iotype ('read' for input or 'calc' for output)
    from path, integrate them into text, and return the integrated text.
    """
    with open(path) as vfile:
        json_text = vfile.read()
    variables = json_to_dict(json_text)
    assert isinstance(variables, dict)
    # construct variable text
    vtext = ''
    for vname in sorted(variables[iotype].keys()):
        vtext += var_text(vname, iotype, variables[iotype][vname])
    # integrate variable text into text
    old = '<!-- {}@variables -->'.format(iotype)
    text = text.replace(old, vtext)
    return text


def assumption_param_text(pname, ptype, param):
    """
    Extract info from param for pname of ptype and return as HTML string.
    """
    sec1 = param.get('section_1', '')
    if sec1:
        txt = '<p><b>{} &mdash; {}</b>'.format(sec1,
                                               param.get('section_2', ''))
    else:
        txt = '<p><b>{} &mdash; {}</b>'.format('Assumption Parameter',
                                               ptype.capitalize())
    txt += '<br><i>tc Name:</i> {}'.format(pname)
    if sec1:
        txt += '<br><i>TB Name:</i> {}'.format(param['title'])
    else:
        txt += '<br><i>Long Name:</i> {}'.format(param['title'])
    txt += '<br><i>Description:</i> {}'.format(param['description'])
    if param.get('notes', ''):
        txt += '<br><i>Notes:</i> {}'.format(param['notes'])
    txt += '<br><i>Default Value:</i>'
    if param.get('vi_vals', []):
        cols = ', '.join(param['vi_vals'])
        txt += '<br>&nbsp;&nbsp; for: [{}]'.format(cols)
    for vo in param["value"]:
        labels = " ".join(
            f"{label}={value}" for label, value in vo.items()
            if label not in ("year", "value")
        )
        txt += f"<br>{vo['year']}: {vo['value']} {labels}"
    txt += '<br><i>Valid Range:</i>'
    validators = param.get("validators", None)
    if validators:
        minval = validators['range']['min']
        maxval = validators['range']['max']
        txt += ' min = {} and max = {}'.format(minval, maxval)
        invalid_action = validators["range"].get('level', 'error')
        txt += '<br><i>Out-of-Range Action:</i> {}'.format(invalid_action)
    txt += '</p>'
    return txt


def assumption_params(ptype, path, text):
    """
    Read assumption parameters of ptype from path, integrate them into text,
    and return the integrated text.
    """
    with open(path) as pfile:
        json_text = pfile.read()
    params = json_to_dict(json_text)
    assert isinstance(params, OrderedDict)
    # construct parameter text for each param
    ptext = ''
    for pname in params:
        if pname == "schema":
            continue
        param = params[pname]
        ptext += assumption_param_text(pname, ptype, param)
    # integrate parameter text into text
    old = '<!-- {}@parameters -->'.format(ptype)
    text = text.replace(old, ptext)
    return text


if __name__ == '__main__':
    sys.exit(main())
