"""
Adds JSON information to input HTML and writes augmented HTML file.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 make.py
# pylint --disable=locally-disabled make.py

import sys
import os
import json
from collections import OrderedDict

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
INPUT_FILENAME = 'index.htmx'
INPUT_PATH = os.path.join(CUR_PATH, INPUT_FILENAME)
POLICY_PATH = os.path.join(CUR_PATH, '..', 'current_law_policy.json')
IOVARS_PATH = os.path.join(CUR_PATH, '..', 'records_variables.json')
CONSUMPTION_PATH = os.path.join(CUR_PATH, '..', 'consumption.json')
BEHAVIOR_PATH = os.path.join(CUR_PATH, '..', 'behavior.json')
GROWDIFF_PATH = os.path.join(CUR_PATH, '..', 'growdiff.json')
OUTPUT_FILENAME = 'index.html'
OUTPUT_PATH = os.path.join(CUR_PATH, OUTPUT_FILENAME)


def main():
    """
    Contains high-level logic of the script.
    """
    # read INPUT file into text variable
    with open(INPUT_PATH, 'r') as ifile:
        text = ifile.read()

    # augment text variable with information from JSON files
    text = policy_params(POLICY_PATH, text)
    text = io_variables('read', IOVARS_PATH, text)
    text = io_variables('calc', IOVARS_PATH, text)
    text = response_params('consumption', CONSUMPTION_PATH, text)
    text = response_params('behavior', BEHAVIOR_PATH, text)
    text = response_params('growdiff', GROWDIFF_PATH, text)

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
    sec1 = param['section_1']
    if len(sec1) > 0:
        txt = '<p><b>{} &mdash; {}</b>'.format(sec1, param['section_2'])
    else:
        txt = '<p><b>{} &mdash; {}</b>'.format('Other Parameters',
                                               'Not in TaxBrain GUI')
    txt += '<br><i>CLI Name:</i> {}'.format(pname)
    if len(sec1) > 0:
        txt += '<br><i>GUI Name:</i> {}'.format(param['long_name'])
    else:
        txt += '<br><i>Long Name:</i> {}'.format(param['long_name'])
    txt += '<br><i>Description:</i> {}'.format(param['description'])
    if len(param['notes']) > 0:
        txt += '<br><i>Notes:</i> {}'.format(param['notes'])
    if param['cpi_inflated']:
        txt += '<br><i>Inflation Indexed:</i> True'
    else:
        txt += '<br><i>Inflation Indexed:</i> False'
    txt += '<br><i>Known Values:</i>'
    if len(param['col_label']) > 0:
        cols = ', '.join(param['col_label'])
        txt += '<br>&nbsp;&nbsp; for: [{}]'.format(cols)
    for cyr, val in zip(param['row_label'], param['value']):
        txt += '<br>{}: {}'.format(cyr, val)
    txt += '</p>'
    return txt


def policy_params(path, text):
    """
    Read policy parameters from path, integrate them into text, and
    return the integrated text.
    """
    with open(path) as pfile:
        params = json.load(pfile, object_pairs_hook=OrderedDict)
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
    txt += '<br><i>Datatype:</i> {}'.format(variable['type'])
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
        variables = json.load(vfile)
    assert isinstance(variables, dict)
    # construct variable text
    vtext = ''
    for vname in sorted(variables[iotype].keys()):
        vtext += var_text(vname, iotype, variables[iotype][vname])
    # integrate variable text into text
    old = '<!-- {}@variables -->'.format(iotype)
    text = text.replace(old, vtext)
    return text


def response_param_text(pname, ptype, param):
    """
    Extract info from param for pname of ptype and return as HTML string.
    """
    sec1 = param['section_1']
    if len(sec1) > 0:
        txt = '<p><b>{} &mdash; {}</b>'.format(sec1, param['section_2'])
    else:
        txt = '<p><b>{} &mdash; {}</b>'.format('Response Parameter',
                                               ptype.capitalize())
    txt += '<br><i>CLI Name:</i> {}'.format(pname)
    if len(sec1) > 0:
        txt += '<br><i>GUI Name:</i> {}'.format(param['long_name'])
    else:
        txt += '<br><i>Long Name:</i> {}'.format(param['long_name'])
    txt += '<br><i>Description:</i> {}'.format(param['description'])
    if len(param['notes']) > 0:
        txt += '<br><i>Notes:</i> {}'.format(param['notes'])
    txt += '<br><i>Default Values:</i>'
    if len(param['col_label']) > 0:
        cols = ', '.join(param['col_label'])
        txt += '<br>&nbsp;&nbsp; for: [{}]'.format(cols)
    for cyr, val in zip(param['row_label'], param['value']):
        txt += '<br>{}: {}'.format(cyr, val)
    txt += '</p>'
    return txt


def response_params(ptype, path, text):
    """
    Read response parameters of ptype from path, integrate them into text,
    and return the integrated text.
    """
    with open(path) as pfile:
        params = json.load(pfile, object_pairs_hook=OrderedDict)
    assert isinstance(params, OrderedDict)
    # construct parameter text for each param
    ptext = ''
    for pname in params:
        param = params[pname]
        ptext += response_param_text(pname, ptype, param)
    # integrate parameter text into text
    old = '<!-- {}@parameters -->'.format(ptype)
    text = text.replace(old, ptext)
    return text


if __name__ == '__main__':
    sys.exit(main())
