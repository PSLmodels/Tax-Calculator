#!/bin/bash
# USAGE: ./install_local_taxcalc_package.sh
# ACTION: (1) uninstalls any installed taxcalc package (conda uninstall)
#         (2) executes "conda install conda-build" (if necessary)
#         (3) builds local taxcalc=0.0.0 package (conda build)
#         (4) installs local taxcalc=0.0.0 package (conda install)
# NOTE: for those with experience working with compiled languages,
#       building a local conda package is analogous to compiling an executable

echo "STARTING : `date`"

# uninstall any existing taxcalc conda package
conda list taxcalc | awk '$1~/taxcalc/{rc=1}END{exit(rc)}'
if [ $? -eq 1 ]; then
    ./uninstall_taxcalc_package.sh
fi

# install conda-build package if not present
conda list build | awk '$1~/conda-build/{rc=1}END{exit(rc)}'
if [ $? -eq 0 ]; then
    echo "==> Installing conda-build package"
    conda install conda-build --yes 2>&1 > /dev/null
    echo "==> Continue building taxcalc package"
fi

# determine this version of Python: 2.x or 3.x
pversion=$(conda list python | awk '$1=="python"{print substr($2,1,3)}')

# build taxcalc conda package for this version of Python
cd ../../conda.recipe/
conda build --python $pversion . 2>&1 | awk '$1~/BUILD/||$1~/TEST/'
conda build purge

# install taxcalc conda package
conda install taxcalc=0.0.0 --use-local --yes 2>&1 > /dev/null

# clean-up after package build
cd ..
rm -fr build/*
rmdir build/
rm -fr dist/*
rmdir dist/
rm -fr taxcalc.egg-info/*
rmdir taxcalc.egg-info/

echo "Execute './uninstall_taxcalc_package.sh' after testing CLI"

echo "FINISHED : `date`"
exit 0
