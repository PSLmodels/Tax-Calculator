try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Tax Calculator',
    'url': 'URL to get it at.',
    'download_url': 'https://github.com/OpenSourcePolicyCenter/Tax-Calculator',
    'install_requires': [],
    'version': '0.0',
    'packages': ['taxcalc'],
    'name': 'taxcalc'
}

setup(**config)
