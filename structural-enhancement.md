# Structural Enhancement Workflow for Tax-Calculator

This workflow outlines the steps involved in preparing a local git
branch that contains Tax-Calculator changes that enable the model to
simulate a specified policy reform that cannot be simulated by the
current version of Tax-Calculator.  This workflow is intended to be
used by a Tax-Calculator developer, who has a forked Tax-Calculator
repository on this computer.

STEP 1: GATHER INFORMATION
- Determine Repository Folder
  * Purpose: Locate the top-level folder of the local repository.
  * Question: What folder contains the local Tax-Calculator repository?
- Determine Specified Reform
  * Purpose: Specify policy reform that cannot be simulated with current
             version of Tax-Calculator.
  * Question: What is the specified reform?
- Determine Branch Name
  * Purpose: Specify new git branch name.
  * Question: What is the name of the new git branch?
  
STEP 2: CREATE GIT BRANCH
- Action: create git branch off master branch with specified name

STEP 3: PLAN BRANCH CHANGES
- Identify any new parameters for `policy_current_law.json`
  * avoid creating new section1 and section2 values
- Identify any new variables for `records_variables.json`
  * place new variables in either the read or calc sections, as appropriate
- Develop changes in `calcfunctions.py` that use new parameters and variables
  * use current `calcfunctions.py` function arguments ordering scheme
- Add unit tests for new parameters, variables, and code, to maintain coverage
  * put new unit tests in `test_calcfunctions.py` module
  * ask user for guidance on nature of the unit tests (possibly an example)
  * always calculate expected unit test results WITHOUT referring to the new
    code in the `calcfunctions.py` module

STEP 4: TEST BRANCH CHANGES
Execute the following test commands until all four pass.  If a test
command fails, return to step 3 revising changes until all tests pass.
Execute the test commands in the top-level Tax-Calculator repo folder.
- Execute the "make cstest > rescs" command
  * Test fails if the rescs file is not empty
- Execute the "make pytest-all > respy" command
  * Test fails if the last line in the respy file contains the word failed
- Execute the "make brtest > resbr" command
  * Test fails if any line in the resbr file contains the word differ
- Execute the "make idtest > resid" command
  * Test fails if any line in the resid file contains the word differ

STEP 5: ASK IF SHOULD COMMIT CHANGES
- Action: ask if any additional changes are needed; if not, commit changes.
