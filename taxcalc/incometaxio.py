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
import six
import pandas as pd
from .policy import Policy
from .records import Records
from .calculate import Calculator
from .simpletaxio import SimpleTaxIO


class IncomeTaxIO(object):
    """
    Constructor for the income tax input-output class.

    Parameters
    ----------
    input_data: string or Pandas DataFrame
        string is name of INPUT file that is CSV formatted containing only
        variable names in the Records.VALID_READ_VARS set, or
        Pandas DataFrame is INPUT data containing only variable names in
        the Records.VALID_READ_VARS set.

    tax_year: integer
        calendar year for which income taxes will be computed for INPUT.

    policy_reform: None or string or dictionary
        None implies no policy reform (current-law policy), or
        string is name of optional REFORM file, or
        dictionary suitable for passing to Policy.implement_reform() method.

    blowup_input_data: boolean
        whether or not to age record data from data year to tax_year.

    output_records: boolean
        whether or not to write CSV-formatted file containing the values
        of the Records.VALID_READ_VARS variables in the tax_year.

    csv_dump: boolean
        whether or not to write CSV-formatted output file containing the
        values of the Records.VALID_READ_VARS and Records.CALCULATE_VARS
        variables.  If true, the CSV-formatted output file replaces the
        usual space-separated-values Internet-TAXSIM output file.

    Raises
    ------
    ValueError:
        if file specified by input_data string does not exist.
        if policy_reform is neither None, string, nor dictionary.
        if tax_year before Policy start_year.
        if tax_year after Policy end_year.

    Returns
    -------
    class instance: IncomeTaxIO
    """

    def __init__(self, input_data, tax_year, policy_reform,
                 blowup_input_data, output_records, csv_dump):
        """
        IncomeTaxIO class constructor.
        """
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-branches
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
        if policy_reform:
            if isinstance(policy_reform, six.string_types):
                if policy_reform.endswith('.json'):
                    ref = '-{}'.format(policy_reform[:-5])
                else:
                    ref = '-{}'.format(policy_reform)
                self._using_reform_file = True
            elif isinstance(policy_reform, dict):
                ref = ''
                self._using_reform_file = False
            else:
                msg = 'IncomeTaxIO.ctor reform is neither None, str, nor dict'
                raise ValueError(msg)
        else:  # if policy_reform is None
            ref = ''
            self._using_reform_file = True
        if output_records:
            self._output_filename = '{}.records{}'.format(inp, ref)
        elif csv_dump:
            self._output_filename = '{}.csvdump{}'.format(inp, ref)
        else:
            self._output_filename = '{}.out-inctax{}'.format(inp, ref)
        if os.path.isfile(self._output_filename):
            os.remove(self._output_filename)
        # check for existence of INPUT file
        if self._using_input_file:
            if not os.path.isfile(input_data):
                msg = 'INPUT file named {} could not be found'
                raise ValueError(msg.format(input_data))
        # create Policy object assuming current-law policy
        policy = Policy()
        # check for valid tax_year value
        if tax_year < policy.start_year:
            msg = 'tax_year {} less than policy.start_year {}'
            raise ValueError(msg.format(tax_year, policy.start_year))
        if tax_year > policy.end_year:
            msg = 'tax_year {} greater than policy.end_year {}'
            raise ValueError(msg.format(tax_year, policy.end_year))
        # implement policy reform if one is specified
        if policy_reform:
            if self._using_reform_file:
                reform = Policy.read_json_reform_file(policy_reform)
            else:
                reform = policy_reform
            policy.implement_reform(reform)
        # set tax policy parameters to specified tax_year
        policy.set_year(tax_year)
        # read input file contents into Records object
        if blowup_input_data:
            recs = Records(data=input_data,
                           start_year=Records.PUF_YEAR,
                           consider_blowup=True)
        else:
            recs = Records(data=input_data,
                           start_year=tax_year,
                           consider_blowup=False)
        # create Calculator object
        self._calc = Calculator(policy=policy, records=recs,
                                sync_years=blowup_input_data)

    def tax_year(self):
        """
        Returns year for which IncomeTaxIO calculations are being done.
        """
        return self._calc.policy.current_year

    def output_records(self, writing_output_file=False):
        """
        Write CSV-formatted file containing the values of the
        Records.VALID_READ_VARS in the tax_year.  The order of the
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
        for varname in Records.VALID_READ_VARS:
            vardata = getattr(self._calc.records, varname)
            recdf[varname] = vardata
        writing_possible = self._using_input_file and self._using_reform_file
        if writing_possible and writing_output_file:
            recdf.to_csv(self._output_filename,
                         float_format='%.4f', index=False)

    def csv_dump(self, writing_output_file=False):
        """
        Write CSV-formatted file containing the values of all the
        Records.VALID_READ_VARS variables and all the Records.CALCULATED_VARS
        variables in the tax_year.

        Parameters
        ----------
        writing_output_file: boolean

        Returns
        -------
        Nothing
        """
        recdf = pd.DataFrame()
        for varname in Records.VALID_READ_VARS | Records.CALCULATED_VARS:
            vardata = getattr(self._calc.records, varname)
            recdf[varname] = vardata
        writing_possible = self._using_input_file and self._using_reform_file
        if writing_possible and writing_output_file:
            recdf.to_csv(self._output_filename,
                         float_format='%.4f', index=False)

    def calculate(self, writing_output_file=False,
                  output_weights=False):
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

        Returns
        -------
        output_lines: string
            empty string if OUTPUT lines are written to a file;
            otherwise output_lines contain all OUTPUT lines
        """
        output = {}  # dictionary indexed by Records index for filing unit
        (mtr_fica, mtr_iitx, _) = self._calc.mtr(wrt_full_compensation=False)
        for idx in range(0, self._calc.records.dim):
            ovar = SimpleTaxIO.extract_output(self._calc.records, idx,
                                              extract_weight=output_weights)
            ovar[7] = 100 * mtr_iitx[idx]
            ovar[9] = 100 * mtr_fica[idx]
            output[idx] = ovar
        assert len(output) == self._calc.records.dim
        # handle disposition of calculated output
        olines = ''
        writing_possible = self._using_input_file and self._using_reform_file
        if writing_possible and writing_output_file:
            SimpleTaxIO.write_output_file(output, self._output_filename)
        else:
            for idx in range(0, len(output)):
                olines += SimpleTaxIO.construct_output_line(output[idx])
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
               'and whose column names are all in Records.VALID_READ_VARS.\n')
        sys.stdout.write(ivd)
        ovd = ('**** IncomeTaxIO OUTPUT variables in Internet-TAXSIM format:\n'
               '[ 1] arbitrary id of income tax filing unit\n'
               '[ 2] calendar year of income tax filing\n'
               '[ 3] state code [ALWAYS ZERO]\n'
               '[ 4] federal income tax liability\n'
               '[ 5] state income tax liability [ALWAYS ZERO]\n'
               '[ 6] FICA tax liability\n'
               '[ 7] marginal federal income tax rate\n'
               '[ 8] marginal state income tax rate [ALWAYS ZERO]\n'
               '[ 9] marginal FICA tax rate\n'
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
               '[19] regular tax on regular taxable income\n'
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

    # --- begin private methods of IncomeTaxIO class --- #

# end IncomeTaxIO class
