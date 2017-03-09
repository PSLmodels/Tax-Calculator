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
from taxcalc.utils import ce_aftertax_income


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
        None implies economic assumptions are baseline assumptions and
        a static analysis of reform is conducted, or
        string is name of optional ASSUMP file.

    aging_input_data: boolean
        whether or not to age record data from data year to tax_year.

    exact_calculations: boolean
        specifies whether or not exact tax calculations are done without
        any smoothing of "stair-step" provisions in the tax law.

    Raises
    ------
    ValueError:
        if file specified by input_data string does not exist.
        if reform is neither None nor string.
        if assump is neither None nor string.
        if tax_year before Policy start_year.
        if tax_year after Policy end_year.

    Returns
    -------
    class instance: TaxCalcIO
    """

    def __init__(self, input_data, tax_year, reform, assump,
                 aging_input_data, exact_calculations):
        """
        TaxCalcIO class constructor.
        """
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-locals
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
        # construct output_filename and delete old output file if it exists
        if reform is None:
            self._reform = False
            ref = ''
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
            asm = ''
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
        if os.path.isfile(self._output_filename):
            os.remove(self._output_filename)
        # get parameter dictionaries
        param_dict = Calculator.read_json_param_files(reform, assump)
        # create growdiff_baseline and growdiff_response objects
        growdiff_baseline = Growdiff()
        growdiff_baseline.update_growdiff(param_dict['growdiff_baseline'])
        growdiff_response = Growdiff()
        growdiff_response.update_growdiff(param_dict['growdiff_response'])
        # create pre-reform and post-reform Growfactors objects
        growfactors_pre = Growfactors()
        growdiff_baseline.apply_to(growfactors_pre)
        growfactors_post = Growfactors()
        growdiff_baseline.apply_to(growfactors_post)
        growdiff_response.apply_to(growfactors_post)
        # create Policy object and implement reform
        if self._reform:
            pol = Policy(gfactors=growfactors_post)
            pol.implement_reform(param_dict['policy'])
        else:
            pol = Policy(gfactors=growfactors_pre)
        # check for valid tax_year value
        if tax_year < pol.start_year:
            msg = 'tax_year {} less than policy.start_year {}'
            raise ValueError(msg.format(tax_year, pol.start_year))
        if tax_year > pol.end_year:
            msg = 'tax_year {} greater than policy.end_year {}'
            raise ValueError(msg.format(tax_year, pol.end_year))
        # set tax policy parameters to specified tax_year
        pol.set_year(tax_year)
        # read input file contents into Records object
        if aging_input_data:
            recs = Records(data=input_data,
                           exact_calculations=exact_calculations)
        else:  # input_data are raw data that are not being aged
            recs = Records(data=input_data,
                           exact_calculations=exact_calculations,
                           gfactors=None,
                           adjust_ratios=None,
                           weights=None,
                           start_year=tax_year)
        # create Calculator object
        con = Consumption()
        con.update_consumption(param_dict['consumption'])
        if self._reform:
            clp = Policy()
            clp.set_year(tax_year)
            recs_clp = copy.deepcopy(recs)
            self._calc_clp = Calculator(policy=clp, records=recs_clp,
                                        verbose=False,
                                        consumption=con,
                                        sync_years=aging_input_data)
            beh = Behavior()
            beh.update_behavior(param_dict['behavior'])
            # prevent both behavioral response and growdiff response
            if beh.has_any_response() and growdiff_response.has_any_response():
                msg = 'BOTH behavior AND growdiff_response HAVE RESPONSE'
                raise ValueError(msg)
            self._calc = Calculator(policy=pol, records=recs,
                                    verbose=True,
                                    consumption=con,
                                    behavior=beh,
                                    sync_years=aging_input_data)
        else:
            self._calc = Calculator(policy=pol, records=recs,
                                    verbose=True,
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

    def calculate(self, writing_output_file=False,
                  output_ceeu=False,
                  output_dump=False):
        """
        Calculate taxes for all INPUT lines and write or return OUTPUT lines.

        Parameters
        ----------
        writing_output_file: boolean

        output_ceeu: boolean
           whether or not to calculate and write to stdout standard
           certainty-equivalent expected-utility statistics

        output_dump: boolean
           whether or not to include all input and calculated variables in
           output

        Returns
        -------
        output_lines: string
            empty string if OUTPUT lines are written to a file;
            otherwise output_lines contain all OUTPUT lines
        """
        # pylint: disable=too-many-arguments,too-many-locals
        # compute mtr wrt taxpayer earnings even if not needed for dump
        # <note that last mtr() step is calc_all()>
        (mtr_paytax, mtr_inctax,
         _) = self._calc.mtr(wrt_full_compensation=False)
        ceeu_results = None
        if self._reform:
            self._calc = Behavior.response(self._calc_clp, self._calc)
            if output_ceeu:
                if not self._calc.behavior.has_response():
                    self._calc_clp.calc_all()
                cedict = ce_aftertax_income(self._calc_clp, self._calc,
                                            require_no_agg_tax_change=False)
                ceeu_results = TaxCalcIO.ceeu_output(cedict)
        # extract output
        if output_dump:
            outdf = self.dump_output(mtr_inctax, mtr_paytax)
        else:
            outdf = self.standard_output()
        assert len(outdf.index) == self._calc.records.dim
        # handle disposition of output
        output_lines = ''
        if writing_output_file:
            outdf.to_csv(self._output_filename, index=False,
                         float_format='%.2f')
        else:
            output_lines = outdf.to_string(index=False,
                                           float_format='%.2f')
        if ceeu_results:
            print(ceeu_results)  # pylint: disable=superfluous-parens
        return output_lines

    """
    @staticmethod
    def construct_output_line(output_dict):

        Construct line of OUTPUT from a filing unit output_dict.

        Parameters
        ----------
        output_dict: dictionary
            calculated output values indexed from 1 to len(output_dict).

        Returns
        -------
        output_line: string

        outline = ''
        for vnum in range(1, len(output_dict) + 1):
            fnum = min(vnum, TaxCalcIO.OVAR_NUM)
            outline += TaxCalcIO.OVAR_FMT[fnum].format(output_dict[vnum])
        outline += '\n'
        return outline



    @staticmethod
    def write_output_file(output, output_filename):

        Write all output to file with output_filename.

        Parameters
        ----------
        output: dictionary of OUTPUT variables for each INPUT tax filing unit

        output_filename: string

        Returns
        -------
        nothing: void

        with open(output_filename, 'w') as output_file:
            for idx in range(0, len(output)):
                outline = TaxCalcIO.construct_output_line(output[idx])
                output_file.write(outline)
    """

    def standard_output(self):
        """
        Extract standard output and return as pandas DataFrame.
        """
        varlist = ['RECID', 'YEAR', 'WEIGHT', 'INCTAX', 'LSTAX', 'PAYTAX']
        odict = dict()
        crecs = self._calc.records
        odict['RECID'] = crecs.RECID  # id for tax filing unit
        odict['YEAR'] = crecs.FLPDYR  # tax calculation year
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
                text = ('because alltax difference is '
                        '{:.3f} which is not zero\n')
                txt += text.format(alltaxdiff)
                txt += 'FIX: adjust _LST or other parameter to bracket\n'
                txt += 'alltax difference equals zero and then interpolate'
            else:
                txt += ('NOTE: baseline and reform can be '
                        'sensibly compared\n')
                txt += 'because alltax difference is essentially zero'
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
