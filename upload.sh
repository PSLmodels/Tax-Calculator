#!/bin/sh
cd $TAXCALC_PACKAGE_DIR
anaconda upload ~/miniconda3/conda-bld/osx-64/taxcalc-$1-py27_0.tar.bz2
anaconda upload ./linux-32/taxcalc-$1-py27_0.tar.bz2
anaconda upload ./linux-64/taxcalc-$1-py27_0.tar.bz2
anaconda upload ./win-64/taxcalc-$1-py27_0.tar.bz2
anaconda upload ./win-32/taxcalc-$1-py27_0.tar.bz2
echo "FINISHED package upload"
