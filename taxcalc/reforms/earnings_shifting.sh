#!/bin/bash
# earnings_shifting.sh calls earnings_shifting.py and earnings_shifting.awk
# USAGE: ./earnings_shifting.sh

function es_run {
    python earnings_shifting.py $1 $2 $3 $4 | awk -f earnings_shifting.awk
}

echo "STARTING : `date`"

HEADER="YEAR   MIN_EARN  MIN_SAVE  SPROB :  NS(#m)    ES(\$b)  TAXDIFF(\$b)"
echo "${HEADER}"

# baseline results with no-earnings-shifting
es_run 2017 0.0 0.0 0.0

# results for some earnings-shifting
es_run 2017 2e5 1e4 1.0
es_run 2017 3e5 1e4 1.0
es_run 2017 4e5 1e4 1.0
es_run 2017 2e5 2e4 1.0
es_run 2017 3e5 2e4 1.0
es_run 2017 4e5 2e4 1.0
es_run 2017 2e5 3e4 1.0
es_run 2017 3e5 3e4 1.0
es_run 2017 4e5 3e4 1.0
es_run 2017 5e5 3e4 1.0
es_run 2017 5e5 4e4 1.0
es_run 2017 5e5 5e4 1.0

echo "FINISHED : `date`"
exit 0
