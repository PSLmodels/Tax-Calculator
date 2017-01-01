call activate %CONDA_ENV%

@echo on

@rem Install taxcalc
%PIP_INSTALL% --no-deps -e .[complete]
