# Structural-Enhancement Workflow for Tax-Calculator

This workflow outlines the steps involved in preparing a local git
branch that contains Tax-Calculator changes that enable the model to
simulate a specified policy reform that cannot be simulated by the
current version of Tax-Calculator.  This workflow is intended to be
used by a Tax-Calculator user, who has forked the Tax-Calculator
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
          and then create the new branch off the master branch
- Action: if currently on a branch other than master, ask the user
          whether to continue working on that branch or to switch to
          master and create the new branch there

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

Execute every command in this step in the top-level Tax-Calculator
repo folder.

Before executing the test commands below, execute the fast
"pytest taxcalc/tests/test_calcfunctions.py" command, which catches
inconsistencies among `calcfunctions.py`, `calculator.py`,
`policy_current_law.json`, and `records_variables.json` without
incurring the cost of the slower test commands

Also, confirm that the three national TMD files (`tmd.csv`,
`tmd_weights.csv.gz`, and `tmd_growfactors.csv`) are in the top-level
repo folder, where they are ignored by git version control.  The idtest
command cannot run without them.

Then execute the following test commands, in the order listed, until
they all pass.  If a test command fails, return to step 3 revising
changes until all tests pass.  These tests should all pass because a
structural enhancment **adds** capabilities; it does not change how
taxes are calculated under current-law policy or under the reforms that
are already parameterized.  The order matters: the pytest-all command
uninstalls the local taxcalc package that the brtest and idtest
commands build and install.  Because they build and install the
package, the brtest and idtest commands take considerably longer than
the other commands.

- Execute the "make cstest > rescs 2>&1" command
  * Test fails if the rescs file is not empty
- Execute the "make pytest-all > respy 2>&1 ; echo EXIT=$?" command
  * Test fails if the EXIT value is not zero (consult the respy file to
    diagnose the failure; do not rely on the last line of respy alone,
    because collection errors and crashes are reported differently from
    test failures)
- Execute the "make brtest > resbr 2>&1" command and then, if the three
  TMD files are available, the "make idtest > resid 2>&1" command
  * Both these commands execute shell scripts that report mismatches but
    always exit with a zero status, so check their output by executing
    the "grep -Ei 'differ|error|traceback' resbr resid" command
  * Test fails if that grep command generates any output; matching the
    error and traceback patterns, as well as the differ pattern, guards
    against a test that appears to pass only because it never ran

The brtest and idtest commands, and some of the pytest-all tests,
compare results against stored expected results.  When such a
comparison fails, the difference indicates a bug in the branch changes
that must be fixed in step 3.  Never revise a test, or a file
containing expected test results, in order to make a failing test pass
without first asking the user for approval.

STEP 5: ASK IF SHOULD COMMIT CHANGES
- Action: remove the rescs, respy, resbr, and resid files generated in
          step 4, because they are not ignored by git and must not be
          committed
- Action: check "git status" for stray test output files, such as
          df-??-#-* files, which are left behind when a failing
          pytest-all command aborts before the Makefile pytest-cleanup
          step runs
- Action: ask if should commit changes or leave that up to the user.
- Action: do not push the branch to GitHub and do not open a pull request;
          those actions are outside the scope of this workflow.
