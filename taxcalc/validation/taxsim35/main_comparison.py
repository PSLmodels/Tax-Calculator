# DESCRIPTIONS of variable outputs can be found on the TAXSIM-35 website near
# the bottom of the page
# URL: https://users.nber.org/~taxsim/taxsim35/

import sys
import os
import pandas as pd
import numpy as np
import tc_sims

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
# check if directory exists, if not create it
if not os.path.isdir(os.path.join(CUR_PATH, "actual_differences")):
    os.mkdir(os.path.join(CUR_PATH, "actual_differences"))


def main(letter, year):

    test_passed = False  # set boolean to False, change in tests pass
    # (1) generate TAXSIM-35-formatted output using Tax-Calculator tc CLI
    tc_sims.io(letter, year)

    # (2) generate tax differences
    print("Trying to read ", f"{letter}{year}.in.out-taxsim")
    taxsim_df = pd.read_csv(
        f"{letter}{year}.in.out-taxsim",
        # skipinitialspace=True,
        # delim_whitespace=True,
        index_col=False,
    )
    # taxsim_df = taxsim_df.iloc[:, 0:28]
    taxcalc_df = pd.read_csv(
        f"{letter}{year}.in.out-taxcalc",
        # skipinitialspace=True,
        index_col=0,
    )

    taxsim_out_cols_map = {
        "taxsimid": "RECID",
        "year": "FLPDYR",
        "state": "state",
        "fiitax": "iitax",
        "siitax": "statetax",
        "fica": "payrolltax",
        "frate": "mtr_inctax",
        "srate": "mtr_state",
        # "ficar": "mtr_paytax",  # not sure why, but this is always zero from taxsim
        # "tfica": "ptax_oasdi",  # I don't understand how fica and tfica differ in taxsim
        "v10": "c00100",  # federal agi
        "v11": "e02300",  # UI in federal AGI
        "v12": "c02500",  # social security in AGI
        # "v13": "zero_bracket_amount", # zero bracket amount (for itemizers) -- always set to zero in taxcalc output
        "v14": "post_phase_out_pe",  # personal exemptions
        "v15": "phased_out_pe",  # exemption phaseout
        "v16": "c21040",  # deduction phaseout
        "v17": "c04470",  # itemized deductions
        "v18": "c04800",  # federal taxable income
        "v19": "taxbc",  # tax on taxable income (no special cap gains rates)
        "v20": "exemption_surtax",  # exemption surtax  -- always set to zero in taxcalc output
        "v21": "gen_tax_credit",  # general tax credit  -- always set to zero in taxcalc output
        "v22": "non_refundable_child_odep_credit",  # child tax credit (as adjusted)  # Is this right?? Should it be c07220 only?
        "v23": "c11070",  # additional child tax credit (refundable)
        "v24": "c07180",  # child care credit
        "v25": "eitc",  # earned income credit (total federal)
        "v26": "c62100",  # income for amt
        "v27": "amt_liability",  # AMT liability
        "v28": "iitax_before_credits_ex_AMT",  # federal tax before credits
        # "v29": , # FICA -- is this not the same as "fica" above?
        # state calculations all zeros since we don't do state calculations
        # "v30": ,  #state household income
        # "v31": , # state rent expense
        # "v32": , # state AGI
        # "v33": , # state exemption amount
        # "v34": , # state standard deduction
        # "v35": , # state itemized deductions
        # "v36": , # state taxable income
        # "v37": , # state property tax credit
        # "v38": , # state child care tax credit
        # "v39": , # state EIC
        # "v40": , # state total credits
        # "v41": , # state bracket rate
        # "v42": , # earned self-employed income for FICA
        # "v43": , # medicare tax on unearned income
        # "v44": , # medicare tax on earned income
        "v45": "recovery_rebate_credit",  # CARES act Recovery Rebates
        # "v46": ,
        # "v47": ,
    }

    # give tax-calculator variable names to taxsim output variables
    taxsim_df.rename(columns=taxsim_out_cols_map, inplace=True)
    taxsim_df = taxsim_df[list(taxsim_out_cols_map.values())]

    diff_dict = {
        "# of differing records": [],
        "max_diff": [],
        "max_diff_index": [],
        "max_diff_taxsim_val": [],
        "max_diff_taxcalc_val": [],
    }
    diff_df = taxcalc_df - taxsim_df
    input_df = pd.read_csv(
        f"{letter}{year}.in",
        # skipinitialspace=True,
        # delim_whitespace=True,
        index_col=False,
    )
    with pd.ExcelWriter(
        os.path.join(
            CUR_PATH, "actual_differences", f"{letter}{year}differences.xlsx"
        )
    ) as writer:
        # use to_excel function and specify the sheet_name and index
        # to store the dataframe in specified sheet
        taxsim_df.to_excel(writer, sheet_name="taxsim", index=False)
        taxcalc_df.to_excel(writer, sheet_name="taxcalc", index=False)
        diff_df.to_excel(writer, sheet_name="differences", index=False)
        input_df.to_excel(writer, sheet_name="inputs", index=False)

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

        diff_dict["max_diff"].append(
            taxcalc_df.loc[ind, col] - taxsim_df.loc[ind, col]
        )
        if max_val != 0:
            diff_dict["max_diff_index"].append(ind)
            diff_dict["max_diff_taxsim_val"].append(taxsim_df.loc[ind, col])
            diff_dict["max_diff_taxcalc_val"].append(taxcalc_df.loc[ind, col])
        else:
            diff_dict["max_diff_index"].append("no diff")
            diff_dict["max_diff_taxsim_val"].append("no diff")
            diff_dict["max_diff_taxcalc_val"].append("no diff")

    actual_df = pd.DataFrame(diff_dict, index=taxsim_df.columns[3:])
    print(
        f"Difference in dataframes for assumption set {letter} in year {year}"
    )
    print(actual_df)

    # (3) check for difference between LYY.taxdiffs-actual and LYY.taxdiffs-expect
    expected_file_name = os.path.join(
        CUR_PATH, "expected_differences", f"{letter}{year}-taxdiffs-expect.csv"
    )
    if os.path.isfile(expected_file_name):
        expect_df = pd.read_csv(expected_file_name, index_col=0)
        print(actual_df.eq(expect_df))
        test_passed = np.allclose(
            actual_df[["# of differing records", "max_diff"]].values,
            expect_df[["# of differing records", "max_diff"]].values
                      )

        print(
            "Above, True values mean the element is the same between the ACTUAL and EXPECT dataframes. "
            + "(EXPECT files are used for debugging purposes.)"
        )
    else:
        print("This EXPECT file doesn't exist.")

    # (4) Write the created df to *.taxdiffs-actual
    actual_df.to_csv(
        os.path.join(
            CUR_PATH,
            "actual_differences",
            f"{letter}{year}-taxdiffs-actual.csv",
        )
    )

    return test_passed


if __name__ == "__main__":
    sys.exit(main())
