# GNU Makefile that documents and automates common Tax-Calculator operations
#     using the GNU make tool (version >= 3.81)
# USAGE: tax-calculator$ make [TARGET]

.PHONY=help
help:
	@echo "USAGE: make [TARGET]"
	@echo "TARGETS:"
	@echo "  help : help description "

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
