# GNU Makefile that documents and automates common development operations
#              using the GNU make tool (version >= 3.81)
# Development is typically conducted on Linux or Max OS X (with the Xcode
#              command-line tools installed), so this Makefile is designed
#              to work in that environment (and not on Windows).
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
	@echo "cstest     : generate coding-style errors using the"
	@echo "             pycodestyle (nee pep8) and pylint tools"
	@echo "coverage   : generate test coverage report"
	@echo "git-sync   : synchronize local, origin, and upstream Git repos"
	@echo "git-pr N=n : create local pr-n branch containing upstream PR"

.PHONY=clean
clean:
	@find . -name *pyc -exec rm {} \;
	@find . -name *cache -maxdepth 1 -exec rm -r {} \;
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
	@cd taxcalc ; pytest -n4 -m "not requires_pufcsv and not pre_release"
	@$(pytest-cleanup)

.PHONY=pytest
pytest:
	@cd taxcalc ; pytest -n4 -m "not pre_release"
	@$(pytest-cleanup)

.PHONY=pytest-all
pytest-all:
	@cd taxcalc ; pytest -n4 -m ""
	@$(pytest-cleanup)

define tctest-cleanup
rm -f test.csv
rm -f test-18-*
./conda.recipe/remove_local_taxcalc_package.sh	
endef

.PHONY=tctest
tctest: package
	tc --test
	@$(tctest-cleanup)
	@echo "validation tests using tc will be added in the future"

TAXCALC_JSON_FILES := $(shell ls -l ./taxcalc/*json | awk '{print $$9}')
TESTS_JSON_FILES := $(shell ls -l ./taxcalc/tests/*json | awk '{print $$9}')
PYLINT_FILES := $(shell grep -rl --include="*py" disable=locally-disabled .)

.PHONY=cstest
cstest:
	pycodestyle taxcalc
	pycodestyle docs/cookbook
	@pycodestyle --ignore=E501,E121 $(TAXCALC_JSON_FILES)
	@pycodestyle --ignore=E501,E121 $(TESTS_JSON_FILES)
	@pylint --disable=locally-disabled --score=no --jobs=4 $(PYLINT_FILES)

define coverage-cleanup
rm -f .coverage htmlcov/*
endef

COVMARK = "not requires_pufcsv and not pre_release"

OS := $(shell uname -s)

.PHONY=coverage
coverage:
	@$(coverage-cleanup)
	@coverage run -m pytest -v -m $(COVMARK) > /dev/null
	@coverage html --ignore-errors
ifeq ($(OS), Darwin) # on Mac OS X
	@open htmlcov/index.html
else
	@echo "Open htmlcov/index.html in browser to view report"
endif
	@$(pytest-cleanup)

.PHONY=git-sync
git-sync:
	@./gitsync

.PHONY=git-pr
git-pr:
	@./gitpr $(N)
