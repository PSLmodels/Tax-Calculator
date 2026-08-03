# Structural-Enhancement Workflow for Tax-Calculator

This workflow outlines the steps involved in preparing a local git
branch that contains Tax-Calculator changes that enable the model to
simulate a specified policy reform that cannot be simulated by the
current version of Tax-Calculator.  This workflow is intended to be
used by a Tax-Calculator user, who has a forked Tax-Calculator
repository on this computer.

STEP 1: GATHER INFORMATION
- Determine Repository Folder
  * Purpose: Locate the top-level folder of the local repository
  * Question: What folder contains the local Tax-Calculator repository?
- Determine Specified Reform
  * Purpose: Specify policy reform that cannot be simulated with current
             version of Tax-Calculator
  * Question: What is the specified reform?
- Determine Reform Details
  * Purpose: Specify information needed to write parameter metadata
  * Question: What is the first tax year in which the reform applies?
  * Question: Are the new parameters inflation-indexed (and if so, wage
              indexed or price indexed)?
- Determine Branch Name
  * Purpose: Specify new git branch name only if on master branch
  * Question: What is the name of the new git branch?

STEP 2: CREATE GIT BRANCH
- Action: confirm the working tree is clean; if it is not, ask the user
          how to proceed before making any changes
- Action: if currently on master branch, synchronize master with the
          central GitHub repository using the "make git-sync" command
- Action: create git branch off master branch if currently on master branch

STEP 3: MAKE BRANCH CHANGES
- Identify any new parameters for `policy_current_law.json`
  * avoid creating new section1 and section2 values
  * set current-law parameter values so that they leave results generated
    by the current version of Tax-Calculator unchanged
- Identify any new variables for `records_variables.json`
  * place new variables in the calc section of `records_variables.json`
- Develop changes in `calcfunctions.py` that use new parameters and variables
  * use current `calcfunctions.py` function arguments ordering scheme
- Make the corresponding changes in `calculator.py`
  * add new functions to the import list at the top of the module
  * add or revise the function calls in the `_calc_one_year` function
- Add unit tests for new parameters, variables, and code, to maintain coverage
  * put new unit tests at the bottom of the `test_calcfunctions.py` module
  * ask user for guidance on nature of the unit tests (possibly an example)
  * always calculate expected unit test results WITHOUT referring to the new
    code in the `calcfunctions.py` module
- Do not hand-edit the generated documentation files in the `docs/guide`
  folder (`policy_params.md`, `input_vars.md`, `output_vars.md`,
  `assumption_params.md`); they are generated from the JSON files by the
  scripts in the `docs/guide/make` folder

STEP 4: TEST BRANCH CHANGES

Before executing the test commands below, execute the fast
"cd taxcalc ; pytest tests/test_calcfunctions.py" command, which catches
inconsistencies among `calcfunctions.py`, `calculator.py`,
`policy_current_law.json`, and `records_variables.json` without
incurring the cost of the slower test commands

Then execute the following test commands until all four pass.  If a
test command fails, return to step 3 revising changes until all tests
pass.  Execute the test commands in the top-level Tax-Calculator repo
folder.  Note that the brtest and idtest commands build and install
the taxcalc package, and therefore take considerably longer than the
other commands.

- Execute the "make cstest > rescs 2>&1" command
  * Test fails if the rescs file is not empty
- Execute the "make pytest-all > respy 2>&1 ; echo EXIT=$?" command
  * Test fails if the EXIT value is not zero (consult the respy file to
    diagnose the failure; do not rely on the last line of respy alone,
    because collection errors and crashes are reported differently from
    test failures)
- Execute the "make brtest > resbr 2>&1" command
  * Test fails if any line in the resbr file contains the word differ
- Execute the "make idtest > resid 2>&1" command
  * Test fails if any line in the resid file contains the word differ

The brtest and idtest commands, and some of the pytest-all tests,
compare results against stored expected results.  When such a
comparison fails, distinguish between these two cases:
- The enhancement is supposed to leave current-law results unchanged, in
  which case a difference indicates a bug in the branch changes that must
  be fixed in step 3.
- The enhancement is expected to change results, in which case the stored
  expected results need to be updated.
NEVER revise a test, or a file containing expected test results, in order
to make a failing test pass without first asking the user for approval.

STEP 5: ASK IF SHOULD COMMIT CHANGES
- Action: remove the rescs, respy, resbr, and resid files generated in
          step 4, because they are not ignored by git and must not be
          committed
- Action: ask if should commit changes or leave that up to the user.
- Action: do not push the branch to GitHub and do not open a pull request;
          those actions are outside the scope of this workflow.
