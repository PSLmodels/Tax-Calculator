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
from taxcalc.utils import (delete_file, write_graph_file,
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

    silent: boolean
        whether or not to suppress action messages.

    outdir: None or string
        None implies output files written to current directory,
        or string is name of optional output directory

    Returns
    -------
    class instance: TaxCalcIO
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, input_data, tax_year, baseline, reform, assump,
                 silent=True, outdir=None):
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
        # check name and existence of BASELINE file
        bas = '-x'
        if baseline is None:
            bas = '-#'
        elif isinstance(baseline, str):
            # remove any leading directory path from BASELINE filename
            fname = os.path.basename(baseline)
            # check if fname ends with ".json"
            if fname.endswith('.json'):
                bas = f'-{fname[:-5]}'
            else:
                msg = 'BASELINE file name does not end in .json'
                self.errmsg += f'ERROR: {msg}\n'
            # check existence of BASELINE file
            if not os.path.isfile(baseline):
                msg = 'BASELINE file could not be found'
                self.errmsg += f'ERROR: {msg}\n'
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
                if not os.path.isfile(rfm):
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
        # check name and existence of OUTDIR
        if outdir is None:
            valid_outdir = True
        elif isinstance(outdir, str):
            # check existence of OUTDIR
            if os.path.isdir(outdir):
                valid_outdir = True
            else:
                valid_outdir = False
                msg = 'OUTDIR could not be found'
                self.errmsg += f'ERROR: {msg}\n'
        else:
            valid_outdir = False
            msg = 'TaxCalcIO.ctor: outdir is neither None nor str'
            self.errmsg += f'ERROR: {msg}\n'
        # create OUTPUT file name and delete any existing output files
        output_filename = f'{inp}{bas}{ref}{asm}.csv'
        if outdir is None:
            self._output_filename = output_filename
            delete_old_files = True
        elif valid_outdir:
            self._output_filename = os.path.join(outdir, output_filename)
            delete_old_files = True
        else:
            delete_old_files = False
        if delete_old_files:
            delete_file(self._output_filename)
            delete_file(self._output_filename.replace('.csv', '.db'))
            delete_file(self._output_filename.replace('.csv', '-doc.text'))
            delete_file(self._output_filename.replace('.csv', '-tab.text'))
            delete_file(self._output_filename.replace('.csv', '-atr.html'))
            delete_file(self._output_filename.replace('.csv', '-mtr.html'))
            delete_file(self._output_filename.replace('.csv', '-pch.html'))
        # initialize variables whose values are set in init method
        self.calc = None
        self.calc_base = None
        self.param_dict = None
        self.policy_dicts = []

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
            gfactors_base = GrowFactors(self.tmd_gfactor)  # pragma: no cover
            gfactors_ref = GrowFactors(self.tmd_gfactor)  # pragma: no cover
        else:
            gfactors_base = GrowFactors()
            gfactors_ref = GrowFactors()
        # check tax_year validity
        max_tax_year = gfactors_base.last_year
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
        # get policy parameter dictionary from --baseline file
        basedict = Calculator.read_json_param_objects(baseline, None)
        # get assumption sub-dictionaries
        paramdict = Calculator.read_json_param_objects(None, assump)
        # get policy parameter dictionaries from --reform file(s)
        policydicts = []
        if self.specified_reform:
            reforms = reform.split('+')
            for ref in reforms:
                pdict = Calculator.read_json_param_objects(ref, None)
                policydicts.append(pdict['policy'])
            paramdict['policy'] = policydicts[0]
        # remember parameters for reform documentation
        self.param_dict = paramdict
        self.policy_dicts = policydicts
        # set last_b_year
        last_b_year = max(tax_year, Policy.LAST_BUDGET_YEAR)
        # create gdiff_baseline object
        gdiff_baseline = GrowDiff(last_budget_year=last_b_year)
        try:
            gdiff_baseline.update_growdiff(paramdict['growdiff_baseline'])
        except paramtools.ValidationError as valerr_msg:
            self.errmsg += str(valerr_msg)
        # apply gdiff_baseline to gfactor_base
        gdiff_baseline.apply_to(gfactors_base)
        # specify gdiff_response object
        gdiff_response = GrowDiff(last_budget_year=last_b_year)
        try:
            gdiff_response.update_growdiff(paramdict['growdiff_response'])
        except paramtools.ValidationError as valerr_msg:
            self.errmsg += str(valerr_msg)
        # apply gdiff_baseline and gdiff_response to gfactor_ref
        gdiff_baseline.apply_to(gfactors_ref)
        gdiff_response.apply_to(gfactors_ref)
        self.gf_reform = copy.deepcopy(gfactors_ref)
        # create Policy objects:
        # ... the baseline Policy object
        base = Policy(gfactors=gfactors_base, last_budget_year=last_b_year)
        try:
            base.implement_reform(basedict['policy'],
                                  print_warnings=True,
                                  raise_errors=False)
            for _, errors in base.parameter_errors.items():
                self.errmsg += "\n".join(errors)
        except paramtools.ValidationError as valerr_msg:
            self.errmsg += str(valerr_msg)
        # ... the reform Policy object
        if self.specified_reform:
            pol = Policy(gfactors=gfactors_ref, last_budget_year=last_b_year)
            for poldict in policydicts:
                try:
                    pol.implement_reform(poldict,
                                         print_warnings=True,
                                         raise_errors=False)
                    if self.errmsg:
                        self.errmsg += "\n"
                    for _, errors in pol.parameter_errors.items():
                        self.errmsg += "\n".join(errors)
                except paramtools.ValidationError as valerr_msg:
                    self.errmsg += str(valerr_msg)
        else:
            pol = Policy(gfactors=gfactors_base, last_budget_year=last_b_year)
        # create Consumption object
        con = Consumption(last_budget_year=last_b_year)
        try:
            con.update_consumption(paramdict['consumption'])
        except paramtools.ValidationError as valerr_msg:
            self.errmsg += str(valerr_msg)
        # any errors imply cannot proceed with calculations
        if self.errmsg:
            return
        # set policy to tax_year
        pol.set_year(tax_year)
        base.set_year(tax_year)
        # read input file contents into Records objects
        if aging_input_data:
            if self.cps_input_data:
                recs = Records.cps_constructor(
                    gfactors=gfactors_ref,
                    exact_calculations=exact_calculations
                )
                recs_base = Records.cps_constructor(
                    gfactors=gfactors_base,
                    exact_calculations=exact_calculations
                )
            elif self.tmd_input_data:  # pragma: no cover
                wghts = pd.read_csv(self.tmd_weights)
                recs = Records(
                    data=pd.read_csv(input_data),
                    start_year=Records.TMDCSV_YEAR,
                    weights=wghts,
                    gfactors=gfactors_ref,
                    adjust_ratios=None,
                    exact_calculations=exact_calculations,
                    weights_scale=1.0,
                )
                recs_base = Records(
                    data=pd.read_csv(input_data),
                    start_year=Records.TMDCSV_YEAR,
                    weights=wghts,
                    gfactors=gfactors_base,
                    adjust_ratios=None,
                    exact_calculations=exact_calculations,
                    weights_scale=1.0,
                )
            else:  # if not {cps|tmd}_input_data but aging_input_data: puf
                recs = Records(
                    data=input_data,
                    gfactors=gfactors_ref,
                    exact_calculations=exact_calculations
                )
                recs_base = Records(
                    data=input_data,
                    gfactors=gfactors_base,
                    exact_calculations=exact_calculations
                )
        else:  # input_data are raw data that are not being aged
            recs = Records(data=input_data,
                           start_year=tax_year,
                           gfactors=None,
                           weights=None,
                           adjust_ratios=None,
                           exact_calculations=exact_calculations)
            recs_base = copy.deepcopy(recs)
        # create Calculator objects
        self.calc = Calculator(policy=pol, records=recs,
                               verbose=(not self.silent),
                               consumption=con,
                               sync_years=aging_input_data)
        self.calc_base = Calculator(policy=base, records=recs_base,
                                    verbose=False,
                                    consumption=con,
                                    sync_years=aging_input_data)

    def custom_dump_variables(self, tcdumpvars_str):
        """
        Return set of variable names extracted from tcdumpvars_str, which
        contains the contents of the tcdumpvars file in the current directory.
        Also, builds self.errmsg if any custom variables are not valid.
        """
        assert isinstance(tcdumpvars_str, str)
        self.errmsg = ''
        # change some common delimiter characters into spaces
        dump_vars_str = tcdumpvars_str.replace(',', ' ')
        dump_vars_str = dump_vars_str.replace(';', ' ')
        dump_vars_str = dump_vars_str.replace('|', ' ')
        # split dump_vars_str into a list of dump variables
        dump_vars_list = dump_vars_str.split()
        # check that all dump_vars_list items are valid
        recs_vinfo = Records(data=None)  # contains records VARINFO only
        valid_set = recs_vinfo.USABLE_READ_VARS | recs_vinfo.CALCULATED_VARS
        for var in dump_vars_list:
            if var not in valid_set:
                msg = f'invalid variable name in tcdumpvars file: {var}'
                self.errmsg += f'ERROR: {msg}\n'
        # add essential variables even if not on custom list
        if 'RECID' not in dump_vars_list:
            dump_vars_list.append('RECID')
        if 'FLPDYR' not in dump_vars_list:
            dump_vars_list.append('FLPDYR')
        # convert list into a set and return
        return set(dump_vars_list)

    def tax_year(self):
        """
        Return calendar year for which TaxCalcIO calculations are being done.
        """
        return self.calc.current_year

    def output_filepath(self):
        """
        Return full path to output file named in TaxCalcIO constructor.
        """
        dirpath = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(dirpath, self._output_filename)

    def analyze(self, writing_output_file=False,
                output_tables=False,
                output_graphs=False,
                dump_varset=None,
                output_dump=False,
                output_sqldb=False):
        """
        Conduct tax analysis.

        Parameters
        ----------
        writing_output_file: boolean
           whether or not to generate and write output file

        output_tables: boolean
           whether or not to generate and write distributional tables
           to a text file

        output_graphs: boolean
           whether or not to generate and write HTML graphs of average
           and marginal tax rates by income percentile

        dump_varset: set
           custom set of variables to include in dump and sqldb output;
           None implies include all variables in dump and sqldb output

        output_dump: boolean
           whether or not to replace standard output with all input and
           calculated variables using their Tax-Calculator names

        output_sqldb: boolean
           whether or not to write SQLite3 database with two tables
           (baseline and reform) each containing same output as written
           by output_dump to a csv file

        Returns
        -------
        Nothing
        """
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        # pylint: disable=too-many-branches,too-many-locals
        if self.puf_input_data and self.calc.reform_warnings:
            print(  # pragma: no cover
                'PARAMETER VALUE WARNING(S):  '
                '(read documentation for each parameter)\n'
                f'{self.calc.reform_warnings}'
                'CONTINUING WITH CALCULATIONS...'
            )
        calc_base_calculated = False
        self.calc.calc_all()
        if output_dump or output_sqldb:
            # might need marginal tax rates
            (mtr_paytax, mtr_inctax,
             _) = self.calc.mtr(wrt_full_compensation=False,
                                calc_all_already_called=True)
            self.calc_base.calc_all()
            calc_base_calculated = True
            (mtr_paytax_base, mtr_inctax_base,
             _) = self.calc_base.mtr(wrt_full_compensation=False,
                                     calc_all_already_called=True)
        else:
            # definitely do not need marginal tax rates
            mtr_paytax = None
            mtr_inctax = None
            mtr_paytax_base = None
            mtr_inctax_base = None
        # extract output if writing_output_file
        if writing_output_file:
            self.write_output_file(output_dump, dump_varset,
                                   mtr_paytax, mtr_inctax)
            self.write_doc_file()
        # optionally write --sqldb output to SQLite3 database
        if output_sqldb:
            self.write_sqldb_file(
                dump_varset, mtr_paytax, mtr_inctax,
                mtr_paytax_base, mtr_inctax_base
            )
        # optionally write --tables output to text file
        if output_tables:
            if not calc_base_calculated:
                self.calc_base.calc_all()
                calc_base_calculated = True
            self.write_tables_file()
        # optionally write --graphs output to HTML files
        if output_graphs:
            if not calc_base_calculated:
                self.calc_base.calc_all()
                calc_base_calculated = True
            self.write_graph_files()

    def write_output_file(self, output_dump, dump_varset,
                          mtr_paytax, mtr_inctax):
        """
        Write output to CSV-formatted file.
        """
        if output_dump:
            outdf = self.dump_output(
                self.calc, dump_varset, mtr_inctax, mtr_paytax
            )
            column_order = sorted(outdf.columns)
            # place RECID at start of column_order list
            assert 'RECID' in column_order, 'RECID not in dump output list'
            column_order.remove('RECID')
            column_order.insert(0, 'RECID')
            weight_vname = 's006'
        else:
            outdf = self.minimal_output()
            column_order = outdf.columns
            weight_vname = 'WEIGHT'
        assert len(outdf.index) == self.calc.array_len
        if self.tmd_input_data:  # pragma: no cover
            if weight_vname in outdf:
                weights = outdf[weight_vname].round(5)
            outdf = outdf.round(2)
            if weight_vname in outdf:
                outdf[weight_vname] = weights
            outdf.to_csv(self._output_filename, columns=column_order,
                         index=False)
        else:
            outdf.to_csv(self._output_filename, columns=column_order,
                         index=False, float_format='%.2f')
        del outdf
        gc.collect()
        if not self.silent:
            print(  # pragma: no cover
                f'Write tax-unit output to file {self._output_filename}'
            )

    def write_doc_file(self):
        """
        Write reform documentation to text file.
        """
        if len(self.policy_dicts) <= 1:
            doc = Calculator.reform_documentation(
                self.param_dict, self.gf_reform
            )
        else:
            doc = Calculator.reform_documentation(
                self.param_dict, self.gf_reform, self.policy_dicts[1:]
            )
        doc_fname = self._output_filename.replace('.csv', '-doc.text')
        with open(doc_fname, 'w', encoding='utf-8') as dfile:
            dfile.write(doc)
        if not self.silent:
            print(  # pragma: no cover
                f'Write reform documentation to file {doc_fname}'
            )

    def write_sqldb_file(self, dump_varset, mtr_paytax, mtr_inctax,
                         mtr_paytax_base, mtr_inctax_base):
        """
        Write dump output to SQLite3 database table dump.
        """
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        db_fname = self._output_filename.replace('.csv', '.db')
        dbcon = sqlite3.connect(db_fname)
        # write baseline table
        outdf = self.dump_output(
            self.calc_base, dump_varset, mtr_inctax_base, mtr_paytax_base
        )
        assert len(outdf.index) == self.calc.array_len
        outdf.to_sql('baseline', dbcon, if_exists='replace', index=False)
        # write reform table
        outdf = self.dump_output(
            self.calc, dump_varset, mtr_inctax, mtr_paytax
        )
        assert len(outdf.index) == self.calc.array_len
        outdf.to_sql('reform', dbcon, if_exists='replace', index=False)
        dbcon.close()
        del outdf
        gc.collect()
        if not self.silent:
            print(  # pragma: no cover
                f'Write tax-unit output to sqlite3 database file {db_fname}'
            )

    def write_tables_file(self):
        """
        Write tables to text file.
        """
        # pylint: disable=too-many-locals
        tab_fname = self._output_filename.replace('.csv', '-tab.text')
        # skip tables if there are not some positive weights
        if self.calc_base.total_weight() <= 0.:
            with open(tab_fname, 'w', encoding='utf-8') as tfile:
                msg = 'No tables because sum of weights is not positive\n'
                tfile.write(msg)
            return
        # create list of results for nontax variables
        # - weights don't change with reform
        # - expanded_income may change, so always use baseline expanded income
        nontax_vars = ['s006', 'expanded_income']
        nontax = [self.calc_base.array(var) for var in nontax_vars]
        # create list of results for tax variables from reform Calculator
        tax_vars = ['iitax', 'payrolltax', 'lumpsum_tax', 'combined']
        reform = [self.calc.array(var) for var in tax_vars]
        # create DataFrame with tax distribution under reform
        dist = nontax + reform  # using expanded_income under baseline policy
        all_vars = nontax_vars + tax_vars
        distdf = pd.DataFrame(data=np.column_stack(dist), columns=all_vars)
        # create DataFrame with tax differences (reform - baseline)
        base = [self.calc_base.array(var) for var in tax_vars]
        change = [(reform[idx] - base[idx]) for idx in range(0, len(tax_vars))]
        diff = nontax + change  # using expanded_income under baseline policy
        diffdf = pd.DataFrame(data=np.column_stack(diff), columns=all_vars)
        # write each kind of distributional table
        with open(tab_fname, 'w', encoding='utf-8') as tfile:
            TaxCalcIO.write_decile_table(distdf, tfile, tkind='Reform Totals')
            tfile.write('\n')
            TaxCalcIO.write_decile_table(diffdf, tfile, tkind='Differences')
        # delete intermediate DataFrame objects
        del distdf
        del diffdf
        gc.collect()
        if not self.silent:
            print(  # pragma: no cover
                f'Write tabular output to file {tab_fname}'
            )

    @staticmethod
    def write_decile_table(dfx, tfile, tkind='Totals'):
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
        row = f'Weighted Tax {tkind} by Baseline Expanded-Income Decile\n'
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
        pos_wght_sum = self.calc.total_weight() > 0.0
        fig = None
        # percentage-aftertax-income-change graph
        pch_fname = self._output_filename.replace('.csv', '-pch.html')
        pch_title = 'PCH by Income Percentile'
        if pos_wght_sum:
            fig = self.calc_base.pch_graph(self.calc, pop_quantiles=False)
            write_graph_file(fig, pch_fname, pch_title)
        else:
            reason = 'No graph because sum of weights is not positive'
            TaxCalcIO.write_empty_graph_file(pch_fname, pch_title, reason)
        # average-tax-rate graph
        atr_fname = self._output_filename.replace('.csv', '-atr.html')
        atr_title = 'ATR by Income Percentile'
        if pos_wght_sum:
            fig = self.calc_base.atr_graph(self.calc, pop_quantiles=False)
            write_graph_file(fig, atr_fname, atr_title)
        else:
            reason = 'No graph because sum of weights is not positive'
            TaxCalcIO.write_empty_graph_file(atr_fname, atr_title, reason)
        # marginal-tax-rate graph
        mtr_fname = self._output_filename.replace('.csv', '-mtr.html')
        mtr_title = 'MTR by Income Percentile'
        if pos_wght_sum:
            fig = self.calc_base.mtr_graph(
                self.calc,
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

    def minimal_output(self):
        """
        Extract minimal output and return it as Pandas DataFrame.
        """
        varlist = ['RECID', 'YEAR', 'WEIGHT', 'INCTAX', 'LSTAX', 'PAYTAX']
        odict = {}
        scalc = self.calc
        odict['RECID'] = scalc.array('RECID')  # id for tax filing unit
        odict['YEAR'] = self.tax_year()  # tax calculation year
        odict['WEIGHT'] = scalc.array('s006')  # sample weight
        odict['INCTAX'] = scalc.array('iitax')  # federal income taxes
        odict['LSTAX'] = scalc.array('lumpsum_tax')  # lump-sum tax
        odict['PAYTAX'] = scalc.array('payrolltax')  # payroll taxes (ee+er)
        odf = pd.DataFrame(data=odict, columns=varlist)
        return odf

    def dump_output(self, calcx, dump_varset, mtr_inctax, mtr_paytax):
        """
        Extract dump output and return it as Pandas DataFrame.
        """
        recs_vinfo = Records(data=None)  # contains only Records VARINFO
        if dump_varset is None:
            varset = recs_vinfo.USABLE_READ_VARS | recs_vinfo.CALCULATED_VARS
        else:
            varset = dump_varset
        # create and return dump output DataFrame
        odf = pd.DataFrame()
        for varname in varset:
            vardata = calcx.array(varname)
            if varname in recs_vinfo.INTEGER_VARS:
                odf[varname] = vardata
            else:  # specify precision that can handle small TMD area weights
                odf[varname] = vardata.round(5)
            odf = odf.copy()
        # specify mtr values in percentage terms
        if 'mtr_inctax' in varset:
            odf['mtr_inctax'] = (mtr_inctax * 100).round(2)
        if 'mtr_paytax' in varset:
            odf['mtr_paytax'] = (mtr_paytax * 100).round(2)
        # specify tax calculation year
        odf['FLPDYR'] = self.tax_year()
        return odf
