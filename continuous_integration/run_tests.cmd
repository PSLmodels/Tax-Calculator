call activate %CONDA_ENV%

@echo on

set PYTHONFAULTHANDLER=1

set PYTEST=pytest --capture=sys

%PYTEST% -v -m "not requires_pufcsv and not pre_release and not local"
