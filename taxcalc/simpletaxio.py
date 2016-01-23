"""
Tax-Calculator simple tax input-output class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 simpletaxio.py
# pylint --disable=locally-disabled simpletaxio.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import os
import sys
import pandas as pd
from .policy import Policy
from .records import Records
from .calculate import Calculator


class SimpleTaxIO(object):
    """
    Constructor for the simple tax input-output class.

    Parameters
    ----------
    input_filename: string
        name of required INPUT file.

    reform_filename: string or None
        name of optional REFORM file with None implying current-law policy.

    emulate_taxsim_2441_logic: boolean
        true implies emulation of questionable Internet-TAXSIM logic, which
        is necessary if the SimpleTaxIO class is being used in validation
        tests against Internet-TAXSIM output.

    Raises
    ------
    ValueError:
        if file with input_filename does not exist.
        if earliest INPUT year before simtax start year.
        if latest INPUT year after simtax end year.

    Returns
    -------
    class instance: SimpleTaxIO
    """

    def __init__(self,
                 input_filename,
                 reform_filename,
                 emulate_taxsim_2441_logic):
        """
        SimpleTaxIO class constructor.
        """
        # construct output_filename and delete old output file if it exists
        if reform_filename:
            if reform_filename.endswith('.json'):
                ref = '-{}'.format(reform_filename[:-5])
            else:
                ref = '-{}'.format(reform_filename)
        else:
            ref = ''
        self._output_filename = '{}.out-simtax{}'.format(input_filename, ref)
        if os.path.isfile(self._output_filename):
            os.remove(self._output_filename)
        # check for existence of file named input_filename
        if not os.path.isfile(input_filename):
            msg = 'INPUT file named {} could not be found'
            raise ValueError(msg.format(input_filename))
        # read input file contents into self._input dictionary
        self._read_input(input_filename)
        self._policy = Policy()
        # implement reform if reform file is specified
        if reform_filename:
            reform = Policy.read_json_reform_file(reform_filename)
            self._policy.implement_reform(reform)
        # validate input variable values
        self._validate_input()
        self._calc = self._calc_object(emulate_taxsim_2441_logic)

    def start_year(self):
        """
        Returns starting year for SimpleTaxIO calculations
        """
        return self._policy.start_year

    def end_year(self):
        """
        Returns ending year for SimpleTaxIO calculations
        """
        return self._policy.end_year

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
        # loop through self._year_set doing tax calculations and saving output
        output = {}  # dictionary indexed by Records index for filing unit
        for calcyr in self._year_set:
            if calcyr != self._calc.policy.current_year:
                self._calc.policy.set_year(calcyr)
            self._calc.calc_all()
            (mtr_fica, mtr_itax,
             _) = self._calc.mtr(wrt_full_compensation=False)
            cr_taxyr = self._calc.records.FLPDYR  # pylint: disable=no-member
            for idx in range(0, self._calc.records.dim):
                indyr = cr_taxyr[idx]
                if indyr == calcyr:
                    ovar = SimpleTaxIO.extract_output(self._calc.records, idx)
                    ovar[7] = 100 * mtr_itax[idx]
                    ovar[9] = 100 * mtr_fica[idx]
                    output[idx] = ovar
        # write contents of output
        if write_output_file:
            assert len(output) == len(self._input)
            self.write_output_file(output, self._output_filename)

    def number_input_lines(self):
        """
        Return number of lines read from INPUT file.
        """
        return len(self._input)

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
        ivd = ('**** SimpleTaxIO INPUT variables in Internet-TAXSIM format:\n'
               'Note that each INPUT variable must be an integer.\n'
               '(NEG) notation means that variable can be negative;\n'
               '      otherwise variable must be non-negative.\n'
               '[ 1] arbitrary id of income tax filing unit\n'
               '[ 2] calendar year of income tax filing\n'
               '[ 3] state code [MUST BE ZERO]\n'
               '[ 4] filing status [MUST BE 1, 2, or 3]\n'
               '     1=single, 2=married_filing_jointly, 3=head_of_household\n'
               '[ 5] total number of dependents\n'
               '[ 6] number of taxpayer/spouse who are age 65+\n'
               '[ 7] taxpayer wage and salary income\n'
               '[ 8] spouse wage and salary income\n'
               '[ 9] qualified dividend income\n'
               '[10] other property income (NEG)\n'
               '[11] pension benefits that are federally taxable\n'
               '[12] total social security (OASDI) benefits\n'
               '[13] other non-fed-taxable transfer income [MUST BE ZERO]\n'
               '[14] rent paid [MUST BE ZERO]\n'
               '[15] real-estate taxes paid: an AMT-preference item\n'
               '[16] other itemized deductions that are AMT-preference items\n'
               '[17] child care expenses\n'
               '[18] unemployment (UI) benefits received\n'
               '[19] number of dependents under age 17\n'
               '[20] itemized deductions that are not AMT-preference items\n'
               '[21] short-term capital gains or losses (NEG)\n'
               '[22] long-term capital gains or losses (NEG)\n')
        sys.stdout.write(ivd)
        ovd = ('**** SimpleTaxIO OUTPUT variables in Internet-TAXSIM format:\n'
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

    @staticmethod
    def extract_output(crecs, idx, extract_weight=False):
        """
        Extracts tax output from crecs object for one tax filing unit.

        Parameters
        ----------
        crecs: Records
            Records object embedded in Calculator object.

        idx: integer
            crecs object index of the one tax filing unit.

        extract_weight: boolean
            whether or not to extract s006 sample weight into ovar[29]

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
        ovar[6] = crecs._fica[idx]  # FICA taxes (ee+er) for OASDI+HI
        ovar[7] = 0.0  # marginal federal income tax rate as percent
        ovar[8] = 0.0  # no state income tax calculation
        ovar[9] = 0.0  # marginal FICA tax rate as percent
        ovar[10] = crecs.c00100[idx]  # federal AGI
        ovar[11] = crecs.e02300[idx]  # UI benefits in AGI
        ovar[12] = crecs.c02500[idx]  # OASDI benefits in AGI
        ovar[13] = 0.0  # always set zero-bracket amount to zero
        pre_phase_out_pe = crecs._prexmp[idx]
        post_phase_out_pe = crecs.c04600[idx]
        phased_out_pe = pre_phase_out_pe - post_phase_out_pe
        ovar[14] = post_phase_out_pe  # post-phase-out personal exemption
        ovar[15] = phased_out_pe  # personal exemption that is phased out
        # ovar[16] can be positive for non-itemizer:
        ovar[16] = crecs.c21040[idx]  # itemized deduction that is phased out
        # ovar[17] is zero for non-itemizer:
        ovar[17] = crecs.c04470[idx]  # post-phase-out itemized deduction
        ovar[18] = crecs.c04800[idx]  # federal regular taxable income
        ovar[19] = crecs.c05200[idx]  # regular tax on taxable income
        ovar[20] = 0.0  # always set exemption surtax to zero
        ovar[21] = 0.0  # always set general tax credit to zero
        ovar[22] = crecs.c07220[idx]  # child tax credit (adjusted)
        ovar[23] = crecs.c11070[idx]  # extra child tax credit (refunded)
        ovar[24] = crecs.c07180[idx]  # child care credit
        ovar[25] = crecs._eitc[idx]  # federal EITC
        ovar[26] = crecs.c62100_everyone[idx]  # federal AMT taxable income
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
            num = SimpleTaxIO.OVAR_NUM + 1
        else:
            num = SimpleTaxIO.OVAR_NUM
        for dvar_name in SimpleTaxIO.DVAR_NAMES:
            num += 1
            dvar = getattr(crecs, dvar_name, None)
            if dvar is None:
                msg = 'debugging variable name "{}" not in calc.records object'
                raise ValueError(msg.format(dvar_name))
            else:
                ovar[num] = dvar[idx]
        return ovar

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
                SimpleTaxIO._write_output_line(output[idx], output_file)

    # --- begin private methods of SimpleTaxIO class --- #

    IVAR_NUM = 22
    IVAR_NONNEG = {1: True, 2: True, 3: True, 4: True, 5: True,
                   6: True, 7: True, 8: True, 9: True, 10: False,
                   11: True, 12: True, 13: True, 14: True, 15: True,
                   16: True, 17: True, 18: True, 19: True, 20: True,
                   21: False, 22: False}  # True ==> value must be non-negative

    def _read_input(self, input_filename):
        """
        Read INPUT and save input variables in self._input dictionary.

        Parameters
        ----------
        input_filename: string
            name of simtax INPUT file.

        Raises
        ------
        ValueError:
            if INPUT variables are not in Internet-TAXSIM format.
            if INPUT variables have improper numeric type or value.

        Returns
        -------
        nothing: void

        Notes
        -----
        The integer value of each input variable is stored in the
        self._input dictionary, which is indexed by INPUT file line
        number and by INPUT file variable number (where both indexes
        begin with one).
        """
        self._input = {}  # indexed by line number and by variable number
        lnum = 0
        used_var1_strings = set()
        with open(input_filename, 'r') as input_file:
            for line in input_file:
                lnum += 1
                istrlist = line.split()
                if len(istrlist) != SimpleTaxIO.IVAR_NUM:
                    msg = ('simtax INPUT line {} has {} not '
                           '{} space-delimited variables')
                    raise ValueError(msg.format(lnum, len(istrlist),
                                                SimpleTaxIO.IVAR_NUM))
                vnum = 0
                vardict = {}
                for istr in istrlist:
                    vnum += 1
                    # convert istr to integer value
                    try:
                        val = int(istr)
                    except:
                        msg = ('simtax INPUT line {} variable {} has '
                               'value {} that is not an integer')
                        raise ValueError(msg.format(lnum, vnum, istr))
                    # check val for proper value range
                    if SimpleTaxIO.IVAR_NONNEG[vnum]:
                        if val < 0:
                            msg = ('var[{}]={} on line {} of simtax INPUT has '
                                   'a negative value')
                            raise ValueError(msg.format(vnum, val, lnum))
                    # check that var[1] is unique in INPUT file
                    if vnum == 1:
                        if istr in used_var1_strings:
                            msg = ('var[1]={} on line {} of simtax INPUT has '
                                   'already been used')
                            raise ValueError(msg.format(istr, lnum))
                        else:
                            used_var1_strings.add(istr)
                    # add val for vnum to vardict
                    vardict[vnum] = val
                # add lnum:vardict pair to self._input dictionary
                self._input[lnum] = vardict

    def _validate_input(self):
        """
        Validate INPUT variable values stored in self._input dictionary.

        Parameters
        ----------
        none: void

        Raises
        ------
        ValueError:
            if INPUT variable values are not in proper range of values.

        Returns
        -------
        nothing: void

        Notes
        -----
        The integer value of each input variable is stored in the
        self._input dictionary, which is indexed by INPUT file line
        number and by INPUT file variable number (where both indexes
        begin with one).
        """
        self._year_set = set()
        min_year = self.start_year()
        max_year = self.end_year()
        for lnum in range(1, len(self._input) + 1):
            var = self._input[lnum]
            year = var[2]
            if year < min_year or year > max_year:
                msg = ('var[2]={} on line {} of simtax INPUT is not in '
                       '[{},{}] Policy start-year, end-year range')
                raise ValueError(msg.format(year, lnum, min_year, max_year))
            if year not in self._year_set:
                self._year_set.add(year)
            state = var[3]
            if state != 0:
                msg = ('var[3]={} on line {} of simtax INPUT is not zero '
                       'to indicate no state income tax calculations')
                raise ValueError(msg.format(state, lnum))
            filing_status = var[4]
            if filing_status < 1 or filing_status > 3:
                msg = ('var[4]={} on line {} of simtax INPUT is not '
                       'in [1,3] filing-status range')
                raise ValueError(msg.format(filing_status, lnum))
            num_all_dependents = var[5]
            if filing_status == 3 and num_all_dependents == 0:
                msg = ('var[5]={} on line {} of simtax INPUT is not '
                       'positive when var[4] equals 3')
                raise ValueError(msg.format(num_all_dependents, lnum))
            num_aged = var[6]
            if filing_status == 2:
                if num_aged > 2:
                    msg = ('var[6]={} on line {} of simtax INPUT is not '
                           'less than or equal to two')
                    raise ValueError(msg.format(num_aged, lnum))
            else:  # if filing_status is 1=single or 3=head_of_household
                if num_aged > 1:
                    msg = ('var[6]={} on line {} of simtax INPUT is not '
                           'less than or equal to one')
                    raise ValueError(msg.format(num_aged, lnum))
            transfers = var[13]
            if transfers != 0:
                msg = ('var[13]={} on line {} of simtax INPUT is not zero '
                       'to indicate no state income tax calculations')
                raise ValueError(msg.format(transfers, lnum))
            rent = var[14]
            if rent != 0:
                msg = ('var[14]={} on line {} of simtax INPUT is not zero '
                       'to indicate no state income tax calculations')
                raise ValueError(msg.format(rent, lnum))
            num_young_dependents = var[19]
            if num_young_dependents > num_all_dependents:
                msg = ('var[19]={} on line {} of simtax INPUT is not less '
                       'than or equal to var[5]={}')
                raise ValueError(msg.format(num_young_dependents, lnum,
                                            num_all_dependents))

    def _calc_object(self, emulate_taxsim_2441_logic):
        """
        Create and return Calculator object to conduct the tax calculations.

        Parameters
        ----------
        emulate_taxsim_2441_logic: boolean

        Returns
        -------
        calc: Calculator
        """
        # create all-zeros dictionary and then list of all-zero dictionaries
        zero_dict = {}
        for varname in Records.VALID_READ_VARS:
            zero_dict[varname] = 0
        dict_list = [zero_dict for _ in range(0, len(self._input))]
        # use dict_list to create a Pandas DataFrame and Records object
        recsdf = pd.DataFrame(dict_list, dtype='int64')
        recs = Records(data=recsdf, start_year=self._policy.start_year,
                       consider_imputations=False)
        assert recs.dim == len(self._input)
        # specify input for each tax filing unit in Records object
        lnum = 0
        for idx in range(0, recs.dim):
            lnum += 1
            SimpleTaxIO._specify_input(recs, idx, self._input[lnum],
                                       emulate_taxsim_2441_logic)
        # create Calculator object containing all tax filing units
        return Calculator(policy=self._policy, records=recs, sync_years=False)

    @staticmethod
    def _specify_input(recs, idx, ivar, emulate_taxsim_2441_logic):
        """
        Specifies recs values for index idx using ivar input variables.

        Parameters
        ----------
        recs: Records
            Records object containing a row for each tax filing unit.

        idx: integer
            recs index of the tax filing unit whose input is in ivar.

        ivar: dictionary
            input variables for a single tax filing unit.

        emulate_taxsim_2441_logic: boolean

        Returns
        -------
        nothing: void
        """
        recs.RECID[idx] = ivar[1]  # tax filing unit id
        recs.FLPDYR[idx] = ivar[2]  # tax year
        # no use of ivar[3], state code (always equal to zero)
        if ivar[4] == 3:  # head-of-household is 3 in SimpleTaxIO INPUT file
            mars_value = 4  # head-of-household is MARS=4 in Tax-Calculator
            num_taxpayers = 1
        else:  # if ivar[4] is 1=single or 2=married_filing_jointly
            mars_value = ivar[4]
            num_taxpayers = ivar[4]
        recs.MARS[idx] = mars_value  # income tax filing status
        num_dependents = ivar[5]  # total number of dependents
        num_eitc_qualified_kids = num_dependents  # simplifying assumption
        recs.EIC[idx] = min(num_eitc_qualified_kids, 3)
        total_num_exemptions = num_taxpayers + num_dependents
        recs.XTOT[idx] = total_num_exemptions
        # pylint: disable=protected-access
        recs._numextra[idx] = ivar[6]  # number of taxpayers age 65+
        recs.e00200p[idx] = ivar[7]  # wage+salary income of taxpayer
        recs.e00200s[idx] = ivar[8]  # wage+salary income of spouse
        recs.e00200[idx] = ivar[7] + ivar[8]  # combined wage+salary income
        recs.e00650[idx] = ivar[9]  # qualified dividend income
        recs.e00600[idx] = ivar[9]  # qual.div. included in ordinary dividends
        recs.e00300[idx] = ivar[10]  # other property income (+/-)
        recs.e01700[idx] = ivar[11]  # federally taxable pensions
        recs.e02400[idx] = ivar[12]  # gross social security benefits
        recs.e00400[idx] = ivar[13]  # federal tax-exempt interest
        # no use of ivar[14] because no state income tax calculations
        recs.e18500[idx] = ivar[15]  # real-estate (property) taxes paid
        recs.e18400[idx] = ivar[16]  # other AMT-preferred deductions
        recs.e32800[idx] = ivar[17]  # child care expenses (Form 2441)
        recs.e32750[idx] = ivar[17]  # child care expenses (Form 2441)
        # approximate number of Form 2441 qualified persons associated with
        # the child care expenses specified by ivar[17] (Note that the exact
        # number is the number of dependents under age 13, but that is not
        # an Internet-TAXSIM input variable; hence the need to approximate.)
        if emulate_taxsim_2441_logic:
            recs.f2441[idx] = num_dependents  # all dependents of any age
        else:
            recs.f2441[idx] = ivar[19]  # number dependents under age 17
        recs.e02300[idx] = ivar[18]  # unemployment compensation received
        recs.n24[idx] = ivar[19]  # number dependents under age 17
        recs.e19200[idx] = ivar[20]  # AMT-nonpreferred deductions
        recs.p22250[idx] = ivar[21]  # short-term capital gains (+/-)
        recs.p23250[idx] = ivar[22]  # long-term capital gains (+/-)

    OVAR_NUM = 28
    DVAR_NAMES = [  # OPTIONAL DEBUGGING OUTPUT VARIABLE NAMES
        # '...',  # first debugging variable
        # '...',  # second debugging variable
        # etc.
        # '...'   # last debugging variable
    ]
    OVAR_FMT = {1: '{:d}.',  # add decimal point as in Internet-TAXSIM output
                2: ' {:d}',
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
    def _write_output_line(output_dict, output_file):
        """
        Write line of OUTPUT in output_dict to output_file.

        Parameters
        ----------
        output_dict: dictionary
            calculated output values indexed from 1 to OVAR_NUM.

        output_file: file handle
            output text file.

        Returns
        -------
        nothing: void
        """
        num_ovar = len(output_dict)
        for vnum in range(1, num_ovar + 1):
            fnum = min(vnum, SimpleTaxIO.OVAR_NUM)
            ostr = SimpleTaxIO.OVAR_FMT[fnum].format(output_dict[vnum])
            output_file.write(ostr)
        output_file.write('\n')


# end SimpleTaxIO class
