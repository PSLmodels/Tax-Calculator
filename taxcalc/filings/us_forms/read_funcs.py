from taxcalc.filings import trace_map_func
from taxcalc.utils import string_to_number


@trace_map_func(['line1', 'line2', 'line3', 'line4', 'line5'], 'MARS')
def mars(fields):
    for i in [1, 2, 3, 4, 5]:
        line = 'line{}'.format(i)
        if line in fields and fields[line]:
            return {'MARS': i}


@trace_map_func('line6a', 'DSI')
def dsi(fields):
    # DSI - 1 if claimed as a dependent on another tax return, else 0
    # TODO rely on formatting instead once marked as binary in rvars.json
    return {'DSI': 0 if fields.get('line6a') else 1}


@trace_map_func(['line13', 'line13_check'], 'e01100')
def e01100(fields):
    # e01100 - Capital gain Distrib. not reported on Sch D
    if fields.get('line13') and fields.get('line13_check'):
        return {'e01100': fields['line13']}


@trace_map_func('line39a_blind', 'blind_head')
def blind_head(fields):
    # TODO rely on formatting instead once marked as binary in rvars.json
    return {
        'blind_head': 1 if fields.get('line39a_blind') else 0,
    }


@trace_map_func('line39a_blind_spouse', 'blind_spouse')
def blind_spouse(fields):
    # TODO rely on formatting instead once marked as binary in rvars.json
    return {
        'blind_spouse': 1 if fields.get('line39a_blind_spouse') else 0,
    }


@trace_map_func('line39b', 'MIDR')
def midr(fields):
    # MIDR - Separately filing spouse itemizing
    # TODO rely on formatting instead once marked as binary in rvars.json
    return {
        'MIDR': 1 if fields.get('line39b') else 0,
    }


@trace_map_func(['line53', 'line53a', 'line53b', 'line53c'], 'e07600')
def e07600_2013(fields):
    # e07600 - Prior year minimum tax credit
    line = 'line53'
    if (fields.get(line) and fields.get(line + 'b') and
            not (fields.get(line + 'a') or fields.get(line + 'c'))):
        return {'e07600': fields[line]}


@trace_map_func(['line54', 'line54a', 'line54b', 'line54c'], 'e07600')
def e07600_2014_2015(fields):
    # e07600 - Prior year minimum tax credit
    line = 'line54'
    if (fields.get(line) and fields.get(line + 'b') and
            not (fields.get(line + 'a') or fields.get(line + 'c'))):
        return {'e07600': fields[line]}


@trace_map_func(['line57', 'line57a', 'line57b'], 'e09800')
def e09800_2013(fields):
    # e09800 - Social security tax on tip income
    line = 'line57'
    if (fields.get(line) and fields.get(line + 'a') and
            not fields.get(line + 'b')):
        return {'e09800': fields[line]}


@trace_map_func(['line58', 'line58a', 'line58b'], 'e09800')
def e09800_2014_2015(fields):
    # e09800 - Social security tax on tip income
    line = 'line58'
    if (fields.get(line) and fields.get(line + 'a') and
            not fields.get(line + 'b')):
        return {'e09800': fields[line]}


@trace_map_func(['line5', 'line5a', 'line5b'], 'e18400')
def e18400(fields):
    # e18400 - State and local income taxes
    if (fields.get('line5') and fields.get('line5a') and
            not fields.get('line5b')):
        return {'e18400': fields['line5']}


@trace_map_func(['line18a', 'line18b', 'line18c'], 'p25470')
def p25470(fields):
    # p25470 - Royalty depletion
    if any('line18' + x in fields for x in ['a', 'b', 'c']):
        a = string_to_number(fields.get('line18a', ''))
        b = string_to_number(fields.get('line18b', ''))
        c = string_to_number(fields.get('line18c', ''))
        return {'p25470': a + b + c}


@trace_map_func(['line2_1', 'line2_2', 'line2_3'], 'EIC')
def eic(fields):
    # EIC - Earned Income Credit code: categorical variable
    child_ssns = ['line2_1', 'line2_2', 'line2_3']
    return {'EIC': sum([1 if fields.get(key) else 0 for key in child_ssns])}


@trace_map_func(['line2b_1', 'line2b_2'], 'f2441')
def f2441(fields):
    # f2441 -  Number of Child Care Credit qualified individuals
    # TODO Parse from attached statements if more than 2 - move to filing?
    ssns = ['line2b_1', 'line2b_2']
    return {'f2441': sum([1 if fields.get(key) else 0 for key in ssns])}


READ_FUNCS_BY_FORM = {
    'us1040': {
        'all_years': [mars, dsi, e01100, blind_head, blind_spouse, midr],
        '2013': [e07600_2013, e09800_2013],
        '2014_2015': [e07600_2014_2015, e09800_2014_2015],
    },
    'us1040sa': {
        'all_years': [e18400],
    },
    'us1040se': {
        'all_years': [p25470],
    },
    'us1040seic': {
        'all_years': [eic],
    },
    'us2441': {
        'all_years': [f2441],
    },
}
