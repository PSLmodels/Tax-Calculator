"""
Tax-Calculator Input-Output class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 taxcalcio.py
# pylint --disable=locally-disabled taxcalcio.py

import os
import copy
import six
import pandas as pd
from taxcalc.policy import Policy
from taxcalc.records import Records
from taxcalc.consumption import Consumption
from taxcalc.behavior import Behavior
from taxcalc.growdiff import Growdiff
from taxcalc.growfactors import Growfactors
from taxcalc.calculate import Calculator
from taxcalc.utils import delete_file
from taxcalc.utils import ce_aftertax_income
from taxcalc.utils import atr_graph_data, mtr_graph_data
from taxcalc.utils import xtr_graph_plot, write_graph_file


class TaxCalcIO(object):
    """
    Constructor for the Tax-Calculator Input-Output class.

    Parameters
    ----------
    input_data: string or Pandas DataFrame
        string is name of INPUT file that is CSV formatted containing
        variable names in the Records.USABLE_READ_VARS set, or
        Pandas DataFrame is INPUT data containing variable names in
        the Records.USABLE_READ_VARS set.  INPUT vsrisbles not in the
        Records.USABLE_READ_VARS set can be present but are ignored.

    tax_year: integer
        calendar year for which taxes will be computed for INPUT.

    reform: None or string
        None implies no policy reform (current-law policy), or
        string is name of optional REFORM file.

    assump: None or string
        None implies economic assumptions are standard assumptions,
        or string is name of optional ASSUMP file.

    growdiff_response: Growdiff object or None
        growdiff_response Growdiff object used only in dynamic analysis;
        must be None when not conducting dynamic analysis.

    aging_input_data: boolean
        whether or not to extrapolate Records data from data year to tax_year.

    exact_calculations: boolean
        specifies whether or not exact tax calculations are done without
        any smoothing of "stair-step" provisions in the tax law.

    Raises
    ------
    ValueError:
        if input_data is neither string nor pandas DataFrame.
        if input_data string does not have .csv extension.
        if file specified by input_data string does not exist.
        if reform is neither None nor string.
        if reform string does not have .json extension.
        if file specified by reform string does not exist.
        if assump is neither None nor string.
        if assump string does not have .json extension.
        if growdiff_response is not a Growdiff object or None
        if file specified by assump string does not exist.
        if tax_year before Policy start_year.
        if tax_year after Policy end_year.
        if growdiff_response in --assump ASSUMP has any response.

    Returns
    -------
    class instance: TaxCalcIO
    """

    def __init__(self, input_data, tax_year, reform, assump,
                 growdiff_response,  # =None except in dynamic analysis
                 aging_input_data, exact_calculations):
        """
        TaxCalcIO class constructor.
        """
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
        # check for existence of INPUT file
        if isinstance(input_data, six.string_types):
            # remove any leading directory path from INPUT filename
            fname = os.path.basename(input_data)
            # check if fname ends with ".csv"
            if fname.endswith('.csv'):
                inp = '{}-{}'.format(fname[:-4], str(tax_year)[2:])
            else:
                msg = 'INPUT file named {} does not end in .csv'
                raise ValueError(msg.format(fname))
            # check existence of INPUT file
            if not os.path.isfile(input_data):
                msg = 'INPUT file named {} could not be found'
                raise ValueError(msg.format(input_data))
        elif isinstance(input_data, pd.DataFrame):
            inp = 'df-{}'.format(str(tax_year)[2:])
        else:
            msg = 'INPUT is neither string nor Pandas DataFrame'
            raise ValueError(msg)
        # construct output_filename and delete old output files if they exist
        if reform is None:
            self._reform = False
            ref = '-clp'
        elif isinstance(reform, six.string_types):
            self._reform = True
            # remove any leading directory path from REFORM filename
            fname = os.path.basename(reform)
            # check if fname ends with ".json"
            if fname.endswith('.json'):
                ref = '-{}'.format(fname[:-5])
            else:
                msg = 'REFORM file named {} does not end in .json'
                raise ValueError(msg.format(fname))
        else:
            msg = 'TaxCalcIO.ctor reform is neither None nor str'
            raise ValueError(msg)
        if assump is None:
            asm = '-std'
        elif isinstance(assump, six.string_types):
            # remove any leading directory path from ASSUMP filename
            fname = os.path.basename(assump)
            # check if fname ends with ".json"
            if fname.endswith('.json'):
                asm = '-{}'.format(fname[:-5])
            else:
                msg = 'ASSUMP file named {} does not end in .json'
                raise ValueError(msg.format(fname))
        else:
            msg = 'TaxCalcIO.ctor assump is neither None nor str'
            raise ValueError(msg)
        self._output_filename = '{}{}{}.csv'.format(inp, ref, asm)
        delete_file(self._output_filename)
        delete_file(self._output_filename.replace('.csv', '-atr.html'))
        delete_file(self._output_filename.replace('.csv', '-mtr.html'))
        # get parameter dictionaries from --reform and --assump files
        param_dict = Calculator.read_json_param_files(reform, assump)
        # make sure no growdiff_response is specified in --assump
        gdiff_response = Growdiff()
        gdiff_response.update_growdiff(param_dict['growdiff_response'])
        if gdiff_response.has_any_response():
            msg = '--assump ASSUMP cannot assume any "growdiff_response"'
            raise ValueError(msg)
        # create gdiff_baseline object
        gdiff_baseline = Growdiff()
        gdiff_baseline.update_growdiff(param_dict['growdiff_baseline'])
        # create Growfactors clp object that incorporates gdiff_baseline
        gfactors_clp = Growfactors()
        gdiff_baseline.apply_to(gfactors_clp)
        # specify gdiff_response object
        if growdiff_response is None:
            gdiff_response = Growdiff()
        elif isinstance(growdiff_response, Growdiff):
            gdiff_response = growdiff_response
        else:
            msg = 'TaxCalcIO.ctor growdiff_response is neither None nor {}'
            raise ValueError(msg.format('a Growdiff object'))
        # create Growfactors ref object that has both gdiff objects applied
        gfactors_ref = Growfactors()
        gdiff_baseline.apply_to(gfactors_ref)
        gdiff_response.apply_to(gfactors_ref)
        # create Policy object and implement reform if specified
        if self._reform:
            pol = Policy(gfactors=gfactors_ref)
            pol.implement_reform(param_dict['policy'])
            clp = Policy(gfactors=gfactors_clp)
        else:
            pol = Policy(gfactors=gfactors_clp)
        # check for valid tax_year value
        if tax_year < pol.start_year:
            msg = 'tax_year {} less than policy.start_year {}'
            raise ValueError(msg.format(tax_year, pol.start_year))
        if tax_year > pol.end_year:
            msg = 'tax_year {} greater than policy.end_year {}'
            raise ValueError(msg.format(tax_year, pol.end_year))
        # set policy to tax_year
        pol.set_year(tax_year)
        if self._reform:
            clp.set_year(tax_year)
        # read input file contents into Records object(s)
        if aging_input_data:
            if self._reform:
                recs = Records(data=input_data,
                               gfactors=gfactors_ref,
                               exact_calculations=exact_calculations)
                recs_clp = Records(data=input_data,
                                   gfactors=gfactors_clp,
                                   exact_calculations=exact_calculations)
            else:
                recs = Records(data=input_data,
                               gfactors=gfactors_clp,
                               exact_calculations=exact_calculations)
        else:  # input_data are raw data that are not being aged
            recs = Records(data=input_data,
                           exact_calculations=exact_calculations,
                           gfactors=None,
                           adjust_ratios=None,
                           weights=None,
                           start_year=tax_year)
            if self._reform:
                recs_clp = copy.deepcopy(recs)
        # create Calculator object(s)
        con = Consumption()
        con.update_consumption(param_dict['consumption'])
        beh = Behavior()
        beh.update_behavior(param_dict['behavior'])
        self._calc = Calculator(policy=pol, records=recs,
                                verbose=True,
                                consumption=con,
                                behavior=beh,
                                sync_years=aging_input_data)
        if self._reform:
            self._calc_clp = Calculator(policy=clp, records=recs_clp,
                                        verbose=False,
                                        consumption=con,
                                        sync_years=aging_input_data)

    def tax_year(self):
        """
        Returns year for which TaxCalcIO calculations are being done.
        """
        return self._calc.policy.current_year

    def output_filepath(self):
        """
        Return full path to output file named in TaxCalcIO constructor.
        """
        dirpath = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(dirpath, self._output_filename)

    def analyze(self, writing_output_file=False,
                output_graph=False,
                output_ceeu=False,
                output_dump=False):
        """
        Conduct non-dynamic tax analysis.

        Parameters
        ----------
        writing_output_file: boolean

        output_graph: boolean
           whether or not to generate and show HTML graphs of average
           and marginal tax rates by income percentile

        output_ceeu: boolean
           whether or not to calculate and write to stdout standard
           certainty-equivalent expected-utility statistics

        output_dump: boolean
           whether or not to replace standard output with all input and
           calculated variables using their Tax-Calculator names

        Returns
        -------
        Nothing
        """
        # pylint: disable=too-many-arguments,too-many-locals,too-many-branches
        # conduct non-dynamic tax analysis
        if output_dump:
            (mtr_paytax, mtr_inctax,
             _) = self._calc.mtr(wrt_full_compensation=False)
        else:  # do not need marginal tax rates
            mtr_paytax = None
            mtr_inctax = None
            self._calc.calc_all()
        # optionally conduct normative welfare analysis
        if output_ceeu:
            self._calc_clp.calc_all()
            cedict = ce_aftertax_income(self._calc_clp, self._calc,
                                        require_no_agg_tax_change=False)
            ceeu_results = TaxCalcIO.ceeu_output(cedict)
        else:
            ceeu_results = None
        # extract output if writing_output_file
        if writing_output_file:
            self.write_output_file(output_dump, mtr_paytax, mtr_inctax)
        # optionally write --graph output to HTML files
        if output_graph:
            self.write_graph_files()
        # optionally write --ceeu output to stdout
        if ceeu_results:
            print(ceeu_results)  # pylint: disable=superfluous-parens

    def write_output_file(self, output_dump, mtr_paytax, mtr_inctax):
        """
        Write output to CSV-formatted file.
        """
        if output_dump:
            outdf = self.dump_output(mtr_inctax, mtr_paytax)
        else:
            outdf = self.minimal_output()
        assert len(outdf.index) == self._calc.records.dim
        outdf.to_csv(self._output_filename, index=False, float_format='%.2f')

    def write_graph_files(self):
        """
        Write graphs to HTML files.
        """
        atr_data = atr_graph_data(self._calc_clp, self._calc)
        atr_plot = xtr_graph_plot(atr_data)
        atr_fname = self._output_filename.replace('.csv', '-atr.html')
        atr_title = 'ATR by Income Percentile'
        write_graph_file(atr_plot, atr_fname, atr_title)
        mtr_data = mtr_graph_data(self._calc_clp, self._calc,
                                  alt_e00200p_text='Taxpayer Earnings')
        mtr_plot = xtr_graph_plot(mtr_data)
        mtr_fname = self._output_filename.replace('.csv', '-mtr.html')
        mtr_title = 'MTR by Income Percentile'
        write_graph_file(mtr_plot, mtr_fname, mtr_title)

    def minimal_output(self):
        """
        Extract minimal output and return as pandas DataFrame.
        """
        varlist = ['RECID', 'YEAR', 'WEIGHT', 'INCTAX', 'LSTAX', 'PAYTAX']
        odict = dict()
        crecs = self._calc.records
        odict['RECID'] = crecs.RECID  # id for tax filing unit
        odict['YEAR'] = self.tax_year()  # tax calculation year
        odict['WEIGHT'] = crecs.s006  # sample weight
        # pylint: disable=protected-access
        odict['INCTAX'] = crecs._iitax  # federal income taxes
        odict['LSTAX'] = crecs.lumpsum_tax  # lump-sum tax
        odict['PAYTAX'] = crecs._payrolltax  # payroll taxes (ee+er)
        odf = pd.DataFrame(data=odict, columns=varlist)
        return odf

    @staticmethod
    def ceeu_output(cedict):
        """
        Extract --ceeu output and return as text string.
        """
        text = ('Aggregate {} Pre-Tax Expanded Income and '
                'Tax Revenue ($billion)\n')
        txt = text.format(cedict['year'])
        txt += '           baseline     reform   difference\n'
        fmt = '{} {:12.3f} {:10.3f} {:12.3f}\n'
        txt += fmt.format('income', cedict['inc1'], cedict['inc2'],
                          cedict['inc2'] - cedict['inc1'])
        alltaxdiff = cedict['tax2'] - cedict['tax1']
        txt += fmt.format('alltax', cedict['tax1'], cedict['tax2'],
                          alltaxdiff)
        txt += ('Certainty Equivalent of Expected Utility of '
                'After-Tax Expanded Income ($)\n')
        txt += ('(assuming consumption equals '
                'after-tax expanded income)\n')
        txt += 'crra       baseline     reform     pctdiff\n'
        fmt = '{} {:17.2f} {:10.2f} {:11.2f}\n'
        for crra, ceeu1, ceeu2 in zip(cedict['crra'],
                                      cedict['ceeu1'],
                                      cedict['ceeu2']):
            txt += fmt.format(crra, ceeu1, ceeu2,
                              100.0 * (ceeu2 - ceeu1) / ceeu1)
        if abs(alltaxdiff) >= 0.0005:
            txt += ('WARN: baseline and reform cannot be '
                    'sensibly compared\n')
            text = ('      because "alltax difference" is '
                    '{:.3f} which is not zero\n')
            txt += text.format(alltaxdiff)
            txt += ('FIX: adjust _LST or another reform policy parameter '
                    'to bracket\n')
            txt += ('     "alltax difference" equals zero and '
                    'then interpolate')
        else:
            txt += 'NOTE: baseline and reform can be sensibly compared\n'
            txt += '      because "alltax difference" is essentially zero'
        return txt

    def dump_output(self, mtr_inctax, mtr_paytax):
        """
        Extract --dump output and return as pandas DataFrame.
        """
        odf = pd.DataFrame()
        varset = Records.USABLE_READ_VARS | Records.CALCULATED_VARS
        for varname in varset:
            vardata = getattr(self._calc.records, varname)
            odf[varname] = vardata
        odf['mtr_inctax'] = mtr_inctax
        odf['mtr_paytax'] = mtr_paytax
        return odf

    @staticmethod
    def dynamic_analysis(input_data, tax_year, reform, assump,
                         aging_input_data, exact_calculations,
                         writing_output_file=False,
                         output_graph=False,
                         output_ceeu=False,
                         output_dump=False):
        """
        High-level logic for dyanamic tax analysis.

        Parameters
        ----------
        First six parameters are same as the first six parameters of
        the TaxCalcIO constructor.

        Last four parameters are same as the first four parameters of
        the TaxCalcIO analyze method.

        Returns
        -------
        Nothing
        """
        # pylint: disable=too-many-arguments
        # pylint: disable=superfluous-parens
        progress = 'STARTING ANALYSIS FOR YEAR {}'
        gdiff_dict = {Policy.JSON_START_YEAR: {}}
        for year in range(Policy.JSON_START_YEAR, tax_year + 1):
            print(progress.format(year))
            # specify growdiff_response using gdiff_dict
            growdiff_response = Growdiff()
            growdiff_response.update_growdiff(gdiff_dict)
            gd_dict = TaxCalcIO.annual_analysis(input_data, tax_year,
                                                reform, assump,
                                                aging_input_data,
                                                exact_calculations,
                                                growdiff_response, year,
                                                writing_output_file,
                                                output_graph,
                                                output_ceeu,
                                                output_dump)
            gdiff_dict[year + 1] = gd_dict

    @staticmethod
    def annual_analysis(input_data, tax_year, reform, assump,
                        aging_input_data, exact_calculations,
                        growdiff_response, year,
                        writing_output_file,
                        output_graph,
                        output_ceeu,
                        output_dump):
        """
        Conduct static analysis for specifed year and growdiff_response.

        Parameters
        ----------
        First six parameters are same as the first six parameters of
        the TaxCalcIO constructor.

        Last four parameters are same as the first four parameters of
        the TaxCalcIO static_analysis method.

        Returns
        -------
        gd_dict: Growdiff sub-dictionary for year+1
        """
        # pylint: disable=too-many-arguments
        # instantiate TaxCalcIO object for specified year and growdiff_response
        tcio = TaxCalcIO(input_data=input_data,
                         tax_year=year,
                         reform=reform,
                         assump=assump,
                         growdiff_response=growdiff_response,
                         aging_input_data=aging_input_data,
                         exact_calculations=exact_calculations)
        if year == tax_year:
            # conduct final tax analysis for year equal to tax_year
            tcio.analyze(writing_output_file=writing_output_file,
                         output_graph=output_graph,
                         output_ceeu=output_ceeu,
                         output_dump=output_dump)
            gd_dict = {}
        else:
            # conduct intermediate tax analysis for year less than tax_year
            tcio.analyze()
            # build dict in gdiff_dict key:dict pair for key equal to next year
            # ... extract tcio results for year needed by GrowModel class
            # >>>>> add logic here <<<<<
            # ... use extracted results to advance GrowModel to next year
            # >>>>> add logic here <<<<<
            # ... extract next year GrowModel results for next year gdiff_dict
            # >>>>> add logic here <<<<<
            gd_dict = {}  # TEMPORARY CODE
        return gd_dict
