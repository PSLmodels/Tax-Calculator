"""
Testing file for calculate.py
"""

from pandas import DataFrame, concat
from taxcalc.calculate import *
from taxcalc.puf import *
from taxcalc.constants import *
import taxcalc.constants as constants


def to_csv(fname, df):
    """
    Save this dataframe to a CSV file with name 'fname' and containing
    a header with the column names of the dataframe.
    """
    df.to_csv(fname, float_format= '%1.3f', sep=',', header=True, index=False)


def split_into_CSVs(calculatedDF):
    filenames_cols = {
    'FilingStatus' : ['_sep', '_txp'],
    'Adj' : ['_feided', 'c02900'],
    'CapGains' : ['c23650', 'c01000', 'c02700', '_ymod1', '_ymod2',
                               '_ymod3', '_ymod'],
    'SSBenefits' : ['c02500', 'e02500'],
    'AGI' : ['c02650', 'c00100', '_agierr', '_posagi',
                              '_ywossbe', '_ywossbc', '_prexmp', 'c04600'],
    'ItemDed' : ['c17750', 'c17000', '_sit1', '_sit', '_statax', 'c18300', 'c37703',
             'c20500', 'c20750', 'c20400', 'c19200', 'c20800', '_lim50',
             '_lim30', 'c19700', 'c21060', '_phase2', '_itemlimit',
             '_nonlimited', '_limitratio', 'c04470', '_itemlimit', '_dedpho',
             '_dedmin', 'c21040'],
    'EIFICA' : ['_sey', '_fica', '_setax', '_seyoff', 'c11055', '_earned'],
    'StdDed' : ['c15100', 'c04100', '_numextra', '_txpyers', 'c04200', 'c15200',
              '_standard', '_othded', 'c04100', 'c04200', '_standard',
              'c04500', 'c04800', 'c60000', '_amtstd', '_taxinc', '_feitax',
              '_oldfei'],
    'XYZD' : ['_xyztax', 'c05200'],
    'NonGain' : ['_cglong', '_noncg'],
    'TaxGains' : ['e00650', '_hasgain', '_dwks5', 'c24505', 'c24510', '_dwks9',
              'c24516', 'c24580', 'c24516', '_dwks12', 'c24517', 'c24520',
              'c24530', '_dwks16', '_dwks17', 'c24540', 'c24534', '_dwks21',
              'c24597', 'c24598', '_dwks25', '_dwks26', '_dwks28', 'c24610',
              'c24615', '_dwks31', 'c24550', 'c24570', '_addtax', 'c24560',
              '_taxspecial', 'c05100', 'c05700', 'c59430', 'c59450', 'c59460',
              '_line17', '_line19', '_line22', '_line30', '_line31',
              '_line32', '_line36', '_line33', '_line34', '_line35',
              'c59485', 'c59490', 'c05700', '_s1291', '_parents', 'c05750',
              '_taxbc'],
    'MUI' : ['c05750'],
    'AMTI' : ['c62720', 'c60260', 'c63100', 'c60200', 'c60240', 'c60220',
              'c60130', 'c62730', '_addamt', 'c62100', '_cmbtp', '_edical',
              '_amtsepadd', 'c62600', '_agep', '_ages', 'c62600', 'c62700',
              '_alminc', '_amtfei', 'c62780', 'c62900', 'c63000', 'c62740',
              '_ngamty', 'c62745', 'y62745', '_tamt2', '_amt5pc', '_amt15pc',
              '_amt25pc', 'c62747', 'c62755', 'c62770', '_amt', 'c62800',
              'c09600', '_othtax', 'c05800'],
    'F2441' : ['_earned', 'c32880', 'c32890', '_ncu13', '_dclim', 'c32800'],
    'DepCareBen' : ['_seywage', 'c33465', 'c33470', 'c33475', 'c33480', 'c32840',
              'c32800', 'c33000'],
    'ExpEarnedInc' : ['_tratio', 'c33200', 'c33400', 'c07180'],
    'RateRed' : ['c07970', 'c05800', 'c59560'],
    'NumDep' : ['_ieic', 'EICYB1', 'EICYB2', 'EICYB3', '_modagi',
              'c59660', '_val_ymax', '_preeitc', '_val_rtbase',
              '_val_rtless', '_dy'],
    'ChildTaxCredit' : ['c11070', 'c07220', 'c07230', '_precrd', '_num', '_nctcr',
              '_precrd', '_ctcagi'],
    'AmOppCr' : ['c87482', 'c87487', 'c87492', 'c87497', 'c87483', 'c87488',
              'c87493', 'c87498', 'c87521'],
    'LLC' : ['c87540', 'c87550', 'c87530'],
    'RefAmOpp' : ['c87654', 'c87656', 'c87658', 'c87660', 'c87662', 'c87664',
              'c87666', 'c10960', 'c87668', 'c87681'],
    'NonEdCr' : ['c87560', 'c87570', 'c87580', 'c87590', 'c87600', 'c87610',
              'c87620', '_ctc1', '_ctc2', '_regcrd', '_exocrd', '_ctctax',
              'c07220'],
    'AddCTC' : ['c82940', 'c82925', 'c82930', 'c82935', 'c82880', 'h82880',
              'c82885', 'c82890', 'c82900', 'c82905', 'c82910', 'c82915',
              'c82920', 'c82937', 'c82940', 'c11070', 'e59660', '_othadd'],
    'F5405' : ['c64450'],
    'C1040' : ['c07100', 'y07100', 'x07100', 'c08795', 'c08800', 'e08795',
              'c09200'],
    'DEITC' : ['c59680', 'c59700', 'c59720', '_comb', 'c07150', 'c10950'],
    'SOIT' : ['c10300', '_eitc']
    }

    for file_name in filenames_cols:
        relevant_columns = filenames_cols[file_name]
        relevant_df = calculatedDF[relevant_columns]
        to_csv(file_name + '.csv', relevant_df)

    
def run(puf=True):
    """
    Run each function defined in calculate.py, saving the ouput to a CSV file.
    'puf' set to True by default, to use the 'puf2.csv' as an input
    
    For functions returning an additional non-global variable in addition
    to the DataFrame to be printed, one line saves the dataFrame to be printed 
    first, and then saves the variable to be used by a following function second. 
    """
    tax_dta = pd.read_csv("puf2.csv")
    calc = Calculator(tax_dta)
    set_input_data(calc)
    update_globals_from_calculator(calc)
    update_calculator_from_module(calc, constants)

    calculated = DataFrame()

    calculated = concat([calculated, FilingStatus()], axis=1)
    calculated = concat([calculated, Adj()], axis=1)
    calculated = concat([calculated, CapGains()], axis=1)
    calculated = concat([calculated, SSBenefits()], axis=1)
    calculated = concat([calculated, AGI()], axis=1)
    calculated = concat([calculated, ItemDed(puf)], axis=1)
    df_EI_FICA, _earned = EI_FICA()
    calculated = concat([calculated, df_EI_FICA], axis=1)
    calculated = concat([calculated, StdDed()], axis=1)
    calculated = concat([calculated, XYZD()], axis=1)
    calculated = concat([calculated, NonGain()], axis=1)
    df_Tax_Gains, c05750 = TaxGains()
    calculated = concat([calculated, df_Tax_Gains], axis=1)
    calculated = concat([calculated, MUI(c05750)], axis=1)
    df_AMTI, c05800 = AMTI(puf)
    calculated = concat([calculated, df_AMTI], axis=1)
    df_F2441, c32800 = F2441(puf, _earned)
    calculated = concat([calculated, df_F2441], axis=1)
    calculated = concat([calculated, DepCareBen(c32800)], axis=1)
    calculated = concat([calculated, ExpEarnedInc()], axis=1)
    calculated = concat([calculated, RateRed(c05800)], axis=1)
    calculated = concat([calculated, NumDep(puf)], axis=1)
    calculated = concat([calculated, ChildTaxCredit()], axis=1)
    calculated = concat([calculated, AmOppCr()], axis=1)
    df_LLC, c87550 = LLC(puf)
    calculated = concat([calculated, df_LLC], axis=1)
    to_csv('LLC.csv', df_LLC)
    calculated = concat([calculated, RefAmOpp()], axis=1)
    calculated = concat([calculated, NonEdCr(c87550)], axis=1)
    calculated = concat([calculated, AddCTC(puf)], axis=1)
    calculated = concat([calculated, F5405()], axis=1)
    df_C1040, _eitc = C1040(puf)
    calculated = concat([calculated, df_C1040], axis=1)
    calculated = concat([calculated, DEITC()], axis=1)
    calculated = concat([calculated, SOIT(_eitc)], axis=1)
    split_into_CSVs(calculated)


if __name__ == '__main__':
    run()

