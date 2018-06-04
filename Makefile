# GNU Makefile that documents and automates common development operations
#              using the GNU make tool (version >= 3.81)
# USAGE: tax-calculator$ make [TARGET]

.PHONY=help
help:
	@echo "USAGE: make [TARGET]"
	@echo "TARGETS:"
	@echo "help : show help message"
	@echo "clean : remove .pyc files, caches, and local taxcalc package"
	@echo "package : build and install local taxcalc package"
	@echo "pytest-cps : generate report for and cleanup after"
	@echo "             pytest -m 'not requires_pufcsv and not pre_release'"
	@echo "pytest     : generate report for and cleanup after"
	@echo "             pytest -m 'not pre_release'"
	@echo "pytest-all : generate report for and cleanup after"
	@echo "             pytest -m ''"

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

define pytest-cleanup
find . -name *cache -maxdepth 1 -exec rm -rf {} \;
rm -f df-??-#-*
rm -f tmp??????-??-#-tmp*
endef

.PHONY=pytest-cps
pytest-cps:
	@cd taxcalc
	@pytest -n4 -m "not requires_pufcsv and not pre_release"
	@$(pytest-cleanup)
	@cd ..

.PHONY=pytest
pytest:
	@cd taxcalc
	@pytest -n4 -m "not pre_release"
	@$(pytest-cleanup)
	@cd ..

.PHONY=pytest-all
pytest-all:
	@cd taxcalc
	@pytest -n4 -m ""
	@$(pytest-cleanup)
	@cd ..
