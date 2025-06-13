"""
Tax-Calculator Input-Output class.
"""
# CODING-STYLE CHECKS:
# pycodestyle taxcalcio.py
# pylint --disable=locally-disabled taxcalcio.py

import os
import gc
import copy
import sqlite3
import numpy as np
import pandas as pd
import paramtools
from taxcalc.policy import Policy
from taxcalc.records import Records
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

    runid: int
        run id value to use for simpler output file names

    silent: boolean
        whether or not to suppress action messages.

    Returns
    -------
    class instance: TaxCalcIO
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, input_data, tax_year, baseline, reform, assump,
                 runid=0, silent=True):
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        self.silent = silent
        self.gf_reform = None
        self.errmsg = ''
        # check name and existence of INPUT file
        inp = 'x'
        self.puf_input_data = False
        self.cps_input_data = False
        self.tmd_input_data = False
        self.tmd_weights = None
        self.tmd_gfactor = None
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
            self.puf_input_data = input_data.endswith('puf.csv')
            self.cps_input_data = input_data.endswith('cps.csv')
            self.tmd_input_data = input_data.endswith('tmd.csv')
            if not self.cps_input_data and not os.path.isfile(input_data):
                msg = 'INPUT file could not be found'
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
        bas = '-x'
        if baseline is None:
            self.specified_baseline = False
            bas = '-#'
        elif isinstance(baseline, str):
            self.specified_baseline = True
            # split any compound baseline into list of simple reforms
            basnames = []
            baselines = baseline.split('+')
            for bas in baselines:
                # remove any leading directory path from bas filename
                fname = os.path.basename(bas)
                # check if fname ends with ".json"
                if not fname.endswith('.json'):
                    msg = f'{fname} does not end in .json'
                    self.errmsg += f'ERROR: BASELINE file name {msg}\n'
                # check existence of BASELINE file
                if os.path.isfile(bas):
                    # check validity of JSON text
                    with open(bas, 'r', encoding='utf-8') as jfile:
                        json_text = jfile.read()
                        try:
                            _ = json_to_dict(json_text)
                        except ValueError as valerr:  # pragma: no cover
                            msg = f'{bas} contains invalid JSON'
                            self.errmsg += f'ERROR: BASELINE file {msg}\n'
                            self.errmsg += f'{valerr}'
                else:
                    msg = f'{bas} could not be found'
                    self.errmsg += f'ERROR: BASELINE file {msg}\n'
                # add fname to list of basnames used in output file names
                basnames.append(fname)
            # create (possibly compound) baseline name for output file names
            bas = '-'
            num_basnames = 0
            for basname in basnames:
                num_basnames += 1
                if num_basnames > 1:
                    bas += '+'
                bas += f'{basname[:-5]}'
        else:
            msg = 'TaxCalcIO.ctor: baseline is neither None nor str'
            self.errmsg += f'ERROR: {msg}\n'
        # check name(s) and existence of REFORM file(s)
        ref = '-x'
        if reform is None:
            self.specified_reform = False
            ref = '-#'
        elif isinstance(reform, str):
            self.specified_reform = True
            # split any compound reform into list of simple reforms
            refnames = []
            reforms = reform.split('+')
            for rfm in reforms:
                # remove any leading directory path from rfm filename
                fname = os.path.basename(rfm)
                # check if fname ends with ".json"
                if not fname.endswith('.json'):
                    msg = f'{fname} does not end in .json'
                    self.errmsg += f'ERROR: REFORM file name {msg}\n'
                # check existence of REFORM file
                if os.path.isfile(rfm):
                    # check validity of JSON text
                    with open(rfm, 'r', encoding='utf-8') as jfile:
                        json_text = jfile.read()
                        try:
                            _ = json_to_dict(json_text)
                        except ValueError as valerr:  # pragma: no cover
                            msg = f'{rfm} contains invalid JSON'
                            self.errmsg += f'ERROR: REFORM file {msg}\n'
                            self.errmsg += f'{valerr}'
                else:
                    msg = f'{rfm} could not be found'
                    self.errmsg += f'ERROR: REFORM file {msg}\n'
                # add fname to list of refnames used in output file names
                refnames.append(fname)
            # create (possibly compound) reform name for output file names
            ref = '-'
            num_refnames = 0
            for refname in refnames:
                num_refnames += 1
                if num_refnames > 1:
                    ref += '+'
                ref += f'{refname[:-5]}'
        else:
            msg = 'TaxCalcIO.ctor: reform is neither None nor str'
            self.errmsg += f'ERROR: {msg}\n'
        # check name and existence of ASSUMP file
        asm = '-x'
        if assump is None:
            asm = '-#'
        elif isinstance(assump, str):
            # remove any leading directory path from ASSUMP filename
            fname = os.path.basename(assump)
            # check if fname ends with ".json"
            if fname.endswith('.json'):
                asm = f'-{fname[:-5]}'
            else:
                msg = 'ASSUMP file name does not end in .json'
                self.errmsg += f'ERROR: {msg}\n'
            # check existence of ASSUMP file
            if not os.path.isfile(assump):
                msg = 'ASSUMP file could not be found'
                self.errmsg += f'ERROR: {msg}\n'
        else:
            msg = 'TaxCalcIO.ctor: assump is neither None nor str'
            self.errmsg += f'ERROR: {msg}\n'
        # create OUTPUT file name and delete any existing output files
        self.output_filename = f'{inp}{bas}{ref}{asm}.xxx'
        self.runid = runid
        if runid > 0:
            self.output_filename = f'run{runid}-{str(tax_year)[2:]}.xxx'
        self.delete_output_files()
        # initialize variables whose values are set in init method
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

    def init(self, input_data, tax_year, baseline, reform, assump,
             aging_input_data, exact_calculations):
        """
        TaxCalcIO class post-constructor method that completes initialization.

        Parameters
        ----------
        First five are same as the first five of the TaxCalcIO constructor:
            input_data, tax_year, baseline, reform, assump.

        aging_input_data: boolean
            whether or not to extrapolate Records data from data year to
            tax_year.

        exact_calculations: boolean
            specifies whether or not exact tax calculations are done without
            any smoothing of "stair-step" provisions in the tax law.
        """
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        # pylint: disable=too-many-statements,too-many-branches,too-many-locals
        self.errmsg = ''
        # instantiate base and reform GrowFactors objects
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
        # ... the baseline Policy object
        if self.specified_baseline:
            pol_bas = Policy(
                gfactors=gfactors_bas,
                last_budget_year=last_b_year,
            )
            for poldict in poldicts_bas:
                try:
                    pol_bas.implement_reform(
                        poldict,
                        print_warnings=True,
                        raise_errors=False,
                    )
                    if self.errmsg:
                        self.errmsg += "\n"
                    for _, errors in pol_bas.parameter_errors.items():
                        self.errmsg += "\n".join(errors)
                except paramtools.ValidationError as valerr_msg:
                    self.errmsg += str(valerr_msg)
        else:
            pol_bas = Policy(
                gfactors=gfactors_bas,
                last_budget_year=last_b_year,
            )
        # ... the reform Policy object
        if self.specified_reform:
            pol_ref = Policy(
                gfactors=gfactors_ref,
                last_budget_year=last_b_year,
            )
            for poldict in poldicts_ref:
                try:
                    pol_ref.implement_reform(
                        poldict,
                        print_warnings=True,
                        raise_errors=False,
                    )
                    if self.errmsg:
                        self.errmsg += "\n"
                    for _, errors in pol_ref.parameter_errors.items():
                        self.errmsg += "\n".join(errors)
                except paramtools.ValidationError as valerr_msg:
                    self.errmsg += str(valerr_msg)
        else:
            pol_ref = Policy(
                gfactors=gfactors_bas,
                last_budget_year=last_b_year,
            )
        # create Consumption object
        con = Consumption(last_budget_year=last_b_year)
        try:
            con.update_consumption(assumpdict['consumption'])
        except paramtools.ValidationError as valerr_msg:
            self.errmsg += str(valerr_msg)
        # any errors imply cannot proceed with calculations
        if self.errmsg:
            return
        # set policy to tax_year
        pol_ref.set_year(tax_year)
        pol_bas.set_year(tax_year)
        # read input file contents into Records objects
        if aging_input_data:
            if self.cps_input_data:
                recs_ref = Records.cps_constructor(
                    gfactors=gfactors_ref,
                    exact_calculations=exact_calculations,
                )
                recs_bas = Records.cps_constructor(
                    gfactors=gfactors_bas,
                    exact_calculations=exact_calculations,
                )
            elif self.tmd_input_data:  # pragma: no cover
                wghts = pd.read_csv(self.tmd_weights)
                recs_ref = Records(
                    data=pd.read_csv(input_data),
                    start_year=Records.TMDCSV_YEAR,
                    weights=wghts,
                    gfactors=gfactors_ref,
                    adjust_ratios=None,
                    exact_calculations=exact_calculations,
                    weights_scale=1.0,
                )
                recs_bas = Records(
                    data=pd.read_csv(input_data),
                    start_year=Records.TMDCSV_YEAR,
                    weights=wghts,
                    gfactors=gfactors_bas,
                    adjust_ratios=None,
                    exact_calculations=exact_calculations,
                    weights_scale=1.0,
                )
            else:  # if not {cps|tmd}_input_data but aging_input_data: puf
                recs_ref = Records(
                    data=input_data,
                    gfactors=gfactors_ref,
                    exact_calculations=exact_calculations
                )
                recs_bas = Records(
                    data=input_data,
                    gfactors=gfactors_bas,
                    exact_calculations=exact_calculations
                )
        else:  # input_data are raw data that are not being aged
            recs_ref = Records(
                data=input_data,
                start_year=tax_year,
                gfactors=None,
                weights=None,
                adjust_ratios=None,
                exact_calculations=exact_calculations,
            )
            recs_bas = copy.deepcopy(recs_ref)
        # create Calculator objects
        self.calc_ref = Calculator(
            policy=pol_ref,
            records=recs_ref,
            verbose=(not self.silent),
            consumption=con,
            sync_years=aging_input_data,
        )
        self.calc_bas = Calculator(
            policy=pol_bas,
            records=recs_bas,
            verbose=False,
            consumption=con,
            sync_years=aging_input_data,
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

    def advance_to_year(self, year, aging_data):
        """
        Update self.output_filename and advance Calculator objects to year.
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
        # advance baseline and reform Calculator objects to specified year
        self.calc_bas.advance_to_year(year)
        self.calc_ref.advance_to_year(year)
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
        self.calc_bas.calc_all()
        self.calc_ref.calc_all()
        if output_dump:
            assert isinstance(dump_varlist, list)
            assert len(dump_varlist) > 0
            # might need marginal tax rates for dumpdb
            (mtr_ptax_ref, mtr_itax_ref,
             _) = self.calc_ref.mtr(wrt_full_compensation=False,
                                    calc_all_already_called=True)
            (mtr_ptax_bas, mtr_itax_bas,
             _) = self.calc_bas.mtr(wrt_full_compensation=False,
                                    calc_all_already_called=True)
        else:
            # do not need marginal tax rates for dumpdb
            mtr_ptax_ref = None
            mtr_itax_ref = None
            mtr_ptax_bas = None
            mtr_itax_bas = None
        # optionally write --tables output to text file
        if output_tables:
            self.write_tables_file()
        # optionally write --graphs output to HTML files
        if output_graphs:
            self.write_graph_files()
        # optionally write --dumpdb output to SQLite database file
        if output_dump:
            self.write_dumpdb_file(
                dump_varlist,
                mtr_ptax_ref, mtr_itax_ref,
                mtr_ptax_bas, mtr_itax_bas,
            )

    def write_policy_params_files(self):
        """
        Write baseline and reform policy parameter values to separate files.
        """
        year = self.calc_bas.current_year
        param_names = Policy.parameter_list()
        fname = self.output_filename.replace('.xxx', '-params.baseline')
        with open(fname, 'w', encoding='utf-8') as pfile:
            for pname in param_names:
                pval = self.calc_bas.policy_param(pname)
                pfile.write(f'{year} {pname} {pval}\n')
        if not self.silent:
            print(  # pragma: no cover
                f'Write baseline policy parameter values to file {fname}'
            )
        fname = self.output_filename.replace('.xxx', '-params.reform')
        with open(fname, 'w', encoding='utf-8') as pfile:
            for pname in param_names:
                pval = self.calc_ref.policy_param(pname)
                pfile.write(f'{year} {pname} {pval}\n')
        if not self.silent:
            print(  # pragma: no cover
                f'Write reform policy parameter values to file {fname}'
            )

    def write_tables_file(self):
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
            TaxCalcIO.write_decile_table(
                distdf,
                tfile,
                year,
                tkind='Reform Totals',
            )
            tfile.write('\n')
            TaxCalcIO.write_decile_table(
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
    def write_decile_table(dfx, tfile, year, tkind='Totals'):
        """
        Write to tfile the tkind decile table using dfx DataFrame.
        """
        dfx = add_quantile_table_row_variable(dfx, 'expanded_income', 10,
                                              decile_details=False,
                                              pop_quantiles=False,
                                              weight_by_income_measure=False)
        gdfx = dfx.groupby('table_row', as_index=False, observed=True)
        rtns_series = gdfx.apply(
            unweighted_sum, 's006', include_groups=False
        ).values[:, 1]
        xinc_series = gdfx.apply(
            weighted_sum, 'expanded_income', include_groups=False
        ).values[:, 1]
        itax_series = gdfx.apply(
            weighted_sum, 'iitax', include_groups=False
        ).values[:, 1]
        ptax_series = gdfx.apply(
            weighted_sum, 'payrolltax', include_groups=False
        ).values[:, 1]
        htax_series = gdfx.apply(
            weighted_sum, 'lumpsum_tax', include_groups=False
        ).values[:, 1]
        ctax_series = gdfx.apply(
            weighted_sum, 'combined', include_groups=False
        ).values[:, 1]
        # write decile table to text file
        row = (
            f'Weighted Tax {tkind} by '
            f'Baseline Expanded-Income Decile for {year}\n'
        )
        tfile.write(row)
        # pylint: disable=consider-using-f-string
        rowfmt = '{}{}{}{}{}{}\n'
        row = rowfmt.format('    Returns',
                            '    ExpInc',
                            '    IncTax',
                            '    PayTax',
                            '     LSTax',
                            '    AllTax')
        tfile.write(row)
        row = rowfmt.format('       (#m)',
                            '      ($b)',
                            '      ($b)',
                            '      ($b)',
                            '      ($b)',
                            '      ($b)')
        tfile.write(row)
        rowfmt = '{:9.2f}{:10.1f}{:10.1f}{:10.1f}{:10.1f}{:10.1f}\n'
        for decile in range(0, 10):
            row = f'{decile:2d}'
            row += rowfmt.format(rtns_series[decile] * 1e-6,
                                 xinc_series[decile] * 1e-9,
                                 itax_series[decile] * 1e-9,
                                 ptax_series[decile] * 1e-9,
                                 htax_series[decile] * 1e-9,
                                 ctax_series[decile] * 1e-9)
            tfile.write(row)
        row = ' A'
        row += rowfmt.format(rtns_series.sum() * 1e-6,
                             xinc_series.sum() * 1e-9,
                             itax_series.sum() * 1e-9,
                             ptax_series.sum() * 1e-9,
                             htax_series.sum() * 1e-9,
                             ctax_series.sum() * 1e-9)
        tfile.write(row)
        # pylint: enable=consider-using-f-string
        del gdfx
        del rtns_series
        del xinc_series
        del itax_series
        del ptax_series
        del htax_series
        del ctax_series
        gc.collect()

    def write_graph_files(self):
        """
        Write graphs to HTML files.
        All graphs contain same number of filing units in each quantile.
        """
        pos_wght_sum = self.calc_ref.total_weight() > 0.0
        fig = None
        # percentage-aftertax-income-change graph
        pch_fname = self.output_filename.replace('.xxx', '-chg.html')
        pch_title = 'CHG by Income Percentile'
        if pos_wght_sum:
            fig = self.calc_bas.pch_graph(self.calc_ref, pop_quantiles=False)
            write_graph_file(fig, pch_fname, pch_title)
        else:
            reason = 'No graph because sum of weights is not positive'
            TaxCalcIO.write_empty_graph_file(pch_fname, pch_title, reason)
        # average-tax-rate graph
        atr_fname = self.output_filename.replace('.xxx', '-atr.html')
        atr_title = 'ATR by Income Percentile'
        if pos_wght_sum:
            fig = self.calc_bas.atr_graph(self.calc_ref, pop_quantiles=False)
            write_graph_file(fig, atr_fname, atr_title)
        else:
            reason = 'No graph because sum of weights is not positive'
            TaxCalcIO.write_empty_graph_file(atr_fname, atr_title, reason)
        # marginal-tax-rate graph
        mtr_fname = self.output_filename.replace('.xxx', '-mtr.html')
        mtr_title = 'MTR by Income Percentile'
        if pos_wght_sum:
            fig = self.calc_bas.mtr_graph(
                self.calc_ref,
                alt_e00200p_text='Taxpayer Earnings',
                pop_quantiles=False
            )
            write_graph_file(fig, mtr_fname, mtr_title)
        else:
            reason = 'No graph because sum of weights is not positive'
            TaxCalcIO.write_empty_graph_file(mtr_fname, mtr_title, reason)
        if fig:
            del fig
            gc.collect()
        if not self.silent:
            print(  # pragma: no cover
                f'Write graphical output to file {pch_fname}\n'
                f'Write graphical output to file {atr_fname}\n'
                f'Write graphical output to file {mtr_fname}'
            )

    @staticmethod
    def write_empty_graph_file(fname, title, reason):
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
        # change some common non-space delimiter characters into spaces
        dumpvars_str = dumpvars_str.replace(',', ' ')
        dumpvars_str = dumpvars_str.replace(';', ' ')
        dumpvars_str = dumpvars_str.replace('|', ' ')
        # split dumpvars_str into a set of dump variables
        dumpvars = dumpvars_str.split()
        # check that all dumpvars items are valid
        recs_vinfo = Records(data=None)  # contains records VARINFO only
        valid_set = recs_vinfo.USABLE_READ_VARS | recs_vinfo.CALCULATED_VARS
        for var in dumpvars:
            if var not in valid_set and var not in TaxCalcIO.MTR_DUMPVARS:
                msg = f'invalid variable name {var} in DUMPVARS file'
                self.errmsg += f'ERROR: {msg}\n'
        if self.errmsg:
            return []
        # construct variable list
        dumpvars_list = TaxCalcIO.MINIMAL_DUMPVARS
        for var in dumpvars:
            if var not in dumpvars_list and var not in TaxCalcIO.BASE_DUMPVARS:
                dumpvars_list.append(var)
        return dumpvars_list

    def write_dumpdb_file(
            self,
            dump_varlist,
            mtr_ptax_ref, mtr_itax_ref,
            mtr_ptax_bas, mtr_itax_bas,
    ):
        """
        Write dump output to SQLite database file.
        """
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        def dump_output(calcx, dumpvars, mtr_itax, mtr_ptax):
            """
            Extract dump output from calcx and return it as Pandas DataFrame.
            """
            odf = pd.DataFrame()
            for var in dumpvars:
                if var in TaxCalcIO.MTR_DUMPVARS:
                    if var == 'mtr_itax':
                        odf[var] = mtr_itax
                    elif var == 'mtr_ptax':
                        odf[var] = mtr_ptax
                else:
                    odf[var] = calcx.array(var)
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
        outdf = dump_output(
            self.calc_bas, dump_varlist, mtr_itax_bas, mtr_ptax_bas,
        )
        assert len(outdf.index) == self.calc_bas.array_len
        outdf.to_sql('baseline', dbcon, index=False)
        del outdf
        # write reform table
        outdf = dump_output(
            self.calc_ref, dump_varlist, mtr_itax_ref, mtr_ptax_ref,
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
