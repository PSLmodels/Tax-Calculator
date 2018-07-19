"""
Tests for Tax-Calculator TaxCalcIO class.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_taxcalcio.py
# pylint --disable=locally-disabled test_taxcalcio.py
#
# pylint: disable=too-many-lines

import os
import tempfile
import pytest
import pandas as pd
from taxcalc import TaxCalcIO  # pylint: disable=import-error


@pytest.fixture(scope='module', name='rawinputfile')
def fixture_rawinputfile():
    """
    Temporary input file that contains minimum required input variables.
    """
    ifile = tempfile.NamedTemporaryFile(suffix='.csv', mode='a', delete=False)
    contents = (
        u'RECID,MARS\n'
        u'    1,   2\n'
        u'    2,   1\n'
        u'    3,   4\n'
        u'    4,   3\n'
    )
    ifile.write(contents)
    ifile.close()
    # must close and then yield for Windows platform
    yield ifile
    if os.path.isfile(ifile.name):
        try:
            os.remove(ifile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='module', name='reformfile0')
def fixture_reformfile0():
    """
    Specify JSON reform file.
    """
    txt = """
    { "policy": {
        "_SS_Earnings_c": {"2016": [300000],
                           "2018": [500000],
                           "2020": [700000]}
      }
    }
    """
    rfile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    rfile.write(txt + '\n')
    rfile.close()
    # Must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='module', name='assumpfile0')
def fixture_assumpfile0():
    """
    Temporary assumption file with .json extension.
    """
    afile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    contents = """
    {
    "consumption": {},
    "behavior": {"_BE_sub": {"2020": [0.05]}},
    "growdiff_baseline": {"_ABOOK": {"2015": [-0.01]}},
    "growdiff_response": {},
    "growmodel": {}
    }
    """
    afile.write(contents)
    afile.close()
    # must close and then yield for Windows platform
    yield afile
    if os.path.isfile(afile.name):
        try:
            os.remove(afile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='module', name='reformfile1')
def fixture_reformfile1():
    """
    Temporary reform file with .json extension.
    """
    rfile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    contents = """
    {"policy": {
        "_AMT_brk1": { // top of first AMT tax bracket
          "2015": [200000],
          "2017": [300000]},
        "_EITC_c": { // max EITC amount by number of qualifying kids (0,1,2,3+)
          "2016": [[ 900, 5000,  8000,  9000]],
          "2019": [[1200, 7000, 10000, 12000]]},
        "_II_em": { // personal exemption amount (see indexing changes below)
          "2016": [6000],
          "2018": [7500],
          "2020": [9000]},
        "_II_em_cpi": { // personal exemption amount indexing status
          "2016": false, // values in future years are same as this year value
          "2018": true // values in future years indexed with this year as base
          },
        "_SS_Earnings_c": { // social security (OASDI) maximum taxable earnings
          "2016": [300000],
          "2018": [500000],
          "2020": [700000]},
        "_AMT_em_cpi": { // AMT exemption amount indexing status
          "2017": false, // values in future years are same as this year value
          "2020": true // values in future years indexed with this year as base
        }
      }
    }
    """
    rfile.write(contents)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='module', name='baselinebad')
def fixture_baselinebad():
    """
    Temporary baseline file with .json extension.
    """
    rfile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    contents = '{ "policy": {"_AMT_brk1": {"2011": [0.0]}}}'
    rfile.write(contents)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='module', name='errorreformfile')
def fixture_errorreformfile():
    """
    Temporary reform file with .json extension.
    """
    rfile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    contents = '{ "policy": {"_xxx": {"2015": [0]}}}'
    rfile.write(contents)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='module', name='errorassumpfile')
def fixture_errorassumpfile():
    """
    Temporary assumption file with .json extension.
    """
    rfile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    contents = """
    {
    "consumption": {"_MPC_e18400": {"2018": [-9]}},
    "behavior": {"_BE_inc": {"2018": [0.4]}},
    "growdiff_baseline": {"_ABOOKxx": {"2017": [0.02]}},
    "growdiff_response": {"_ABOOKxx": {"2017": [0.02]}},
    "growmodel": {"_activexx": {"2018": [true]}}
    }
    """
    rfile.write(contents)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='module', name='assumpfile1')
def fixture_assumpfile1():
    """
    Temporary assumption file with .json extension.
    """
    afile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    contents = """
    {
    "consumption": { "_MPC_e18400": {"2018": [0.05]} },
    "behavior": {},
    "growdiff_baseline": {},
    "growdiff_response": {},
    "growmodel": {}
    }
    """
    afile.write(contents)
    afile.close()
    # must close and then yield for Windows platform
    yield afile
    if os.path.isfile(afile.name):
        try:
            os.remove(afile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='module', name='lumpsumreformfile')
def fixture_lumpsumreformfile():
    """
    Temporary reform file without .json extension.
    """
    rfile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    lumpsum_reform_contents = '{"policy": {"_LST": {"2013": [200]}}}'
    rfile.write(lumpsum_reform_contents)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='module', name='assumpfile2')
def fixture_assumpfile2():
    """
    Temporary assumption file with .json extension.
    """
    afile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    assump2_contents = """
    {
    "consumption": {},
    "behavior": {"_BE_sub": {"2020": [0.05]}},
    "growdiff_baseline": {},
    "growdiff_response": {},
    "growmodel": {}
    }
    """
    afile.write(assump2_contents)
    afile.close()
    # must close and then yield for Windows platform
    yield afile
    if os.path.isfile(afile.name):
        try:
            os.remove(afile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.mark.parametrize('input_data, baseline, reform, assump, outdir', [
    ('no-dot-csv-filename', 'no-dot-json-filename',
     'no-dot-json-filename',
     'no-dot-json-filename', 'no-output-directory'),
    (list(), list(), list(), list(), list()),
    ('no-exist.csv', 'no-exist.json', 'no-exist.json', 'no-exist.json', '.'),
])
def test_ctor_errors(input_data, baseline, reform, assump, outdir):
    """
    Ensure error messages are generated by TaxCalcIO.__init__.
    """
    tcio = TaxCalcIO(input_data=input_data, tax_year=2013,
                     baseline=baseline, reform=reform, assump=assump,
                     outdir=outdir)
    assert tcio.errmsg


@pytest.mark.parametrize('year, base, ref, asm', [
    (2000, 'reformfile0', 'reformfile0', None),
    (2099, 'reformfile0', 'reformfile0', None),
    (2020, 'reformfile0', 'reformfile0', 'errorassumpfile'),
    (2020, 'errorreformfile', 'errorreformfile', None)
])
def test_init_errors(reformfile0, errorreformfile, errorassumpfile,
                     year, base, ref, asm):
    """
    Ensure error messages generated correctly by TaxCalcIO.init method.
    """
    # pylint: disable=too-many-arguments,too-many-locals,too-many-branches
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    # test TaxCalcIO ctor
    if base == 'reformfile0':
        baseline = reformfile0.name
    elif base == 'errorreformfile':
        baseline = errorreformfile.name
    else:
        baseline = base
    if ref == 'reformfile0':
        reform = reformfile0.name
    elif ref == 'errorreformfile':
        reform = errorreformfile.name
    else:
        reform = ref
    if asm == 'errorassumpfile':
        assump = errorassumpfile.name
    else:
        assump = asm
    # call TaxCalcIO constructor
    tcio = TaxCalcIO(input_data=recdf,
                     tax_year=year,
                     baseline=baseline,
                     reform=reform,
                     assump=assump)
    assert not tcio.errmsg
    # test TaxCalcIO.init method
    tcio.init(input_data=recdf, tax_year=year,
              baseline=baseline, reform=reform, assump=assump,
              growdiff_growmodel=None,
              aging_input_data=False,
              exact_calculations=True)
    assert tcio.errmsg


def test_creation_with_aging(rawinputfile, reformfile0):
    """
    Test TaxCalcIO instantiation with/without no policy reform and with aging.
    """
    taxyear = 2021
    tcio = TaxCalcIO(input_data=rawinputfile.name,
                     tax_year=taxyear,
                     baseline=None,
                     reform=reformfile0.name,
                     assump=None)
    assert not tcio.errmsg
    tcio.init(input_data=rawinputfile.name,
              tax_year=taxyear,
              baseline=None,
              reform=reformfile0.name,
              assump=None,
              growdiff_growmodel=None,
              aging_input_data=True,
              exact_calculations=False)
    assert not tcio.errmsg
    assert tcio.tax_year() == taxyear
    taxyear = 2016
    tcio = TaxCalcIO(input_data=rawinputfile.name,
                     tax_year=taxyear,
                     baseline=None,
                     reform=None,
                     assump=None)
    assert not tcio.errmsg
    tcio.init(input_data=rawinputfile.name,
              tax_year=taxyear,
              baseline=None,
              reform=None,
              assump=None,
              growdiff_growmodel=None,
              aging_input_data=True,
              exact_calculations=False)
    assert not tcio.errmsg
    assert tcio.tax_year() == taxyear


def test_ctor_init_with_cps_files():
    """
    Test use of CPS input files.
    """
    # specify valid tax_year for cps.csv input data
    txyr = 2020
    tcio = TaxCalcIO('cps.csv', txyr, None, None, None)
    tcio.init('cps.csv', txyr, None, None, None,
              growdiff_growmodel=None,
              aging_input_data=True,
              exact_calculations=False)
    assert not tcio.errmsg
    assert tcio.tax_year() == txyr
    # specify invalid tax_year for cps.csv input data
    txyr = 2013
    tcio = TaxCalcIO('cps.csv', txyr, None, None, None)
    tcio.init('cps.csv', txyr, None, None, None,
              growdiff_growmodel=None,
              aging_input_data=True,
              exact_calculations=False)
    assert tcio.errmsg


@pytest.mark.parametrize("dumpvar_str, str_valid, num_vars", [
    ("""
    MARS;iitax	payrolltax|combined,
    c00100
    surtax
    """, True, 8),  # these six plus added RECID and FLPDYR

    ("""
    MARS;iitax	payrolltax|kombined,c00100
    surtax
    RECID
    FLPDYR
    """, False, 8)
])
def test_custom_dump_variables(dumpvar_str, str_valid, num_vars):
    """
    Test TaxCalcIO custom_dump_variables method.
    """
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    year = 2018
    tcio = TaxCalcIO(input_data=recdf, tax_year=year,
                     baseline=None, reform=None, assump=None)
    assert not tcio.errmsg
    tcio.init(input_data=recdf, tax_year=year,
              baseline=None, reform=None, assump=None,
              growdiff_growmodel=None,
              aging_input_data=False,
              exact_calculations=False)
    assert not tcio.errmsg
    varset = tcio.custom_dump_variables(dumpvar_str)
    assert isinstance(varset, set)
    valid = len(tcio.errmsg) == 0
    assert valid == str_valid
    if valid:
        assert len(varset) == num_vars


def test_output_options(rawinputfile, reformfile1, assumpfile1):
    """
    Test TaxCalcIO output_ceeu & output_dump options when writing_output_file.
    """
    taxyear = 2021
    tcio = TaxCalcIO(input_data=rawinputfile.name,
                     tax_year=taxyear,
                     baseline=None,
                     reform=reformfile1.name,
                     assump=assumpfile1.name)
    assert not tcio.errmsg
    tcio.init(input_data=rawinputfile.name,
              tax_year=taxyear,
              baseline=None,
              reform=reformfile1.name,
              assump=assumpfile1.name,
              growdiff_growmodel=None,
              aging_input_data=False,
              exact_calculations=False)
    assert not tcio.errmsg
    outfilepath = tcio.output_filepath()
    # --ceeu output and standard output
    try:
        tcio.analyze(writing_output_file=True, output_ceeu=True)
    except Exception:  # pylint: disable=broad-except
        if os.path.isfile(outfilepath):
            try:
                os.remove(outfilepath)
            except OSError:
                pass  # sometimes we can't remove a generated temporary file
        assert 'TaxCalcIO.analyze(ceeu)_ok' == 'no'
    # --dump output with full dump
    try:
        tcio.analyze(writing_output_file=True, output_dump=True)
    except Exception:  # pylint: disable=broad-except
        if os.path.isfile(outfilepath):
            try:
                os.remove(outfilepath)
            except OSError:
                pass  # sometimes we can't remove a generated temporary file
        assert 'TaxCalcIO.analyze(dump)_ok' == 'no'
    # --dump output with partial dump
    try:
        tcio.analyze(writing_output_file=True,
                     dump_varset=set(['combined']),
                     output_dump=True)
    except Exception:  # pylint: disable=broad-except
        if os.path.isfile(outfilepath):
            try:
                os.remove(outfilepath)
            except OSError:
                pass  # sometimes we can't remove a generated temporary file
        assert 'TaxCalcIO.analyze(dump)_ok' == 'no'
    # if tries were successful, remove doc file and output file
    docfilepath = outfilepath.replace('.csv', '-doc.text')
    if os.path.isfile(docfilepath):
        os.remove(docfilepath)
    if os.path.isfile(outfilepath):
        os.remove(outfilepath)


def test_write_doc_file(rawinputfile, reformfile1, assumpfile1):
    """
    Test write_doc_file with compound reform.
    """
    taxyear = 2021
    compound_reform = '{}+{}'.format(reformfile1.name, reformfile1.name)
    tcio = TaxCalcIO(input_data=rawinputfile.name,
                     tax_year=taxyear,
                     baseline=None,
                     reform=compound_reform,
                     assump=assumpfile1.name)
    assert not tcio.errmsg
    tcio.init(input_data=rawinputfile.name,
              tax_year=taxyear,
              baseline=None,
              reform=compound_reform,
              assump=assumpfile1.name,
              growdiff_growmodel=None,
              aging_input_data=False,
              exact_calculations=False)
    assert not tcio.errmsg
    tcio.write_doc_file()
    outfilepath = tcio.output_filepath()
    docfilepath = outfilepath.replace('.csv', '-doc.text')
    if os.path.isfile(docfilepath):
        os.remove(docfilepath)


def test_sqldb_option(rawinputfile, reformfile1, assumpfile1):
    """
    Test TaxCalcIO output_sqldb option when not writing_output_file.
    """
    taxyear = 2021
    tcio = TaxCalcIO(input_data=rawinputfile.name,
                     tax_year=taxyear,
                     baseline=None,
                     reform=reformfile1.name,
                     assump=assumpfile1.name)
    assert not tcio.errmsg
    tcio.init(input_data=rawinputfile.name,
              tax_year=taxyear,
              baseline=None,
              reform=reformfile1.name,
              assump=assumpfile1.name,
              growdiff_growmodel=None,
              aging_input_data=False,
              exact_calculations=False)
    assert not tcio.errmsg
    outfilepath = tcio.output_filepath()
    dbfilepath = outfilepath.replace('.csv', '.db')
    # --sqldb output
    try:
        tcio.analyze(writing_output_file=False, output_sqldb=True)
    except Exception:  # pylint: disable=broad-except
        if os.path.isfile(dbfilepath):
            try:
                os.remove(dbfilepath)
            except OSError:
                pass  # sometimes we can't remove a generated temporary file
        assert 'TaxCalcIO.analyze(sqldb)_ok' == 'no'
    # if try was successful, remove the db file
    if os.path.isfile(dbfilepath):
        os.remove(dbfilepath)


def test_no_tables_or_graphs(reformfile1):
    """
    Test TaxCalcIO with output_tables=True and output_graphs=True but
    INPUT has zero weights.
    """
    # create input sample that cannot output tables or graphs
    nobs = 10
    idict = dict()
    idict['RECID'] = [i for i in range(1, nobs + 1)]
    idict['MARS'] = [2 for i in range(1, nobs + 1)]
    idict['s006'] = [0.0 for i in range(1, nobs + 1)]
    idict['e00300'] = [10000 * i for i in range(1, nobs + 1)]
    idict['expanded_income'] = idict['e00300']
    idf = pd.DataFrame(idict, columns=list(idict))
    # create and initialize TaxCalcIO object
    tcio = TaxCalcIO(input_data=idf,
                     tax_year=2020,
                     baseline=None,
                     reform=reformfile1.name,
                     assump=None)
    assert not tcio.errmsg
    tcio.init(input_data=idf,
              tax_year=2020,
              baseline=None,
              reform=reformfile1.name,
              assump=None,
              growdiff_growmodel=None,
              aging_input_data=False,
              exact_calculations=False)
    assert not tcio.errmsg
    # create TaxCalcIO tables file
    tcio.analyze(writing_output_file=False,
                 output_tables=True,
                 output_graphs=True)
    # delete tables and graph files
    output_filename = tcio.output_filepath()
    fname = output_filename.replace('.csv', '-tab.text')
    if os.path.isfile(fname):
        os.remove(fname)
    fname = output_filename.replace('.csv', '-atr.html')
    if os.path.isfile(fname):
        os.remove(fname)
    fname = output_filename.replace('.csv', '-mtr.html')
    if os.path.isfile(fname):
        os.remove(fname)
    fname = output_filename.replace('.csv', '-pch.html')
    if os.path.isfile(fname):
        os.remove(fname)


def test_tables(reformfile1):
    """
    Test TaxCalcIO with output_tables=True and with positive weights.
    """
    # create tabable input
    nobs = 100
    idict = dict()
    idict['RECID'] = [i for i in range(1, nobs + 1)]
    idict['MARS'] = [2 for i in range(1, nobs + 1)]
    idict['s006'] = [10.0 for i in range(1, nobs + 1)]
    idict['e00300'] = [10000 * i for i in range(1, nobs + 1)]
    idict['expanded_income'] = idict['e00300']
    idf = pd.DataFrame(idict, columns=list(idict))
    # create and initialize TaxCalcIO object
    tcio = TaxCalcIO(input_data=idf,
                     tax_year=2020,
                     baseline=None,
                     reform=reformfile1.name,
                     assump=None)
    assert not tcio.errmsg
    tcio.init(input_data=idf,
              tax_year=2020,
              baseline=None,
              reform=reformfile1.name,
              assump=None,
              growdiff_growmodel=None,
              aging_input_data=False,
              exact_calculations=False)
    assert not tcio.errmsg
    # create TaxCalcIO tables file
    tcio.analyze(writing_output_file=False, output_tables=True)
    # delete tables file
    output_filename = tcio.output_filepath()
    fname = output_filename.replace('.csv', '-tab.text')
    if os.path.isfile(fname):
        os.remove(fname)


def test_graphs(reformfile1):
    """
    Test TaxCalcIO with output_graphs=True.
    """
    # create graphable input
    nobs = 100
    idict = dict()
    idict['RECID'] = [i for i in range(1, nobs + 1)]
    idict['MARS'] = [2 for i in range(1, nobs + 1)]
    idict['s006'] = [10.0 for i in range(1, nobs + 1)]
    idict['e00300'] = [10000 * i for i in range(1, nobs + 1)]
    idict['expanded_income'] = idict['e00300']
    idf = pd.DataFrame(idict, columns=list(idict))
    # create and initialize TaxCalcIO object
    tcio = TaxCalcIO(input_data=idf,
                     tax_year=2020,
                     baseline=None,
                     reform=reformfile1.name,
                     assump=None)
    assert not tcio.errmsg
    tcio.init(input_data=idf,
              tax_year=2020,
              baseline=None,
              reform=reformfile1.name,
              assump=None,
              growdiff_growmodel=None,
              aging_input_data=False,
              exact_calculations=False)
    assert not tcio.errmsg
    tcio.analyze(writing_output_file=False, output_graphs=True)
    # delete graph files
    output_filename = tcio.output_filepath()
    fname = output_filename.replace('.csv', '-atr.html')
    if os.path.isfile(fname):
        os.remove(fname)
    fname = output_filename.replace('.csv', '-mtr.html')
    if os.path.isfile(fname):
        os.remove(fname)
    fname = output_filename.replace('.csv', '-pch.html')
    if os.path.isfile(fname):
        os.remove(fname)


def test_ceeu_output1(lumpsumreformfile):
    """
    Test TaxCalcIO calculate method with no output writing using ceeu option.
    """
    taxyear = 2020
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    tcio = TaxCalcIO(input_data=recdf,
                     tax_year=taxyear,
                     baseline=None,
                     reform=lumpsumreformfile.name,
                     assump=None)
    assert not tcio.errmsg
    tcio.init(input_data=recdf,
              tax_year=taxyear,
              baseline=None,
              reform=lumpsumreformfile.name,
              assump=None,
              growdiff_growmodel=None,
              aging_input_data=False,
              exact_calculations=False)
    assert not tcio.errmsg
    tcio.analyze(writing_output_file=False, output_ceeu=True)
    assert tcio.tax_year() == taxyear


def test_ceeu_output2():
    """
    Test TaxCalcIO calculate method with no output writing using ceeu option.
    """
    taxyear = 2020
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    tcio = TaxCalcIO(input_data=recdf,
                     tax_year=taxyear,
                     baseline=None,
                     reform=None,
                     assump=None)
    assert not tcio.errmsg
    tcio.init(input_data=recdf,
              tax_year=taxyear,
              baseline=None,
              reform=None,
              assump=None,
              growdiff_growmodel=None,
              aging_input_data=False,
              exact_calculations=False)
    assert not tcio.errmsg
    tcio.analyze(writing_output_file=False, output_ceeu=True)
    assert tcio.tax_year() == taxyear


def test_ceeu_with_behavior(lumpsumreformfile, assumpfile2):
    """
    Test TaxCalcIO.analyze method when assuming behavior & doing ceeu calcs.
    """
    taxyear = 2020
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    tcio = TaxCalcIO(input_data=recdf,
                     tax_year=taxyear,
                     baseline=None,
                     reform=lumpsumreformfile.name,
                     assump=assumpfile2.name)
    assert not tcio.errmsg
    tcio.init(input_data=recdf,
              tax_year=taxyear,
              baseline=None,
              reform=lumpsumreformfile.name,
              assump=assumpfile2.name,
              growdiff_growmodel=None,
              aging_input_data=False,
              exact_calculations=False)
    assert not tcio.errmsg
    tcio.analyze(writing_output_file=False, output_ceeu=True)
    assert tcio.tax_year() == taxyear


@pytest.fixture(scope='module', name='warnreformfile')
def fixture_warnreformfile():
    """
    Temporary reform file with .json extension.
    """
    rfile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    contents = '{"policy": {"_STD_Dep": {"2015": [0]}}}'
    rfile.write(contents)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_analyze_warnings_print(warnreformfile):
    """
    Test TaxCalcIO.analyze method when there is a reform warning.
    """
    taxyear = 2020
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    tcio = TaxCalcIO(input_data=recdf,
                     tax_year=taxyear,
                     baseline=None,
                     reform=warnreformfile.name,
                     assump=None)
    assert not tcio.errmsg
    tcio.init(input_data=recdf,
              tax_year=taxyear,
              baseline=None,
              reform=warnreformfile.name,
              assump=None,
              growdiff_growmodel=None,
              aging_input_data=False,
              exact_calculations=False)
    assert not tcio.errmsg
    tcio.analyze(writing_output_file=False, output_ceeu=False)
    assert tcio.tax_year() == taxyear


@pytest.fixture(scope='module', name='reformfile9')
def fixture_reformfile9():
    """
    Temporary reform file with .json extension.
    """
    rfile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    contents = """
    { "policy": {
        "_SS_Earnings_c": {
          "2014": [300000],
          "2015": [500000],
          "2016": [700000]}
      }
    }
    """
    rfile.write(contents)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='module', name='assumpfile3')
def fixture_assumpfile3():
    """
    Temporary assumption file with .json extension.
    """
    afile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    contents = """
    {
    "consumption": {},
    "behavior": {},
    "growdiff_baseline": {},
    "growdiff_response": {},
    "growmodel": {"_active": {"2019": [true]}}
    }
    """
    afile.write(contents)
    afile.close()
    # must close and then yield for Windows platform
    yield afile
    if os.path.isfile(afile.name):
        try:
            os.remove(afile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_growmodel_analysis(reformfile9, assumpfile3):
    """
    Test TaxCalcIO.growmodel_analysis logic.
    """
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    TaxCalcIO.growmodel_analysis(input_data=recdf,
                                 tax_year=2019,
                                 baseline=None,
                                 reform=reformfile9.name,
                                 assump=assumpfile3.name,
                                 aging_input_data=True,
                                 exact_calculations=False,
                                 writing_output_file=False,
                                 output_tables=False,
                                 output_graphs=False,
                                 output_ceeu=False,
                                 dump_varset=None,
                                 output_dump=False,
                                 output_sqldb=False)
