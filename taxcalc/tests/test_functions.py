"""
Tests for Tax-Calculator functions.py file.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_functions.py
# pylint --disable=locally-disabled test_functions.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import os
import sys
import re
CUR_PATH = os.path.abspath(os.path.dirname(__file__))


def test_function_args_usage():
    """
    Checks each function argument in functions.py for use in its function body.
    """
    funcfilename = '{}/../functions.py'.format(CUR_PATH)
    with open(funcfilename, 'r') as funcfile:
        fcontent = funcfile.read()
    fcontent = re.sub('#.*', '', fcontent)  # remove all '#...' comments
    fcontent = re.sub('\n', ' ', fcontent)  # replace EOL character with space
    funcs = fcontent.split('def ')  # list of function text
    for func in funcs[1:]:  # skip first item in list, which is imports, etc.
        fcode = func.split('return ')[0]  # fcode is between def and return
        match = re.search(r'^(.+?)\((.*?)\):(.*)$', fcode)
        if match is None:
            sys.stdout.write('==========\n{}\n==========\n'.format(fcode))
            assert 'match' == 'None'
        else:
            fname = match.group(1)
            fargs = match.group(2).split(',')  # list of function arguments
            fbody = match.group(3)
        for farg in fargs:
            arg = farg.strip()
            if fbody.find(arg) < 0:
                msg = '{} function argument {} never used\n'.format(fname, arg)
                sys.stdout.write(msg)
                assert 'arg' == 'UNUSED'
