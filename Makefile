# GNU Makefile that documents and automates common Tax-Calculator operations.
# USAGE: tax-calculator$ make <TARGET>

.PHONY=help
help:
	@echo "HELP MSG"

.PHONY=clean-pyc
clean-pyc:
	@find . -name *pyc -exec rm -f {} \;

.PHONY=clean-cache
clean-cache:
	@find . -name *cache -maxdepth 1 -exec rm -rf {} \;

.PHONY=clean-package
clean-package:
	@./conda.recipe/remove_local_taxcalc_package.sh

.PHONY=clean
clean: clean-pyc clean-cache clean-package
