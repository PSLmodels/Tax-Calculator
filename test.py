"""
Test program for Calculator class logic that uses 'puf.csv' records and
writes results to the 'results_puf.csv' file.

COMMAND-LINE USAGE: python test.py

Note that the puf.csv file that is required to run this program has
been constructed by the Tax-Calculator development team by merging
information from the most recent publicly available IRS SOI PUF file
and from the Census CPS file for the corresponding year.  If you have
acquired from IRS the most recent SOI PUF file and want to execute
this program, contact the Tax-Calculator development team to discuss
your options.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test.py
# pylint --disable=locally-disabled test.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)
import argparse
import pandas as pd
from taxcalc import Policy, Records, Calculator

'''
the main funtion gives the option to either produce real inputs after
extrapolation, or outputs based on real inputs. The real inputs can be served
for the purpose of debugging.
'''


def main():
    parser = argparse.ArgumentParser(prog='python test.py')

    parser.add_argument('--realin', default=False, action="store_true")

    args = parser.parse_args()
    if args.realin == 1:
        dontrun()
    else:
        run()


def run():
    """
    Execute Calculator.calc_all() method using 'puf.csv' input and
    writing truncated ouput to a CSV file named 'results_puf.csv'.
    """
    # create a Policy object containing current-law policy (clp) parameters
    clp = Policy()

    # create a Records object (puf) containing puf.csv input records
    puf = Records()

    # create a Calculator object using clp policy and puf records
    calc = Calculator(policy=clp, records=puf)

    calc.calc_all()
    rshape = calc.records.e00100.shape
    dataf = pd.DataFrame()
    for attr in dir(calc.records):
        value = getattr(calc.records, attr)
        if hasattr(value, "shape"):
            if value.shape == rshape:
                dataf[attr] = value

    # truncate the outputs
    col_names = ['EICYB1', 'EICYB2', 'EICYB3', 'NIIT', '_addamt', '_addtax',
                 '_agep', '_ages', '_agierr', '_alminc', '_amed', '_amt15pc',
                 '_amt20pc', '_amt25pc', '_amt5pc', '_amtfei', '_amtsepadd',
                 '_amtstd', '_avail', '_cglong', '_cmbtp', '_comb',
                 '_combined', '_ctc1', '_ctc2', '_ctcagi', '_ctctax', '_dclim',
                 '_dwks12', '_dwks16', '_dwks17', '_dwks21', '_dwks25',
                 '_dwks26', '_dwks28', '_dwks31', '_dwks5', '_dwks9', '_dy',
                 '_earned', '_eitc', '_exocrd', '_expanded_income', '_feided',
                 '_feitax', '_fica', '_hasgain', '_ieic', 'c03260',
                 '_limitratio', '_line17', '_line19', '_line22', '_line30',
                 '_line31', '_line32', '_line33', '_line34', '_line35',
                 '_line36', '_modagi', '_nctcr', '_ncu13', '_ngamty', '_noncg',
                 '_nonlimited', '_num', '_numextra', '_oldfei', '_othadd',
                 '_othded', '_othertax', '_othtax', '_parents', '_phase2_i',
                 '_posagi', '_precrd', '_preeitc', '_prexmp', '_refund',
                 '_regcrd', '_s1291', '_sep', '_sey', 'c09400', 'c03260',
                 '_seywage', '_standard', '_statax', '_tamt2', '_taxbc',
                 '_taxinc', '_taxspecial', '_tratio', '_txpyers',
                 '_val_rtbase', '_val_rtless', '_val_ymax', '_xyztax', '_ymod',
                 '_ymod1', '_ymod2', '_ymod3', '_ywossbc', '_ywossbe',
                 'c00100', 'c01000', 'c02500', 'c02650', 'c02700', 'c02900',
                 'c04100', 'c04200', 'c04470', 'c04500', 'c04600', 'c04800',
                 'c05100', 'c05200', 'c05700', 'c05750', 'c05800', 'c07100',
                 'c07150', 'c07180', 'c07220', 'c07230', 'c07240', 'c07300',
                 'c07600', 'c07970', 'c08795', 'c08800', 'c09200', 'c09600',
                 'c10300', 'c10950', 'c10960', 'c11055', 'c11070', 'c15100',
                 'c15200', 'c17000', 'c17750', 'c18300', 'c19200', 'c19700',
                 'c20400', 'c20500', 'c20750', 'c20800', 'c21040', 'c21060',
                 'c23650', 'c24505', 'c24510', 'c24516', 'c24517', 'c24520',
                 'c24530', 'c24534', 'c24540', 'c24550', 'c24560', 'c24570',
                 'c24580', 'c24597', 'c24598', 'c24610', 'c24615', 'c32800',
                 'c32840', 'c32880', 'c32890', 'c33000', 'c33200', 'c33400',
                 'c33465', 'c33470', 'c33475', 'c33480', 'c37703', 'c59430',
                 'c59450', 'c59460', 'c59485', 'c59490', 'c59560', 'c59660',
                 'c59680', 'c59700', 'c59720', 'c60000', 'c60130', 'c60200',
                 'c60220', 'c60240', 'c60260', 'c62100', 'c62100_everyone',
                 'c62600', 'c62700', 'c62720', 'c62730', 'c62740', 'c62745',
                 'c62747', 'c62755', 'c62760', 'c62770', 'c62780', 'c62800',
                 'c62900', 'c63000', 'c63100', 'c82880', 'c82885', 'c82890',
                 'c82900', 'c82905', 'c82910', 'c82915', 'c82920', 'c82925',
                 'c82930', 'c82935', 'c82937', 'c82940', 'c87482', 'c87483',
                 'c87487', 'c87488', 'c87492', 'c87493', 'c87497', 'c87498',
                 'c87521', 'c87530', 'c87540', 'c87550', 'c87560', 'c87570',
                 'c87580', 'c87590', 'c87600', 'c87610', 'c87620', 'c87654',
                 'c87656', 'c87658', 'c87660', 'c87662', 'c87664', 'c87666',
                 'c87668', 'c87681', 'e00650', 'e02500', 'e08795',
                 'x04500', 'x07100', 'y07100', 'y62745']
    dataf_truncated = dataf[col_names]

    # write test output to csv file named 'results_puf.csv'
    dataf_truncated.to_csv('results_puf.csv', float_format='%1.3f', sep=',',
                           header=True, index=False)


def dontrun():
    clp = Policy()

    puf = Records()

    calc = Calculator(policy=clp, records=puf)

    rshape = calc.records.e00100.shape
    dataf = pd.DataFrame()
    for attr in dir(calc.records):
        value = getattr(calc.records, attr)
        if hasattr(value, "shape"):
            if value.shape == rshape:
                dataf[attr] = value

# VALID_READ_VARS is a list of variables that run through tax-logic

    VALID_READ_VARS = [
        'AGIR1', 'DSI', 'EFI', 'EIC', 'ELECT', 'FDED', 'FLPDYR', 'FLPDMO',
        'f2441', 'f3800', 'f6251', 'f8582', 'f8606', 'f8829', 'f8910', 'f8936',
        'n20', 'n24', 'n25', 'n30', 'PREP', 'SCHB', 'SCHCF', 'SCHE',
        'TFORM', 'IE', 'TXST', 'XFPT', 'XFST', 'RECID', 'MARS',
        'XOCAH', 'XOCAWH', 'XOODEP', 'XOPAR', 'XTOT',
        'e00200', 'e00300', 'e00400', 'e00600', 'e00650', 'e00700', 'e00800',
        'e00200p', 'e00200s',
        'e00900', 'e01000', 'e01100', 'e01200', 'e01400', 'e01500', 'e01700',
        'e00900p', 'e00900s',
        'e02000', 'e02100', 'e02300', 'e02400', 'e02500', 'e03150', 'e03210',
        'e02100p', 'e02100s',
        'e03220', 'e03230', 'e03260', 'e03270', 'e03240', 'e03290', 'e03300',
        'e03400', 'e03500', 'e00100', 'p04470', 'e04250', 'e04600', 'e04800',
        'e05100', 'e05200', 'e05800', 'e06000', 'e06200', 'e06300', 'e09600',
        'e07180', 'e07200', 'e07220', 'e07230', 'e07240', 'e07260', 'e07300',
        'e07400', 'e07600', 'p08000', 'e07150', 'e06500', 'e08800', 'e09400',
        'e09700', 'e09800', 'e09900', 'e10300', 'e10700', 'e10900', 'e10950',
        'e10960', 'e15100', 'e15210', 'e15250', 'e15360', 'e18600', 'e59560',
        'e59680', 'e59700', 'e59720', 'e11550', 'e11070', 'e11100', 'e11200',
        'e11300', 'e11400', 'e11570', 'e11580', 'e11581', 'e11582', 'e11583',
        'e10605', 'e11900', 'e12000', 'e12200', 'e17500', 'e18400', 'e18500',
        'e19200', 'e19550', 'e19800', 'e20100', 'e19700', 'e20550', 'e20600',
        'e20400', 'e20800', 'e20500', 'e21040', 'p22250', 'e22320', 'e22370',
        'p23250', 'e24515', 'e24516', 'e24518', 'e24535', 'e24560', 'e24598',
        'e24615', 'e24570', 'p25350', 'p25380', 'p25470', 'p25700', 'e25820',
        'e25850', 'e25860', 'e25940', 'e25980', 'e25920', 'e25960', 'e26110',
        'e26170', 'e26190', 'e26160', 'e26180', 'e26270', 'e26100', 'e26390',
        'e26400', 'e27200', 'e30400', 'e30500', 'e32800', 'e33000', 'e53240',
        'e53280', 'e53410', 'e53300', 'e53317', 'e53458', 'e58950', 'e58990',
        'p60100', 'p61850', 'e60000', 'e62100', 'e62900', 'e62720', 'e62730',
        'e62740', 'p65300', 'p65400', 'p87482', 'p87521', 'e68000', 'e82200',
        't27800', 's27860', 'p27895', 'e87530', 'e87550', 'e87870', 'e87875',
        'e87880', 'MARS', 'MIDR', 'RECID', 'gender',
        'wage_head', 'wage_spouse', 'earnsplit',
        'age', 'agedp1', 'agedp2', 'agedp3', 'AGERANGE',
        's006', 's008', 's009', 'WSAMP', 'TXRT', 'filer', 'matched_weight']

    dataf_truncated = dataf[VALID_READ_VARS]

    dataf_truncated.to_csv('realin_puf.csv', float_format='%1.3f', sep=',',
                           header=True, index=False)


if __name__ == '__main__':
    main()
