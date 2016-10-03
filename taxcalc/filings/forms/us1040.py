from .tax_form import TaxForm
from taxcalc.utils import string_to_number


class US1040(TaxForm):
    _DESCRIPTIVE_NAME = 'U.S. Individual Income Tax Return'
    _EVAR_MAP = {
        'line6d': 'XTOT',  # Total number of exemptions for filing unit
        'line7': 'e00200',  # Wages, salaries, tips, etc.
        'line8a': 'e00300',  # Taxable interest
        'line8b': 'e00400',  # Tax-exempt interest income
        'line9a': 'e00600',  # Ordinary dividends
        'line9b': 'e00650',  # Qualified dividends
        'line10': 'e00700',  # Taxable refunds... of state and local income tax
        'line11': 'e00800',  # Alimony received
        'line12': 'e00900',  # Business income or loss (Sch C)
        'line14': 'e01200',  # Other gain or loss (Form 4797)
        'line15b': 'e01400',  # IRA distributions, taxable
        'line16a': 'e01500',  # Pensions and annuities in income
        'line16b': 'e01700',  # Pensions and annuities in AGI
        'line17': 'e02000',  # Rental real estate, royalties, partnerships...
        'line18': 'e02100',  # Farm income or loss
        'line19': 'e02300',  # Unemployment compensation
        'line20a': 'e02400',  # Social security benefits
        'line23': 'e03220',  # Educator expenses
        'line25': 'e03290',  # Health savings account deduction (Form 8889)
        'line28': 'e03300',  # Self-employed SEP, SIMPLE, and qualified plans
        'line29': 'e03270',  # Self-employed health insurance deduction
        'line30': 'e03400',  # Penalty on early withdrawal of savings
        'line31a': 'e03500',  # Alimony paid
        'line32': 'e03150',  # IRA deduction
        'line33': 'e03210',  # Student loan interest deduction
        'line34': 'e03230',  # Tuition and fees (Form 8917)
        'line35': 'e03240',  # Domestic production activities (Form 8903)
    }
    __EVAR_MAP_2013 = {
        'line47': 'e07300',  # Foreign tax credit - Form 1116
        'line50': 'e07240',  # Retirement Savings contrib. Credit New 2002
        'line52': 'e07260',  # Residential Energy Credit
        'line53': 'p08000',  # Other statutory credit (computer)
        'line58': 'e09900',  # Penalty tax on qualified retirement plans
        'line63': 'e11200',  # Tax Payment: Excess FICA/RRTA
        'line65': 'e11070',  # Tax Payment: Additional Child Tax Credit
    }
    __EVAR_MAP_2014_2015 = {
        'line48': 'e07300',  # Foreign tax credit - Form 1116
        'line51': 'e07240',  # Retirement Savings contrib. Credit New 2002
        'line53': 'e07260',  # Residential Energy Credit
        'line54': 'p08000',  # Other statutory credit (computer)
        'line59': 'e09900',  # Penalty tax on qualified retirement plans
        'line65': 'e11200',  # Tax Payment: Excess FICA/RRTA
        'line67': 'e11070',  # Tax Payment: Additional Child Tax Credit
    }

    # Refundable credit payment New 2007
    # I believe this is only 2008
    # https://www.irs.gov/uac/questions-and-answers-about-the-recovery-rebate-credit
    # 'line71': 'e11550',

    # First Time Homebuyer Credit New 2008
    # I believe this only applies to 2008, 2009, 2010
    # https://www.irs.gov/uac/first-time-homebuyer-credit-1
    # 'line69': 'e11580',

    _EVAR_MAP_BY_YEAR = {
        2013: __EVAR_MAP_2013,
        2014: __EVAR_MAP_2014_2015,
        2015: __EVAR_MAP_2014_2015,
    }

    __EVAR_INDIRECT_FIELDS = {
        2013: {
            'e07600': 'line53',
            'e09800': 'line57',
        },
        2014: {
            'e07600': 'line54',
            'e09800': 'line58',
        },
        2015: {
            'e07600': 'line54',
            'e09800': 'line58',
        },
    }
    _NUMERIC_NAME = 'Form 1040'
    _SUPPORTED_YEARS = [2013, 2014, 2015]

    def to_evars_indirect(self):
        results = {}
        fields = self._fields

        # MARS - Marital (filing) status
        for i in [1, 2, 3, 4, 5]:
            line = 'line{}'.format(i)
            if line in fields and fields[line]:
                results['MARS'] = i
                break

        # DSI - 1 if claimed as a dependent on another tax return, else 0
        if 'line6a' in fields:
            results['DSI'] = 0 if fields['line6a'] else 1

        # e01100 - Capital gain Distrib. not reported on Sch D
        if fields.get('line13') and fields.get('line13_no_sch_d'):
            results['e01100'] = string_to_number(fields['line13'])

        # blind_head & blind_spouse
        if 'line39a_blind' in fields:
            results['blind_head'] = 1 if fields['line39a_blind'] else 0
        if 'line39a_blind_spouse' in fields:
            if fields['line39a_blind_spouse']:
                results['blind_spouse'] = 1
            else:
                results['blind_spouse'] = 0

        # MIDR - Separately filing spouse itemizing
        if 'line39b' in fields:
            results['MIDR'] = 1 if fields['line39b'] else 0

        # e07600 - Prior year minimum tax credit
        line = self.__EVAR_INDIRECT_FIELDS[self.year]['e07600']
        if fields.get(line) and fields.get(line + 'b') and \
                not (fields.get(line + 'a') or fields.get(line + 'c')):
            results['e07600'] = string_to_number(fields[line])

        # e09800 - Social security tax on tip income
        line = self.__EVAR_INDIRECT_FIELDS[self.year]['e09800']
        if fields.get(line) and fields.get(line + 'a') and \
                not fields.get(line + 'b'):
            results['e09800'] = string_to_number(fields[line])

        return results
