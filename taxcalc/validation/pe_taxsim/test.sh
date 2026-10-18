#!/bin/zsh
# Validation test against PolicyEngine-US using PolicyEngine-TAXSIM tool.
# See Makefile target valtest for usage.

SECONDS=0

python validate.py > test_results.actual
diff -q test_results.actual test_results.expect
PASS=$?
if [ $PASS -eq 0 ]; then
    rm test_results.actual
fi

echo "Runtime: $SECONDS seconds" >&2
exit $PASS
