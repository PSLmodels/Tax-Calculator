"""
Tax-Calculator income tax input-output class that
either
reads CSV-formatted file input and writes Internet-TAXSIM-formatted output,
or
takes DataFrame input and returns Internet-TAXSIM-formatted output as string.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 incometaxio.py
# pylint --disable=locally-disabled incometaxio.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)


import os
import sys
import copy
import six
import pandas as pd
from .policy import Policy
from .records import Records
from .behavior import Behavior
from .growth import Growth
from .consumption import Consumption
from .calculate import Calculator
from .simpletaxio import SimpleTaxIO
from .utils import ce_aftertax_income


class IncomeTaxIO(object):
    """
    Constructor for the income tax input-output class.

    Parameters
    ----------
    input_data: string or Pandas DataFrame
        string is name of INPUT file that is CSV formatted containing
        variable names in the Records.USABLE_READ_VARS set, or
        Pandas DataFrame is INPUT data containing variable names in
        the Records.USABLE_READ_VARS set.  INPUT vsrisbles not in the
        Records.USABLE_READ_VARS set can be present but are ignored.

    tax_year: integer
        calendar year for which income taxes will be computed for INPUT.

    reform: None or string
        None implies no policy reform (current-law policy), or
        string is name of optional REFORM file.

    assump: None or string
        None implies economic assumptions are baseline assumptions and
        a static analysis of reform is conducted, or
        string is name of optional ASSUMP file.

    exact_calculations: boolean
        specifies whether or not exact tax calculations are done without
        any smoothing of "stair-step" provisions in income tax law.

    blowup_input_data: boolean
        whether or not to age record data from data year to tax_year.

    output_weights: boolean
        whether or will be including sample weights in output.

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
    class instance: IncomeTaxIO
    """

    def __init__(self, input_data, tax_year, reform, assump,
                 exact_calculations,
                 blowup_input_data, adjust_input_data, output_weights,
                 output_records, csv_dump):
        """
        IncomeTaxIO class constructor.
        """
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-locals
        if isinstance(input_data, six.string_types):
            self._using_input_file = True
            # check that input_data string ends with ".csv"
            if input_data.endswith('.csv'):
                inp = '{}-{}'.format(input_data[:-4], str(tax_year)[2:])
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
        if assump is None:
            asm = ''
        elif isinstance(assump, six.string_types):
            if assump.endswith('.json'):
                asm = '-{}'.format(assump[:-5])
            else:
                asm = '-{}'.format(assump)
        else:
            msg = 'IncomeTaxIO.ctor assump is neither None nor str'
            raise ValueError(msg)
        if reform is None:
            self._reform = False
            ref = ''
        elif isinstance(reform, six.string_types):
            self._reform = True
            if reform.endswith('.json'):
                ref = '-{}'.format(reform[:-5])
            else:
                ref = '-{}'.format(reform)
        else:
            msg = 'IncomeTaxIO.ctor reform is neither None nor str'
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
        # create Policy object assuming current-law policy
        pol = Policy()
        # check for valid tax_year value
        if tax_year < pol.start_year:
            msg = 'tax_year {} less than policy.start_year {}'
            raise ValueError(msg.format(tax_year, pol.start_year))
        if tax_year > pol.end_year:
            msg = 'tax_year {} greater than policy.end_year {}'
            raise ValueError(msg.format(tax_year, pol.end_year))
        # get reform & assump dictionaries and implement reform
        (ref_d, beh_d, con_d,
         gro_d) = Calculator.read_json_param_files(reform, assump)
        pol.implement_reform(ref_d)
        # set tax policy parameters to specified tax_year
        pol.set_year(tax_year)
        # read input file contents into Records object
        if blowup_input_data:
            if output_weights:
                if adjust_input_data:
                    recs = Records(data=input_data,
                                   exact_calculations=exact_calculations)
                else:
                    recs = Records(data=input_data,
                                   exact_calculations=exact_calculations,
                                   adjust_ratios=None)
            else:
                if adjust_input_data:
                    recs = Records(data=input_data,
                                   exact_calculations=exact_calculations,
                                   weights=None)
                else:
                    recs = Records(data=input_data,
                                   exact_calculations=exact_calculations,
                                   adjust_ratios=None,
                                   weights=None)
        else:
            if output_weights:
                if adjust_input_data:
                    recs = Records(data=input_data,
                                   exact_calculations=exact_calculations,
                                   blowup_factors=None,
                                   start_year=tax_year)
                else:
                    recs = Records(data=input_data,
                                   exact_calculations=exact_calculations,
                                   blowup_factors=None,
                                   adjust_ratios=None,
                                   start_year=tax_year)
            else:
                if adjust_input_data:
                    recs = Records(data=input_data,
                                   exact_calculations=exact_calculations,
                                   blowup_factors=None,
                                   weights=None,
                                   start_year=tax_year)
                else:
                    recs = Records(data=input_data,
                                   exact_calculations=exact_calculations,
                                   blowup_factors=None,
                                   adjust_ratios=None,
                                   weights=None,
                                   start_year=tax_year)
        # create Calculator object
        con = Consumption()
        con.update_consumption(con_d)
        gro = Growth()
        gro.update_growth(gro_d)
        if self._reform:
            clp = Policy()
            clp.set_year(tax_year)
            recs_clp = copy.deepcopy(recs)
            self._calc_clp = Calculator(policy=clp, records=recs_clp,
                                        verbose=False,
                                        consumption=con,
                                        growth=gro,
                                        sync_years=blowup_input_data)
            beh = Behavior()
            beh.update_behavior(beh_d)
            self._calc = Calculator(policy=pol, records=recs,
                                    verbose=True,
                                    behavior=beh,
                                    consumption=con,
                                    growth=gro,
                                    sync_years=blowup_input_data)
        else:
            self._calc = Calculator(policy=pol, records=recs,
                                    verbose=True,
                                    consumption=con,
                                    growth=gro,
                                    sync_years=blowup_input_data)

    def tax_year(self):
        """
        Returns year for which IncomeTaxIO calculations are being done.
        """
        return self._calc.policy.current_year

    def output_records(self, writing_output_file=False):
        """
        Write CSV-formatted file containing the values of the
        Records.USABLE_READ_VARS in the tax_year.  The order of the
        columns in this output file might not be the same as in the
        input_data passed to IncomeTaxIO constructor.

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

        Output lines will be written to file if IncomeTaxIO constructor
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
            ovar = SimpleTaxIO.extract_output(self._calc.records, idx,
                                              exact=exact_output,
                                              extract_weight=output_weights)
            ovar[7] = 100 * mtr_itax[idx]
            ovar[9] = 100 * mtr_ptax[idx]
            output[idx] = ovar
        assert len(output) == self._calc.records.dim
        # handle disposition of calculated output
        olines = ''
        if self._using_input_file and writing_output_file:
            SimpleTaxIO.write_output_file(output, self._output_filename)
        else:
            for idx in range(0, len(output)):
                olines += SimpleTaxIO.construct_output_line(output[idx])
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
        ivd = ('**** IncomeTaxIO INPUT variables determined by INPUT file,\n'
               'which is a CSV-formatted text file whose name ends in .csv\n'
               'and whose column names include the Records.MUST_READ_VARS.\n')
        sys.stdout.write(ivd)
        ovd = ('**** IncomeTaxIO OUTPUT variables in Internet-TAXSIM format:\n'
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
