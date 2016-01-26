"""
Aggregate diagnostic test program for Calculator class logic that
reads in puf.csv records and writes out diagnostic table results
to a text file named testagg-results.txt, which is under Git version
control.

COMMAND-LINE USAGE: python testagg.py

Note that the puf.csv file that is required to run this program has
been constructed by the Tax-Calculator development team by merging
information from the most recent publicly available IRS SOI PUF file
and from the Census CPS file for the corresponding year.  If you have
acquired from IRS the most recent SOI PUF file and want to execute
this program, contact the Tax-Calculator development team to discuss
your options.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 testagg.py
# pylint --disable=locally-disabled testagg.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

from taxcalc import Policy, Records, Calculator


def run():
    """
    Compute aggregate diagnostic table reading in sample data from
    the puf.csv file and writing diagnostic table contents to the
    testagg-results.txt file.
    """
    # create a Policy object (clp) containing current-law policy parameters
    clp = Policy()

    # create a Records object (puf) containing puf.csv input records
    puf = Records()

    # create a Calculator object using clp policy and puf records
    calc = Calculator(policy=clp, records=puf)

    # create aggregate diagnostic table (adt) as a Pandas DataFrame object
    adt = calc.diagnostic_table(num_years=10)

    # convert adt results to a string for writing to a text file
    adt_str = adt.to_string()

    # write adt results to the testagg-results.txt file
    with open('taxcalc/tests/pufcsv_agg_expected.txt', 'w') as output_file:
        output_file.write(adt_str)
        output_file.write('\n')


if __name__ == '__main__':
    run()
