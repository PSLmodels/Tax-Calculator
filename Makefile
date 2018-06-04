# GNU Makefile that documents and automates common development operations
#              using the GNU make tool (version >= 3.81)
# USAGE: tax-calculator$ make [TARGET]

.PHONY=help
help:
	@echo "USAGE: make [TARGET]"
	@echo "TARGETS:"
	@echo "help       : show help message"
	@echo "clean      : remove .pyc files and local taxcalc package"
	@echo "package    : build and install local taxcalc package"
	@echo "pytest-cps : generate report for and cleanup after"
	@echo "             pytest -m 'not requires_pufcsv and not pre_release'"
	@echo "pytest     : generate report for and cleanup after"
	@echo "             pytest -m 'not pre_release'"
	@echo "pytest-all : generate report for and cleanup after"
	@echo "             pytest -m ''"
	@echo "tctest     : generate report for and cleanup after"
	@echo "             tc --test"

.PHONY=clean
clean: clean-pyc clean-package
	@find . -name *pyc -exec rm {} \;
	@./conda.recipe/remove_local_taxcalc_package.sh

.PHONY=package
package:
	@./conda.recipe/install_local_taxcalc_package.sh

define pytest-cleanup
find . -name *cache -maxdepth 1 -exec rm -r {} \;
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

define tctest-cleanup
rm -f test.csv
rm -f test-18-*
./conda.recipe/remove_local_taxcalc_package.sh	
endef

.PHONY=tctest
tctest: package
	tc --test
	@$(tctest-cleanup)
# TODO: add validation tests that use tc tool from package before cleanup
