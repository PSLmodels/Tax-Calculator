"""
Tests for Tax-Calculator TaxCalcIO class.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_taxcalcio.py
# pylint --disable=locally-disabled test_taxcalcio.py
#
# pylint: disable=too-many-lines

import os
import json
from io import StringIO
from pathlib import Path
import tempfile
import pytest
import pandas as pd
from taxcalc import TaxCalcIO


RAWINPUT = (
    'RECID,MARS\n'
    '    1,   2\n'
    '    2,   1\n'
    '    3,   4\n'
    '    4,   3\n'
)


@pytest.fixture(scope='session', name='reformfile0')
def fixture_reformfile0():
    """
    Specify JSON reform file.
    """
    txt = """
    { "policy": {
        "SS_Earnings_c": {"2016": 300000,
                          "2018": 500000,
                          "2020": 700000}
      }
    }
    """
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as rfile:
        rfile.write(txt + '\n')
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='session', name='assumpfile0')
def fixture_assumpfile0():
    """
    Temporary assumption file with .json extension.
    """
    contents = """
    {
    "consumption": {},
    "growdiff_baseline": {"ABOOK": {"2015": -0.01}},
    "growdiff_response": {}
    }
    """
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as afile:
        afile.write(contents)
    yield afile
    if os.path.isfile(afile.name):
        try:
            os.remove(afile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='session', name='reformfile1')
def fixture_reformfile1():
    """
    Temporary reform file with .json extension.
    """
    contents = """
    {"policy": {
        "AMT_brk1": { // top of first AMT tax bracket by MARS
          "2015": [200000, 200000, 100000, 200000, 200000],
          "2017": [300000, 300000, 150000, 300000, 300000]},
        "EITC_c": { // max EITC amount by number of qualifying kids (0,1,2,3+)
          "2016": [ 900, 5000,  8000,  9000],
          "2019": [1200, 7000, 10000, 12000]},
        "II_em": { // personal exemption amount (see indexing changes below)
          "2016": 6000,
          "2018": 7500,
          "2021": 9000},
        "II_em-indexed": { // personal exemption amount indexing status
          "2016": false, // values in future years are same as this year value
          "2018": true // values in future years indexed with this year as base
          },
        "SS_Earnings_c": { // social security (OASDI) maximum taxable earnings
          "2016": 300000,
          "2018": 500000,
          "2020": 700000},
        "AMT_em-indexed": { // AMT exemption amount indexing status
          "2017": false, // values in future years are same as this year value
          "2020": true // values in future years indexed with this year as base
        }
      }
    }
    """
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as rfile:
        rfile.write(contents)
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='session', name='baselinebad')
def fixture_baselinebad():
    """
    Temporary baseline file with .json extension.
    """
    contents = '{ "policy": {"CTC_c": {"2011": 0.0}}}'
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as rfile:
        rfile.write(contents)
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='session', name='errorreformfile')
def fixture_errorreformfile():
    """
    Temporary reform file with .json extension.
    """
    contents = '{ "policy": {"xxx": {"2015": 0}}}'
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as rfile:
        rfile.write(contents)
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='session', name='ereformfile')
def fixture_ereformfile():
    """
    Temporary reform file with .json extension.
    """
    contents = '{"II_em": {"2022": 1000},}'
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as rfile:
        rfile.write(contents)
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='session', name='errorassumpfile')
def fixture_errorassumpfile():
    """
    Temporary assumption file with .json extension.
    """
    contents = """
    {
    "consumption": {"MPC_e18400": {"2018": -9}},
    "growdiff_baseline": {"ABOOKxx": {"2017": 0.02}},
    "growdiff_response": {"ABOOKxx": {"2017": 0.02}}
    }
    """
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as rfile:
        rfile.write(contents)
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='session', name='assumpfile1')
def fixture_assumpfile1():
    """
    Temporary assumption file with .json extension.
    """
    contents = """
    {
    "consumption": { "MPC_e18400": {"2018": 0.05} },
    "growdiff_baseline": {},
    "growdiff_response": {}
    }
    """
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as afile:
        afile.write(contents)
    yield afile
    if os.path.isfile(afile.name):
        try:
            os.remove(afile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='session', name='lumpsumreformfile')
def fixture_lumpsumreformfile():
    """
    Temporary reform file without .json extension.
    """
    lumpsum_reform_contents = '{"policy": {"LST": {"2013": 200}}}'
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as rfile:
        rfile.write(lumpsum_reform_contents)
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='session', name='assumpfile2')
def fixture_assumpfile2():
    """
    Temporary assumption file with .json extension.
    """
    assump2_contents = """
    {
    "consumption":  {"BEN_snap_value": {"2018": 0.90}},
    "growdiff_baseline": {},
    "growdiff_response": {}
    }
    """
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as afile:
        afile.write(assump2_contents)
    yield afile
    if os.path.isfile(afile.name):
        try:
            os.remove(afile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.mark.parametrize('input_data, baseline, reform, assump, behavior', [
    ('no-dot-csv-filename', 'no-dot-json-filename', 'no-dot-json-filename',
     'no-dot-json-filename', 'no-dot-json-filename'),
    ([], [], [], [], []),
    ('no-exist.csv', 'no-exist.json', 'no-exist.json',
     'no-exist.json', 'no-exist.json'),
    ('cps.csv', 'ereformfile', 'ereformfile',
     'no-exist.json', 'no-exist.json')
])
def test_ctor_errors(input_data, baseline, reform, assump, behavior):
    """
    Ensure error messages are generated by TaxCalcIO.__init__.
    """
    tcio = TaxCalcIO(input_data=input_data, tax_year=2013,
                     baseline=baseline, reform=reform,
                     assump=assump, behavior=behavior)
    assert tcio.errmsg


@pytest.mark.parametrize('input_data', [
    ('puf.csv'),
    (os.path.join('no-such-directory', 'puf.csv')),
])
def test_ctor_puf_input_data_error(input_data):
    """
    Ensure TaxCalcIO.__init__ rejects INPUT file name ending in puf.csv.
    """
    tcio = TaxCalcIO(input_data=input_data, tax_year=2025,
                     baseline=None, reform=None,
                     assump=None, behavior=None)
    assert 'puf.csv is not supported' in tcio.errmsg
    assert 'INPUT file could not be found' not in tcio.errmsg


def test_ctor_cps_input_data_detection(tmp_path):
    """
    Ensure only INPUT of exactly cps.csv uses the packaged CPS data, and
    that a user file whose name merely ends in cps.csv is read as raw data.
    """
    # INPUT of exactly cps.csv implies packaged CPS input data
    tcio = TaxCalcIO(input_data='cps.csv', tax_year=2020,
                     baseline=None, reform=None,
                     assump=None, behavior=None)
    assert not tcio.errmsg
    assert tcio.cps_input_data
    # nonexistent INPUT file ending in cps.csv generates an error
    missing = str(tmp_path / 'no-such-directory' / 'mycps.csv')
    tcio = TaxCalcIO(input_data=missing, tax_year=2020,
                     baseline=None, reform=None,
                     assump=None, behavior=None)
    assert 'INPUT file could not be found' in tcio.errmsg
    assert not tcio.cps_input_data
    # existing INPUT file ending in cps.csv is read as raw input data
    userfile = tmp_path / 'mycps.csv'
    userfile.write_text(RAWINPUT, encoding='utf-8')
    tcio = TaxCalcIO(input_data=str(userfile), tax_year=2020,
                     baseline=None, reform=None,
                     assump=None, behavior=None)
    assert not tcio.errmsg
    assert not tcio.cps_input_data
    tcio.init(input_data=str(userfile), tax_year=2020,
              baseline=None, reform=None,
              assump=None, behavior=None,
              exact_calculations=False)
    assert not tcio.errmsg
    assert not tcio.aging_input_data
    assert tcio.calc_ref.array_len == 4
    assert tcio.calc_bas.array_len == 4


@pytest.fixture(name='tmdfolder')
def fixture_tmdfolder(tmp_path, monkeypatch):
    """
    Folder containing fake TMD files (with national weights for 2022-2026
    and nm area weights for 2022-2024) that is also the current directory.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv('TMD_AREA', raising=False)
    (tmp_path / 'tmd.csv').write_text(RAWINPUT, encoding='utf-8')
    gfpath = Path(__file__).resolve().parents[1] / 'growfactors.csv'
    (tmp_path / 'tmd_growfactors.csv').write_text(
        gfpath.read_text(encoding='utf-8'), encoding='utf-8'
    )
    for fname, last_year in [('tmd_weights.csv.gz', 2026),
                             ('nm_tmd_weights.csv.gz', 2024)]:
        wdf = pd.DataFrame(
            {f'WT{year}': [100] * 4 for year in range(2022, last_year + 1)}
        )
        wdf.to_csv(tmp_path / fname, index=False)
    return tmp_path


def _tmd_tcio(tmdfolder, tax_year):
    """
    Return TaxCalcIO object constructed using TMD input data in tmdfolder.
    """
    return TaxCalcIO(input_data=str(tmdfolder / 'tmd.csv'),
                     tax_year=tax_year,
                     baseline=None, reform=None,
                     assump=None, behavior=None)


def _init_tmd_tcio(tcio, tmdfolder, tax_year):
    """
    Call init method of TaxCalcIO object that uses TMD input data.
    """
    tcio.init(input_data=str(tmdfolder / 'tmd.csv'), tax_year=tax_year,
              baseline=None, reform=None,
              assump=None, behavior=None,
              exact_calculations=False)


@pytest.mark.parametrize('area, last_year, stem', [
    (None, 2026, 'tmd'),
    ('nm', 2024, 'tmd_nm'),
])
def test_tmd_weights_last_year(tmdfolder, monkeypatch,
                               area, last_year, stem):
    """
    Ensure TMD TAXYEAR must not be after the last year in the weights file
    nor before the TMD data year.
    """
    if area is not None:
        monkeypatch.setenv('TMD_AREA', area)
    tcio = _tmd_tcio(tmdfolder, last_year)
    assert not tcio.errmsg
    assert tcio.tmd_input_data
    assert tcio.tmd_weights_last_year == last_year
    assert tcio.output_filename.startswith(f'{stem}-{last_year % 100}-')
    for year, msg in [(last_year + 1, f'is greater than {last_year}'),
                      (2021, 'is less than 2022')]:
        tcio = _tmd_tcio(tmdfolder, year)
        assert not tcio.errmsg
        _init_tmd_tcio(tcio, tmdfolder, year)
        assert msg in tcio.errmsg


@pytest.mark.parametrize('area', ['', 'NM', 'nm-01', '../nm', 'nm 01'])
def test_tmd_area_invalid(tmdfolder, monkeypatch, area):
    """
    Ensure TMD_AREA value must be lowercase letters and digits.
    """
    monkeypatch.setenv('TMD_AREA', area)
    tcio = _tmd_tcio(tmdfolder, 2024)
    assert 'is not a non-empty string of lowercase' in tcio.errmsg
    assert tcio.tmd_weights is None


def test_tmd_area_missing_weights_file(tmdfolder, monkeypatch):
    """
    Ensure missing area weights file generates an error.
    """
    monkeypatch.setenv('TMD_AREA', 'nm01')
    tcio = _tmd_tcio(tmdfolder, 2024)
    assert 'nm01_tmd_weights.csv.gz could not be found' in tcio.errmsg


def test_tmd_weights_file_without_wt_columns(tmdfolder):
    """
    Ensure weights file containing no WTyyyy columns generates an error.
    """
    pd.DataFrame({'RECID': [1, 2, 3, 4]}).to_csv(
        tmdfolder / 'tmd_weights.csv.gz', index=False
    )
    tcio = _tmd_tcio(tmdfolder, 2024)
    assert 'contains no WTyyyy columns' in tcio.errmsg


@pytest.mark.parametrize('input_data', ['cps.csv', 'dataframe'])
def test_tmd_area_with_non_tmd_input(monkeypatch, input_data):
    """
    Ensure TMD_AREA is rejected when INPUT is not TMD data.
    """
    monkeypatch.setenv('TMD_AREA', 'nm')
    if input_data == 'dataframe':
        input_data = pd.read_csv(StringIO(RAWINPUT))
    tcio = TaxCalcIO(input_data=input_data, tax_year=2024,
                     baseline=None, reform=None,
                     assump=None, behavior=None)
    assert 'TMD_AREA environment variable is set' in tcio.errmsg


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
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    # pylint: disable=too-many-locals,too-many-branches
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
    behavior = None
    # call TaxCalcIO constructor
    tcio = TaxCalcIO(input_data=recdf,
                     tax_year=year,
                     baseline=baseline,
                     reform=reform,
                     assump=assump,
                     behavior=behavior)
    assert not tcio.errmsg
    # test TaxCalcIO.init method
    tcio.init(input_data=recdf, tax_year=year,
              baseline=baseline, reform=reform,
              assump=assump, behavior=behavior,
              exact_calculations=True)
    assert tcio.errmsg


@pytest.mark.parametrize('reform, growdiff_response, error_expected', [
    (None, '{}', False),
    (None, '{"ABOOK": {"2020": 0.0}}', False),
    (None, '{"ABOOK": {"2020": 0.01}}', True),
    ('reformfile0', '{"ABOOK": {"2020": 0.01}}', False),
])
def test_init_growdiff_response_without_reform(
        tmp_path, reformfile0, reform, growdiff_response, error_expected,
):
    """
    Ensure TaxCalcIO.init method generates an error message when ASSUMP
    file specifies a nonzero growdiff_response but there is no REFORM.
    """
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    assumpfile = tmp_path / 'assump.json'
    assumpfile.write_text(
        '{"consumption": {}, "growdiff_baseline": {}, '
        f'"growdiff_response": {growdiff_response}}}\n',
        encoding='utf-8',
    )
    reform = reformfile0.name if reform else None
    tcio = TaxCalcIO(input_data='cps.csv', tax_year=2020,
                     baseline=None, reform=reform,
                     assump=str(assumpfile), behavior=None)
    assert not tcio.errmsg
    tcio.init(input_data='cps.csv', tax_year=2020,
              baseline=None, reform=reform,
              assump=str(assumpfile), behavior=None,
              exact_calculations=False)
    msg = 'ASSUMP file has growdiff_response but there is no REFORM'
    assert (msg in tcio.errmsg) == error_expected
    if not error_expected:
        assert not tcio.errmsg


def test_ctor_init_with_cps_files():
    """
    Test use of CPS input files.
    """
    # specify valid tax_year for cps.csv input data
    txyr = 2020
    tcio = TaxCalcIO('cps.csv', txyr,
                     None, None, None, None)
    assert tcio.output_filename == 'cps-20-#-#-#-#.xxx'
    tcio.init('cps.csv', txyr,
              None, None, None, None,
              exact_calculations=False)
    assert not tcio.errmsg
    assert tcio.tax_year() == txyr
    # test advance_to_year method
    tcio.silent = False
    tcio.advance_to_year(txyr + 1)
    assert tcio.tax_year() == txyr + 1
    assert tcio.output_filename == 'cps-21-#-#-#-#.xxx'
    # specify runid, which affects only the output file name that is
    # set in the TaxCalcIO constructor, so no need to call init method
    tcio = TaxCalcIO('cps.csv', txyr,
                     None, None, None, None,
                     runid=99)
    assert not tcio.errmsg
    assert tcio.output_filename == 'run99-20.xxx'
    # specify invalid tax_year for cps.csv input data
    txyr = 2013
    tcio = TaxCalcIO('cps.csv', txyr,
                     None, None, None, None)
    tcio.init('cps.csv', txyr,
              None, None, None, None,
              exact_calculations=False)
    assert tcio.errmsg


@pytest.mark.param_var_count
@pytest.mark.parametrize('dumpvar_str, str_valid, num_vars', [
    ("""
    MARS;iitax	payrolltax|combined,
    c00100
    surtax
    """, True, 6),  # these 6 variables minus MARS plus RECID

    ('ALL', True, 204),
    # 204 =
    # all 209 vars in records_variables.json (see test_records.py)
    # minus 2 TaxCalcIO.UNUSED_DUMPVARS (see taxcalcio.py)
    # minus 5 TaxCalcIO.BASE_DUMPVARS omitting RECID (see taxcalcio.py)
    # plus 2 TaxCalcIO.MTR_DUMPVARS (see taxcalcio.py)

    ("""
    MARS;iitax	payrolltax|kombined,c00100
    surtax
    RECID
    FLPDYR
    """, False, 0)
])
def test_dump_variables(dumpvar_str, str_valid, num_vars):
    """
    Test TaxCalcIO dump_variables method.
    """
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    year = 2018
    tcio = TaxCalcIO(input_data=recdf, tax_year=year,
                     baseline=None, reform=None,
                     assump=None, behavior=None)
    assert not tcio.errmsg
    tcio.init(input_data=recdf, tax_year=year,
              baseline=None, reform=None, assump=None, behavior=None,
              exact_calculations=False)
    assert not tcio.errmsg
    varlist = tcio.dump_variables(dumpvar_str)
    assert isinstance(varlist, list)
    valid = len(tcio.errmsg) == 0
    assert valid == str_valid
    if valid:
        assert len(varlist) == num_vars


def test_dump_variables_preserves_errmsg():
    """
    Ensure TaxCalcIO dump_variables method appends to, rather than resets,
    any existing error message, and that an existing error message does not
    cause valid dump variables to be treated as invalid.
    """
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    tcio = TaxCalcIO(input_data=recdf, tax_year=2018,
                     baseline=None, reform=None,
                     assump=None, behavior=None)
    assert not tcio.errmsg
    prior_errmsg = 'ERROR: prior error\n'
    # valid dump variables leave existing error message unchanged
    tcio.errmsg = prior_errmsg
    varlist = tcio.dump_variables('iitax payrolltax c00100')
    assert varlist == ['RECID', 'iitax', 'payrolltax', 'c00100']
    assert tcio.errmsg == prior_errmsg
    # invalid dump variables are appended to existing error message
    varlist = tcio.dump_variables('iitax kombined')
    assert not varlist
    assert tcio.errmsg == (
        prior_errmsg +
        'ERROR: invalid variable name kombined in DUMPVARS file\n'
    )


def test_output_options_min(reformfile1, assumpfile1):
    """
    Test TaxCalcIO output_dump options with minimal dump variables.
    """
    taxyear = 2021
    tcio = TaxCalcIO(input_data=pd.read_csv(StringIO(RAWINPUT)),
                     tax_year=taxyear,
                     baseline=None,
                     reform=reformfile1.name,
                     assump=assumpfile1.name,
                     behavior=None)
    assert not tcio.errmsg
    tcio.init(input_data=pd.read_csv(StringIO(RAWINPUT)),
              tax_year=taxyear,
              baseline=None,
              reform=reformfile1.name,
              assump=assumpfile1.name,
              behavior=None,
              exact_calculations=False)
    assert not tcio.errmsg
    dumppath = tcio.output_filepath().replace('.xxx', '.dumpdb')
    # minimal dump output
    dumpvars = list(TaxCalcIO.MINIMAL_DUMPVARS)
    try:
        tcio.analyze(output_dump=True, dump_varlist=dumpvars)
    except Exception:  # pylint: disable=broad-except
        if os.path.isfile(dumppath):
            try:
                os.remove(dumppath)
            except OSError:
                pass  # sometimes we can't remove a generated temporary file
        assert False, 'TaxCalcIO.analyze(minimal_dump_output) failed'
    if os.path.isfile(dumppath):
        os.remove(dumppath)


def test_output_options_mtr(reformfile1, assumpfile1):
    """
    Test TaxCalcIO output_dump options with mtr_* dump variables.
    """
    taxyear = 2021
    tcio = TaxCalcIO(input_data=pd.read_csv(StringIO(RAWINPUT)),
                     tax_year=taxyear,
                     baseline=None,
                     reform=reformfile1.name,
                     assump=assumpfile1.name,
                     behavior=None)
    assert not tcio.errmsg
    tcio.init(input_data=pd.read_csv(StringIO(RAWINPUT)),
              tax_year=taxyear,
              baseline=None,
              reform=reformfile1.name,
              assump=assumpfile1.name,
              behavior=None,
              exact_calculations=False)
    assert not tcio.errmsg
    dumppath = tcio.output_filepath().replace('.xxx', '.dumpdb')
    # minimal+mtr_* dump output
    dumpvars = list(TaxCalcIO.MINIMAL_DUMPVARS)
    for var in TaxCalcIO.MTR_DUMPVARS:
        dumpvars.append(var)
    try:
        tcio.analyze(output_dump=True, dump_varlist=dumpvars)
    except Exception:  # pylint: disable=broad-except
        if os.path.isfile(dumppath):
            try:
                os.remove(dumppath)
            except OSError:
                pass  # sometimes we can't remove a generated temporary file
        assert False, 'TaxCalcIO.analyze(minimal_dump_output) failed'
    if os.path.isfile(dumppath):
        os.remove(dumppath)


def test_write_policy_param_files(reformfile1):
    """
    Test write_policy_params_files with compound reform.
    """
    taxyear = 2021
    compound_reform = f'{reformfile1.name}+{reformfile1.name}'
    tcio = TaxCalcIO(
        input_data=pd.read_csv(StringIO(RAWINPUT)),
        tax_year=taxyear,
        baseline=compound_reform,
        reform=compound_reform,
        assump=None,
        behavior=None,
    )
    assert not tcio.errmsg
    tcio.init(input_data=pd.read_csv(StringIO(RAWINPUT)),
              tax_year=taxyear,
              baseline=compound_reform,
              reform=compound_reform,
              assump=None,
              behavior=None,
              exact_calculations=False)
    assert not tcio.errmsg
    tcio.write_policy_params_files()
    outfilepath = tcio.output_filepath()
    for ext in ['-params.baseline', '-params.reform']:
        filepath = outfilepath.replace('.xxx', ext)
        if os.path.isfile(filepath):
            os.remove(filepath)


def test_write_json_policy_param_files(reformfile1):
    """
    Test write_policy_params_files with jsonparams=True.
    """
    taxyear = 2021
    tcio = TaxCalcIO(
        input_data=pd.read_csv(StringIO(RAWINPUT)),
        tax_year=taxyear,
        baseline=None,
        reform=reformfile1.name,
        assump=None,
        behavior=None,
    )
    assert not tcio.errmsg
    tcio.init(input_data=pd.read_csv(StringIO(RAWINPUT)),
              tax_year=taxyear,
              baseline=None,
              reform=reformfile1.name,
              assump=None,
              behavior=None,
              exact_calculations=False)
    assert not tcio.errmsg
    tcio.write_policy_params_files(jsonparams=True)
    for ext in ['-params.baseline', '-params.reform']:
        filepath = tcio.output_filename.replace('.xxx', ext)
        assert os.path.isfile(filepath)
        with open(filepath, 'r', encoding='utf-8') as pfile:
            pdict = json.load(pfile)
        # each parameter maps to a dict containing its year and value
        assert isinstance(pdict, dict)
        assert len(pdict) > 0
        for pval in pdict.values():
            assert set(pval.keys()) == {f'{taxyear}'}
        os.remove(filepath)


def test_no_tables_or_graphs(reformfile1):
    """
    Test TaxCalcIO with output_params=True and output_tables=True and
    output_graphs=True but INPUT has zero weights.
    """
    # create input sample that cannot output tables or graphs
    nobs = 10
    idict = {}
    idict['RECID'] = list(range(1, nobs + 1))
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
                     assump=None,
                     behavior=None)
    assert not tcio.errmsg
    tcio.init(input_data=idf,
              tax_year=2020,
              baseline=None,
              reform=reformfile1.name,
              assump=None,
              behavior=None,
              exact_calculations=False)
    assert not tcio.errmsg
    # create several TaxCalcIO output files
    tcio.analyze(output_params=True,
                 output_tables=True,
                 output_graphs=True)
    # delete tables and graph files
    tcio.delete_output_files()


def test_tables(reformfile1):
    """
    Test TaxCalcIO with output_tables=True and with positive weights.
    """
    # create tabable input
    nobs = 100
    idict = {}
    idict['RECID'] = list(range(1, nobs + 1))
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
                     assump=None,
                     behavior=None)
    assert not tcio.errmsg
    tcio.init(input_data=idf,
              tax_year=2020,
              baseline=None,
              reform=reformfile1.name,
              assump=None,
              behavior=None,
              exact_calculations=False)
    assert not tcio.errmsg
    # create TaxCalcIO tables file
    tcio.analyze(output_tables=True)
    tcio.delete_output_files()


def test_output_filename_containing_xxx(tmp_path, monkeypatch):
    """
    Ensure output file names are correct when the INPUT file name
    contains the .xxx string that ends the TaxCalcIO.output_filename.
    """
    monkeypatch.chdir(tmp_path)
    infile = tmp_path / 'data.xxx.csv'
    infile.write_text(RAWINPUT, encoding='utf-8')
    tcio = TaxCalcIO(input_data=str(infile), tax_year=2020,
                     baseline=None, reform=None,
                     assump=None, behavior=None)
    assert not tcio.errmsg
    assert tcio.output_filename == 'data.xxx-20-#-#-#-#.xxx'
    tcio.init(input_data=str(infile), tax_year=2020,
              baseline=None, reform=None,
              assump=None, behavior=None,
              exact_calculations=False)
    assert not tcio.errmsg
    tcio.analyze(output_params=True, output_tables=True)
    expected = {
        'data.xxx-20-#-#-#-#-params.baseline',
        'data.xxx-20-#-#-#-#-params.reform',
        'data.xxx-20-#-#-#-#.tables',
    }
    written = {path.name for path in tmp_path.iterdir()} - {infile.name}
    assert written == expected
    tcio.delete_output_files()
    written = {path.name for path in tmp_path.iterdir()} - {infile.name}
    assert not written


def test_graphs(reformfile1):
    """
    Test TaxCalcIO with output_graphs=True.
    """
    # create graphable input
    nobs = 100
    idict = {}
    idict['RECID'] = list(range(1, nobs + 1))
    idict['MARS'] = [2 for i in range(1, nobs + 1)]
    idict['XTOT'] = [3 for i in range(1, nobs + 1)]
    idict['s006'] = [10.0 for i in range(1, nobs + 1)]
    idict['e00300'] = [10000 * i for i in range(1, nobs + 1)]
    idict['expanded_income'] = idict['e00300']
    idf = pd.DataFrame(idict, columns=list(idict))
    # create and initialize TaxCalcIO object
    tcio = TaxCalcIO(input_data=idf,
                     tax_year=2020,
                     baseline=None,
                     reform=reformfile1.name,
                     assump=None,
                     behavior=None)
    assert not tcio.errmsg
    tcio.init(input_data=idf,
              tax_year=2020,
              baseline=None,
              reform=reformfile1.name,
              assump=None,
              behavior=None,
              exact_calculations=False)
    assert not tcio.errmsg
    tcio.analyze(output_graphs=True)
    # delete graph files
    tcio.delete_output_files()


@pytest.fixture(scope='session', name='warnreformfile')
def fixture_warnreformfile():
    """
    Temporary reform file with .json extension.
    """
    contents = '{"policy": {"STD_Dep": {"2015": 0}}}'
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as rfile:
        rfile.write(contents)
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
                     assump=None,
                     behavior=None)
    assert not tcio.errmsg
    tcio.init(input_data=recdf,
              tax_year=taxyear,
              baseline=None,
              reform=warnreformfile.name,
              assump=None,
              behavior=None,
              exact_calculations=False)
    assert not tcio.errmsg
    tcio.analyze()
    assert tcio.tax_year() == taxyear


@pytest.fixture(scope='session', name='reformfile9')
def fixture_reformfile9():
    """
    Temporary reform file with .json extension.
    """
    contents = """
    { "policy": {
        "SS_Earnings_c": {
          "2014": 300000,
          "2015": 500000,
          "2016": 700000}
      }
    }
    """
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as rfile:
        rfile.write(contents)
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.fixture(scope='session', name='regression_reform_file')
def fixture_regression_reform_file():
    """
    Temporary reform file with .json extension.

    Example causing regression reported in issue:
    https://github.com/PSLmodels/Tax-Calculator/issues/2622
    """
    contents = '{ "policy": {"AMEDT_rt": {"2021": 1.8}}}'
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as rfile:
        rfile.write(contents)
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_error_message_parsed_correctly(regression_reform_file):
    """Test docstring"""
    tcio = TaxCalcIO(input_data=pd.read_csv(StringIO(RAWINPUT)),
                     tax_year=2022,
                     baseline=regression_reform_file.name,
                     reform=regression_reform_file.name,
                     assump=None,
                     behavior=None)
    assert not tcio.errmsg

    tcio.init(input_data=pd.read_csv(StringIO(RAWINPUT)),
              tax_year=2022,
              baseline=regression_reform_file.name,
              reform=regression_reform_file.name,
              assump=None,
              behavior=None,
              exact_calculations=False)
    assert isinstance(tcio.errmsg, str) and tcio.errmsg
    exp_errmsg = (
        'AMEDT_rt[year=2021] 1.8 > max 1\n'
        'AMEDT_rt[year=2021] 1.8 > max 1\n'
    )
    assert tcio.errmsg == exp_errmsg


@pytest.fixture(scope='session', name='behvfile0')
def fixture_behvfile0():
    """
    Temporary behavior file with .json extension.
    """
    contents = """
    {
    "sub": 0,
    "inc": 0,
    "cg": 0,
    "extra_key": 0
    }
    """
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as bfile:
        bfile.write(contents)
    yield bfile
    if os.path.isfile(bfile.name):
        try:
            os.remove(bfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_init_behavior0_errors(behvfile0):
    """
    Check behavior error messages generated correctly by TaxCalcIO.init method.
    """
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    behv_fname = behvfile0.name
    tcio = TaxCalcIO(input_data=recdf, tax_year=2024, baseline=None,
                     reform=None, assump=None, behavior=behv_fname)
    assert not tcio.errmsg
    tcio.init(input_data=recdf, tax_year=2024, baseline=None, reform=None,
              assump=None, behavior=behv_fname, exact_calculations=True)
    assert 'extra or missing parameters' in tcio.errmsg


@pytest.fixture(scope='session', name='behvfile0m')
def fixture_behvfile0m():
    """
    Temporary behavior file, with .json extension, that omits the
    esf parameter.
    """
    contents = """
    {
    "sub": 0,
    "inc": 0,
    "cg": 0
    }
    """
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as bfile:
        bfile.write(contents)
    yield bfile
    if os.path.isfile(bfile.name):
        try:
            os.remove(bfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_init_behavior0m_errors(behvfile0m):
    """
    Check that a behavior file omitting the esf parameter is rejected by
    the TaxCalcIO.init method.
    """
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    behv_fname = behvfile0m.name
    tcio = TaxCalcIO(input_data=recdf, tax_year=2024, baseline=None,
                     reform=None, assump=None, behavior=behv_fname)
    assert not tcio.errmsg
    tcio.init(input_data=recdf, tax_year=2024, baseline=None, reform=None,
              assump=None, behavior=behv_fname, exact_calculations=True)
    assert 'extra or missing parameters' in tcio.errmsg


@pytest.fixture(scope='session', name='behvfile1')
def fixture_behvfile1():
    """
    Temporary behavior file with .json extension.
    """
    contents = """
    {
    "esf": 1.5,
    "sub": -0.3,
    "inc": 0.5,
    "cg": 1
    }
    """
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as bfile:
        bfile.write(contents)
    yield bfile
    if os.path.isfile(bfile.name):
        try:
            os.remove(bfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_init_behavior1_errors(behvfile1):
    """
    Check behavior error messages generated correctly by TaxCalcIO.init method.
    """
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    behv_fname = behvfile1.name
    tcio = TaxCalcIO(input_data=recdf, tax_year=2024, baseline=None,
                     reform=None, assump=None, behavior=behv_fname)
    assert not tcio.errmsg
    tcio.init(input_data=recdf, tax_year=2024, baseline=None, reform=None,
              assump=None, behavior=behv_fname, exact_calculations=True)
    assert '"esf" outside [0,1] range' in tcio.errmsg
    assert 'negative "sub" elasticity' in tcio.errmsg
    assert 'positive "inc" elasticity' in tcio.errmsg
    assert 'positive "cg" elasticity' in tcio.errmsg


def test_init_behavior_nonnumeric_errors(tmp_path):
    """
    Check TaxCalcIO.init method generates error messages rather than
    raising an exception when BEHAVIOR file contains non-numeric values.
    """
    behvfile = tmp_path / 'behv.json'
    behvfile.write_text(
        '{"esf": "0.5", "sub": true, "inc": null, "cg": 0}\n',
        encoding='utf-8',
    )
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    tcio = TaxCalcIO(input_data=recdf, tax_year=2024, baseline=None,
                     reform=None, assump=None, behavior=str(behvfile))
    assert not tcio.errmsg
    tcio.init(input_data=recdf, tax_year=2024, baseline=None, reform=None,
              assump=None, behavior=str(behvfile), exact_calculations=True)
    assert 'non-numeric "esf" elasticity' in tcio.errmsg
    assert 'non-numeric "sub" elasticity' in tcio.errmsg
    assert 'non-numeric "inc" elasticity' in tcio.errmsg
    assert 'non-numeric "cg" elasticity' not in tcio.errmsg


@pytest.fixture(scope='session', name='badjsonfile')
def fixture_badjsonfile():
    """
    Temporary file, with .json extension, that contains invalid JSON.
    """
    contents = """
    {
    "esf": 0,
    "sub": 0,,
    "inc": 0,
    "cg": 0
    }
    """
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as jfile:
        jfile.write(contents)
    yield jfile
    if os.path.isfile(jfile.name):
        try:
            os.remove(jfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.mark.parametrize('label', ['BASELINE', 'REFORM'])
def test_ctor_policy_file_invalid_json(badjsonfile, label):
    """
    Check TaxCalcIO constructor generates error message when BASELINE or
    REFORM file contains invalid JSON.
    """
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    json_fname = badjsonfile.name
    tcio = TaxCalcIO(
        input_data=recdf, tax_year=2024,
        baseline=json_fname if label == 'BASELINE' else None,
        reform=json_fname if label == 'REFORM' else None,
        assump=None, behavior=None,
    )
    exp_msg = f'ERROR: {label} file {json_fname} contains invalid JSON\n'
    assert exp_msg in tcio.errmsg


def test_init_behavior_file_invalid_json(badjsonfile):
    """
    Check TaxCalcIO.init method generates error message when BEHAVIOR file
    contains invalid JSON.
    """
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])
    behv_fname = badjsonfile.name
    tcio = TaxCalcIO(input_data=recdf, tax_year=2024, baseline=None,
                     reform=None, assump=None, behavior=behv_fname)
    assert not tcio.errmsg
    tcio.init(input_data=recdf, tax_year=2024, baseline=None, reform=None,
              assump=None, behavior=behv_fname, exact_calculations=True)
    exp_msg = f'ERROR: BEHAVIOR file {behv_fname} contains invalid JSON\n'
    assert exp_msg in tcio.errmsg
    assert tcio.behvdict is None


@pytest.fixture(scope='session', name='behvfile2')
def fixture_behvfile2():
    """
    Temporary behavior file with .json extension.
    """
    contents = """
    {
    "esf": 0.0,
    "sub": 0.25,
    "inc": 0.0,
    "cg": 0.0
    }
    """
    with tempfile.NamedTemporaryFile(
            suffix='.json', mode='a', delete=False
    ) as bfile:
        bfile.write(contents)
    yield bfile
    if os.path.isfile(bfile.name):
        try:
            os.remove(bfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_tc_analyze_with_behavior(reformfile1, behvfile2):
    """
    Test TaxCalcIO.analyze method when assuming behavioral responses to reform.
    """
    tcio = TaxCalcIO(
        'cps.csv', 2020, baseline=None, reform=reformfile1.name,
        assump=None, behavior=behvfile2.name,
        runid=11,
    )
    tcio.init(
        'cps.csv', 2020, baseline=None, reform=reformfile1.name,
        assump=None, behavior=behvfile2.name,
        exact_calculations=True,
    )
    assert not tcio.errmsg
    assert tcio.tax_year() == 2020
    tcio.analyze(output_tables=True)
    assert tcio.tax_year() == 2020
    table_path = Path('run11-20.tables')
    table_path.unlink(missing_ok=True)
