call activate %CONDA_ENV%

@echo on

@rem Install code
%PIP_INSTALL% --no-deps -e .[complete]
