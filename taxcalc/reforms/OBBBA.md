OBBBA REFORM
============

The One Big Beautiful Bill Act (OBBBA) became law on July 4, 2025.

During July-August of 2025, Tax-Calculator was revised so that OBBBA
represents current-law policy.  The changes required to do this were
made in a sequence of pull requests described in [issue
2926](https://github.com/PSLmodels/Tax-Calculator/issues/2926).

The final `taxcalc/policy_current_law.json` was not created by hand,
but rather was generated using an `OBBBA/implement.py` script.  In that
script, OBBBA reform provisions were specified in the [`OBBBA_PARAMS`
dictionary](https://github.com/PSLmodels/Tax-Calculator/blob/4944d2e0da5c2ae525e691f5f15c47b831c4d322/OBBBA/implement.py#L22-L545)
and the logic of using the information in that dictionary was in [this
function](https://github.com/PSLmodels/Tax-Calculator/blob/4944d2e0da5c2ae525e691f5f15c47b831c4d322/OBBBA/implement.py#L548-L565),
which was called for each policy parameter in the dictionary from the
[main
function](https://github.com/PSLmodels/Tax-Calculator/blob/4944d2e0da5c2ae525e691f5f15c47b831c4d322/OBBBA/implement.py#L591-L655).
