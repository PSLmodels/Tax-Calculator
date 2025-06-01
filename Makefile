# GNU Makefile that documents and automates common development operations
#              using the GNU make tool (version >= 3.81)
# Development is typically conducted on Linux or Max OS X (with the Xcode
#              command-line tools installed), so this Makefile is designed
#              to work in that environment (and not on Windows).
# USAGE: Tax-Calculator$ make [TARGET]

.PHONY=help
help:
	@echo "USAGE: make [TARGET]"
	@echo "TARGETS:"
	@echo "help       : show help message"
	@echo "clean      : remove .pyc files and local taxcalc package"
	@echo "package    : build and install local package"
	@echo "pytest-cps : generate report for and cleanup after"
	@echo "             pytest -m 'not requires_pufcsv and not pre_release'"
	@echo "pytest     : generate report for and cleanup after"
	@echo "             pytest -m 'not pre_release'"
	@echo "pytest-all : generate report for and cleanup after"
	@echo "             pytest -m ''"
	@echo "tctest     : generate report for and cleanup after"
	@echo "             tc --test"
	@echo "tctest-jit : generate report for and cleanup after"
	@echo "             tc --test when environment var NOTAXCALCJIT is set"
	@echo "cstest     : generate coding-style errors using the"
	@echo "             pycodestyle (nee pep8) and pylint tools"
	@echo "coverage   : generate test coverage report"
	@echo "git-sync   : synchronize local, origin, and upstream Git repos"
	@echo "git-pr N=n : create local pr-n branch containing upstream PR"

.PHONY=clean
clean:
	@find . -name *pyc -exec rm {} \;
	@find . -name *cache -maxdepth 1 -exec rm -r {} \;
	@pip uninstall taxcalc --yes --quiet 2>&1 > /dev/null

.PHONY=package
package:
	@pip install -e .

define pytest-setup
rm -f taxcalc/tests/reforms_actual_init
endef

define pytest-cleanup
find . -name *cache -maxdepth 1 -exec rm -r {} \;
rm -f df-??-#-*
rm -f tmp??????-??-#-tmp*
endef

.PHONY=pytest-cps
pytest-cps: clean
	@$(pytest-setup)
	@cd taxcalc ; pytest -n4 --disable-warnings --durations=0 --durations-min=2 -m "not requires_pufcsv and not pre_release"
	@$(pytest-cleanup)

.PHONY=pytest
pytest: clean
	@$(pytest-setup)
	@cd taxcalc ; pytest -n4 --disable-warnings --durations=0 --durations-min=2 -m "not pre_release"
	@$(pytest-cleanup)

.PHONY=pytest-all
pytest-all: clean
	@$(pytest-setup)
	@cd taxcalc ; pytest -n4 --disable-warnings --durations=0 --durations-min=2 -m ""
	@$(pytest-cleanup)

define tctest-cleanup
rm -f test.csv
rm -f test-18-*
pip uninstall taxcalc --yes --quiet 2>&1 > /dev/null
endef

.PHONY=tctest
tctest: package
	tc --test
	@$(tctest-cleanup)

.PHONY=tctest-jit
tctest-jit:
	@./tctest-nojit.sh

TOPLEVEL_JSON_FILES := $(shell ls -l ./*json | awk '{print $$9}')
TAXCALC_JSON_FILES := $(shell ls -l ./taxcalc/*json | awk '{print $$9}')
TESTS_JSON_FILES := $(shell ls -l ./taxcalc/tests/*json | awk '{print $$9}')
PYLINT_DISABLE = locally-disabled,duplicate-code,cyclic-import
PYLINT_OPTIONS = --disable=$(PYLINT_DISABLE) --score=no --jobs=4
EXCLUDED_PATHS = docs,taxcalc/validation

.PHONY=cstest
cstest:
	@-pycodestyle --ignore=W503,W504,E712 --exclude=$(EXCLUDED_PATHS) .
	@-pycodestyle --ignore=E501,E121 $(TOPLEVEL_JSON_FILES)
	@-pycodestyle --ignore=E501,E121 $(TAXCALC_JSON_FILES)
	@-pycodestyle --ignore=E501,E121 $(TESTS_JSON_FILES)
	@-pylint $(PYLINT_OPTIONS) --ignore-paths=$(EXCLUDED_PATHS) .

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
