#!/bin/zsh
# Install Tax-Calculator Assistant in specified FOLDER
USAGE="./install.sh FOLDER"

# check existence of FOLDER argument
if [[ $# -ne 1 ]]; then
    echo "ERROR: install.sh does not have exactly one argument" >&2
    echo "USAGE: $USAGE" >&2
    exit 1
fi
FOLDER=$1

# create new FOLDER if it does not exist
if ! [[ -d $FOLDER ]]; then
    ERRMSG=$({ mkdir $FOLDER } 2>&1)
    if [[ -n $ERRMSG ]]; then
        echo "The mkdir command failed with error: $ERRMSG"
        exit 1
    fi
fi

# optionally copy TMD input data files to FOLDER
TMDV=../../tmd.csv
TMDW=../../tmd_weights.csv.gz
TMDF=../../tmd_growfactors.csv
if [[ -f $TMDV && -f $TMDW && -f $TMDF ]]; then
    cp $TMDV $FOLDER
    cp $TMDW $FOLDER
    cp $TMDF $FOLDER
else
    echo "TMD input files not found"
fi

# copy tca.zip to FOLDER
cp tca.zip $FOLDER

# install TCA in FOLDER removing any existing runs.db or run*-??.* files
cd $FOLDER
if [[ -f runs.db ]]; then
    cp runs.db runs.db-old
    rm -f runs.db
fi
find . -regex "\./run[0-9]+-[0-9]+.*" -exec rm -f {} \;
unzip -oq tca.zip
rm tca.zip
./add_mcp_tca.sh > /dev/null

# install TCA dependencies
pip install "mcp[cli]>=2.0.0" > pip_install.results
pip install "psutil>=7.2.0" >> pip_install.results

# execute installation verification test in the FOLDER
echo "-- Installation verification test takes about half a minute to execute"
./tca-test
echo "-- Move into the new FOLDER using the 'cd $FOLDER' command, then"
echo "   start using TCA interactively by executing the './tca-exec' command"
exit 0
