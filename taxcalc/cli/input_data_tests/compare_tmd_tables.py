"""
Compare tmd-35-#-#-#-#.tables total statistics with those from tmd-35.tables.
"""
import sys
from pathlib import Path
import numpy as np

TEST_FOLDER = Path(__file__).resolve().parent
ACTUAL_PATH = TEST_FOLDER / "tmd-35-#-#-#-#.tables"
EXPECT_PATH = TEST_FOLDER / "tmd-35.tables"
REL_TOLERANCE = {
    "rtn": 0.0002,
    "inc": 0.0002,
    "itx": 0.0002,
    "ptx": 0.0002,
}


def main():
    """
    Compare total statistics from the ACTUAL_PATH and EXPECT_PATH.
    """
    def total_stat_dict(tpath):
        """
        Returns total statistics dictionary for specified table path.
        """
        stat = {}
        with open(tpath, "r", encoding="utf-8") as tfile:
            lines = tfile.readlines()
        for line in lines:
            token = line.split()
            if token[0] == "A":
                stat["rtn"] = float(token[1])
                stat["inc"] = float(token[2])
                stat["itx"] = float(token[3])
                stat["ptx"] = float(token[4])
                break  # out of for loop
        return stat

    # begin high-level function logic
    act = total_stat_dict(ACTUAL_PATH)
    exp = total_stat_dict(EXPECT_PATH)
    if act.keys() != exp.keys():
        print("ERROR: act and exp dictionary keys differ")
        return 1
    rcode = 0
    for stat, actual in act.items():
        expect = exp[stat]
        r_tol = REL_TOLERANCE[stat]
        if not np.allclose([actual], [expect], atol=0.0, rtol=r_tol):
            print(
                "TMD_STAT_DIFF:stat,act,exp,atol,rtol= "
                f"{stat} {actual} {expect} 0.0 {r_tol}"
            )
            rcode = 1
    return rcode


if __name__ == "__main__":
    sys.exit(main())
