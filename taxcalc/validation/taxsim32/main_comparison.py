# DESCRIPTIONS of variable outputs can be found on the TAXSIM-32 website near
# the bottom of the page
# URL: https://users.nber.org/~taxsim/taxsim32/

import sys
import os
import pandas as pd


def main(assump_set, year):

    # (1) generate TAXSIM-32-formatted output using Tax-Calculator tc CLI
    os.system(f"python taxcalc.py {assump_set}{year}.in")

    # (2) generate tax differences
    taxsim_df = pd.read_csv(
        f"{assump_set}{year}.in.out-taxsim",
        sep=" ",
        skipinitialspace=True,
        index_col=False,
    )
    taxsim_df = taxsim_df.iloc[:, 0:28]
    taxcalc_df = pd.read_csv(
        f"{assump_set}{year}.in.out-taxcalc",
        sep=" ",
        skipinitialspace=True,
        index_col=False,
        header=None,
    )

    taxcalc_df.columns = taxsim_df.columns  # rename taxcalc output columns

    diff_dict = {
        "# of differing records": [],
        "max_diff": [],
        "max_diff_index": [],
        "max_diff_taxsim_val": [],
        "max_diff_taxcalc_val": [],
    }

    for col in taxsim_df.columns[3:]:

        df_diff = pd.DataFrame({"a": taxsim_df[col], "b": taxcalc_df[col]})
        df_diff_recs = df_diff[df_diff["a"] != df_diff["b"]]
        diff_dict["# of differing records"].append(df_diff_recs.shape[0])

        ind, max_val = max(
            enumerate(
                abs(x - y)
                for x, y in zip(taxcalc_df.loc[:, col], taxsim_df.loc[:, col])
            ),
            key=lambda x: x[1],
        )

        diff_dict["max_diff"].append(taxcalc_df.loc[ind, col] - taxsim_df.loc[ind, col])
        if max_val != 0:
            diff_dict["max_diff_index"].append(ind)
            diff_dict["max_diff_taxsim_val"].append(taxsim_df.loc[ind, col])
            diff_dict["max_diff_taxcalc_val"].append(taxcalc_df.loc[ind, col])
        else:
            diff_dict["max_diff_index"].append("no diff")
            diff_dict["max_diff_taxsim_val"].append("no diff")
            diff_dict["max_diff_taxcalc_val"].append("no diff")

    actual_df = pd.DataFrame(diff_dict, index=taxsim_df.columns[3:])
    print(f"Difference in dataframes for assumption set {assump_set} in year {year}")
    print(actual_df)

    # (3) check for difference between LYY.taxdiffs-actual and LYY.taxdiffs-expect
    if os.path.isfile(f"{assump_set}{year}-taxdiffs-expect.csv"):
        expect_df = pd.read_csv(f"{assump_set}{year}-taxdiffs-expect.csv", index_col=0)

        print(actual_df.eq(expect_df))

        print(
            "Above, True values mean the element is the same between the ACTUAL and EXPECT dataframes. "
            + "(EXPECT files are used for debugging purposes.)"
        )
    else:
        print("This EXPECT file doesn't exist.")

    # (4) Write the created df to *.taxdiffs-actual
    actual_df.to_csv(f"{assump_set}{year}-taxdiffs-actual.csv")


if __name__ == "__main__":
    sys.exit(main())
