"""
Tax-Calculator Input-Output class.
"""
# CODING-STYLE CHECKS:
# pycodestyle taxcalcio.py
# pylint --disable=locally-disabled taxcalcio.py
# pylint: disable=too-many-lines
import os
import gc
import copy
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
import paramtools
import behresp
from taxcalc.policy import Policy
from taxcalc.records import Records
from taxcalc.consumption import Consumption
from taxcalc.growdiff import GrowDiff
from taxcalc.growfactors import GrowFactors
from taxcalc.calculator import Calculator
from taxcalc.utils import (json_to_dict, delete_file, write_graph_file,
                           add_quantile_table_row_variable,
                           unweighted_sum, weighted_sum)

TMD_ASSUMES_FULL_CREDIT_CLAIMING = True
TMD_CREDIT_CLAIMING = {
    # IMPORTANT NOTE: when changing either TMDCSV_YEAR or _claim_thd value(s),
    # be sure to update changed info in the Tax-Calculator-LLM CLAUDE.md file.
    'eitc_claim_thd': {f'{Records.TMDCSV_YEAR}': 1600},
    'actc_claim_thd': {f'{Records.TMDCSV_YEAR}': 1500},
}


class TaxCalcIO():
    """
    Constructor for the Tax-Calculator Input-Output class.

    TaxCalcIO class constructor call must be followed by init() call.

    Parameters
    ----------
    input_data: string or Pandas DataFrame
        string is name of INPUT file that is CSV formatted containing
        variable names in the Records USABLE_READ_VARS set, or
        Pandas DataFrame is INPUT data containing variable names in
        the Records USABLE_READ_VARS set.  INPUT vsrisbles not in the
        Records USABLE_READ_VARS set can be present but are ignored.

    tax_year: integer
        calendar year for which taxes will be computed for INPUT.

    baseline: None or string
        None implies baseline policy is current-law policy, or
        string is name of optional BASELINE file that is a JSON
        reform file.

    reform: None or string
        None implies no policy reform (current-law policy), or
        string is name of optional REFORM file(s).

    assump: None or string
        None implies economic assumptions are standard assumptions,
        or string is name of optional ASSUMP file.

    behavior: None or string
        None implies behavioral response elasticities are all zero,
        or string is name of optional BEHAVIOR file.

    runid: int
        run id value to use for simpler output file names

    silent: boolean
        whether or not to suppress action messages.

    Returns
    -------
    class instance: TaxCalcIO
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, input_data, tax_year, baseline, reform,
                 assump, behavior, runid=0, silent=True):
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        self.silent = silent
        self.gf_reform = None
        self.errmsg = ''
        # check name and existence of INPUT file
        inp = 'x'
        self.cps_input_data = False
        self.puf_input_data = False
        self.tmd_input_data = False
        if isinstance(input_data, str):
            # remove any leading directory path from INPUT filename
            fname = os.path.basename(input_data)
            # check if fname ends with ".csv"
            if fname.endswith('.csv'):
                inp = f'{fname[:-4]}-{str(tax_year)[2:]}'
            else:
                msg = 'INPUT file name does not end in .csv'
                self.errmsg += f'ERROR: {msg}\n'
            # check existence of INPUT file
            self.cps_input_data = input_data.endswith('cps.csv')
            self.puf_input_data = input_data.endswith('puf.csv')
            self.tmd_input_data = input_data.endswith('tmd.csv')
            if not self.cps_input_data and not os.path.isfile(input_data):
                msg = 'INPUT file could not be found'
                self.errmsg += f'ERROR: {msg}\n'
            # if puf_input_data is True, construct weights and ratios paths
            if self.puf_input_data:  # pragma: no cover
                puf_dir = os.path.dirname(input_data)
                self.puf_weights = os.path.join(puf_dir, 'puf_weights.csv.gz')
                self.puf_ratios = os.path.join(puf_dir, 'puf_ratios.csv')
                if not os.path.isfile(self.puf_weights):
                    msg = f'weights file {self.puf_weights} could not be found'
                    self.errmsg += f'ERROR: {msg}\n'
                if not os.path.isfile(self.puf_ratios):
                    msg = f'gfactor file {self.puf_ratios} could not be found'
                    self.errmsg += f'ERROR: {msg}\n'
            # if tmd_input_data is True, construct weights and gfactor paths
            if self.tmd_input_data:  # pragma: no cover
                tmd_dir = os.path.dirname(input_data)
                if 'TMD_AREA' in os.environ:
                    area = os.environ['TMD_AREA']
                    wfile = f'{area}_tmd_weights.csv.gz'
                    inp = f'{fname[:-4]}_{area}-{str(tax_year)[2:]}'
                else:  # using national weights
                    wfile = 'tmd_weights.csv.gz'
                self.tmd_weights = os.path.join(tmd_dir, wfile)
                self.tmd_gfactor = os.path.join(tmd_dir, 'tmd_growfactors.csv')
                if not os.path.isfile(self.tmd_weights):
                    msg = f'weights file {self.tmd_weights} could not be found'
                    self.errmsg += f'ERROR: {msg}\n'
                if not os.path.isfile(self.tmd_gfactor):
                    msg = f'gfactor file {self.tmd_gfactor} could not be found'
                    self.errmsg += f'ERROR: {msg}\n'
        elif isinstance(input_data, pd.DataFrame):
            inp = f'df-{str(tax_year)[2:]}'
        else:
            msg = 'INPUT is neither string nor Pandas DataFrame'
            self.errmsg += f'ERROR: {msg}\n'
        # check name(s) and existence of BASELINE file(s)
        if baseline is None:
            self.specified_baseline = False
            bas = '-#'
        elif isinstance(baseline, str):
            self.specified_baseline = True
            bas = self._check_policy_files(baseline, 'BASELINE')
        else:
            bas = '-x'
            msg = 'TaxCalcIO.ctor: baseline is neither None nor str'
            self.errmsg += f'ERROR: {msg}\n'
        # check name(s) and existence of REFORM file(s)
        if reform is None:
            self.specified_reform = False
            ref = '-#'
        elif isinstance(reform, str):
            self.specified_reform = True
            ref = self._check_policy_files(reform, 'REFORM')
        else:
            ref = '-x'
            msg = 'TaxCalcIO.ctor: reform is neither None nor str'
            self.errmsg += f'ERROR: {msg}\n'
        # check name and existence of ASSUMP file
        if assump is None:
            asm = '-#'
        elif isinstance(assump, str):
            asm = self._check_single_json_file(assump, 'ASSUMP')
        else:
            asm = '-x'
            msg = 'TaxCalcIO.ctor: assump is neither None nor str'
            self.errmsg += f'ERROR: {msg}\n'
        # check name and existence of BEHAVIOR file
        self.behvdict = None
        if behavior is None:
            beh = '-#'
        elif isinstance(behavior, str):
            beh = self._check_single_json_file(behavior, 'BEHAVIOR')
        else:
            beh = '-x'
            msg = 'TaxCalcIO.ctor: behavior is neither None nor str'
            self.errmsg += f'ERROR: {msg}\n'
        # create OUTPUT file name and delete any existing output files
        self.output_filename = f'{inp}{bas}{ref}{asm}{beh}.xxx'
        self.runid = runid
        if runid > 0:
            self.output_filename = f'run{runid}-{str(tax_year)[2:]}.xxx'
        self.delete_output_files()
        # initialize variables whose values are set in init method
        self.pol_ref = None
        self.pol_bas = None
        self.recs_ref = None
        self.recs_bas = None
        self.con = None
        self.aging_input_data = None
        self.calc_ref = None
        self.calc_bas = None

    def delete_output_files(self):
        """
        Delete all output files derived from self.output_filename.
        """
        extensions = [
            '-params.baseline',
            '-params.reform',
            '.tables',
            '-atr.html',
            '-mtr.html',
            '-chg.html',
            '.dumpdb',
        ]
        for ext in extensions:
            delete_file(self.output_filename.replace('.xxx', ext))

    def init(self, input_data, tax_year, baseline, reform,
             assump, behavior, exact_calculations):
        """
        TaxCalcIO class post-constructor method that completes initialization.

        Parameters
        ----------
        First six are same as the first six of the TaxCalcIO constructor:
            input_data, tax_year, baseline, reform, assump, behavior.

        exact_calculations: boolean
            specifies whether or not exact tax calculations are done without
            any smoothing of "stair-step" provisions in the tax law.
        """
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        # pylint: disable=too-many-statements,too-many-branches,too-many-locals
        self.errmsg = ''
        # instantiate base/reform GrowFactors objects used for param indexing
        policy_gfactors_bas = GrowFactors()
        policy_gfactors_ref = GrowFactors()
        # instantiate base/reform GrowFactors objects used to extrapolate data
        if self.tmd_input_data:
            gfactors_bas = GrowFactors(self.tmd_gfactor)  # pragma: no cover
            gfactors_ref = GrowFactors(self.tmd_gfactor)  # pragma: no cover
        else:
            gfactors_bas = GrowFactors()
            gfactors_ref = GrowFactors()
        # check tax_year validity
        max_tax_year = gfactors_bas.last_year
        if tax_year > max_tax_year:
            msg = f'TAXYEAR={tax_year} is greater than {max_tax_year}'
            self.errmsg += f'ERROR: {msg}\n'
        if self.puf_input_data:
            min_tax_year = max(  # pragma: no cover
                Policy.JSON_START_YEAR, Records.PUFCSV_YEAR)
        elif self.cps_input_data:
            min_tax_year = max(
                Policy.JSON_START_YEAR, Records.CPSCSV_YEAR)
        elif self.tmd_input_data:
            min_tax_year = max(  # pragma: no cover
                Policy.JSON_START_YEAR, Records.TMDCSV_YEAR)
        else:
            min_tax_year = Policy.JSON_START_YEAR
        if tax_year < min_tax_year:
            msg = f'TAXYEAR={tax_year} is less than {min_tax_year}'
            self.errmsg += f'ERROR: {msg}\n'
        # tax_year out of valid range means cannot proceed with calculations
        if self.errmsg:
            return
        # get assumption sub-dictionaries
        assumpdict = Calculator.read_json_param_objects(None, assump)
        # get behavior dictionary
        if behavior:
            with open(behavior, 'r', encoding='utf-8') as jfile:
                json_text = jfile.read()
            try:
                self.behvdict = json_to_dict(json_text)
            except ValueError as valerr:  # pragma: no cover
                msg = f'{behavior} contains invalid JSON'
                self.errmsg = f'ERROR: BEHAVIOR file {msg}\n'
                self.errmsg += f'{valerr}'
                return
            # check behavior response elasticity names and values
            elasticity_set = set(self.behvdict.keys())
            if elasticity_set != set(['sub', 'inc', 'cg']):
                msg = f'{behavior} contains extra or missing elasticities'
                self.errmsg = f'ERROR: BEHAVIOR file {msg}\n'
                self.errmsg += 'Valid elasticities are "sub", "inc", "cg"'
                return
            if self.behvdict['sub'] < 0.0:
                msg = f'{behavior} contains negative "sub" elasticity'
                self.errmsg = f'ERROR: BEHAVIOR file {msg}\n'
            if self.behvdict['inc'] > 0.0:
                msg = f'{behavior} contains positive "inc" elasticity'
                self.errmsg += f'ERROR: BEHAVIOR file {msg}\n'
            if self.behvdict['cg'] > 0.0:
                msg = f'{behavior} contains positive "cg" elasticity'
                self.errmsg += f'ERROR: BEHAVIOR file {msg}\n'
            if self.errmsg:
                return
        # get policy parameter dictionaries from --baseline file(s)
        poldicts_bas = []
        if self.specified_baseline:
            for bas in baseline.split('+'):
                pdict = Calculator.read_json_param_objects(bas, None)
                poldicts_bas.append(pdict['policy'])
        # get policy parameter dictionaries from --reform file(s)
        poldicts_ref = []
        if self.specified_reform:
            for ref in reform.split('+'):
                pdict = Calculator.read_json_param_objects(ref, None)
                poldicts_ref.append(pdict['policy'])
        # set last_b_year
        last_b_year = max(tax_year, Policy.LAST_BUDGET_YEAR)
        # create gdiff_baseline object
        gdiff_baseline = GrowDiff(last_budget_year=last_b_year)
        try:
            gdiff_baseline.update_growdiff(assumpdict['growdiff_baseline'])
        except paramtools.ValidationError as valerr_msg:
            self.errmsg += str(valerr_msg)
        # apply gdiff_baseline to gfactor_bas
        gdiff_baseline.apply_to(gfactors_bas)
        # specify gdiff_response object
        gdiff_response = GrowDiff(last_budget_year=last_b_year)
        try:
            gdiff_response.update_growdiff(assumpdict['growdiff_response'])
        except paramtools.ValidationError as valerr_msg:
            self.errmsg += str(valerr_msg)
        # apply gdiff_baseline and gdiff_response to gfactor_ref
        gdiff_baseline.apply_to(gfactors_ref)
        gdiff_response.apply_to(gfactors_ref)
        self.gf_reform = copy.deepcopy(gfactors_ref)
        # create Policy objects:
        # ... apply gdiff_baseline to policy_gfactor_baseline
        gdiff_baseline.apply_to(policy_gfactors_bas)
        # ... apply gdiff_baseline and gdiff_response to policy_gfactor_ref
        gdiff_baseline.apply_to(policy_gfactors_ref)
        gdiff_response.apply_to(policy_gfactors_ref)
        # ... the baseline Policy object
        self.pol_bas = self._make_policy(policy_gfactors_bas, last_b_year)
        if self.specified_baseline:
            self._apply_poldicts(self.pol_bas, poldicts_bas)
        # ... the reform Policy object (no reform implies reform == baseline)
        if self.specified_reform:
            self.pol_ref = self._make_policy(policy_gfactors_ref, last_b_year)
            self._apply_poldicts(self.pol_ref, poldicts_ref)
        else:
            self.pol_ref = self._make_policy(policy_gfactors_bas, last_b_year)
        # create Consumption object
        self.con = Consumption(last_budget_year=last_b_year)
        try:
            self.con.update_consumption(assumpdict['consumption'])
        except paramtools.ValidationError as valerr_msg:
            self.errmsg += str(valerr_msg)
        # any errors imply cannot proceed with calculations
        if self.errmsg:
            return
        # set policy to tax_year
        self.pol_ref.set_year(tax_year)
        self.pol_bas.set_year(tax_year)
        # read input file contents into Records objects
        self.aging_input_data = (
            self.cps_input_data or
            self.puf_input_data or
            self.tmd_input_data
        )
        if self.aging_input_data:
            self.recs_ref = self._make_records(
                gfactors_ref, input_data, tax_year, exact_calculations,
            )
            self.recs_bas = self._make_records(
                gfactors_bas, input_data, tax_year, exact_calculations,
            )
            # extrapolate input data to tax_year
            while self.recs_ref.current_year < tax_year:
                self.recs_ref.increment_year()
                self.recs_bas.increment_year()
        else:  # input_data are raw data that are not being aged
            self.recs_ref = self._make_records(
                None, input_data, tax_year, exact_calculations,
            )
            self.recs_bas = copy.deepcopy(self.recs_ref)
        # create Calculator objects
        self.calc_ref = self._make_calculator(
            self.pol_ref, self.recs_ref, not self.silent,
        )
        self.calc_bas = self._make_calculator(
            self.pol_bas, self.recs_bas, False,
        )

    def tax_year(self):
        """
        Return calendar year for which TaxCalcIO calculations are being done.
        """
        return self.calc_ref.current_year

    def output_filepath(self):
        """
        Return full path to output file named in TaxCalcIO constructor.
        """
        dirpath = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(dirpath, self.output_filename)

    def advance_to_year(self, year):
        """
        Update self.output_filename and create Calculator objects for year.
        """
        # update self.output_filename and delete output files
        parts = self.output_filename.split('-')
        if self.runid == 0:  # if using legacy output file names
            parts[1] = str(year)[2:]
        else:  # if using simpler output file names (runN-YY.xxx)
            subparts = parts[1].split('.')
            subparts[0] = str(year)[2:]
            parts[1] = '.'.join(subparts)
        self.output_filename = '-'.join(parts)
        self.delete_output_files()
        # create baseline and reform Calculator objects for specified year
        # ... set policy for year
        self.pol_ref.set_year(year)
        self.pol_bas.set_year(year)
        # ... set consumption for year
        self.con.set_year(year)
        # ... increment records to year
        self.recs_ref.increment_year()
        self.recs_bas.increment_year()
        # ... delete old and create new Calculator objects
        del self.calc_ref
        self.calc_ref = self._make_calculator(
            self.pol_ref, self.recs_ref, False,
        )
        del self.calc_bas
        self.calc_bas = self._make_calculator(
            self.pol_bas, self.recs_bas, False,
        )
        # report advance to new year
        aging_data = (
            self.cps_input_data or
            self.puf_input_data or
            self.tmd_input_data
        )
        idata = 'Advance input data and' if aging_data else 'Advance'
        if not self.silent:
            print(f'{idata} policy to {year}')

    def analyze(
            self,
            output_params=False,
            output_tables=False,
            output_graphs=False,
            output_dump=False,
            dump_varlist=None,
    ):
        """
        Conduct tax analysis.

        Parameters
        ----------
        output_params: boolean
           whether or not to write baseline and reform policy parameter
           values to separate text files

        output_tables: boolean
           whether or not to generate and write distributional tables
           to a text file

        output_graphs: boolean
           whether or not to generate and write HTML graphs of average
           and marginal tax rates by income percentile

        output_dump: boolean
           whether or not to write SQLite3 database with baseline and
           reform tables each containing the variables in dump_varlist.

        dump_varlist: list
           list of variables to include in dumpdb output;
           list must include at least one variable.

        Returns
        -------
        Nothing
        """
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        # pylint: disable=too-many-branches,too-many-locals
        doing_calcs = output_tables or output_graphs or output_dump
        # optionally write --params output to text files
        if output_params:
            self.write_policy_params_files()
        if not doing_calcs:
            return
        # do output calculations
        if self.behvdict:  # if assuming behavioral responses
            br_dump_bas, br_dump_ref = behresp.response(
                self.calc_bas, self.calc_ref,
                self.behvdict, dump=True,
            )
            # copy returned dump dataframe values back into calc objects
            self._copy_dump_into_calc(self.calc_bas, br_dump_bas)
            del br_dump_bas
            self._copy_dump_into_calc(self.calc_ref, br_dump_ref)
            del br_dump_ref
        else:  # if assuming no behavioral responses
            self.calc_bas.calc_all()
            self.calc_ref.calc_all()
        # handle MTR output variables
        mtr_ptax_bas = None
        mtr_itax_bas = None
        mtr_ptax_ref = None
        mtr_itax_ref = None
        if output_dump:
            assert isinstance(dump_varlist, list)
            assert len(dump_varlist) > 0
            mtr_output = (
                'mtr_itax' in dump_varlist or
                'mtr_ptax' in dump_varlist
            )
            if mtr_output:
                (mtr_ptax_bas, mtr_itax_bas,
                 _) = self.calc_bas.mtr(
                     wrt_full_compensation=False,
                     calc_all_already_called=True)
                (mtr_ptax_ref, mtr_itax_ref,
                 _) = self.calc_ref.mtr(
                     wrt_full_compensation=False,
                     calc_all_already_called=True)
        # optionally write --tables output to text file
        if output_tables:
            self._write_tables_file()
        # optionally write --graphs output to HTML files
        if output_graphs:
            self._write_graph_files()
        # optionally write --dumpdb output to SQLite database file
        if output_dump:
            self._write_dumpdb_file(
                dump_varlist,
                mtr_ptax_ref, mtr_itax_ref,
                mtr_ptax_bas, mtr_itax_bas,
            )

    def write_policy_params_files(self):
        """
        Write baseline and reform policy parameter values to separate files.
        """
        self._write_params(self.calc_bas, '-params.baseline', 'baseline')
        self._write_params(self.calc_ref, '-params.reform', 'reform')

    BASE_DUMPVARS = [
        'RECID',
        's006',
        'data_source',
        'XTOT',
        'MARS',
        'expanded_income',
    ]
    MINIMAL_DUMPVARS = [
        'RECID',
        'iitax',
    ]
    MTR_DUMPVARS = [
        'mtr_itax',
        'mtr_ptax',
    ]

    def dump_variables(self, dumpvars_str):
        """
        Return list of variable names extracted from dumpvars_str, plus
        minimal baseline/reform variables even if not in dumpvars_str.
        Also, builds self.errmsg if any specified variables are not valid.
        """
        assert isinstance(dumpvars_str, str)
        self.errmsg = ''
        # get read and calc Records variables
        recs_vinfo = Records(data=None)  # contains records VARINFO only
        valid_set = recs_vinfo.USABLE_READ_VARS | recs_vinfo.CALCULATED_VARS
        # construct dumpvars list
        if dumpvars_str == 'ALL':
            dumpvars = list(valid_set) + TaxCalcIO.MTR_DUMPVARS
        else:
            # ... change some common non-space delimiter characters into spaces
            dumpvars_str = dumpvars_str.replace(',', ' ')
            dumpvars_str = dumpvars_str.replace(';', ' ')
            dumpvars_str = dumpvars_str.replace('|', ' ')
            # ... split dumpvars_str into dumpvars list
            dumpvars = dumpvars_str.split()
            # ... check that all dumpvars items are valid
            for var in dumpvars:
                if var not in valid_set and var not in TaxCalcIO.MTR_DUMPVARS:
                    msg = f'invalid variable name {var} in DUMPVARS file'
                    self.errmsg += f'ERROR: {msg}\n'
            if self.errmsg:
                return []
        # construct variable list
        dumpvars_list = list(TaxCalcIO.MINIMAL_DUMPVARS)
        for var in dumpvars:
            if var not in dumpvars_list and var not in TaxCalcIO.BASE_DUMPVARS:
                dumpvars_list.append(var)
        return dumpvars_list

    # --- Begin private methods of the TaxCalcIO class --- #

    def _check_policy_files(self, filespec, label):
        """
        Check validity of the (possibly compound) BASELINE or REFORM filespec,
        appending any errors to self.errmsg, and return the name fragment used
        in constructing output file names.
        """
        names = []
        for path in filespec.split('+'):
            # remove any leading directory path from filename
            fname = os.path.basename(path)
            # check if fname ends with ".json"
            if not fname.endswith('.json'):
                self.errmsg += (
                    f'ERROR: {label} file name {fname} does not end in .json\n'
                )
            # check existence of file
            if os.path.isfile(path):
                # check validity of JSON text
                with open(path, 'r', encoding='utf-8') as jfile:
                    json_text = jfile.read()
                    try:
                        _ = json_to_dict(json_text)
                    except ValueError as valerr:  # pragma: no cover
                        msg = f'{path} contains invalid JSON'
                        self.errmsg += f'ERROR: {label} file {msg}\n'
                        self.errmsg += f'{valerr}'
            else:
                msg = f'{path} could not be found'
                self.errmsg += f'ERROR: {label} file {msg}\n'
            # add fname to list of names used in output file names
            names.append(fname)
        # return (possibly compound) name fragment for output file names
        return '-' + '+'.join(name[:-5] for name in names)

    def _check_single_json_file(self, path, label):
        """
        Check name and existence of the single ASSUMP or BEHAVIOR file,
        appending any errors to self.errmsg, and return the name fragment
        used in constructing output file names.
        """
        # remove any leading directory path from filename
        fname = os.path.basename(path)
        # check if fname ends with ".json"
        if fname.endswith('.json'):
            fragment = f'-{fname[:-5]}'
        else:
            fragment = '-x'
            self.errmsg += f'ERROR: {label} file name does not end in .json\n'
        # check existence of file
        if not os.path.isfile(path):
            self.errmsg += f'ERROR: {label} file could not be found\n'
        return fragment

    def _make_policy(self, policy_gfactors, last_b_year):
        """
        Return Policy object that uses the specified growfactors and that
        optionally implements TMD credit-claiming thresholds.
        """
        pol = Policy(
            gfactors=policy_gfactors,
            last_budget_year=last_b_year,
        )
        if self.tmd_input_data:  # pragma: no cover
            if not TMD_ASSUMES_FULL_CREDIT_CLAIMING:
                pol.implement_reform(TMD_CREDIT_CLAIMING)
        return pol

    def _apply_poldicts(self, pol, poldicts):
        """
        Implement each reform dict in poldicts on the pol Policy object,
        appending any parameter errors to self.errmsg.
        """
        for poldict in poldicts:
            try:
                pol.implement_reform(
                    poldict,
                    print_warnings=True,
                    raise_errors=False,
                )
                if self.errmsg:
                    self.errmsg += '\n'
                for _, errors in pol.parameter_errors.items():
                    self.errmsg += '\n'.join(errors)
            except paramtools.ValidationError as valerr_msg:
                self.errmsg += str(valerr_msg)

    def _make_records(self, gfactors, input_data,
                      tax_year, exact_calculations):
        """
        Construct and return a Records object using the specified gfactors
        and the input data type implied by the constructor arguments.
        """
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        if self.cps_input_data:
            return Records.cps_constructor(
                gfactors=gfactors,
                exact_calculations=exact_calculations,
            )
        if self.puf_input_data:  # pragma: no cover
            return Records.puf_constructor(
                data=input_data,
                gfactors=gfactors,
                weights=self.puf_weights,
                ratios=self.puf_ratios,
                exact_calculations=exact_calculations,
            )
        if self.tmd_input_data:  # pragma: no cover
            return Records.tmd_constructor(
                data_path=Path(input_data),
                weights_path=Path(self.tmd_weights),
                growfactors=gfactors,
                exact_calculations=exact_calculations,
            )
        # input_data are raw data that are not being aged
        return Records(
            data=input_data,
            start_year=tax_year,
            gfactors=None,
            weights=None,
            adjust_ratios=None,
            exact_calculations=exact_calculations,
        )

    def _make_calculator(self, policy, records, verbose):
        """
        Construct and return a Calculator object from the specified policy
        and records objects.
        """
        return Calculator(
            policy=policy,
            records=records,
            verbose=verbose,
            consumption=self.con,
            sync_years=self.aging_input_data,
        )

    def _copy_dump_into_calc(self, calc, br_dump):
        """
        Copy behavioral-response dump DataFrame values back into the calc
        object, skipping the marginal-tax-rate columns.
        """
        int_variables = self.recs_bas.INTEGER_VARS
        vnames = list(br_dump.columns)
        for mtr_vname in ['mtr_ptax', 'mtr_itax', 'mtr_combined']:
            if mtr_vname in vnames:
                vnames.remove(mtr_vname)
        for vname in vnames:
            if vname in int_variables:
                vdtype = np.int32
            else:
                vdtype = np.float64
            calc.array(
                vname,
                br_dump[vname].to_numpy(dtype=vdtype, copy=True)
            )

    def _write_params(self, calc, ext, label):
        """
        Write policy parameter values from calc to the ext output file.
        """
        year = calc.current_year
        fname = self.output_filename.replace('.xxx', ext)
        with open(fname, 'w', encoding='utf-8') as pfile:
            for pname in Policy.parameter_list():
                pval = calc.policy_param(pname)
                pfile.write(f'{year} {pname} {pval}\n')
        if not self.silent:
            print(  # pragma: no cover
                f'Write {label} policy parameter values to file {fname}'
            )

    def _write_tables_file(self):
        """
        Write tables to text file.
        """
        # pylint: disable=too-many-locals
        tab_fname = self.output_filename.replace('.xxx', '.tables')
        # skip tables if there are not some positive weights
        if self.calc_bas.total_weight() <= 0.:
            with open(tab_fname, 'w', encoding='utf-8') as tfile:
                msg = 'No tables because sum of weights is not positive\n'
                tfile.write(msg)
            return
        # create list of results for nontax variables
        # - weights don't change with reform
        # - expanded_income may change, so always use baseline expanded income
        nontax_vars = ['s006', 'expanded_income']
        nontax = [self.calc_bas.array(var) for var in nontax_vars]
        # create list of results for tax variables from reform Calculator
        tax_vars = ['iitax', 'payrolltax', 'lumpsum_tax', 'combined']
        reform = [self.calc_ref.array(var) for var in tax_vars]
        # create DataFrame with tax distribution under reform
        dist = nontax + reform  # using expanded_income under baseline policy
        all_vars = nontax_vars + tax_vars
        distdf = pd.DataFrame(data=np.column_stack(dist), columns=all_vars)
        # create DataFrame with tax differences (reform - baseline)
        base = [self.calc_bas.array(var) for var in tax_vars]
        change = [(reform[idx] - base[idx]) for idx in range(0, len(tax_vars))]
        diff = nontax + change  # using expanded_income under baseline policy
        diffdf = pd.DataFrame(data=np.column_stack(diff), columns=all_vars)
        # write each kind of distributional table
        year = self.calc_bas.current_year
        with open(tab_fname, 'w', encoding='utf-8') as tfile:
            TaxCalcIO._write_decile_table(
                distdf,
                tfile,
                year,
                tkind='Reform Totals',
            )
            tfile.write('\n')
            TaxCalcIO._write_decile_table(
                diffdf,
                tfile,
                year,
                tkind='Differences',
            )
        # delete intermediate DataFrame objects
        del distdf
        del diffdf
        gc.collect()
        if not self.silent:
            print(  # pragma: no cover
                f'Write tabular output to file {tab_fname}'
            )

    @staticmethod
    def _write_decile_table(dfx, tfile, year, tkind='Totals'):
        """
        Write to tfile the tkind decile table using dfx DataFrame.
        """
        dfx = add_quantile_table_row_variable(dfx, 'expanded_income', 10,
                                              decile_details=False,
                                              pop_quantiles=False,
                                              weight_by_income_measure=False)
        # each table column: variable, aggregator, scale, header, units
        wsum = weighted_sum
        usum = unweighted_sum
        columns = [
            ('s006', usum, 1e-6, '    Returns', '       (#m)'),
            ('expanded_income', wsum, 1e-9, '    ExpInc', '      ($b)'),
            ('iitax', wsum, 1e-9, '    IncTax', '      ($b)'),
            ('payrolltax', wsum, 1e-9, '    PayTax', '      ($b)'),
            ('lumpsum_tax', wsum, 1e-9, '     LSTax', '      ($b)'),
            ('combined', wsum, 1e-9, '    AllTax', '      ($b)'),
        ]
        gdfx = dfx.groupby('table_row', as_index=False, observed=True)
        series = [
            gdfx.apply(agg, var, include_groups=False).values[:, 1]
            for var, agg, _, _, _ in columns
        ]
        scales = [scale for _, _, scale, _, _ in columns]
        # write decile table to text file
        row = (
            f'Weighted Tax {tkind} by '
            f'Baseline Expanded-Income Decile for {year}\n'
        )
        tfile.write(row)
        # pylint: disable=consider-using-f-string
        rowfmt = '{}{}{}{}{}{}\n'
        tfile.write(rowfmt.format(*[header for _, _, _, header, _ in columns]))
        tfile.write(rowfmt.format(*[units for _, _, _, _, units in columns]))
        rowfmt = '{:9.2f}{:10.1f}{:10.1f}{:10.1f}{:10.1f}{:10.1f}\n'
        for decile in range(0, 10):
            row = f'{decile:2d}'
            row += rowfmt.format(*[
                ser[decile] * scl for ser, scl in zip(series, scales)
            ])
            tfile.write(row)
        row = ' A'
        row += rowfmt.format(*[
            ser.sum() * scl for ser, scl in zip(series, scales)
        ])
        tfile.write(row)
        # pylint: enable=consider-using-f-string
        del gdfx
        del series
        gc.collect()

    def _write_graph_files(self):
        """
        Write graphs to HTML files.
        All graphs contain same number of filing units in each quantile.
        """
        pos_wght_sum = self.calc_ref.total_weight() > 0.0
        # each graph is specified by output-file suffix, title, and builder
        graph_specs = [
            ('-chg.html', 'CHG by Income Percentile',
             lambda: self.calc_bas.pch_graph(
                 self.calc_ref, pop_quantiles=False)),
            ('-atr.html', 'ATR by Income Percentile',
             lambda: self.calc_bas.atr_graph(
                 self.calc_ref, pop_quantiles=False)),
            ('-mtr.html', 'MTR by Income Percentile',
             lambda: self.calc_bas.mtr_graph(
                 self.calc_ref,
                 alt_e00200p_text='Taxpayer Earnings',
                 pop_quantiles=False)),
        ]
        fnames = []
        for suffix, title, build_graph in graph_specs:
            fname = self.output_filename.replace('.xxx', suffix)
            fnames.append(fname)
            if pos_wght_sum:
                fig = build_graph()
                write_graph_file(fig, fname, title)
                del fig
                gc.collect()
            else:
                reason = 'No graph because sum of weights is not positive'
                TaxCalcIO._write_empty_graph_file(fname, title, reason)
        if not self.silent:
            print(  # pragma: no cover
                f'Write graphical output to file {fnames[0]}\n'
                f'Write graphical output to file {fnames[1]}\n'
                f'Write graphical output to file {fnames[2]}'
            )

    @staticmethod
    def _write_empty_graph_file(fname, title, reason):
        """
        Write HTML graph file with title but no graph for specified reason.
        """
        txt = (
            '<html>\n'
            f'<head><title>{title}</title></head>\n'
            f'<body><center<h1>{reason}</h1></center></body>\n'
            '</html>\n'
        )
        with open(fname, 'w', encoding='utf-8') as gfile:
            gfile.write(txt)

    def _write_dumpdb_file(
            self,
            dump_varlist,
            mtr_ptax_ref, mtr_itax_ref,
            mtr_ptax_bas, mtr_itax_bas,
    ):
        """
        Write dump output to SQLite database file.
        """
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        def _dump_output(calcx, dumpvars, mtr_itax, mtr_ptax):
            """
            Extract dump output from calcx and return it as Pandas DataFrame.
            """
            odict = {}
            for var in dumpvars:
                if var == 'mtr_itax':
                    odict[var] = pd.Series(mtr_itax)
                elif var == 'mtr_ptax':
                    odict[var] = pd.Series(mtr_ptax)
                else:
                    odict[var] = pd.Series(calcx.array(var))
            odf = pd.concat(odict, axis=1)
            del odict
            return odf
        # begin main logic
        assert isinstance(dump_varlist, list)
        assert len(dump_varlist) > 0
        db_fname = self.output_filename.replace('.xxx', '.dumpdb')
        dbcon = sqlite3.connect(db_fname)
        # write base table
        outdf = pd.DataFrame()
        for var in TaxCalcIO.BASE_DUMPVARS:
            outdf[var] = self.calc_bas.array(var)
        expanded_income_bin_edges = [  # default income_group definition
            -1e300,  # essentially -infinity
            50e3,
            100e3,
            250e3,
            500e3,
            1e6,
            1e300,  # essentially +infinity
        ]
        outdf['income_group'] = 1 + pd.cut(  # default base.income_group values
            outdf['expanded_income'],
            expanded_income_bin_edges,
            right=False,  # bins are defined as [lo_edge, hi_edge)
            labels=False,  # pd.cut returns bins numbered 0,1,2,...
        )
        assert len(outdf.index) == self.calc_bas.array_len
        outdf.to_sql('base', dbcon, index=False)
        del outdf
        # write income_group_definition table
        num_groups = len(expanded_income_bin_edges) - 1
        outdf = pd.DataFrame()
        outdf['income_group'] = np.array([
            1 + grp for grp in range(0, num_groups)
        ])
        outdf['income_lower'] = np.array(expanded_income_bin_edges[:-1])
        outdf['income_up_to'] = np.array(expanded_income_bin_edges[1:])
        assert len(outdf.index) == num_groups
        outdf.to_sql('income_group_definition', dbcon, index=False)
        del outdf
        # write baseline table
        outdf = _dump_output(
            self.calc_bas, dump_varlist,
            mtr_itax_bas, mtr_ptax_bas,
        )
        assert len(outdf.index) == self.calc_bas.array_len
        outdf.to_sql('baseline', dbcon, index=False)
        del outdf
        # write reform table
        outdf = _dump_output(
            self.calc_ref, dump_varlist,
            mtr_itax_ref, mtr_ptax_ref,
        )
        assert len(outdf.index) == self.calc_ref.array_len
        outdf.to_sql('reform', dbcon, index=False)
        del outdf
        dbcon.close()
        del dbcon
        gc.collect()
        if not self.silent:
            print(  # pragma: no cover
                f'Write dump output to sqlite3 database file {db_fname}'
            )
