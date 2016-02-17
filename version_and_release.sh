#!/bin/sh
# Run this at the root of the repo!
source activate taxcalc-dev
git tag $1
echo "finished tag, now distributing to PyPI"
python setup.py register sdist upload
echo "FINISHED UPLOAD TO PYPI"
git push; git push --tags
echo "FINISHED push "
rm ~/code/tc.tar
echo "FINISHED rm tar "
rm -rf ~/code/Tax-Calculator
echo "FINISHED rm dir "
git archive --prefix=Tax-Calculator/ -o ~/code/tc.tar $1
echo "FINISHED git archive"
cd ~/code/
tar xvf tc.tar
echo "FINISHED tar extract"
cd Tax-Calculator/conda.recipe
sed -i '' 's/version: 0.4/version: '${1}'/g' meta.yaml
echo "FINISHED changing meta.yaml"
conda build --python 2.7 .
echo "FINISHED CONDA BUILD"
cd $TAXCALC_PACKAGE_DIR
conda convert -p all ~/miniconda3/conda-bld/osx-64/taxcalc-$1-py27_0.tar.bz2 -o .
echo "FINISHED CONDA CONVERT"
