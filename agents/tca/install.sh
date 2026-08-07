#!/bin/zsh
# Install Tax-Calculator Assistant in specified empty FOLDER
USAGE="./install.sh FOLDER"

# check existence of FOLDER argument
if [[ $# -ne 1 ]]; then
    echo "ERROR: install.sh does not have exactly one argument" >&2
    echo "USAGE: $USAGE" >&2
    exit 1
fi
FOLDER=$1

# check non-existence of FOLDER directory
if [[ -d $FOLDER ]]; then
    echo "ERROR: cannot install in an existing FOLDER" >&2
    exit 1
fi

# create new FOLDER
mkdir $FOLDER

# optionally copy TMD input data files to new FOLDER
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

# copy tca.zip to new FOLDER
cp tca.zip $FOLDER

# install TCA in new FOLDER
cd $FOLDER
unzip -oq tca.zip
rm tca.zip
./add_mcp_tca.sh > /dev/null

# execute installation verification test in the new FOLDER
echo "Installation verification test takes about half a minute to execute"
./tca-test
echo "Move into the new FOLDER using the 'cd $FOLDER' command, then"
echo "start using TCA interactively using the './tca-exec' command"
exit 0
