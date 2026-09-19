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
import json
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
import paramtools
from taxcalc.policy import Policy
from taxcalc.records import Records
from taxcalc.behresp import response
from taxcalc.consumption import Consumption
from taxcalc.growdiff import GrowDiff
from taxcalc.growfactors import GrowFactors
from taxcalc.calculator import Calculator
from taxcalc.utils import (json_to_dict, delete_file, write_graph_file,
                           add_quantile_table_row_variable,
                           unweighted_sum, weighted_sum)


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
        self.silent = silent
        self.gf_reform = None
        self.errmsg = ''
        self.behvdict = None
        self.cps_input_data = False
        self.tmd_input_data = False
        self.tmd_weights = None
        self.tmd_gfactor = None
        # check INPUT data and get stem, the year-independent part of the
        # output file name (the tax year is spliced in when
        # self.output_filename is built below and when the advance_to_year
        # method rebuilds it for a later year)
        stem = self._check_input_data(input_data)
        # check each optional input file, getting the fragment that it
        # contributes to legacy output file names
        self.specified_baseline = isinstance(baseline, str)
        self.specified_reform = isinstance(reform, str)
        bas = self._check_file_arg(
            baseline, 'BASELINE', self._check_policy_files)
        ref = self._check_file_arg(
            reform, 'REFORM', self._check_policy_files)
        asm = self._check_file_arg(
            assump, 'ASSUMP', self._check_single_json_file)
        beh = self._check_file_arg(
            behavior, 'BEHAVIOR', self._check_single_json_file)
        # create OUTPUT file name and delete any existing output files
        # Note: the name is always stem + '-' + two-digit year + tail, which
        # is what lets advance_to_year replace the year without having to
        # parse a name whose stem or tail may itself contain a hyphen
        self.runid = runid
        if runid > 0:  # if using simpler output file names (runN-YY.xxx)
            self.fname_stem = f'run{runid}'
            self.fname_tail = '.xxx'
        else:  # if using legacy output file names
            self.fname_stem = stem
            self.fname_tail = f'{bas}{ref}{asm}{beh}.xxx'
        self.output_filename = self._filename_for_year(tax_year)
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
        # NOTE: self.errmsg is not reset here because doing so would discard
        #       any error messages generated by the class constructor.
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
        if self.cps_input_data:
            min_data_year = Records.CPSCSV_YEAR
        elif self.tmd_input_data:
            min_data_year = Records.TMDCSV_YEAR  # pragma: no cover
        else:
            min_data_year = Policy.JSON_START_YEAR
        min_tax_year = max(Policy.JSON_START_YEAR, min_data_year)
        if tax_year < min_tax_year:
            msg = f'TAXYEAR={tax_year} is less than {min_tax_year}'
            self.errmsg += f'ERROR: {msg}\n'
        # tax_year out of valid range means cannot proceed with calculations
        if self.errmsg:
            return
        # get assumption sub-dictionaries
        assumpdict = Calculator.read_json_param_objects(None, assump)
        # read and check contents of optional BEHAVIOR file
        if behavior and not self._read_behavior_file(behavior):
            return
        # get policy parameter dictionaries from --baseline/--reform file(s)
        poldicts_bas = self._read_poldicts(baseline, self.specified_baseline)
        poldicts_ref = self._read_poldicts(reform, self.specified_reform)
        # set last_b_year
        last_b_year = max(tax_year, Policy.LAST_BUDGET_YEAR)
        # create GrowDiff objects from the assumption sub-dictionaries
        gdiff_baseline = self._make_growdiff(
            assumpdict['growdiff_baseline'], last_b_year)
        gdiff_response = self._make_growdiff(
            assumpdict['growdiff_response'], last_b_year)
        # baseline GrowFactors objects reflect only gdiff_baseline, while
        # reform GrowFactors objects reflect gdiff_baseline plus gdiff_response
        for gfactors in (gfactors_bas, policy_gfactors_bas):
            gdiff_baseline.apply_to(gfactors)
        for gfactors in (gfactors_ref, policy_gfactors_ref):
            gdiff_baseline.apply_to(gfactors)
            gdiff_response.apply_to(gfactors)
        self.gf_reform = copy.deepcopy(gfactors_ref)
        # create Policy objects:
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

        Note that output files are written using the bare
        self.output_filename, so they are located in the current working
        directory, which is what this method returns a path into.
        """
        return os.path.abspath(self.output_filename)

    def advance_to_year(self, year):
        """
        Update self.output_filename and create Calculator objects for year.
        """
        # update self.output_filename and delete output files
        self.output_filename = self._filename_for_year(year)
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
        if not self.silent:
            idata = 'Advance input data and' if self.aging_input_data else \
                    'Advance'
            print(f'{idata} policy to {year}')

    def analyze(
            self,
            output_params=False,
            output_jsonparams=False,
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

        output_jsonparams: boolean
           whether the baseline and reform policy parameter files written
           when output_params is True use JSON format rather than text format

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
        # optionally write --params output files
        if output_params:
            self.write_policy_params_files(output_jsonparams)
        if not doing_calcs:
            return
        # do output calculations
        if self.behvdict:  # if assuming behavioral responses
            # The response function does its own calc_all calls on copies
            # of the two calc objects and returns results as dataframes,
            # so the results are copied back into the two calc objects in
            # order that the --tables, --graphs, and --dumpdb output logic
            # below can use the behavior-adjusted results in the same way
            # it uses static results.
            br_dump_bas, br_dump_ref = response(
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
                mtr_ptax_bas, mtr_itax_bas, _ = self.calc_bas.mtr(
                    wrt_full_compensation=False,
                    calc_all_already_called=True)
                mtr_ptax_ref, mtr_itax_ref, _ = self.calc_ref.mtr(
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

    def write_policy_params_files(self, jsonparams=False):
        """
        Write baseline and reform policy parameter values to separate files.
        """
        self._write_params(self.calc_bas, '-params.baseline', 'baseline',
                           jsonparams)
        self._write_params(self.calc_ref, '-params.reform', 'reform',
                           jsonparams)

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
    # Records variables that are never calculated, and hence are always zero,
    # so they are excluded from dump output.  The marginal tax rates they are
    # named for are supplied by the MTR_DUMPVARS variables, which are computed
    # by the Calculator.mtr method rather than read from a Records object.
    UNUSED_DUMPVARS = [
        'mtr_inctax',
        'mtr_paytax',
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
        valid_set = (
            (recs_vinfo.USABLE_READ_VARS | recs_vinfo.CALCULATED_VARS) -
            set(TaxCalcIO.UNUSED_DUMPVARS)
        )
        # construct dumpvars list
        # Note: valid_set is sorted because iteration order of a Python set
        # is not stable across runs, and dumpvars order determines the column
        # order of the baseline and reform dumpdb tables
        if dumpvars_str == 'ALL':
            dumpvars = sorted(valid_set) + TaxCalcIO.MTR_DUMPVARS
        else:
            # ... change some common non-space delimiter characters into
            #     spaces and split the result into the dumpvars list
            dumpvars = dumpvars_str.translate(
                str.maketrans(',;|', '   ')
            ).split()
            # ... check that all dumpvars items are valid
            valid_set |= set(TaxCalcIO.MTR_DUMPVARS)
            for var in dumpvars:
                if var not in valid_set:
                    msg = f'invalid variable name {var} in DUMPVARS file'
                    self.errmsg += f'ERROR: {msg}\n'
            if self.errmsg:
                return []
        # construct variable list, omitting duplicates and the BASE_DUMPVARS
        # variables, which are written to the dumpdb base table
        dumpvars_list = list(TaxCalcIO.MINIMAL_DUMPVARS)
        omitted = set(dumpvars_list) | set(TaxCalcIO.BASE_DUMPVARS)
        for var in dumpvars:
            if var not in omitted:
                dumpvars_list.append(var)
                omitted.add(var)
        return dumpvars_list

    # --- Begin private methods of the TaxCalcIO class --- #

    def _filename_for_year(self, year):
        """
        Return output file name for the specified year.
        """
        return f'{self.fname_stem}-{str(year)[2:]}{self.fname_tail}'

    def _check_input_data(self, input_data):
        """
        Check the INPUT data specified in the constructor, appending any
        errors to self.errmsg, and return the year-independent part of the
        output file name.
        """
        if isinstance(input_data, pd.DataFrame):
            return 'df'
        if not isinstance(input_data, str):
            self.errmsg += (
                'ERROR: INPUT is neither string nor Pandas DataFrame\n'
            )
            return 'x'
        # remove any leading directory path from INPUT file name
        fname = os.path.basename(input_data)
        # check that fname ends in .csv
        if fname.endswith('.csv'):
            stem = fname[:-4]
        else:
            stem = 'x'
            self.errmsg += 'ERROR: INPUT file name does not end in .csv\n'
        # check that fname does not end in puf.csv
        puf_input_data = fname.endswith('puf.csv')
        if puf_input_data:
            self.errmsg += (
                'ERROR: INPUT file name ending in puf.csv is not supported\n'
            )
        # check existence of INPUT file
        # (cps.csv data are packaged with the taxcalc package)
        self.cps_input_data = input_data.endswith('cps.csv')
        self.tmd_input_data = input_data.endswith('tmd.csv')
        if (
                not self.cps_input_data and
                not puf_input_data and
                not os.path.isfile(input_data)
        ):
            self.errmsg += 'ERROR: INPUT file could not be found\n'
        # TMD input data imply weights and gfactor files in the same folder
        if self.tmd_input_data:  # pragma: no cover
            tmd_dir = os.path.dirname(input_data)
            if 'TMD_AREA' in os.environ:
                area = os.environ['TMD_AREA']
                wfile = f'{area}_tmd_weights.csv.gz'
                stem = f'{fname[:-4]}_{area}'
            else:  # using national weights
                wfile = 'tmd_weights.csv.gz'
            self.tmd_weights = os.path.join(tmd_dir, wfile)
            self.tmd_gfactor = os.path.join(tmd_dir, 'tmd_growfactors.csv')
            for kind, path in [('weights', self.tmd_weights),
                               ('gfactor', self.tmd_gfactor)]:
                if not os.path.isfile(path):
                    msg = f'{kind} file {path} could not be found'
                    self.errmsg += f'ERROR: {msg}\n'
        return stem

    def _check_file_arg(self, arg, label, check_files):
        """
        Check the type of the optional arg, which must be None or a file
        specification string that is checked by the check_files method,
        and return the fragment used in constructing output file names.
        """
        if arg is None:
            return '-#'
        if isinstance(arg, str):
            return check_files(arg, label)
        msg = f'TaxCalcIO.ctor: {label.lower()} is neither None nor str'
        self.errmsg += f'ERROR: {msg}\n'
        return '-x'

    def _read_behavior_file(self, behavior):
        """
        Read the BEHAVIOR file into self.behvdict and check the elasticity
        names and values it contains, appending any errors to self.errmsg.
        Return True if no errors were found; otherwise return False.
        """
        def add_error(msg):
            """
            Append BEHAVIOR file error message to self.errmsg.
            """
            self.errmsg += f'ERROR: BEHAVIOR file {behavior} {msg}\n'
        # read JSON file contents into self.behvdict
        with open(behavior, 'r', encoding='utf-8') as jfile:
            json_text = jfile.read()
        try:
            self.behvdict = json_to_dict(json_text)
        except ValueError as valerr:  # pragma: no cover
            add_error('contains invalid JSON')
            self.errmsg += f'{valerr}'
            return False
        # check elasticity names
        if set(self.behvdict.keys()) != {'esf', 'sub', 'inc', 'cg'}:
            add_error('contains extra or missing parameters')
            self.errmsg += 'Valid parameters are "esf", "sub", "inc", "cg"'
            return False
        # check elasticity values
        if self.behvdict['esf'] < 0.0 or self.behvdict['esf'] > 1.0:
            add_error('contains "esf" outside [0,1] range')
        if self.behvdict['sub'] < 0.0:
            add_error('contains negative "sub" elasticity')
        if self.behvdict['inc'] > 0.0:
            add_error('contains positive "inc" elasticity')
        if self.behvdict['cg'] > 0.0:
            add_error('contains positive "cg" elasticity')
        return not self.errmsg

    @staticmethod
    def _read_poldicts(filespec, specified):
        """
        Return list containing the policy parameter dictionary in each of
        the (possibly several) JSON files named in the BASELINE or REFORM
        filespec; return an empty list if no filespec was specified.
        """
        if not specified:
            return []
        return [
            Calculator.read_json_param_objects(path, None)['policy']
            for path in filespec.split('+')
        ]

    def _make_growdiff(self, growdiff_dict, last_b_year):
        """
        Return GrowDiff object updated using growdiff_dict, appending any
        parameter errors to self.errmsg.
        """
        gdiff = GrowDiff(last_budget_year=last_b_year)
        try:
            gdiff.update_growdiff(growdiff_dict)
        except paramtools.ValidationError as valerr_msg:
            self.errmsg += str(valerr_msg)
        return gdiff

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

    @staticmethod
    def _make_policy(policy_gfactors, last_b_year):
        """
        Return Policy object that uses the specified growfactors.
        """
        return Policy(
            gfactors=policy_gfactors,
            last_budget_year=last_b_year,
        )

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
                if self.errmsg and not self.errmsg.endswith('\n'):
                    self.errmsg += '\n'
                for _, errors in pol.parameter_errors.items():
                    for error in errors:
                        self.errmsg += f'{error.rstrip()}\n'
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

        Note that after this method is called, the calc object contains
        input and output variables that incorporate behavioral responses,
        which means those variables are no longer the ones that a plain
        calc_all() call on the calc object would generate from its own
        Policy parameters.  Any subsequent calc_all() call on the calc
        object would recalculate output variables from the response-
        adjusted input variables; the mtr method is called with
        calc_all_already_called=True in order to avoid doing that.
        """
        int_variables = self.recs_bas.INTEGER_VARS
        mtr_vnames = {'mtr_ptax', 'mtr_itax', 'mtr_combined'}
        for vname in br_dump.columns:
            if vname in mtr_vnames:
                continue
            vdtype = np.int32 if vname in int_variables else np.float64
            calc.array(
                vname,
                br_dump[vname].to_numpy(dtype=vdtype, copy=True)
            )

    def _write_params(self, calc, ext, label, jsonparams=False):
        """
        Write policy parameter values from calc to the ext output file.
        """
        year = calc.current_year
        fname = self.output_filename.replace('.xxx', ext)
        pnames = Policy.parameter_list()
        if jsonparams:
            pdict = {}
            for pname in pnames:
                pval = calc.policy_param(pname)
                # convert NumPy values into JSON-serializable Python values
                if isinstance(pval, np.ndarray):
                    pval = pval.tolist()
                elif isinstance(pval, np.generic):
                    pval = pval.item()
                pdict[pname] = {year: pval}
            with open(fname, 'w', encoding='utf-8') as pfile:
                json.dump(pdict, pfile, indent=4)
                pfile.write('\n')
        else:
            with open(fname, 'w', encoding='utf-8') as pfile:
                for pname in pnames:
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
        change = [ref - bas for ref, bas in zip(reform, base)]
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
        # Note: input data containing too few filing units to populate every
        # decile leave some table_row values unobserved, so each aggregated
        # series is reindexed over all the deciles, with an unpopulated
        # decile getting a zero in every column.
        deciles = range(1, 11)
        gdfx = dfx.groupby('table_row', observed=True)
        series = [
            gdfx.apply(agg, var, include_groups=False).reindex(
                deciles, fill_value=0.
            ).values
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
        # - weights don't change with reform, so use calc_bas as in tables
        pos_wght_sum = self.calc_bas.total_weight() > 0.0
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
