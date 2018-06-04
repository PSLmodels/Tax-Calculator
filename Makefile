# GNU Makefile that documents and automates common development operations
#              using the GNU make tool (version >= 3.81)
# USAGE: tax-calculator$ make [TARGET]

.PHONY=help
help:
	@echo "USAGE: make [TARGET]"
	@echo "TARGETS:"
	@echo "help    : show help message"
	@echo "clean   : remove .pyc files, caches, and local taxcalc package"
	@echo "package : build and install local taxcalc package"

.PHONY=clean-pyc
clean-pyc:
	@find . -name *pyc -exec rm -f {} \;

.PHONY=clean-caches
clean-caches:
	@find . -name *cache -maxdepth 1 -exec rm -rf {} \;

.PHONY=clean-package
clean-package:
	@./conda.recipe/remove_local_taxcalc_package.sh

.PHONY=clean
clean: clean-pyc clean-caches clean-package

.PHONY=package
package:
	@./conda.recipe/install_local_taxcalc_package.sh
