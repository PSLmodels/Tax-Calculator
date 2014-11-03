try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md') as f:
        longdesc = f.read()

config = {
    'description': 'Tax Calculator',
    'url': 'https://github.com/OpenSourcePolicyCenter/Tax-Calculator',
    'download_url': 'https://github.com/OpenSourcePolicyCenter/Tax-Calculator',
    'description':'taxcalc',
    'long_description':longdesc,
    'install_requires': [],
    'version': '0.0',
    'license': 'MIT',
    'packages': ['taxcalc'],
    'include_package_data': True,
    'name': 'taxcalc',
    'install_requires': ['numpy', 'pandas'],
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    'tests_require': ['pytest']
}

setup(**config)
