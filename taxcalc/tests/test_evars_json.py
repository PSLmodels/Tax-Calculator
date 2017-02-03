import os
import pandas
from taxcalc.records import Records
from taxcalc.utils import read_json_from_file


def test_evars_json():
    path = os.path.join(os.path.dirname(__file__), '..', 'evars.json')
    data = read_json_from_file(path)

    # Records - In
    int_read_vars = set(
        [k for k, v in data['in'].items() if v['format'] == 'int']
    )
    float_read_vars = set(
        [k for k, v in data['in'].items() if v['format'] == 'float']
    )
    all_read_vars = int_read_vars | float_read_vars
    required_read_vars = set(
        [k for k, v in data['in'].items() if v.get('required')]
    )

    assert Records.INTEGER_READ_VARS == int_read_vars
    assert Records.MUST_READ_VARS == required_read_vars
    assert Records.USABLE_READ_VARS == all_read_vars

    # Records - Out
    int_calc_vars = set(
        [k for k, v in data['out'].items() if v['format'] == 'int']
    )
    float_calc_vars = set(
        [k for k, v in data['out'].items() if v['format'] == 'float']
    )
    binary_calc_vars = set(
        [k for k, v in data['out'].items() if v['format'] == 'binary']
    )
    all_calc_vars = int_calc_vars | float_calc_vars | binary_calc_vars

    assert Records.INTEGER_CALCULATED_VARS == int_calc_vars
    assert Records.CHANGING_CALCULATED_VARS == float_calc_vars
    assert Records.CALCULATED_VARS == all_calc_vars

    # E_variable_info - Descriptions
    e_var_info_path = os.path.join(
        os.path.dirname(__file__), '..', 'e_variable_info.csv'
    )
    e_var_info = pandas.read_csv(e_var_info_path)

    for k, v in data['in'].items():
        fetched = e_var_info.Definition_2014[(e_var_info.Input_Name == k)]
        info_description = fetched.values[0] if fetched.any() else ''
        assert v['description'] == info_description
        assert v['description'] == info_description

    for k, v in data['out'].items():
        fetched = e_var_info.Definition_2014[(e_var_info.Output_Name == k)]
        info_description = fetched.values[0] if fetched.any() else ''
        assert v['description'] == info_description
