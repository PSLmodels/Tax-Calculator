"""
Reads skeletal uguide.htmx file and writes fleshed-out uguide.html file
containing information from several JSON files.
"""
# CODING-STYLE CHECKS:
# pycodestyle --ignore=E402 make_uguide.py
# pylint --disable=locally-disabled make_uguide.py

import os
import sys
from collections import OrderedDict
CURDIR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CURDIR_PATH, '..'))
# pylint: disable=import-error,wrong-import-position
from taxcalc import Policy, json_to_dict


INPUT_FILENAME = 'uguide.htmx'
OUTPUT_FILENAME = 'uguide.html'

TAXCALC_PATH = os.path.join(CURDIR_PATH, '..', 'taxcalc')

INPUT_PATH = os.path.join(CURDIR_PATH, INPUT_FILENAME)
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

    # augment text variable with information from JSON files
    text = policy_params(POLICY_PATH, text)
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


def policy_param_text(pname, param):
    """
    Extract info from param for pname and return as HTML string.
    """
    # pylint: disable=too-many-statements,too-many-branches,len-as-condition
    sec1 = param['section_1']
    if len(sec1) > 0:
        txt = '<p><b>{} &mdash; {}</b>'.format(sec1, param['section_2'])
    else:
        txt = '<p><b>{} &mdash; {}</b>'.format('Other Parameters',
                                               'Not in Tax-Brain webapp')
    txt += '<br><i>tc Name:</i> {}'.format(pname)
    if len(sec1) > 0:
        txt += '<br><i>TB Name:</i> {}'.format(param['long_name'])
    else:
        txt += '<br><i>Long Name:</i> {}'.format(param['long_name'])
    txt += '<br><i>Description:</i> {}'.format(param['description'])
    if len(param.get('notes', '')) > 0:
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
    txt += '<br><i>Value Type:</i> {}'.format(param['value_type'])
    txt += '<br><i>Known Values:</i>'
    if len(param.get('vi_vals', [])) > 0:
        cols = ', '.join(param['vi_vals'])
        txt += '<br>&nbsp;&nbsp; for: [{}]'.format(cols)
    for cyr, val in zip(param['value_yrs'], param['value']):
        final_cyr = cyr
        final_val = val
        txt += '<br>{}: {}'.format(cyr, val)
    if not param['indexed']:
        fcyr = int(final_cyr)
        if fcyr < Policy.LAST_KNOWN_YEAR:
            # extrapolate final_val thru Policy.LAST_KNOWN_YEAR if not indexed
            for cyr in range(fcyr + 1, Policy.LAST_KNOWN_YEAR + 1):
                txt += '<br>{}: {}'.format(cyr, final_val)
    txt += '<br><i>Valid Range:</i>'
    minval = param['valid_values']['min']
    maxval = param['valid_values']['max']
    txt += ' min = {} and max = {}'.format(minval, maxval)
    invalid_action = param.get('invalid_action', 'stop')
    txt += '<br><i>Out-of-Range Action:</i> {}'.format(invalid_action)
    txt += '</p>'
    return txt


def policy_params(path, text):
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
            param = params[pname]
            if sec1 == param['section_1'] and sec2 == param['section_2']:
                ptext += policy_param_text(pname, param)
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
    # pylint: disable=len-as-condition
    sec1 = param.get('section_1', '')
    if len(sec1) > 0:
        txt = '<p><b>{} &mdash; {}</b>'.format(sec1,
                                               param.get('section_2', ''))
    else:
        txt = '<p><b>{} &mdash; {}</b>'.format('Assumption Parameter',
                                               ptype.capitalize())
    txt += '<br><i>tc Name:</i> {}'.format(pname)
    if len(sec1) > 0:
        txt += '<br><i>TB Name:</i> {}'.format(param['long_name'])
    else:
        txt += '<br><i>Long Name:</i> {}'.format(param['long_name'])
    txt += '<br><i>Description:</i> {}'.format(param['description'])
    if len(param.get('notes', '')) > 0:
        txt += '<br><i>Notes:</i> {}'.format(param['notes'])
    txt += '<br><i>Default Value:</i>'
    if len(param.get('vi_vals', [])) > 0:
        cols = ', '.join(param['vi_vals'])
        txt += '<br>&nbsp;&nbsp; for: [{}]'.format(cols)
    for cyr, val in zip(param['value_yrs'], param['value']):
        txt += '<br>{}: {}'.format(cyr, val)
    txt += '<br><i>Valid Range:</i>'
    minval = param['valid_values']['min']
    maxval = param['valid_values']['max']
    txt += ' min = {} and max = {}'.format(minval, maxval)
    invalid_action = param.get('invalid_action', 'stop')
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
        param = params[pname]
        ptext += assumption_param_text(pname, ptype, param)
    # integrate parameter text into text
    old = '<!-- {}@parameters -->'.format(ptype)
    text = text.replace(old, ptext)
    return text


if __name__ == '__main__':
    sys.exit(main())
