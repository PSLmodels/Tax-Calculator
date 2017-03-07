"""
Tax-Calculator Input-Output class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 taxcalcio.py
# pylint --disable=locally-disabled taxcalcio.py

import os
import sys
import copy
import six
import pandas as pd
from .policy import Policy
from .records import Records
from .consumption import Consumption
from .behavior import Behavior
from .growdiff import Growdiff
from .growfactors import Growfactors
from .calculate import Calculator
from .utils import ce_aftertax_income


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

    output_records: boolean
        whether or not to write CSV-formatted file containing the values
        of the Records.USABLE_READ_VARS variables in the tax_year.

    csv_dump: boolean
        whether or not to write CSV-formatted output file containing the
        values of the Records.USABLE_READ_VARS and Records.CALCULATED_VARS
        variables.  If true, the CSV-formatted output file replaces the
        usual space-separated-values Internet-TAXSIM output file.

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
                 aging_input_data, exact_calculations,
                 output_records, csv_dump):
        """
        TaxCalcIO class constructor.
        """
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-locals
        if isinstance(input_data, six.string_types):
            self._using_input_file = True
            # remove any leading directory path from INPUT filename
            fname = os.path.basename(input_data)
            # check if fname ends with ".csv"
            if fname.endswith('.csv'):
                inp = '{}-{}'.format(fname[:-4], str(tax_year)[2:])
            else:
                msg = 'INPUT file named {} does not end in .csv'
                raise ValueError(msg.format(input_data))
        elif isinstance(input_data, pd.DataFrame):
            self._using_input_file = False
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
                ref = '-{}'.format(fname)
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
                asm = '-{}'.format(fname)
        else:
            msg = 'TaxCalcIO.ctor assump is neither None nor str'
            raise ValueError(msg)
        if output_records:
            self._output_filename = '{}.records{}{}'.format(inp, ref, asm)
        elif csv_dump:
            self._output_filename = '{}.csvdump{}{}'.format(inp, ref, asm)
        else:
            self._output_filename = '{}.out-inctax{}{}'.format(inp, ref, asm)
        if os.path.isfile(self._output_filename):
            os.remove(self._output_filename)
        # check for existence of INPUT file
        if self._using_input_file:
            if not os.path.isfile(input_data):
                msg = 'INPUT file named {} could not be found'
                raise ValueError(msg.format(input_data))
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
        else:  # input_data are raw data
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
            # Prevent both behavioral response and growdiff response
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

    def output_records(self, writing_output_file=False):
        """
        Write CSV-formatted file containing the values of the
        Records.USABLE_READ_VARS in the tax_year.  The order of the
        columns in this output file might not be the same as in the
        input_data passed to TaxCalcIO constructor.

        Parameters
        ----------
        writing_output_file: boolean

        Returns
        -------
        Nothing
        """
        recdf = pd.DataFrame()
        for varname in Records.USABLE_READ_VARS:
            vardata = getattr(self._calc.records, varname)
            recdf[varname] = vardata
        if self._using_input_file and writing_output_file:
            recdf.to_csv(self._output_filename,
                         float_format='%.4f', index=False)

    def csv_dump(self, writing_output_file=False):
        """
        Write CSV-formatted file containing the values of all the
        Records.USABLE_READ_VARS variables and all the Records.CALCULATED_VARS
        variables in the tax_year.

        Parameters
        ----------
        writing_output_file: boolean

        Returns
        -------
        Nothing
        """
        recdf = pd.DataFrame()
        for varname in Records.USABLE_READ_VARS | Records.CALCULATED_VARS:
            vardata = getattr(self._calc.records, varname)
            recdf[varname] = vardata
        if self._using_input_file and writing_output_file:
            recdf.to_csv(self._output_filename,
                         float_format='%.2f', index=False)

    def calculate(self, writing_output_file=False,
                  exact_output=False,
                  output_weights=False,
                  output_mtr_wrt_fullcomp=False,
                  output_ceeu=False):
        """
        Calculate taxes for all INPUT lines and write or return OUTPUT lines.

        Output lines will be written to file if TaxCalcIO constructor
        was passed an input_filename string and a reform string or None,
        and if writing_output_file is True.

        Parameters
        ----------
        writing_output_file: boolean

        output_weights: boolean
            whether or not to use s006 as an additional output variable.

        output_mtr_wrt_fullcomp: boolean
           whether or not to calculate marginal tax rates in OUTPUT file with
           respect to full compensation.

        output_ceeu: boolean
           whether or not to calculate and write to stdout standard
           certainty-equivalent expected-utility statistics

        Returns
        -------
        output_lines: string
            empty string if OUTPUT lines are written to a file;
            otherwise output_lines contain all OUTPUT lines
        """
        # pylint: disable=too-many-arguments,too-many-locals
        output = {}  # dictionary indexed by Records index for filing unit
        (mtr_ptax, mtr_itax,
         _) = self._calc.mtr(wrt_full_compensation=output_mtr_wrt_fullcomp)
        txt = None
        if self._reform:
            self._calc = Behavior.response(self._calc_clp, self._calc)
            if output_ceeu:
                if not self._calc.behavior.has_response():
                    self._calc_clp.calc_all()
                cedict = ce_aftertax_income(self._calc_clp, self._calc,
                                            require_no_agg_tax_change=False)
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
        for idx in range(0, self._calc.records.dim):
            ovar = TaxCalcIO.extract_output(self._calc.records, idx,
                                            exact=exact_output,
                                            extract_weight=output_weights)
            ovar[7] = 100 * mtr_itax[idx]
            ovar[9] = 100 * mtr_ptax[idx]
            output[idx] = ovar
        assert len(output) == self._calc.records.dim
        # handle disposition of calculated output
        olines = ''
        if self._using_input_file and writing_output_file:
            TaxCalcIO.write_output_file(output, self._output_filename)
        else:
            for idx in range(0, len(output)):
                olines += TaxCalcIO.construct_output_line(output[idx])
        if txt:
            print(txt)  # pylint: disable=superfluous-parens
        return olines

    @staticmethod
    def show_iovar_definitions():
        """
        Write definitions of INPUT and OUTPUT variables to stdout.

        Parameters
        ----------
        none: void

        Returns
        -------
        nothing: void
        """
        ivd = ('**** TaxCalcIO INPUT variables determined by INPUT file,\n'
               'which is a CSV-formatted text file whose name ends in .csv\n'
               'and whose column names include the Records.MUST_READ_VARS.\n')
        sys.stdout.write(ivd)
        ovd = ('**** TaxCalcIO OUTPUT variables in Internet-TAXSIM format:\n'
               '[ 1] arbitrary id of income tax filing unit\n'
               '[ 2] calendar year of income tax filing\n'
               '[ 3] state code [ALWAYS ZERO]\n'
               '[ 4] federal income tax liability\n'
               '[ 5] state income tax liability [ALWAYS ZERO]\n'
               '[ 6] OASDI+HI payroll tax liability (sum of ee and er share)\n'
               '[ 7] marginal federal income tax rate\n'
               '[ 8] marginal state income tax rate [ALWAYS ZERO]\n'
               '[ 9] marginal payroll tax rate\n'
               '[10] federal adjusted gross income, AGI\n'
               '[11] unemployment (UI) benefits included in AGI\n'
               '[12] social security (OASDI) benefits included in AGI\n'
               '[13] [ALWAYS ZERO]\n'
               '[14] personal exemption after phase-out\n'
               '[15] phased-out (i.e., disallowed) personal exemption\n'
               '[16] phased-out (i.e., disallowed) itemized deduction\n'
               '[17] itemized deduction after phase-out '
               '(zero for non-itemizer)\n'
               '[18] federal regular taxable income\n'
               '[19] regular tax on regular taxable income '
               '(no special capital gains rates)\n'
               '     EXCEPT use special rates WHEN --exact OPTION SPECIFIED\n'
               '[20] [ALWAYS ZERO]\n'
               '[21] [ALWAYS ZERO]\n'
               '[22] child tax credit (adjusted)\n'
               '[23] child tax credit (refunded)\n'
               '[24] credit for child care expenses\n'
               '[25] federal earned income tax credit, EITC\n'
               '[26] federal AMT taxable income\n'
               '[27] federal AMT liability\n'
               '[28] federal income tax (excluding AMT) before credits\n')
        sys.stdout.write(ovd)

    @staticmethod
    def construct_output_line(output_dict):
        """
        Construct line of OUTPUT from a filing unit output_dict.

        Parameters
        ----------
        output_dict: dictionary
            calculated output values indexed from 1 to len(output_dict).

        Returns
        -------
        output_line: string
        """
        outline = ''
        for vnum in range(1, len(output_dict) + 1):
            fnum = min(vnum, TaxCalcIO.OVAR_NUM)
            outline += TaxCalcIO.OVAR_FMT[fnum].format(output_dict[vnum])
        outline += '\n'
        return outline

    @staticmethod
    def write_output_file(output, output_filename):
        """
        Write all output to file with output_filename.

        Parameters
        ----------
        output: dictionary of OUTPUT variables for each INPUT tax filing unit

        output_filename: string

        Returns
        -------
        nothing: void
        """
        with open(output_filename, 'w') as output_file:
            for idx in range(0, len(output)):
                outline = TaxCalcIO.construct_output_line(output[idx])
                output_file.write(outline)

    OVAR_NUM = 28
    DVAR_NAMES = [  # OPTIONAL DEBUGGING OUTPUT VARIABLE NAMES
        # '...',  # first debugging variable
        # '...',  # second debugging variable
        # etc.
        # '...'   # last debugging variable
    ]
    OVAR_FMT = {1: '{:d}.',  # add decimal point as in Internet-TAXSIM output
                2: ' {:.0f}',
                3: ' {:d}',
                4: ' {:.2f}',
                5: ' {:.2f}',
                6: ' {:.2f}',
                7: ' {:.2f}',
                8: ' {:.2f}',
                9: ' {:.2f}',
                10: ' {:.2f}',
                11: ' {:.2f}',
                12: ' {:.2f}',
                13: ' {:.2f}',
                14: ' {:.2f}',
                15: ' {:.2f}',
                16: ' {:.2f}',
                17: ' {:.2f}',
                18: ' {:.2f}',
                19: ' {:.2f}',
                20: ' {:.2f}',
                21: ' {:.2f}',
                22: ' {:.2f}',
                23: ' {:.2f}',
                24: ' {:.2f}',
                25: ' {:.2f}',
                26: ' {:.2f}',
                27: ' {:.2f}',
                28: ' {:.2f}'}

    @staticmethod
    def extract_output(crecs, idx, exact=False, extract_weight=False):
        """
        Extracts tax output from crecs object for one tax filing unit.

        Parameters
        ----------
        crecs: Records
            Records object embedded in Calculator object.

        idx: integer
            crecs object index of the one tax filing unit.

        exact: boolean
            whether or not ovar[19] is exact regular tax on regular income.

        extract_weight: boolean
            whether or not to extract s006 sample weight into ovar[29].

        Returns
        -------
        ovar: dictionary of output variables indexed from 1 to OVAR_NUM,
            or from 1 to OVAR_NUM+1 if extract_weight is True,
            of from 1 to OVAR_NUM+? if debugging variables are included.

        Notes
        -----
        The value of each output variable is stored in the ovar dictionary,
        which is indexed as Internet-TAXSIM output variables are (where the
        index begins with one).
        """
        ovar = {}
        ovar[1] = crecs.RECID[idx]  # id for tax filing unit
        ovar[2] = crecs.FLPDYR[idx]  # year for which taxes are calculated
        ovar[3] = 0  # state code is always zero
        # pylint: disable=protected-access
        ovar[4] = crecs._iitax[idx]  # federal income tax liability
        ovar[5] = 0.0  # no state income tax calculation
        ovar[6] = crecs._payrolltax[idx]  # payroll taxes (ee+er) for OASDI+HI
        ovar[7] = 0.0  # marginal federal income tax rate as percent
        ovar[8] = 0.0  # no state income tax calculation
        ovar[9] = 0.0  # marginal payroll tax rate as percent
        ovar[10] = crecs.c00100[idx]  # federal AGI
        ovar[11] = crecs.e02300[idx]  # UI benefits in AGI
        ovar[12] = crecs.c02500[idx]  # OASDI benefits in AGI
        ovar[13] = 0.0  # always set zero-bracket amount to zero
        pre_phase_out_pe = crecs.pre_c04600[idx]
        post_phase_out_pe = crecs.c04600[idx]
        phased_out_pe = pre_phase_out_pe - post_phase_out_pe
        ovar[14] = post_phase_out_pe  # post-phase-out personal exemption
        ovar[15] = phased_out_pe  # personal exemption that is phased out
        # ovar[16] can be positive for non-itemizer:
        ovar[16] = crecs.c21040[idx]  # itemized deduction that is phased out
        # ovar[17] is zero for non-itemizer:
        ovar[17] = crecs.c04470[idx]  # post-phase-out itemized deduction
        ovar[18] = crecs.c04800[idx]  # federal regular taxable income
        if exact:
            ovar[19] = crecs._taxbc[idx]  # regular tax on taxable income
        else:  # Internet-TAXSIM ovar[19] that ignores special qdiv+ltcg rates
            ovar[19] = crecs.c05200[idx]  # regular tax on taxable income
        ovar[20] = 0.0  # always set exemption surtax to zero
        ovar[21] = 0.0  # always set general tax credit to zero
        ovar[22] = crecs.c07220[idx]  # child tax credit (adjusted)
        ovar[23] = crecs.c11070[idx]  # extra child tax credit (refunded)
        ovar[24] = crecs.c07180[idx]  # child care credit
        ovar[25] = crecs._eitc[idx]  # federal EITC
        ovar[26] = crecs.c62100[idx]  # federal AMT taxable income
        amt_liability = crecs.c09600[idx]  # federal AMT liability
        ovar[27] = amt_liability
        # ovar[28] is federal income tax before credits; the Tax-Calculator
        # crecs.c05800[idx] is this concept but includes AMT liability
        # while Internet-TAXSIM ovar[28] explicitly excludes AMT liability, so
        # we have the following:
        ovar[28] = crecs.c05800[idx] - amt_liability
        # add optional weight and debugging output to ovar dictionary
        if extract_weight:
            ovar[29] = crecs.s006[idx]  # sample weight
            num = TaxCalcIO.OVAR_NUM + 1
        else:
            num = TaxCalcIO.OVAR_NUM
        for dvar_name in TaxCalcIO.DVAR_NAMES:
            num += 1
            dvar = getattr(crecs, dvar_name, None)
            if dvar is None:
                msg = 'debugging variable name "{}" not in calc.records object'
                raise ValueError(msg.format(dvar_name))
            else:
                ovar[num] = dvar[idx]
        return ovar
