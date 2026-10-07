"""
Generates random sample of tax filing units with attributes such that
generated file can be directly uploaded to Internet TAXSIM version 35.
"""

# CODING-STYLE CHECKS:
# pycodestyle taxsim_input.py
# pylint --disable=locally-disabled taxsim_input.py

import argparse
import sys
import numpy as np
import pandas as pd


VALID_LETTERS = ["a", "b", "c"]


def generate_datasets(letter, year, offset=0):
    """
    Generates random sample of tax filing units with attributes and
    format such that the file can be directly uploaded to Internet
    TAXSIM version 35. For details on Internet TAXSIM version 35 INPUT
    format, go to https://users.nber.org/~taxsim/taxsim35/

    Args:
        letter (character): letter denoting assumption set to generate data
        year (int): year data will represent
        offset (int): offset to alter the random number seed

    Returns:
        None
    """
    # check year value
    year += 2000
    if year < 2013 or year > 2023:
        sys.stderr.write("ERROR: YEAR not in [2013,2023] range\n")
        assert False
    # check LETTER value
    if letter == "":
        sys.stderr.write("ERROR: must specify LETTER\n")
        assert False
    if letter not in VALID_LETTERS:
        sys.stderr.write("ERROR: LETTER not in VALID_LETTERS, where\n")
        sys.stderr.write("       VALID_LETTERS={}\n".format(VALID_LETTERS))
        assert False
    # check OFFSET value
    if offset < 0 or offset > 999:
        sys.stderr.write("ERROR: OFFSET not in [0,999] range\n")
        assert False
    # get dictionary containing assumption set
    assump = assumption_set(letter, year)
    # generate sample as pandas DataFrame
    sample = sample_dataframe(assump, year, offset)
    # write sample to input file
    header_col = [
        "taxsimid",
        "year",
        "state",
        "mstat",
        "page",
        "sage",
        "depx",
        "dep13",
        "dep17",
        "dep18",
        "pwages",
        "swages",
        "psemp",
        "ssemp",
        "dividends",
        "intrec",
        "stcg",
        "ltcg",
        "otherprop",
        "nonprop",
        "pensions",
        "gssi",
        "pui",
        "sui",
        "transfers",
        "rentpaid",
        "proptax",
        "otheritem",
        "childcare",
        "mortgage",
        "scorp",
        "pbusinc",
        "pprofinc",
        "sbusinc",
        "sprofinc",
        "idtl",
    ]
    filename = "{}{}.in".format(letter, year % 100)
    sample.to_csv(filename, sep=",", header=header_col, index=False)


def assumption_set(letter, year):
    """
    Return dictionary containing assumption parameters.

    Args:
        letter (character): letter denoting assumption set to generate data
        year (int): year data will represent

    Returns:
        adict (dict): assumption set dictionary (defines sampling for
            variables)
    """
    adict = dict()
    if letter in VALID_LETTERS:  # <===========================================
        # basic assumption parameters for all ?YY.in samples:
        adict["sample_size"] = 1000  # 100000
        adict["year"] = year  # TAXSIM ivar 2
        # demographic attributes:
        adict["joint_frac"] = 0.60  # fraction of sample with joint MARS
        adict["min_age"] = 17  # TAXSIM ivar 5 (primary taxpayer age)
        adict["max_age"] = 77  # TAXSIM ivar 5 (primary taxpayer age)
        adict["min_age_diff"] = -10  # min spouse age difference
        adict["max_age_diff"] = 10  # max spouse age difference
        adict["max_depx"] = 5  # TAXSIM ivar 7 (total number of dependents)
        adict["max_dep13"] = 4  # TAXSIM ivar 8
        adict["max_dep17"] = 4  # TAXSIM ivar 9
        adict["max_dep18"] = 4  # TAXSIM ivar 10
        # labor income:
        adict["max_pwages_yng"] = 500  # TAXSIM ivar 11
        adict["max_pwages_old"] = 30  # TAXSIM ivar 11 (65+ ==> old)
        adict["max_swages_yng"] = 500  # TAXSIM ivar 12
        adict["max_swages_old"] = 30  # TAXSIM ivar 12 (65+ ==> old)
        # non-labor income (all zeros):
        adict["max_psemp"] = 0  # TAXSIM ivar 13
        adict["max_ssemp"] = 0  # TAXSIM ivar 14
        adict["max_divinc"] = 0  # TAXSIM ivar 15
        adict["max_intinc"] = 0  # TAXSIM ivar 16
        adict["min_stcg"] = 0  # TAXSIM ivar 17
        adict["max_stcg"] = 0  # TAXSIM ivar 17
        adict["min_ltcg"] = 0  # TAXSIM ivar 18
        adict["max_ltcg"] = 0  # TAXSIM ivar 18
        adict["max_other_prop_inc"] = 0  # TAXSIM ivar 19
        adict["max_other_nonprop_inc"] = 0  # TAXSIM ivar 20
        adict["max_pnben"] = 0  # TAXSIM ivar 21
        adict["max_ssben"] = 0  # TAXSIM ivar 22
        adict["max_puiben"] = 0  # TAXSIM ivar 23
        adict["max_suiben"] = 0  # TAXSIM ivar 24
        # childcare expense amount (all zero):
        adict["max_ccexp"] = 0  # TAXSIM ivar 29
        # itemized expense amounts (all zero):
        adict["max_ided_proptax"] = 0  # TAXSIM ivar 27
        adict["max_ided_nopref"] = 0  # TAXSIM ivar 28
        adict["max_ided_mortgage"] = 0  # TAXSIM ivar 30
        adict["max_scorp_inc"] = 0  # TAXSIM ivar 31
        adict["max_pbus_inc"] = 0  # TAXSIM ivar 32
        adict["max_pprof_inc"] = 0  # TAXSIM ivar 33
        adict["max_sbus_inc"] = 0  # TAXSIM ivar 34
        adict["max_sprof_inc"] = 0  # TAXSIM ivar 35
        # end if letter in VALID_LETTERS
    if letter in ["b", "c"]:  # <==============================================
        # non-labor income:
        adict["max_psemp"] = 350  # TAXSIM ivar 13
        adict["max_ssemp"] = 350  # TAXSIM ivar 14
        adict["max_divinc"] = 20  # TAXSIM ivar 15
        adict["max_intinc"] = 20  # TAXSIM ivar 16
        adict["min_stcg"] = -10  # TAXSIM ivar 17
        adict["max_stcg"] = 10  # TAXSIM ivar 17
        adict["min_ltcg"] = -10  # TAXSIM ivar 18
        adict["max_ltcg"] = 10  # TAXSIM ivar 18
        adict["max_other_prop_inc"] = 30  # TAXSIM ivar 19
        adict["max_other_nonprop_inc"] = 30  # TAXSIM ivar 20
        adict["max_pnben"] = 60  # TAXSIM ivar 21
        adict["max_ssben"] = 60  # TAXSIM ivar 22
        adict["max_puiben"] = 10  # TAXSIM ivar 23
        adict["max_suiben"] = 10  # TAXSIM ivar 24
        adict["max_scorp_inc"] = 350  # TAXSIM ivar 31
        adict["max_pbus_inc"] = 350  # TAXSIM ivar 32
        adict["max_pprof_inc"] = 0  # 1  # TAXSIM ivar 33
        adict["max_sbus_inc"] = 350  # TAXSIM ivar 34
        adict["max_sprof_inc"] = 0  # 1  # TAXSIM ivar 35
    if letter == "c":  # <=====================================================
        # childcare expense amount:
        adict["max_ccexp"] = 10  # TAXSIM ivar 29
        # itemized expense amounts:
        adict["max_ided_proptax"] = 30  # TAXSIM ivar 27
        adict["max_ided_nopref"] = 10  # TAXSIM ivar 28
        adict["max_ided_mortgage"] = 40  # TAXSIM ivar 30
    return adict


def sample_dataframe(assump, year, offset):
    """
    Construct DataFrame containing sample specified by assump and year+offset.

    Args:
        assump (dict): assumption set dictionary (defined sampling for variables)
        year (int): year data will represent
        offset (int): offset to alter the random number seed

    Returns:
        smpl (Pandas DataFrame): Random data in TAXSIM format
    """
    # pylint: disable=too-many-locals
    np.random.seed(123456789 + year + offset)
    size = assump["sample_size"]
    zero = np.zeros(size, dtype=np.int64)
    sdict = dict()
    # (01) RECID
    sdict[1] = range(1, size + 1)
    # (02) YEAR
    sdict[2] = np.full_like(zero, assump["year"], dtype=np.int64)
    # (03) STATE
    sdict[3] = zero
    # (04) MSTAT
    urn = np.random.random(size)
    mstat = np.where(urn < assump["joint_frac"], 2, 1)
    sdict[4] = mstat
    # (05) PAGE
    sdict[5] = np.random.randint(
        assump["min_age"], assump["max_age"] + 1, size
    )
    # (06) SAGE
    age_diff = np.random.randint(
        assump["min_age_diff"], assump["max_age_diff"] + 1, size
    )
    sage = sdict[5] + age_diff
    sdict[6] = np.where(mstat == 2, np.maximum(sage, assump["min_age"]), zero)
    # (07-10) DEPX, DEP13, DEP17, DEP18
    depx = np.random.randint(0, assump["max_depx"] + 1, size)
    d18 = np.random.randint(0, assump["max_dep18"] + 1, size)
    dep18 = np.where(d18 <= depx, d18, depx)
    d17 = np.random.randint(0, assump["max_dep17"] + 1, size)
    dep17 = np.where(d17 <= dep18, d17, dep18)
    d13 = np.random.randint(0, assump["max_dep13"] + 1, size)
    dep13 = np.where(d13 <= dep17, d13, dep17)
    sdict[7] = depx
    # (8)-(10) are ages of 3 youngest dependents
    # If these are zero, then use depx for number of EIC children
    # but TAXIM-35 also accepts dep13-dep18 here to be backward compatible
    # we use that since closer to what's in tax-calculator
    sdict[8] = dep13
    sdict[9] = dep17
    sdict[10] = dep18
    # (11) PWAGES
    pwages_yng = np.random.randint(0, assump["max_pwages_yng"] + 1, size)
    pwages_old = np.random.randint(0, assump["max_pwages_old"] + 1, size)
    sdict[11] = np.where(sdict[5] >= 65, pwages_old, pwages_yng) * 1000
    # (12) SWAGES
    swages_yng = np.random.randint(0, assump["max_swages_yng"] + 1, size)
    swages_old = np.random.randint(0, assump["max_swages_old"] + 1, size)
    swages = np.where(sdict[6] >= 65, swages_old, swages_yng) * 1000
    sdict[12] = np.where(mstat == 2, swages, zero)
    # (13) Primary Filer Self-Employment Income
    sdict[13] = np.random.randint(0, assump["max_psemp"] + 1, size)
    # (14) Secondary Filer Self-Employment Income
    ssemp = np.random.randint(0, assump["max_psemp"] + 1, size)
    sdict[14] = np.where(mstat == 2, ssemp, zero)
    # (15) DIVIDENDS
    sdict[15] = np.random.randint(0, assump["max_divinc"] + 1, size) * 1000
    # (16) INTREC
    sdict[16] = np.random.randint(0, assump["max_intinc"] + 1, size) * 1000
    # (17) STCG
    sdict[17] = (
        np.random.randint(assump["min_stcg"], assump["max_stcg"] + 1, size)
        * 1000
    )
    # (18) LTCG
    sdict[18] = (
        np.random.randint(assump["min_ltcg"], assump["max_ltcg"] + 1, size)
        * 1000
    )
    # (19) OTHERPROP
    sdict[19] = (
        np.random.randint(0, assump["max_other_prop_inc"] + 1, size) * 1000
    )
    # (20) NONPROP
    sdict[20] = (
        np.random.randint(0, assump["max_other_nonprop_inc"] + 1, size) * 1000
    )
    # (21) PENSIONS
    sdict[21] = np.random.randint(0, assump["max_pnben"] + 1, size) * 1000
    # (22) GSSI
    sdict[22] = np.random.randint(0, assump["max_ssben"] + 1, size) * 1000
    # (23) Primary Filer UI (note splitting UI between primary and
    # secondary only matters for 2020 and 2021)
    sdict[23] = np.random.randint(0, assump["max_puiben"] + 1, size) * 1000
    # (24) Secondary Filer UI
    sdict[24] = np.random.randint(0, assump["max_suiben"] + 1, size) * 1000
    # (25) TRANSFERS (non-taxable in federal income tax)
    sdict[25] = zero
    # (26) RENTPAID (used only in some state income tax laws)
    sdict[26] = zero
    # (27) PROPTAX
    sdict[27] = (
        np.random.randint(0, assump["max_ided_proptax"] + 1, size) * 1000
    )
    # (28) OTHERITEM
    sdict[28] = (
        np.random.randint(0, assump["max_ided_nopref"] + 1, size) * 1000
    )
    # (29) CHILDCARE (TAXSIM-35 EXPECTS ZERO IF NO QUALIFYING CHILDRED)
    ccexp = np.random.randint(0, assump["max_ccexp"] + 1, size) * 1000
    sdict[29] = np.where(dep13 > 0, ccexp, zero)
    # (30) MORTGAGE
    sdict[30] = (
        np.random.randint(0, assump["max_ided_mortgage"] + 1, size) * 1000
    )
    # (31) S-Corp income, QBI
    sdict[31] = np.random.randint(0, assump["max_scorp_inc"] + 1, size) * 1000
    # (32) Primary Taxpayer's QBI
    sdict[32] = np.random.randint(0, assump["max_pbus_inc"] + 1, size) * 1000
    # (33) Primary Taxpayer's SSTB
    sdict[33] = np.random.randint(0, assump["max_pprof_inc"] + 1, size)
    # (34) Spouse's QBI
    sqbi = np.random.randint(0, assump["max_sbus_inc"] + 1, size) * 1000
    sdict[34] = np.where(mstat == 2, sqbi, zero)
    # (35) Spouse's SSTB
    spouse_sstb = np.random.randint(0, assump["max_sprof_inc"] + 1, size)
    sdict[35] = np.where(mstat == 2, spouse_sstb, zero)
    # (36) IDTL: variable to request intermediate calculations
    sdict[36] = 2

    smpl = pd.DataFrame(sdict)
    return smpl
