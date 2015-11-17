"""
Tax-Calculator income tax input-output class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 incometaxio.py
# pylint --disable=locally-disabled incometaxio.py

import os
import sys
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
        name of INPUT file that is CSV formatted using SOI PUF varnames.

    tax_year: integer
        calendar year for which income taxes will be computed for INPUT.

    reform_filename: string or None
        name of optional REFORM file with None implying current-law policy.

    Raises
    ------
    ValueError:
        if file with input_filename does not exist.
        if tax_year before Policy start_year.
        if tax_year after Policy end_year.

    Returns
    -------
    class instance: IncomeTaxIO
    """

    def __init__(self,
                 input_filename,
                 tax_year,
                 reform_filename):
        """
        IncomeTaxIO class constructor.
        """
        # check that input_filename ends with .csv
        if not input_filename.endswith('.csv'):
            msg = 'INPUT file named {} does not end in ".csv"'
            raise ValueError(msg.format(input_filename))
        # construct output_filename and delete old output file if it exists
        inp = '-{}'.format(input_filename[:-4])
        if reform_filename:
            if reform_filename.endswith('.json'):
                ref = '-{}'.format(reform_filename[:-5])
            else:
                ref = '-{}'.format(reform_filename)
        else:
            ref = ''
        self._output_filename = '{}.out-inctax{}'.format(inp, ref)
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
        # implement policy reform if reform file is specified
        if reform_filename:
            reform = Policy.read_json_reform_file(reform_filename)
            policy.implement_reform(reform)
        # set tax policy parameters to specified tax_year
        policy.set_year(tax_year)
        # read input file contents into Records object
        # (recs does not include the IRS-SOI-PUF aggregate record)
        recs = Records(data=input_filename,
                       start_year=tax_year,
                       consider_imputations=False)
        recs.FLPDYR = tax_year
        # create Calculator object
        self._calc = Calculator(policy=policy, records=recs, sync_years=False)

    def start_year(self):
        """
        Returns earliest year for IncomeTaxIO calculations
        """
        return self._calc.policy.start_year

    def end_year(self):
        """
        Returns latest year for IncomeTaxIO calculations
        """
        return self._calc.policy.end_year

    def calculate(self, write_output_file=True):
        """
        Calculate taxes for all INPUT lines and write OUTPUT to file.

        Parameters
        ----------
        write_output_file: boolean

        Returns
        -------
        nothing: void
        """
        output = {}
        self._calc.calc_all()
        for idx in range(0, self._calc.records.dim):
            lnum = idx + 1
            ovar = SimpleTaxIO.extract_output(self._calc.records, idx)
            output[lnum] = ovar
        (mtr_fica, mtr_itax, _) = self._calc.mtr(wrt_full_compensation=False)
        for idx in range(0, self._calc.records.dim):
            lnum = idx + 1
            output[lnum][7] = 100 * mtr_itax[idx]
            output[lnum][9] = 100 * mtr_fica[idx]
        # write contents of output
        if write_output_file:
            SimpleTaxIO.write_output_file(output, self._output_filename)

    def number_input_lines(self):
        """
        Return number of lines read from INPUT file.
        """
        return len(self._calc.records.dim)

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
               '[ 6] FICA (OASDI+HI) tax liability (sum of ee and er share)\n'
               '[ 7] marginal federal income tax rate as percent\n'
               '[ 8] marginal state income tax rate [ALWAYS ZERO]\n'
               '[ 9] marginal FICA tax rate as percent\n'
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
