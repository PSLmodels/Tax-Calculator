import pytest
from taxcalc.filings.us_forms.read_funcs import *


@pytest.mark.parametrize('func, input, expected', [
    # US1040 - MARS
    (mars, {'line1': ''}, None),
    (mars, {'line1': 'Checked'}, {'MARS': 1}),
    (mars, {'line2': 'X'}, {'MARS': 2}),
    (mars, {'line3': 'Foo'}, {'MARS': 3}),
    (mars, {'line4': 'Bar'}, {'MARS': 4}),
    (mars, {'line5': '47'}, {'MARS': 5}),

    # US1040 - DSI
    (dsi, {'line6a': 'X'}, {'DSI': 0}),
    (dsi, {'line6a': ''}, {'DSI': 1}),

    # US1040 - e01100
    (e01100, {'line13': '110', 'line13_check': ''}, None),
    (e01100, {'line13': '110', 'line13_check': 'X'}, {'e01100': '110'}),

    # US1040 - blind
    (blind_head, {'line39a_blind': ''}, {'blind_head': 0}),
    (blind_head, {'line39a_blind': 'X'}, {'blind_head': 1}),
    (blind_spouse, {'line39a_blind_spouse': ''}, {'blind_spouse': 0}),
    (blind_spouse, {'line39a_blind_spouse': 'Foo'}, {'blind_spouse': 1}),

    # US1040 - MIDR
    (midr, {'line39b': ''}, {'MIDR': 0}),
    (midr, {'line39b': 'X'}, {'MIDR': 1}),

    # US1040 - e07600 - 2013
    (e07600_2013,
        {'line53': '7600', 'line53a': '', 'line53b': '', 'line53c': ''},
        None),
    (e07600_2013,
        {'line53': '7600', 'line53a': 'X', 'line53b': 'X', 'line53c': 'X'},
        None),
    (e07600_2013,
        {'line53': '7600', 'line53a': 'X', 'line53b': 'X', 'line53c': ''},
        None),
    (e07600_2013,
        {'line53': '7600', 'line53a': '', 'line53b': 'X', 'line53c': 'X'},
        None),
    (e07600_2013,
        {'line53': '7600', 'line53a': '', 'line53b': 'X', 'line53c': ''},
        {'e07600': '7600'}),

    # US1040 - e07600 - 2014 & 2015
    (e07600_2014_2015,
        {'line54': '7600', 'line54a': '', 'line54b': '', 'line54c': ''},
        None),
    (e07600_2014_2015,
        {'line54': '7600', 'line54a': 'X', 'line54b': 'X', 'line54c': 'X'},
        None),
    (e07600_2014_2015,
        {'line54': '7600', 'line54a': 'X', 'line54b': 'X', 'line54c': ''},
        None),
    (e07600_2014_2015,
        {'line54': '7600', 'line54a': '', 'line54b': 'X', 'line54c': 'X'},
        None),
    (e07600_2014_2015,
        {'line54': '7600', 'line54a': '', 'line54b': 'X', 'line54c': ''},
        {'e07600': '7600'}),

    # US1040 - e09800 - 2013
    (e09800_2013, {'line57': '9800', 'line57a': '', 'line57b': ''}, None),
    (e09800_2013, {'line57': '9800', 'line57a': 'X', 'line57b': 'X'}, None),
    (e09800_2013,
        {'line57': '9800', 'line57a': 'X', 'line57b': ''},
        {'e09800': '9800'}),

    # US1040 - e09800 - 2014 & 2015
    (e09800_2014_2015,
        {'line58': '9800', 'line58a': '', 'line58b': ''}, None),
    (e09800_2014_2015,
        {'line58': '9800', 'line58a': 'X', 'line58b': 'X'}, None),
    (e09800_2014_2015,
        {'line58': '9800', 'line58a': 'X', 'line58b': ''},
        {'e09800': '9800'}),

    # US1040SA - e18400
    (e18400, {'line5': '18400', 'line5a': '', 'line5b': ''}, None),
    (e18400, {'line5': '18400', 'line5a': 'X', 'line5b': 'X'}, None),
    (e18400, {'line5': '18400', 'line5a': '', 'line5b': 'X'}, None),
    (e18400,
        {'line5': '18400', 'line5a': 'X', 'line5b': ''},
        {'e18400': '18400'}),

    # US1040SE - p25470
    (p25470, {}, None),
    (p25470, {'line18a': ''}, {'p25470': 0}),
    (p25470, {'line18a': '1', 'line18b': '2', 'line18c': '4'}, {'p25470': 7}),

    # US1040SEIC - EIC
    (eic, {}, {'EIC': 0}),
    (eic,
        {'line2_1': '', 'line2_2': '', 'line2_3': ''},
        {'EIC': 0}),
    (eic,
        {'line2_1': '123', 'line2_2': '', 'line2_3': ''},
        {'EIC': 1}),
    (eic,
        {'line2_1': '123', 'line2_2': '456', 'line2_3': ''},
        {'EIC': 2}),
    (eic,
        {'line2_1': '123', 'line2_2': '456', 'line2_3': '789'},
        {'EIC': 3}),

    # US2441 - f2441
    (f2441, {}, {'f2441': 0}),
    (f2441, {'line2b_1': '', 'line2b_2': ''}, {'f2441': 0}),
    (f2441, {'line2b_1': '123', 'line2b_2': ''}, {'f2441': 1}),
    (f2441, {'line2b_1': '123', 'line2b_2': '456'}, {'f2441': 2}),
])
def test_us_read_funcs(func, input, expected):
    assert func(input) == expected
