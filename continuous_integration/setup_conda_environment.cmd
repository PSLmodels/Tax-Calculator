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
conda create -n %CONDA_ENV% -q -y python=%PYTHON% pytest setuptools

call activate %CONDA_ENV%

@rem Install optional dependencies for tests
%CONDA_INSTALL% numpy=%NUMPY% pandas=%PANDAS% 
%CONDA_INSTALL% numba bokeh=0.12.3 toolz six mock pep8 pylist

%PIP_INSTALL% pytest-pep8

if %PYTHON% LSS 3.0 (%PIP_INSTALL% git+https://github.com/Blosc/castra)
if %PYTHON% LSS 3.0 (%PIP_INSTALL% backports.lzma mock)

@rem Display final environment (for reproducing)
%CONDA% list
%CONDA% list --explicit
python -m site
