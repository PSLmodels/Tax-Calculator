@rem The cmd /C hack circumvents a regression where conda installs a conda.bat
@rem script in non-root environments.
set CONDA=cmd /C conda
set CONDA_INSTALL=%CONDA% install -q -y
set PIP_INSTALL=pip install -q

@echo on

@rem Deactivate any environment
call deactivate
@rem Display root environment (for debugging)
conda list
@rem Clean up any left-over from a previous build
conda remove --all -q -y -n %CONDA_ENV%

@rem Create test environment
@rem (note: no cytoolz as it seems to prevent faulthandler tracebacks on crash)
conda create -n %CONDA_ENV% -q -y python=%PYTHON%

call activate %CONDA_ENV%

%CONDA% env update -f environment.yml

%PIP_INSTALL% pytest-pep8

if %PYTHON% LSS 3.0 (%PIP_INSTALL% backports.lzma mock)

@rem Display final environment (for reproducing)
%CONDA% list
%CONDA% list --explicit
python -m site
