#!/bin/bash
# USAGE: ./install_local_taxcalc_package.sh
# ACTION: (1) uninstalls any installed taxcalc package (conda uninstall)
#         (2) executes "conda install conda-build" (if necessary)
#         (3) builds local taxcalc=0.0.0 package (conda build)
#         (4) installs local taxcalc=0.0.0 package (conda install)
# NOTE: for those with experience working with compiled languages,
#       building a local conda package is analogous to compiling an executable

echo "STARTING : `date`"

echo "BUILD-PREP..."

# uninstall any existing taxcalc conda package
conda list taxcalc | awk '$1~/taxcalc/{rc=1}END{exit(rc)}'
if [ $? -eq 1 ]; then
    echo "==> Uninstalling existing taxcalc package"
    conda uninstall --yes taxcalc 2>&1 > /dev/null
    echo "==> Continuing to build new taxcalc package"
fi

# install conda-build package if not present
conda list build | awk '$1~/conda-build/{rc=1}END{exit(rc)}'
if [ $? -eq 0 ]; then
    echo "==> Installing conda-build package"
    conda install conda-build --yes 2>&1 > /dev/null
    echo "==> Continuing to build new taxcalc package"
fi

# determine this version of Python: 2.x or 3.x
pversion=$(conda list python | awk '$1=="python"{print substr($2,1,3)}')

# build taxcalc conda package for this version of Python
NOHASH=--old-build-string
conda build $NOHASH --python $pversion . 2>&1 | awk '$1~/BUILD/||$1~/TEST/'

# install taxcalc conda package
echo "INSTALLATION..."
#OLD#conda install taxcalc=0.0.0 --use-local --yes 2>&1 > /dev/null
#OLD# doesn't work in conda 4.4.0 or 4.4.1
#OLD# see https://github.com/ContinuumIO/anaconda-issues/issues/7876
#OLD# conda install --use-local can't find the built package with 4.4.0+
#OLD# the Continuum staff seems pretty careless in putting out new versions
#NEW# below works with conda 4.4.1, but users may need to customize ADIR
#NEW# because recently Continuum started installing Anaconda in
#NEW# either the ~/anaconda2 or ~/anaconda3 directory
ADIR=~/anaconda/conda-bld/osx-64
conda install --offline $ADIR/taxcalc-0.0.0-py27_0.tar.bz2 2>&1 > /dev/null

# clean-up after package build
echo "CLEAN-UP..."
conda build purge
cd ..
rm -fr build/*
rmdir build/
rm -fr dist/*
rmdir dist/
rm -fr taxcalc.egg-info/*
rmdir taxcalc.egg-info/

echo "Execute 'conda uninstall taxcalc --yes' after using taxcalc package"

echo "FINISHED : `date`"
exit 0
