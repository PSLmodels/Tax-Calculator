"""
This script uses the input data files to update the compatible_data
values of the policy parameters in the taxcalc/policy_current_law.json file.

USAGE: (taxcalc-dev) T-C% python update_compatibility.py
THEN CHECK:             % git diff taxcalc/policy_current_law.json

A policy parameter is compatible with an input data file when changing
the parameter's value changes the tax liability (or benefits) of at
least MIN_UNITS unweighted filing units in the input data in YEAR.
Each parameter is changed in several small ways, one at a time, relative
to a baseline that is current-law policy plus the parameter's activation
reform (if any) in the ACTIVATION dictionary below.  An activation
reform is needed for a parameter that has no effect under current-law
policy (for example, a phaseout rate for a credit whose amount is zero
under current law).

Only the compatible_data information for the data sources whose input
data files are present is updated; the compatible_data information for
the other data sources is left unchanged.  Each change in compatibility
is written to stdout.  The compatible_data values of the parameters in
the UNCHANGED dictionary below are never changed by this script.

WHEN TO USE: use this script whenever a new version of any input data
file is used or whenever tax logic is changed, then regenerate the
docs/guide/policy_params.md file using the `make docs` command.
"""

import os
import re
import sys
import copy
import json
from pathlib import Path
import numpy as np
from taxcalc import Policy, Records, Calculator

ROOT = os.path.dirname(os.path.abspath(__file__))
PCLJSON_PATH = os.path.join(ROOT, 'taxcalc', 'policy_current_law.json')
# data sources in the order they appear in each compatible_data value
DATA_FILES = {
    'puf': [
        os.path.join(ROOT, 'puf.csv'),
        os.path.join(ROOT, 'puf_weights.csv.gz'),
        os.path.join(ROOT, 'puf_ratios.csv'),
    ],
    'cps': [
        os.path.join(ROOT, 'taxcalc', 'cps.csv.gz'),
    ],
    'tmd': [
        os.path.join(ROOT, 'tmd.csv'),
        os.path.join(ROOT, 'tmd_weights.csv.gz'),
        os.path.join(ROOT, 'tmd_growfactors.csv'),
    ],
}
YEAR = 2026  # year in which the effect of each parameter change is assessed
MIN_UNITS = 1  # minimum number of unweighted filing units that must change
TOLERANCE = 0.1  # dollar change in an output that counts as a change
OUTPUTS = [  # outputs whose change indicates that the parameter has effect
    'iitax', 'payrolltax', 'lumpsum_tax', 'ubi',
    'benefit_cost_total', 'benefit_value_total',
]
HUGE = 1e90  # parameter values at least this large are treated as unlimited
FINITE = (1e5, 1e4)  # values that replace unlimited parameter values

# Activation reforms for parameters that have no effect under current law.
# Each activation reform is a dictionary of {param_name: value} pairs,
# where value is a scalar that is used for every element of the parameter.
# Activation reforms are applied only to the parameter they activate, so
# they do not interfere with each other.  An activation reform may set the
# value of the parameter it activates, in which case the parameter changes
# are made relative to that value.
_II_EM = {'II_em': 5000.}
_II_EM_PO = {'II_em': 5000., 'II_em_ps': 200000.}
_II_CREDIT = {'II_credit': 1000.}
_II_CREDIT_NR = {'II_credit_nr': 1000.}
_RRC_ARPA = {'RRC_c': 1400., 'RRC_ps': 75000., 'RRC_pe': 80000.}
_PEASE = {'ID_ps': 300000., 'ID_prt': 0.03, 'ID_reduction_rate': 0.}
_SALT = {'ID_AllTaxes_c': 9e99}
_CTC_NEW = {'CTC_new_c': 1000., 'CTC_new_rt': 0.5}
_CTC_NEW_PO = {**_CTC_NEW, 'CTC_new_ps': 75000., 'CTC_new_prt': 0.05}
_CTC_NEW_RL = {**_CTC_NEW, 'CTC_new_refund_limited': True,
               'CTC_new_refund_limit_payroll_rt': 0.5}
ACTIVATION = {
    'actc_claim_prob_min': {'actc_claim_prob_min': 0.5},
    'II_em_ps': _II_EM,
    'II_em_prt': _II_EM_PO,
    'II_em_po_step_size': _II_EM_PO,
    'II_no_em_nu18': _II_EM,
    'II_credit_ps': {**_II_CREDIT, 'II_credit_prt': 0.05},
    'II_credit_prt': {**_II_CREDIT, 'II_credit_ps': 50000.},
    'II_credit_nr_ps': {**_II_CREDIT_NR, 'II_credit_nr_prt': 0.05},
    'II_credit_nr_prt': {**_II_CREDIT_NR, 'II_credit_nr_ps': 50000.},
    'RRC_ps': _RRC_ARPA,
    'RRC_pe': _RRC_ARPA,
    'RRC_prt': {'RRC_c_unit': 1200., 'RRC_ps': 75000., 'RRC_prt': 0.05},
    'ID_StateLocalTax_c': _SALT,
    'ID_StateLocalTax_crt': {**_SALT, 'ID_StateLocalTax_crt': 0.1},
    'ID_RealEstate_c': _SALT,
    'ID_RealEstate_crt': {**_SALT, 'ID_RealEstate_crt': 0.1},
    'ID_Casualty_frt': {'ID_Casualty_hc': 0.},
    'ID_Casualty_c': {'ID_Casualty_hc': 0.},
    'ID_Miscellaneous_frt': {'ID_Miscellaneous_hc': 0.},
    'ID_Miscellaneous_c': {'ID_Miscellaneous_hc': 0.},
    'ID_ps': _PEASE,
    'ID_prt': _PEASE,
    'ID_crt': _PEASE,
    'CG_brk3': {'CG_rt4': 0.25},
    'CG_rt4': {'CG_brk3': 1e6},
    'AMT_CG_brk3': {'AMT_CG_rt4': 0.25},
    'AMT_CG_rt4': {'AMT_CG_brk3': 1e6},
    'CG_ec': {'CG_nodiff': True},
    'CG_reinvest_ec_rt': {'CG_nodiff': True},
    'II_rt8': {'II_brk7': 1e6},
    # the alternative W-2-wage/UBIA cap binds only when the W-2-wage cap
    # is smaller, so zero the W-2-wage cap to activate the alternative cap
    'PT_qbid_alt_w2_wages_rt': {'PT_qbid_w2_wages_rt': 0.},
    'PT_qbid_alt_property_rt': {'PT_qbid_w2_wages_rt': 0.},
    'PT_qbid_ps': {'PT_qbid_prt': 0.05},
    'PT_qbid_prt': {'PT_qbid_ps': 200000.},
    'UI_em': {'UI_thd': 150000.},
    'UI_thd': {'UI_em': 10200., 'UI_thd': 150000.},
    'AMT_child_em': {'AMT_child_em_c_age': 24},
    'AMT_child_em_c_age': {'AMT_child_em_c_age': 24},
    'EITC_excess_InvestIncome_rt': {'EITC_excess_InvestIncome_rt': 1.},
    'CTC_new_c': _CTC_NEW,
    'CTC_new_c_under6_bonus': _CTC_NEW,
    'CTC_new_for_all': _CTC_NEW,
    'CTC_new_rt': _CTC_NEW,
    'CTC_new_ps': _CTC_NEW_PO,
    'CTC_new_prt': _CTC_NEW_PO,
    'CTC_new_refund_limited': {**_CTC_NEW,
                               'CTC_new_refund_limit_payroll_rt': 0.5},
    'CTC_new_refund_limit_payroll_rt': _CTC_NEW_RL,
    'CTC_new_refund_limited_all_payroll': _CTC_NEW_RL,
    'UBI_ecrt': {'UBI_21': 1000.},
    'CR_Charity_f': {'CR_Charity_rt': 0.4},
    'CR_Charity_frt': {'CR_Charity_rt': 0.4},
}

# Parameters whose compatible_data values are copied from the parameter
# named in the value, because changing them has no effect on the results
# computed by this script.  The phaseout step sizes have an effect only
# when Records exact_calculations is True.
MIRROR = {
    'OvertimeIncomeDed_po_step_size': 'OvertimeIncomeDed_po_rate_per_step',
    'TipIncomeDed_po_step_size': 'TipIncomeDed_po_rate_per_step',
    'AutoLoanInterestDed_po_step_size':
    'AutoLoanInterestDed_po_rate_per_step',
}

# Parameters whose compatible_data values are not changed by this script,
# along with the reason for not changing them.
UNCHANGED = {
    'parameter_indexing_CPI_offset': (
        'affects only the indexing of other parameters, which is done '
        'when a reform is implemented, and so is compatible with all data'
    ),
}

CDATA_LINE = re.compile(r'^        "compatible_data": \{$')
PNAME_LINE = re.compile(r'^    "(\w+)": \{$')
SOURCE_LINE = re.compile(r'^(\s+)"(puf|cps|tmd)": (true|false)(,?)$')


def records_for(src):
    """
    Return Records object containing data for the specified data source.
    """
    if src == 'puf':
        data, weights, ratios = DATA_FILES[src]
        return Records.puf_constructor(
            data=data, weights=weights, ratios=ratios,
        )
    if src == 'cps':
        return Records.cps_constructor(data=DATA_FILES[src][0])
    data, weights, growfactors = DATA_FILES[src]
    return Records.tmd_constructor(
        data_path=Path(data),
        weights_path=Path(weights),
        growfactors=Path(growfactors),
    )


def output_arrays(calc):
    """
    Return list of OUTPUTS arrays computed by the specified Calculator.
    """
    return [calc.array(var).copy() for var in OUTPUTS]


def num_changed_units(base_outputs, calc):
    """
    Return number of filing units with any output changed relative to
    the specified base_outputs.
    """
    changed = np.zeros_like(base_outputs[0], dtype=bool)
    for base, var in zip(base_outputs, OUTPUTS):
        changed |= np.abs(calc.array(var) - base) > TOLERANCE
    return int(changed.sum())


def set_param(calc, pname, value):
    """
    Set YEAR value of pname parameter in calc to specified value.
    """
    calc.policy_param(pname, np.array([value]))


def numeric_bound(meta, bound):
    """
    Return specified bound of parameter's valid range, or None when the
    bound is not numeric (for example, when it is another parameter name).
    """
    rng = meta.get('validators', {}).get('range', {})
    val = rng.get(bound)
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        return val
    return None


def candidate_values(value, meta):
    """
    Return list of distinct candidate values for the parameter whose
    YEAR value and metadata are specified.
    """
    if value.dtype == bool:
        return [np.logical_not(value)]
    vmin = numeric_bound(meta, 'min')
    vmax = numeric_bound(meta, 'max')
    if value.dtype.kind == 'i':
        cands = [value + 1, value - 1]
    else:
        is_rate = vmax is not None and vmax <= 1.0
        step = 0.05 if is_rate else 1000.
        huge = value >= HUGE
        up_val = np.where(value == 0, step, value * 1.1)
        dn_val = np.where(value == 0, -step, value * 0.9)
        cands = [np.where(huge, value, up_val), np.where(huge, value, dn_val)]
        if huge.any():
            cands.extend(np.where(huge, fval, value) for fval in FINITE)
    candidates = []
    for cand in cands:
        if vmin is not None or vmax is not None:
            cand = np.clip(cand, vmin, vmax)
        cand = cand.astype(value.dtype)
        if not np.array_equal(cand, value) and not any(
                np.array_equal(cand, prior) for prior in candidates):
            candidates.append(cand)
    return candidates


def activated_calc(base_calc, activation):
    """
    Return Calculator that is base_calc with activation reform applied.
    """
    if not activation:
        return base_calc
    calc = copy.deepcopy(base_calc)
    for pname, value in activation.items():
        current = calc.policy_param(pname)
        set_param(calc, pname,
                  np.full_like(current, value, dtype=current.dtype))
    calc.calc_all()
    return calc


def num_units_affected(base_calc, base_outputs, pname, meta):
    """
    Return maximum number of filing units whose outputs are changed by
    any of the candidate changes in the pname parameter, stopping as soon
    as that number is at least MIN_UNITS.
    """
    activation = ACTIVATION.get(pname, {})
    act_calc = activated_calc(base_calc, activation)
    if activation:
        act_outputs = output_arrays(act_calc)
    else:
        act_outputs = base_outputs
    max_changed = 0
    for cand in candidate_values(act_calc.policy_param(pname), meta):
        calc = copy.deepcopy(act_calc)
        set_param(calc, pname, cand)
        calc.calc_all()
        max_changed = max(max_changed, num_changed_units(act_outputs, calc))
        if max_changed >= MIN_UNITS:
            break
    return max_changed


def param_effects(src, params):
    """
    Return dictionary of {pname: max_number_of_changed_units} for the
    specified data source and parameters.
    """
    base_calc = Calculator(policy=Policy(), records=records_for(src))
    base_calc.advance_to_year(YEAR)
    base_calc.calc_all()
    base_outputs = output_arrays(base_calc)
    # check that recomputing an unchanged calculator changes nothing
    check = copy.deepcopy(base_calc)
    check.calc_all()
    assert num_changed_units(base_outputs, check) == 0
    effects = {}
    for num, (pname, meta) in enumerate(params.items(), start=1):
        if num % 40 == 0:
            print(f'  {src}: assessed {num} of {len(params)} parameters',
                  flush=True)
        if pname in UNCHANGED or pname in MIRROR:
            continue
        effects[pname] = num_units_affected(base_calc, base_outputs,
                                            pname, meta)
    for pname, other in MIRROR.items():
        if other in effects:
            effects[pname] = effects[other]
    return effects


def new_compatibility(params, effects):
    """
    Return dictionary of new compatible_data values for each parameter.
    """
    new_cdata = {}
    for pname, meta in params.items():
        old = meta['compatible_data']
        new = dict(old)
        for src, src_effects in effects.items():
            if pname in src_effects:
                new[src] = src_effects[pname] >= MIN_UNITS
                if new[src] != old[src]:
                    print(f'{pname}: {src} {str(old[src]).lower()} ==> '
                          f'{str(new[src]).lower()} '
                          f'({src_effects[pname]} units changed)')
        new_cdata[pname] = new
    return new_cdata


def revised_json_text(old_text, new_cdata):
    """
    Return policy_current_law.json text with revised compatible_data
    values, leaving the rest of the text unchanged.
    """
    new_lines = []
    pname = None
    in_cdata = False
    for line in old_text.split('\n'):
        pmatch = PNAME_LINE.match(line)
        if pmatch:
            pname = pmatch.group(1)
        if CDATA_LINE.match(line):
            in_cdata = True
        elif in_cdata:
            smatch = SOURCE_LINE.match(line)
            if smatch:
                if pname in new_cdata:
                    val = str(new_cdata[pname][smatch.group(2)]).lower()
                    line = (f'{smatch.group(1)}"{smatch.group(2)}": '
                            f'{val}{smatch.group(4)}')
            else:
                in_cdata = False
        new_lines.append(line)
    return '\n'.join(new_lines)


def main():
    """
    High-level logic of the script.
    """
    # read policy_current_law.json file
    with open(PCLJSON_PATH, 'r', encoding='utf-8') as jfile:
        old_text = jfile.read()
    old_dict = json.loads(old_text)
    params = {k: v for k, v in old_dict.items() if k != 'schema'}
    used = set(ACTIVATION) | set(UNCHANGED) | set(MIRROR)
    used |= set(MIRROR.values())
    for activation in ACTIVATION.values():
        used |= set(activation)
    unknown = used - set(params)
    if unknown:
        print(f'ERROR: unknown parameters in script: {sorted(unknown)}')
        return 1
    # compute effects of changing each parameter for each data source
    effects = {}
    for src, paths in DATA_FILES.items():
        missing = [path for path in paths if not os.path.isfile(path)]
        if missing:
            print(f'SKIPPING {src} because {missing[0]} is not present')
            continue
        print(f'ASSESSING {src} data ...', flush=True)
        effects[src] = param_effects(src, params)
    if not effects:
        print('ERROR: no input data files are present')
        return 1
    # compute new compatible_data values and revise JSON text
    new_cdata = new_compatibility(params, effects)
    new_text = revised_json_text(old_text, new_cdata)
    # check that only compatible_data values have changed
    for pname, cdata in new_cdata.items():
        old_dict[pname]['compatible_data'] = cdata
    assert json.loads(new_text) == old_dict
    # write revised policy_current_law.json file
    if new_text == old_text:
        print('NO CHANGES in parameter compatibility information')
    else:
        with open(PCLJSON_PATH, 'w', encoding='utf-8') as jfile:
            jfile.write(new_text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
