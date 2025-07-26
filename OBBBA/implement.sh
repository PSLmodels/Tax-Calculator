#!/bin/zsh
#
# Execute "python implment.py --group $1
# then generate actual diffs and compare with expected diffs

python implement.py --group $1
diff pcl.json pcl-510.json > $1-diffs.act
diff -q $1-diffs.act $1-diffs.exp
if [[ $? -ne 0 ]]; then
    echo "SOME DIFFERENCES between $1-diffs.act $1-diffs.exp"
else
    echo "NO DIFFERENCES between $1-diffs.act $1-diffs.exp"
    rm -f $1-diffs.act
fi
exit 0
