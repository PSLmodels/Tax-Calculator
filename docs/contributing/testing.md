Testing
=======

This description of Tax-Calculator testing procedures is written for a
person who wants to contribute changes to Tax-Calculator source code.

It assumes that you have read {doc}`contributor_guide` and
{doc}`param_naming`, have forked the [central GitHub Tax-Calculator
repository](https://github.com/PSLmodels/Tax-Calculator) to your
GitHub account, and have cloned that forked copy to your local
computer.

This document also assumes that you have read {doc}`pr_workflow`
so that you understand where the testing procedures fit into
the broader workflow of preparing a pull request that changes
Tax-Calculator source code.

There are two phases of testing: testing that the source code
complies with the Tax-Calculator coding style and testing that
the source code does not contain bugs.

You can execute both phases of testing with a single command:
```
make tests
```

No messages indicate the tests pass.

## Interpreting test results

If you are adding an enhancement that expands the capabilities of the
Tax-Calculator, then all the tests you can run should pass before you
submit a pull request containing the enhancement.  In addition, it
essential to add a test to the pytest suite, which is located in the
`taxcalc/tests` directory, that somehow checks that your enhancement
is working as you expect it to work.

On the other hand, if you think you have found a bug in the existing
Tax-Calculator source code, the first thing to do is add a test to the
pytest suite that demonstrates how the source code produces an
incorrect result (that is, the test fails because the result is
incorrect).  Then change the source code to fix the bug and
demonstrate that the newly-added test, which used to fail, now passes.

## Updating test results

After an enhancement or bug fix, you may be convinced that the new and
different second-phase test results are, in fact, correct.  How do you
eliminate the test failures?  Simply edit the appropriate
`taxcalc/tests/test_*.py` file so that the test passes when you rerun
pytest.  If there are failures for the tests that write results files,
read the test error message for instructions about how to update the
test results.
