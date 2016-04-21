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

import pandas as pd
from taxcalc import Policy, Records, Calculator


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
                 'age_head', 'age_spouse',
                 '_agierr', '_alminc', '_amed', '_amt15pc',
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
                 '_nonlimited', '_num', '_oldfei', '_othadd',
                 '_othded', '_othertax', '_othtax', '_parents', '_phase2_i',
                 '_posagi', '_precrd', '_preeitc', '_prexmp', '_refund',
                 '_regcrd', '_s1291', '_sep', '_sey', 'c09400', 'c03260',
                 '_seywage', '_standard', '_statax', '_tamt2', '_taxbc',
                 '_taxinc', '_taxspecial', '_tratio',
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
                 'c87668', 'c87681', 'e00650', 'e02500', 'e08795', 'h82880',
                 'x04500', 'x07100', 'y07100', 'y62745']
    dataf_truncated = dataf[col_names]

    # write test output to csv file named 'results_puf.csv'
    dataf_truncated.to_csv('results_puf.csv', float_format='%1.3f', sep=',',
                           header=True, index=False)


if __name__ == '__main__':
    run()
