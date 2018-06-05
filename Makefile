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
	@echo "cstest     : generate coding-style reports using"
	@echo "             pycodestyle and pylint tools"

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
	@echo "validation tests using tc will be added in the future"

# TAXCALC_JSONFILES list is constructed using the following command:
# tax-calculator$ ls -l ./taxcalc/*json | awk '{print $9}'
TAXCALC_JSONFILES = ./taxcalc/behavior.json \
	./taxcalc/consumption.json \
	./taxcalc/current_law_policy.json \
	./taxcalc/growdiff.json \
	./taxcalc/growmodel.json \
	./taxcalc/records_variables.json

# PYLINT_FILES list is constructed using the following command:
# tax-calculator$ grep -rl --include="*py" disable=locally-disabled .
PYLINT_FILES = ./docs/cookbook/make_cookbook.py \
	./docs/cookbook/test_recipes.py \
	./docs/make_index.py \
	./puf_fuzz.py \
	./simtax.py \
	./taxcalc/behavior.py \
	./taxcalc/calculate.py \
	./taxcalc/cli/tc.py \
	./taxcalc/consumption.py \
	./taxcalc/decorators.py \
	./taxcalc/functions.py \
	./taxcalc/growdiff.py \
	./taxcalc/growfactors.py \
	./taxcalc/growmodel.py \
	./taxcalc/macro_elasticity.py \
	./taxcalc/policy.py \
	./taxcalc/records.py \
	./taxcalc/simpletaxio.py \
	./taxcalc/taxcalcio.py \
	./taxcalc/tbi/tbi.py \
	./taxcalc/tbi/tbi_utils.py \
	./taxcalc/tests/test_4package.py \
	./taxcalc/tests/test_compare.py \
	./taxcalc/tests/test_compatible_data.py \
	./taxcalc/tests/test_cpscsv.py \
	./taxcalc/tests/test_docs.py \
	./taxcalc/tests/test_functions.py \
	./taxcalc/tests/test_growfactors.py \
	./taxcalc/tests/test_macro_elasticity.py \
	./taxcalc/tests/test_parameters.py \
	./taxcalc/tests/test_puf_var_stats.py \
	./taxcalc/tests/test_pufcsv.py \
	./taxcalc/tests/test_reforms.py \
	./taxcalc/tests/test_responses.py \
	./taxcalc/tests/test_simpletaxio.py \
	./taxcalc/tests/test_taxcalcio.py \
	./taxcalc/tests/test_utils.py \
	./taxcalc/utils.py \
	./taxcalc/utilsprvt.py \
	./taxcalc/validation/csv_taxdiffs.py

.PHONY=cstest
cstest:
	pycodestyle taxcalc
	@pycodestyle --ignore=E501,E121 $(TAXCALC_JSONFILES)
	@pylint --disable=locally-disabled --score=no --jobs=4 $(PYLINT_FILES)
