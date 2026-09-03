"""
Tax-Calculator setup.
"""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    longdesc = f.read()

VERSION = "6.8.2"

config = {
    "description": "Tax-Calculator",
    "url": "https://github.com/PSLmodels/Tax-Calculator",
    "download_url": "https://github.com/PSLmodels/Tax-Calculator",
    "long_description_content_type": "text/markdown",
    "long_description": longdesc,
    "version": VERSION,
    "license": "CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
    "packages": ["taxcalc", "taxcalc.cli"],
    "include_package_data": True,
    "name": "taxcalc",
    "python_requires": ">=3.12",
    "install_requires": [
        "numpy>=2.4",
        "pandas>=3.0",
        "bokeh>=3.7",
        "numba>=0.64",
        "paramtools>=0.20.0"
    ],
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    "tests_require": ["pytest"],
    "entry_points": {"console_scripts": ["tc=taxcalc.cli.tc:cli_tc_main"]},
}

setup(**config)
