import pytest

from taxcalc.filings.forms import *

TWENTY_13_TO_15 = [2013, 2014, 2015]


@pytest.mark.parametrize('form_class, supported_years', [
    (US1040, TWENTY_13_TO_15),
    (US1040SA, TWENTY_13_TO_15),
    (US1040SD, TWENTY_13_TO_15),
    (US1040SE, TWENTY_13_TO_15),
    (US1040SEIC, TWENTY_13_TO_15),
    (US2441, TWENTY_13_TO_15),
    (US3800, TWENTY_13_TO_15),
    (US4137, TWENTY_13_TO_15),
    (US4255, [2012, 2013, 2014, 2015]),
    (US4952, TWENTY_13_TO_15),
    (US5695, TWENTY_13_TO_15),
    (US6251, TWENTY_13_TO_15),
    (US8801, TWENTY_13_TO_15),
    (US8863, TWENTY_13_TO_15),
])
def test_year_support(form_class, supported_years):
    # Not necessary right now but might be helpful?
    supported_years.sort()

    # todo - Just use form_class._SUPPORTED_YEARS?
    # Then this test would just assure that the supported years logic remains
    # correct for this child class (i.e. it's not incorrectly overwritten),
    # and skip effectively double checking the SUPPORTED_YEARS constant.
    # Would probably want to expose _SUPPORTED_YEARS via getter.
    assert supported_years == form_class._SUPPORTED_YEARS

    with pytest.raises(UnsupportedFormYearError):
        form_class(supported_years[0] - 1)
    for year in supported_years:
        form_class(year)
    with pytest.raises(UnsupportedFormYearError):
        form_class(supported_years[-1] + 1)


@pytest.mark.parametrize('form_class, year, evar_map', [
    (US1040, 2013, {
        'line6d': 'XTOT',
        'line7': 'e00200',
        'line8a': 'e00300',
        'line8b': 'e00400',
        'line9a': 'e00600',
        'line9b': 'e00650',
        'line10': 'e00700',
        'line11': 'e00800',
        'line12': 'e00900',
        'line14': 'e01200',
        'line15b': 'e01400',
        'line16a': 'e01500',
        'line16b': 'e01700',
        'line17': 'e02000',
        'line18': 'e02100',
        'line19': 'e02300',
        'line20a': 'e02400',
        'line23': 'e03220',
        'line25': 'e03290',
        'line28': 'e03300',
        'line29': 'e03270',
        'line30': 'e03400',
        'line31a': 'e03500',
        'line32': 'e03150',
        'line33': 'e03210',
        'line34': 'e03230',
        'line35': 'e03240',
        'line47': 'e07300',
        'line50': 'e07240',
        'line52': 'e07260',
        'line53': 'p08000',
        'line58': 'e09900',
        'line63': 'e11200',
        'line65': 'e11070',
    }),
    (US1040, 2014, {
        'line6d': 'XTOT',
        'line7': 'e00200',
        'line8a': 'e00300',
        'line8b': 'e00400',
        'line9a': 'e00600',
        'line9b': 'e00650',
        'line10': 'e00700',
        'line11': 'e00800',
        'line12': 'e00900',
        'line14': 'e01200',
        'line15b': 'e01400',
        'line16a': 'e01500',
        'line16b': 'e01700',
        'line17': 'e02000',
        'line18': 'e02100',
        'line19': 'e02300',
        'line20a': 'e02400',
        'line23': 'e03220',
        'line25': 'e03290',
        'line28': 'e03300',
        'line29': 'e03270',
        'line30': 'e03400',
        'line31a': 'e03500',
        'line32': 'e03150',
        'line33': 'e03210',
        'line34': 'e03230',
        'line35': 'e03240',
        'line48': 'e07300',
        'line51': 'e07240',
        'line53': 'e07260',
        'line54': 'p08000',
        'line59': 'e09900',
        'line65': 'e11200',
        'line67': 'e11070',
    }),
    (US1040SA, 2013, {
        'line1': 'e17500',
        'line6': 'e18500',
        'line15': 'e19200',
        'line16': 'e19800',
        'line17': 'e20100',
        'line20': 'e20500',
        'line24': 'e20400',
    }),
    (US1040SD, 2013, {
        'line7': 'p22250',
        'line15': 'p23250',
        'line18': 'e24518',
        'line19': 'e24515',
    }),
    (US1040SE, 2013, {
        'line32': 'e26270',
        'line40': 'e27200',
    }),
    (US2441, 2013, {'line3': 'e32800'}),
    (US3800, 2013, {'line17': 'e07400'}),
    (US4137, 2013, {'line13': 'e09800'}),
    (US4255, 2013, {'line15': 'e09700'}),
    (US4952, 2013, {'line4g': 'e58990'}),
    (US5695, 2013, {'line15': 'e07260'}),
    (US6251, 2013, {'line32': 'e62900'}),
    (US8801, 2013, {'line25': 'e07600'}),
    (US8863, 2013, {
        'line4': 'e87530',
        'line7': 'p87521',
        'line30': 'P87482',
    }),
])
def test_direct_mapping(form_class, year, evar_map):
    # todo - Ensure we test every year for every "used field",
    # and ensure the result set includes every "output evar"
    # for each form.

    # todo - Just use a pre-constructed map provided by form class?
    # then this test would just assure that the direct_mapping logic remains
    # correct for this child class (i.e. it's not incorrectly overwritten),
    # instead of double checking the map vars.
    # That would remove current ability to dynamically change maps, though.
    constructed_map = form_class._EVAR_MAP
    map_by_year = form_class._EVAR_MAP_BY_YEAR
    if map_by_year and year in map_by_year.keys():
        constructed_map = dict(constructed_map, **map_by_year[year])
    assert evar_map == constructed_map

    fields = {}
    expected = {}
    test_value = 0
    for line, evar in evar_map.items():
        fields[line] = str(test_value)
        expected[evar] = test_value
        test_value += 1
    subject = form_class(year, fields)
    assert subject.to_evars_direct() == expected


@pytest.mark.parametrize('form_class, year, fields, expected', [
    # US1040 - MARS
    (US1040, 2013, {'line1': ''}, {}),
    (US1040, 2013, {'line1': 'Checked'}, {'MARS': 1}),
    (US1040, 2013, {'line2': 'X'}, {'MARS': 2}),
    (US1040, 2013, {'line3': 'Foo'}, {'MARS': 3}),
    (US1040, 2013, {'line4': 'Bar'}, {'MARS': 4}),
    (US1040, 2013, {'line5': '47'}, {'MARS': 5}),

    # US1040 - DSI
    (US1040, 2013, {'line6a': 'X'}, {'DSI': 0}),
    (US1040, 2013, {'line6a': ''}, {'DSI': 1}),

    # US1040 - e01100
    (US1040, 2013, {'line13': '110', 'line13_no_sch_d': ''}, {}),
    (US1040, 2013, {'line13': '110', 'line13_no_sch_d': 'X'}, {'e01100': 110}),

    # US1040 - blind
    (US1040, 2013, {'line39a_blind': '', 'line39a_blind_spouse': ''},
        {'blind_head': 0, 'blind_spouse': 0}),
    (US1040, 2013, {'line39a_blind': 'X', 'line39a_blind_spouse': 'Foo'},
        {'blind_head': 1, 'blind_spouse': 1}),

    # US1040 - MIDR
    (US1040, 2013, {'line39b': ''}, {'MIDR': 0}),
    (US1040, 2013, {'line39b': 'X'}, {'MIDR': 1}),

    # US1040 - e07600 - 2013
    (US1040, 2013,
        {'line53': '7600', 'line53a': '', 'line53b': '', 'line53c': ''},
        {}),
    (US1040, 2013,
        {'line53': '7600', 'line53a': 'X', 'line53b': 'X', 'line53c': 'X'},
        {}),
    (US1040, 2013,
        {'line53': '7600', 'line53a': 'X', 'line53b': 'X', 'line53c': ''},
        {}),
    (US1040, 2013,
        {'line53': '7600', 'line53a': '', 'line53b': 'X', 'line53c': 'X'},
        {}),
    (US1040, 2013,
        {'line53': '7600', 'line53a': '', 'line53b': 'X', 'line53c': ''},
        {'e07600': 7600}),

    # US1040 - e07600 - 2014 & 2015
    (US1040, 2014,
        {'line54': '7600', 'line54a': '', 'line54b': '', 'line54c': ''},
        {}),
    (US1040, 2014,
        {'line54': '7600', 'line54a': 'X', 'line54b': 'X', 'line54c': 'X'},
        {}),
    (US1040, 2014,
        {'line54': '7600', 'line54a': 'X', 'line54b': 'X', 'line54c': ''},
        {}),
    (US1040, 2014,
        {'line54': '7600', 'line54a': '', 'line54b': 'X', 'line54c': 'X'},
        {}),
    (US1040, 2014,
        {'line54': '7600', 'line54a': '', 'line54b': 'X', 'line54c': ''},
        {'e07600': 7600}),

    # US1040 - e09800 - 2013
    (US1040, 2013, {'line57': '9800', 'line57a': '', 'line57b': ''}, {}),
    (US1040, 2013, {'line57': '9800', 'line57a': 'X', 'line57b': 'X'}, {}),
    (US1040, 2013, {'line57': '9800', 'line57a': 'X', 'line57b': ''},
        {'e09800': 9800}),

    # US1040 - e09800 - 2014 & 2015
    (US1040, 2014, {'line58': '9800', 'line58a': '', 'line58b': ''}, {}),
    (US1040, 2014, {'line58': '9800', 'line58a': 'X', 'line58b': 'X'}, {}),
    (US1040, 2014, {'line58': '9800', 'line58a': 'X', 'line58b': ''},
        {'e09800': 9800}),

    # US1040SA - e18400
    (US1040SA, 2013, {'line5': '18400', 'line5a': '', 'line5b': ''}, {}),
    (US1040SA, 2013, {'line5': '18400', 'line5a': 'X', 'line5b': 'X'}, {}),
    (US1040SA, 2013, {'line5': '18400', 'line5a': '', 'line5b': 'X'}, {}),
    (US1040SA, 2013, {'line5': '18400', 'line5a': 'X', 'line5b': ''},
        {'e18400': 18400}),

    # US1040SE - p25470
    (US1040SE, 2013, {}, {}),
    (US1040SE, 2013, {'line18a': ''}, {'p25470': 0}),
    (US1040SE, 2013, {'line18a': '1', 'line18b': '2', 'line18c': '4'},
        {'p25470': 7}),

    # US1040SEIC - EIC
    (US1040SEIC, 2013, {}, {'EIC': 0}),
    (US1040SEIC, 2013,
        {'line2_child1': '', 'line2_child2': '', 'line2_child3': ''},
        {'EIC': 0}),
    (US1040SEIC, 2013,
        {'line2_child1': '123', 'line2_child2': '', 'line2_child3': ''},
        {'EIC': 1}),
    (US1040SEIC, 2013,
        {'line2_child1': '123', 'line2_child2': '456', 'line2_child3': ''},
        {'EIC': 2}),
    (US1040SEIC, 2013,
        {'line2_child1': '123', 'line2_child2': '456', 'line2_child3': '789'},
        {'EIC': 3}),

    # US2441 - f2441
    (US2441, 2013, {}, {'f2441': 0}),
    (US2441, 2013, {'line2b_1': '', 'line2b_2': ''}, {'f2441': 0}),
    (US2441, 2013, {'line2b_1': '123', 'line2b_2': ''}, {'f2441': 1}),
    (US2441, 2013, {'line2b_1': '123', 'line2b_2': '456'}, {'f2441': 2}),
])
def test_indirect_mapping(form_class, year, fields, expected):
    # todo - Ensure we test every year for every "used field",
    # and ensure the result set includes every "output evar"
    # for each form.
    # Might want to explore the meta construction abilities of pytest.
    form = form_class(year, fields)
    assert form.to_evars_indirect() == expected
