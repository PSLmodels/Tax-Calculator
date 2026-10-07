"""
Translates TAXSIM-35 input file to Tax-Calculator tc input file.
"""

# CODING-STYLE CHECKS:
# pycodestyle prepare_tc_input.py
# pylint --disable=locally-disabled prepare_tc_input.py

import argparse
import os
import sys
import numpy as np
import pandas as pd


TAXSIM_TC_MAP = {
    "taxsimid": "RECID",
    "year": "FLPDYR",
    # 'state': # no Tax-Calculator use of TAXSIM variable 3, state code
    # 'mstat', # Tax-Calculator MARS differs from TAXSIM mstat
    "page": "age_head",
    "sage": "age_spouse",
    # 'depx': "", # no Tax-Calculator variable for total number of dependents
    "dep13": "nu13",
    "dep17": "nu18",
    # 'dep18': "n24", #"f2441", # no direct Tax-Calculator use of number EIC qualified dependents
    "pwages": "e00200p",
    "swages": "e00200s",
    "psemp": "e00900p",
    "ssemp": "e00900s",
    "dividends": "e00650",
    "intrec": "e00300",
    "stcg": "p22250",
    "ltcg": "p23250",
    "otherprop": "e02000",
    "nonprop": "e00800",
    "pensions": "e01700",
    "gssi": "e02400",
    # 'ui': 'e02300',  # For TAXSIM-35, UI is separated between primary and secondary filers
    # 'transfers': # no Tax-Calculator use of TAXSIM variable 22, non-taxable transfers
    # 'rentpaid' # no Tax-Calculator use of TAXSIM variable 23, rent paid
    "proptax": "e18500",
    "otheritem": "e18400",
    "childcare": "e32800",
    "mortgage": "e19200",
    "scorp": "e26270",
    # 'pbusinc': 'e00900p', # Not perfect match for this in Tax-Calculator -- will add to e00900s below
    # 'pprofinc': # no direct analog in Tax-Calculator
    # 'sbusinc': 'e00900s', # Not perfect match for this in Tax-Calculator -- will add to e00900s below
    # 'sprofinc':# no direct analog in Tax-Calculator
}


def main(file_in_name, file_out_name):
    """
    Translates TAXSIM-35 input file into a Tax-Calculator CSV-formatted
    tc input file. Any pre-existing OUTPUT file contents are overwritten.
    For details on Internet TAXSIM version 32 INPUT format, go to
    https://users.nber.org/~taxsim/taxsim35/

    Args:
        file_in_name (string): name of input file to run taxcalc with
        file_out_name (string): name of file to save taxcalc output to

    Returns:
        None
    """
    print("File in and out names: ", file_in_name, file_out_name)
    # check INPUT filename
    if not os.path.isfile(file_in_name):
        emsg = "INPUT file named {} does not exist".format(file_in_name)
        sys.stderr.write("ERROR: {}\n".format(emsg))
        assert False
    # check OUTPUT filename
    if file_out_name == "":
        sys.stderr.write("ERROR: must specify OUTPUT file name\n")
        assert False
    if os.path.isfile(file_out_name):
        os.remove(file_out_name)
    # read TAXSIM-35 INPUT file into a pandas DataFrame
    ivar = pd.read_csv(file_in_name, header=0, index_col=False)
    # Drop 'idtl' – used to generate detailed output
    ivar.drop(columns=["idtl"], inplace=True)
    # translate INPUT variables into OUTPUT variables
    invar = translate(ivar)
    # write OUTPUT file containing Tax-Calculator input variables
    invar.to_csv(file_out_name, index=False)
    # return no-error exit code
    return 0


# end of main function code


def translate(ivar):
    """
    Translate TAXSIM-35 input variables into Tax-Calculator input variables.
    Both ivar and returned invar are pandas DataFrame objects.
    """
    assert isinstance(ivar, pd.DataFrame)
    # Rename variables to be consistent with Tax-Calculator naming conventions
    invar = ivar.rename(TAXSIM_TC_MAP, axis=1)
    invar["n24"] = ivar["dep17"]
    # Create variables for Tax-Calculator that aren't directly represented in TAXSIM
    invar["e02000"] += invar[
        "e26270"
    ]  # add active scorp income to "otherprop" income from taxsim
    mstat = ivar["mstat"]
    assert np.all(np.logical_or(mstat == 1, mstat == 2))
    num_deps = ivar["depx"]
    mars = np.where(mstat == 1, np.where(num_deps > 0, 4, 1), 2)
    assert np.all(
        np.logical_or(mars == 1, np.logical_or(mars == 2, mars == 4))
    )
    invar["MARS"] = mars
    num_eitc_qualified_kids = ivar["dep18"]
    invar["f2441"] = invar["nu13"]
    invar["EIC"] = np.minimum(num_eitc_qualified_kids, 3)
    num_taxpayers = np.where(mars == 2, 2, 1)
    invar["XTOT"] = num_taxpayers + num_deps
    invar["e00200"] = invar["e00200p"] + invar["e00200s"]
    invar["e00900p"] += invar["pbusinc"]
    invar["e00900s"] += invar[
        "sbusinc"
    ]  # NB: will need to check this later because in TAXSIM, the e00900 does not include QBI, but businc does...
    invar["e00900"] = invar["e00900p"] + invar["e00900s"]
    invar["e00600"] = invar["e00650"]
    invar["e01500"] = invar["e01700"]
    invar["e02300"] = invar["pui"] + invar["sui"]
    # variables for QBID calculation
    invar["PT_SSTB_income"] = (
        0  # np.where(invar['pprofinc'] + invar['sprofinc'] > 0, 1, 0)
    )
    invar["PT_SSTB_income"] = (
        0  # np.where(invar['e26270'] > 0, 1, invar['PT_SSTB_income'])
    )

    # Drop TAXSIM variables not used in Tax-Calculator
    invar.drop(
        columns=[
            "state",
            "mstat",
            "depx",
            # "dep18",
            "transfers",
            "rentpaid",
            "pprofinc",
            "pbusinc",
            "sbusinc",
            "sprofinc",
            "pui",
            "sui",
        ],
        inplace=True,
    )

    return invar


if __name__ == "__main__":
    sys.exit(main())
