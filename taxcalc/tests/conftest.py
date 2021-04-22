import os
import time
import glob
import numpy
import pandas
import pytest

from pytest_harvest import get_session_results_df


# convert all numpy warnings into errors so they can be detected in tests
numpy.seterr(all='raise')


@pytest.fixture
def skip_jit(monkeypatch):
    monkeypatch.setenv("TESTING", "True")
    yield


@pytest.fixture(scope='session')
def tests_path():
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='session')
def cps_path(tests_path):
    return os.path.join(tests_path, '..', 'cps.csv.gz')


@pytest.fixture(scope='session')
def cps_fullsample(cps_path):
    return pandas.read_csv(cps_path)


@pytest.fixture(scope='session')
def cps_subsample(cps_fullsample):
    # draw smaller cps.csv subsample than in test_cpscsv.py
    return cps_fullsample.sample(frac=0.01, random_state=123456789)


@pytest.fixture(scope='session')
def puf_path(tests_path):
    return os.path.join(tests_path, '..', '..', 'puf.csv')


@pytest.fixture(scope='session')
def puf_fullsample(puf_path):
    return pandas.read_csv(puf_path)


@pytest.fixture(scope='session')
def puf_subsample(puf_fullsample):
    # draw same puf.csv subsample as in test_pufcsv.py
    return puf_fullsample.sample(frac=0.05, random_state=2222)


@pytest.fixture(scope='session', name='test_reforms_init')
def fixture_test_reforms(tests_path):
    """
    Execute logic only once rather than on each pytest-xdist node.
    """
    # pylint: disable=too-many-locals
    num_reforms = 64  # must be same as NUM_REFORMS in test_reforms.py
    handling_logic = ('PYTEST_XDIST_WORKER' not in os.environ or
                      os.environ['PYTEST_XDIST_WORKER'] == 'gw0')
    initfile = os.path.join(tests_path, 'reforms_actual_init')
    actfile_path = os.path.join(tests_path, 'reforms_actual.csv')
    afiles = os.path.join(tests_path, 'reform_actual_*.csv')
    wait_secs = 1
    max_waits = 180
    # test_reforms setup
    if handling_logic:
        # remove reforms_actual.csv file if exists
        if os.path.isfile(actfile_path):
            os.remove(actfile_path)
        # remove all reform_actual_*.csv files
        for afile in glob.glob(afiles):
            os.remove(afile)
        # create reforms_actual_init file
        with open(initfile, 'w') as ifile:
            ifile.write('test_reforms initialization done')
    else:
        num_waits = 0
        while not os.path.isfile(initfile):
            time.sleep(wait_secs)
            num_waits += 1
            assert num_waits <= max_waits
    # yield while tests execute
    yield num_reforms
    # test_reforms teardown
    if handling_logic:
        # wait for all actual results files to be written
        num_waits = 0
        while len(glob.glob(afiles)) != num_reforms:
            time.sleep(wait_secs)
            num_waits += 1
            assert num_waits <= max_waits
        # compare actual and expected results for each test
        # ... read expected results
        efile_path = os.path.join(tests_path, 'reforms_expect.csv')
        with open(efile_path, 'r') as efile:
            expect_lines = efile.readlines()
        # ... compare actual and expected results for each test
        diffs = False
        actfile = open(actfile_path, 'w')
        actfile.write('rid,res1,res2,res3,res4\n')
        idx = 1  # expect_lines list index
        for rnum in range(1, num_reforms + 1):
            afile_path = os.path.join(tests_path,
                                      'reform_actual_{}.csv'.format(rnum))
            with open(afile_path, 'r') as afile:
                actual_lines = afile.readlines()
            os.remove(afile_path)
            actfile.write(actual_lines[1])
            actual = [float(itm) for itm in actual_lines[1].split(',')]
            expect = [float(itm) for itm in expect_lines[idx].split(',')]
            if not numpy.allclose(actual, expect, atol=0.0, rtol=0.0):
                diffs = True
            idx += 1
        actfile.close()
        # remove init file
        os.remove(initfile)
        # remove 'reforms_actual.csv' file if no actual-vs-expect diffs
        if diffs:
            msg = 'ACTUAL AND EXPECTED REFORM RESULTS DIFFER\n'
            msg += '-------------------------------------------------\n'
            msg += '--- ACTUAL RESULTS IN reforms_actual.csv FILE ---\n'
            msg += '--- IF ACTUAL OK, COPY reforms_actual.csv TO  ---\n'
            msg += '---                    reforms_expect.csv     ---\n'
            msg += '---               AND RERUN TEST.             ---\n'
            msg += '-------------------------------------------------\n'
            raise ValueError(msg)
        else:
            os.remove(actfile_path)


def pytest_sessionfinish(session):
    """ Gather all test profiling test results and print to user."""

    tests_path = os.path.abspath(os.path.dirname(__file__))

    new_stats_df = get_session_results_df(session)
    # move test_id from index into unique column
    new_stats_df.reset_index(inplace=True)
    old_stats_df = pandas.read_csv(os.path.join(tests_path, 'test_stats_benchmark.csv'))

    merge_df = new_stats_df.merge(old_stats_df, on=['test_id'], how='left')
    # time diff for new tests is set to 0
    merge_df['time_diff'] = merge_df['duration_ms_x'] - merge_df['duration_ms_y']
    merge_df['time_diff'] = merge_df['time_diff'].fillna(0)

    tol = 1.0 # choose tolerance in seconds
    tol *= 1000

    for ind, row in merge_df.iterrows():
        if row['time_diff'] > tol:
            diff = round(abs(row['time_diff']), 3)
            print(f"{row['test_id']} is slower than the current benchmark by {diff} ms")

    print('\n')

    for ind, row in merge_df.iterrows():
        if row['time_diff'] < (-1 * tol):
            diff = round(abs(row['time_diff']), 3)
            print(f"{row['test_id']} is faster than the current benchmark by {diff} ms")

    # Save new test stats to disk including time diff
    new_stats_df['time_diff'] = merge_df['time_diff'].values
    print(new_stats_df['time_diff'])
    new_stats_df.to_csv(os.path.join(tests_path, 'test_stats_current.csv'))
