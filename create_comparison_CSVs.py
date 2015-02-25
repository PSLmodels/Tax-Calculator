
from pandas import DataFrame
import numpy as np
import argparse

both_cols = ['_feided', 'c02900', 'c23650', 'c01000', 'c02700', '_ymod1', '_ymod2', '_ymod3', '_ymod', 'c02500',
             'e02500', 'c02650', 'c00100', '_agierr', '_posagi', '_ywossbe', '_ywossbc', '_prexmp', 'c04600',
             'c17750', 'c17000', '_sit', '_statax', 'c18300', 'c37703', 'c20500', 'c20750', 'c20400', 'c19200',
             'c20800', 'c19700', 'c21060', '_phase2', '_nonlimited', '_limitratio', 'c04470', 'c21040', '_sey',
             '_fica', '_setax', '_seyoff', 'c11055', '_earned', 'c15100', '_numextra', '_txpyers', 'c15200',
             '_othded', 'c04100', 'c04200', '_standard', 'c04500', 'c04800', 'c60000', '_amtstd', '_taxinc',
             '_feitax', '_oldfei', '_xyztax', 'c05200', '_cglong', '_noncg', 'e00650', '_hasgain', '_dwks5',
             'c24505', 'c24510', '_dwks9', 'c24516', 'c24580', '_dwks12', 'c24517', 'c24520', 'c24530', '_dwks16',
             '_dwks17', 'c24540', 'c24534', '_dwks21', 'c24597', 'c24598', '_dwks25', '_dwks26', '_dwks28', 'c24610',
             'c24615', '_dwks31', 'c24550', 'c24570', '_addtax', 'c24560', '_taxspecial', 'c05100', 'c05700', 'c59430',
             'c59450', 'c59460', '_line17', '_line19', '_line22', '_line30', '_line31', '_line32', '_line36', '_line33',
             '_line34', '_line35', 'c59485', 'c59490', '_s1291', '_parents', 'c05750', '_taxbc', 'c62720', 'c60260',
             'c63100', 'c60200', 'c60240', 'c60220', 'c60130', 'c62730', '_addamt', 'c62100', '_cmbtp', '_edical',
             '_amtsepadd', '_agep', '_ages', 'c62600', 'c62700', '_alminc', '_amtfei', 'c62780', 'c62900', 'c63000',
             'c62740', '_ngamty', 'c62745', 'y62745', '_tamt2', '_amt5pc', '_amt15pc', '_amt25pc', 'c62747', 'c62755',
             'c62770', '_amt', 'c62800', 'c09600', '_othtax', 'c05800', 'c32880', 'c32890', '_ncu13', '_dclim', 'c32800',
             '_seywage', 'c33465', 'c33470', 'c33475', 'c33480', 'c32840', 'c33000', '_tratio', 'c33200', 'c33400',
             'c07180', 'c07970', 'c59560', '_ieic', '_modagi', 'c59660', '_val_ymax', '_preeitc', '_val_rtbase',
             '_val_rtless', '_dy', 'c11070', 'c07220', 'c07230', '_num', '_nctcr', '_precrd', '_ctcagi', 'c87482',
             'c87487', 'c87492', 'c87497', 'c87483', 'c87488', 'c87493', 'c87498', 'c87521', 'c87540', 'c87550', 'c87530',
             'c87654', 'c87656', 'c87658', 'c87660', 'c87662', 'c87664', 'c87666', 'c10960', 'c87668', 'c87681', 'c87560',
             'c87570', 'c87580', 'c87590', 'c87600', 'c87610', 'c87620', '_ctc1', '_ctc2', '_regcrd', '_exocrd', '_ctctax',
             'c82925', 'c82930', 'c82935', 'c82880', 'h82880', 'c82885', 'c82890', 'c82900', 'c82905', 'c82910', 'c82915',
             'c82920', 'c82937', 'c82940', 'e59660', '_othadd', 'c64450', 'c07100', 'y07100', 'x07100', 'c08795', 'c08800',
             'e08795', 'c09200', 'c59680', 'c59700', 'c59720', '_comb', 'c07150', 'c10950', 'c10300', '_eitc']


both_cols = ['_addamt', '_addtax', '_agep', '_ages', '_agierr', '_alminc', '_amt', '_amt15pc', '_amt25pc', 
	'_amt5pc', '_amtfei', '_amtsepadd', '_amtstd', '_cglong', '_cmbtp', '_comb', '_ctc1', '_ctc2', 
	'_ctcagi', '_ctctax', '_dclim', '_dwks12', '_dwks16', '_dwks17', '_dwks21', '_dwks25', '_dwks26', 
	'_dwks28', '_dwks31', '_dwks5', '_dwks9', '_dy', '_earned', '_edical', '_eitc', '_exocrd', '_feided', 
	'_feitax', '_fica', '_hasgain', '_ieic', '_limitratio', '_line17', '_line19', '_line22', '_line30', 
	'_line31', '_line32', '_line33', '_line34', '_line35', '_line36', '_modagi', '_nctcr', '_ncu13', '_ngamty', 
	'_noncg', '_nonlimited', '_num', '_numextra', '_oldfei', '_othadd', '_othded', '_othertax', '_othtax', '_parents', 
	'_posagi', '_precrd', '_preeitc', '_prexmp', '_refund', '_regcrd', '_s1291', '_sep', '_setax', '_sey', '_seyoff', 
	'_seywage', '_sit', '_standard', '_statax', '_tamt2', '_taxbc', '_taxinc', '_taxspecial', '_tratio', '_txpyers', 
	'_val_rtbase', '_val_rtless', '_val_ymax', '_xyztax', '_ymod', '_ymod1', '_ymod2', '_ymod3', '_ywossbc', 
	'_ywossbe', 'c00100', 'c01000', 'c02500', 'c02650', 'c02700', 'c02900', 'c04100', 'c04200', 'c04470', 'c04500', 
	'c04600', 'c04800', 'c05100', 'c05200', 'c05700', 'c05750', 'c05800', 'c07100', 'c07150', 'c07180', 'c07220', 
	'c07230', 'c07970', 'c08795', 'c08800', 'c09200', 'c09600', 'c10300', 'c10950', 'c10960', 'c11055', 'c11070', 
	'c15100', 'c15200', 'c17000', 'c17750', 'c18300', 'c19200', 'c19700', 'c20400', 'c20500', 'c20750', 'c20800', 
	'c21040', 'c21060', 'c23650', 'c24505', 'c24510', 'c24516', 'c24517', 'c24520', 'c24530', 'c24534', 'c24540', 
	'c24550', 'c24560', 'c24570', 'c24580', 'c24597', 'c24598', 'c24610', 'c24615', 'c32800', 'c32840', 'c32880', 
	'c32890', 'c33000', 'c33200', 'c33400', 'c33465', 'c33470', 'c33475', 'c33480', 'c37703', 'c59430', 'c59450', 
	'c59460', 'c59485', 'c59490', 'c59560', 'c59660', 'c59680', 'c59700', 'c59720', 'c60000', 'c60130', 'c60200', 
	'c60220', 'c60240', 'c60260', 'c62100', 'c62600', 'c62700', 'c62720', 'c62730', 'c62740', 'c62745', 'c62747', 
	'c62755', 'c62770', 'c62780', 'c62800', 'c62900', 'c63000', 'c63100', 'c64450', 'c82880', 'c82885', 'c82890', 
	'c82900', 'c82905', 'c82910', 'c82915', 'c82920', 'c82925', 'c82930', 'c82935', 'c82937', 'c82940', 'c87482', 
	'c87483', 'c87487', 'c87488', 'c87492', 'c87493', 'c87497', 'c87498', 'c87521', 'c87530', 'c87540', 'c87550', 
	'c87560', 'c87570', 'c87580', 'c87590', 'c87600', 'c87610', 'c87620', 'c87654', 'c87656', 'c87658', 'c87660', 
	'c87662', 'c87664', 'c87666', 'c87668', 'c87681', 'e00650', 'e02500', 'e08795', 'e59660', 'h82880', 'x07100', 'y62745']

#both_cols = ['c00100', 'c04100', 'c04600', 'c04470', 'c04800', 'c05200', 'c09600', 'c05800', 'c09200']

"""
To redetermine the necessary variables to compare (stored in both_cols), uncomment the lines below
"""

# ##Before running this commented out section, run 'test.py' using the 'puf2.csv' as in input,
# ##this will output the 'results.csv' file which is used in this script.

# #load in the data from the exall.csv file, which has all of the SAS input and output variables
# #and the 'results.csv' which has the results from the puf2.csv inputs
# print ("\nreading data from '{}'".format('exall.csv'))
# exall = DataFrame.from_csv('exall.csv')
#
# print ("reading data from '{}'".format('results.csv'))
# results = DataFrame.from_csv('results.csv')
#
# print ("converting the data...")
#
# #change the column names in the 'exall.csv' file to lowercase
# exall_cols = [x.lower() for x in exall.columns.tolist()]
# exall.columns = exall_cols
#
# #we are only interested in the 2013 data
# exall = exall[exall['flpdyr'] == 2013]
#
# #get a list of the variables/columns we care about
# results_cols = results.columns.tolist()
#
# #there are a few (temporary) variables in the results.csv that are not in the exall.csv, we want the ones in both
# both_cols = [x for x in results_cols if x in exall_cols]

"""
Example usage of this script:
python create_comparison_CSVs.py exall_results_1k.csv --digits 2
or
python create_comparison_CSVs.py exall_results.csv
"""
parser = argparse.ArgumentParser()
parser.add_argument("taxcalc_output_fname", help="filename (.csv) resulting from running test.py", type=str)
parser.add_argument("--digits", help="number of digits to round to, default value=2", type=int)
args = parser.parse_args()

#load in the data from the exall.csv file, which has all of the SAS input and output variables
print ("\nreading data from '{}'".format('exall.csv'))
exall = DataFrame.from_csv('exall.csv')
exall.columns = [x.lower() for x in exall.columns.tolist()]
exall = exall.reset_index(drop=True)
exall = exall[exall['flpdyr'] == 2013]

#create a DataFrame with the variables/columns we wish to compare
exall_results_only = exall[both_cols]

#load in the results from the taxcalc
print ("\nreading data from '{}'".format(args.taxcalc_output_fname))
taxcalc_results = DataFrame.from_csv(args.taxcalc_output_fname)

#create a DataFrame with the variables/columns we wish to compare
taxcalc_results = taxcalc_results[both_cols]

#fill in missing numbers with zero
exall_results_only = exall_results_only.fillna(0)
taxcalc_results = taxcalc_results.fillna(0)

#if using subset of data as recommended at the bottom
if len(taxcalc_results) < len(exall_results_only):
    exall_results_only = exall_results_only.head(n=len(taxcalc_results))

#since there are rounding differences in saved CSVs, this tells you which variables are actually inaccurate
inaccurate_variables = []
for label in both_cols:
    lhs = exall_results_only[label].values
    rhs = taxcalc_results[label].values
    res = np.allclose(lhs, rhs, atol=1e-02)
    if not res:
        inaccurate_variables.append(label)

if args.digits:
    digits = args.digits
else:
    digits = 2

#there may still be slight accuracy differences due differences in Python and SAS rounding
print ("\nrounding to {} digits".format(digits))
SAS_results = np.round(exall_results_only, digits)
taxcalc_results = np.round( taxcalc_results, digits)

#save the comparable csv files
SAS_results.to_csv('SAS_results.csv')
taxcalc_results.to_csv('TaxCalc_results.csv')
print ("saved comparable data in:\n{}\n{} ".format('SAS_results.csv', 'TaxCalc_results.csv'))

print ("\nproblems found in {} variables".format(len(inaccurate_variables)))
print (inaccurate_variables)






"""  OPTIONAL (For faster debugging/test.py runtime)
For quicker but not as complete testing, you can use a subset of the first 1000 rows of the exall.csv data
This requires using the new 'exall_1k.csv' as an input for test.py,
and then re-running this script using the output from the smaller data set from test.py, as the input to this script

to export this smaller data_set, change to: small_data_set = 'True'
OR
from a terminal window run this cmd (RECOMMENDED)
'head -n 1000 exall.csv > exall_1k.csv'
"""
small_data_set = False

if small_data_set:
    exall1k = exall.head(n=1000)

    exall1k.to_csv('exall_1k.csv')
    print ("\nsaved 1k subset of exall.csv to '{}'".format('exall_1k.csv'))
