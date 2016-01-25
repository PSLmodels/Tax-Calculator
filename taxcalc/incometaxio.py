"""
Tax-Calculator income tax input-output class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 incometaxio.py
# pylint --disable=locally-disabled incometaxio.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)


import os
import sys
import six
from .policy import Policy
from .records import Records
from .calculate import Calculator
from .simpletaxio import SimpleTaxIO


class IncomeTaxIO(object):
    """
    Constructor for the income tax input-output class.

    Parameters
    ----------
    input_filename: string
        name of INPUT file that is CSV formatted containing only variable
        names in the Records.VALID_READ_VARS set; the CSV file may be
        contained in a compressed GZIP file with a name ending in '.gz'.

    tax_year: integer
        calendar year for which income taxes will be computed for INPUT.

    reform: None or string or dictionary
        None implies no reform (current-law policy), or
        string is name of optional REFORM file, or
        dictionary suitable for passing to Policy.implement_reform() method.

    blowup_input_data: boolean
        whether or not to age record data from data year to tax_year.

    Raises
    ------
    ValueError:
        if file with input_filename does not exist.
        if reform is neither None, string, nor dictionary.
        if tax_year before Policy start_year.
        if tax_year after Policy end_year.

    Returns
    -------
    class instance: IncomeTaxIO
    """

    def __init__(self,
                 input_filename,
                 tax_year,
                 reform,
                 blowup_input_data):
        """
        IncomeTaxIO class constructor.
        """
        # pylint: disable=too-many-branches
        # check that input_filename ends with ".csv", ".csv.gz" or ".gz"
        if input_filename.endswith('.csv'):
            inp_str = '{}-{}'.format(input_filename[:-4], str(tax_year)[2:])
        elif input_filename.endswith('.csv.gz'):
            inp_str = '{}-{}'.format(input_filename[:-7], str(tax_year)[2:])
        elif input_filename.endswith('.gz'):
            inp_str = '{}-{}'.format(input_filename[:-3], str(tax_year)[2:])
        else:
            msg = 'INPUT file named {} does not end in {}'
            raise ValueError(msg.format(input_filename,
                                        '".csv", ".csv.gz", or ".gz"'))
        # construct output_filename and delete old output file if it exists
        if reform:
            if isinstance(reform, six.string_types):
                if reform.endswith('.json'):
                    ref = '-{}'.format(reform[:-5])
                else:
                    ref = '-{}'.format(reform)
                self._using_reform_file = True
            elif isinstance(reform, dict):
                ref = ''
                self._using_reform_file = False
            else:
                msg = 'IncomeTaxIO.ctor reform is neither None, str, nor dict'
                raise ValueError(msg)
        else:
            ref = ''
        self._output_filename = '{}.out-inctax{}'.format(inp_str, ref)
        if os.path.isfile(self._output_filename):
            os.remove(self._output_filename)
        # check for existence of file named input_filename
        if not os.path.isfile(input_filename):
            msg = 'INPUT file named {} could not be found'
            raise ValueError(msg.format(input_filename))
        # create Policy object assuming current-law policy
        policy = Policy()
        # check for valid tax_year value
        if tax_year < policy.start_year:
            msg = 'tax_year {} less than policy.start_year {}'
            raise ValueError(msg.format(tax_year, policy.start_year))
        if tax_year > policy.end_year:
            msg = 'tax_year {} greater than policy.end_year {}'
            raise ValueError(msg.format(tax_year, policy.end_year))
        # implement policy reform if reform is specified
        if reform:
            if self._using_reform_file:
                reform_dict = Policy.read_json_reform_file(reform)
            else:
                reform_dict = reform
            policy.implement_reform(reform_dict)
        # set tax policy parameters to specified tax_year
        policy.set_year(tax_year)
        # read input file contents into Records object
        if blowup_input_data:
            recs = Records(data=input_filename,
                           start_year=Records.PUF_YEAR,
                           consider_imputations=True)
        else:
            recs = Records(data=input_filename,
                           start_year=tax_year,
                           consider_imputations=False)
        # create Calculator object
        self._calc = Calculator(policy=policy, records=recs,
                                sync_years=blowup_input_data)

    def tax_year(self):
        """
        Returns year for which IncomeTaxIO calculations are being done.
        """
        return self._calc.policy.current_year

    def calculate(self, write_output_file=True, output_weights=False):
        """
        Calculate taxes for all INPUT lines and write OUTPUT to file.

        Parameters
        ----------
        write_output_file: boolean

        output_weights: boolean
            whether or not to use s006 as an additional output variable.

        Returns
        -------
        nothing: void
        """
        output = {}  # dictionary indexed by Records index for filing unit
        self._calc.calc_all()
        for idx in range(0, self._calc.records.dim):
            ovar = SimpleTaxIO.extract_output(self._calc.records, idx,
                                              extract_weight=output_weights)
            ovar[6] = 0.0  # no FICA tax liability included in output
            output[idx] = ovar
        # write contents of output dictionary to OUTPUT file
        if write_output_file:
            SimpleTaxIO.write_output_file(output, self._output_filename)

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
               'which is a csv-formatted text file whose name ends in .csv\n'
               'and whose column names are IRS-SOI Public Use File (PUF)\n'
               'variable names.\n')
        sys.stdout.write(ivd)
        ovd = ('**** IncomeTaxIO OUTPUT variables in Internet-TAXSIM format:\n'
               '[ 1] arbitrary id of income tax filing unit\n'
               '[ 2] calendar year of income tax filing\n'
               '[ 3] state code [ALWAYS ZERO]\n'
               '[ 4] federal income tax liability\n'
               '[ 5] state income tax liability [ALWAYS ZERO]\n'
               '[ 6] FICA (OASDI+HI) tax liability [ALWAYS ZERO]\n'
               '[ 7] marginal federal income tax rate [ALWAYS ZERO]\n'
               '[ 8] marginal state income tax rate [ALWAYS ZERO]\n'
               '[ 9] marginal FICA tax rate [ALWAYS ZERO]\n'
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
