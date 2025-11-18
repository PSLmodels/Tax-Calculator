"""
This script uses known values of inflation-indexed policy parameters after
2022 to write an updated version of the taxcalc/policy_current_law.json file.

USAGE: (taxcalc-dev) T-C% python update_pcl.py
THEN CHECK:             % diff pcl.json taxcalc/policy_current_law.json
IF DIFFS OK:            % mv pcl.json taxcalc/policy_current_law.json

WHEN TO USE: use this script to update taxcalc/policy_current_law.json
whenever inflation rates in the growfactors.csv files are changed, or
whenever new known policy parameter values are published.
"""

import os
import sys
import json

LIST_MARS_ZERO = [
    {'year': 2023, 'MARS': 'single', 'value': 0.0},
    {'year': 2023, 'MARS': 'mjoint', 'value': 0.0},
    {'year': 2023, 'MARS': 'mseparate', 'value': 0.0},
    {'year': 2023, 'MARS': 'headhh', 'value': 0.0},
    {'year': 2023, 'MARS': 'widow', 'value': 0.0},

    {'year': 2024, 'MARS': 'single', 'value': 0.0},
    {'year': 2024, 'MARS': 'mjoint', 'value': 0.0},
    {'year': 2024, 'MARS': 'mseparate', 'value': 0.0},
    {'year': 2024, 'MARS': 'headhh', 'value': 0.0},
    {'year': 2024, 'MARS': 'widow', 'value': 0.0},

    {'year': 2025, 'MARS': 'single', 'value': 0.0},
    {'year': 2025, 'MARS': 'mjoint', 'value': 0.0},
    {'year': 2025, 'MARS': 'mseparate', 'value': 0.0},
    {'year': 2025, 'MARS': 'headhh', 'value': 0.0},
    {'year': 2025, 'MARS': 'widow', 'value': 0.0},

    {'year': 2026, 'MARS': 'single', 'value': 0.0},
    {'year': 2026, 'MARS': 'mjoint', 'value': 0.0},
    {'year': 2026, 'MARS': 'mseparate', 'value': 0.0},
    {'year': 2026, 'MARS': 'headhh', 'value': 0.0},
    {'year': 2026, 'MARS': 'widow', 'value': 0.0},
]
LIST_MARS_INF = [
    {'year': 2023, 'MARS': 'single', 'value': 9e99},
    {'year': 2023, 'MARS': 'mjoint', 'value': 9e99},
    {'year': 2023, 'MARS': 'mseparate', 'value': 9e99},
    {'year': 2023, 'MARS': 'headhh', 'value': 9e99},
    {'year': 2023, 'MARS': 'widow', 'value': 9e99},

    {'year': 2024, 'MARS': 'single', 'value': 9e99},
    {'year': 2024, 'MARS': 'mjoint', 'value': 9e99},
    {'year': 2024, 'MARS': 'mseparate', 'value': 9e99},
    {'year': 2024, 'MARS': 'headhh', 'value': 9e99},
    {'year': 2024, 'MARS': 'widow', 'value': 9e99},

    {'year': 2025, 'MARS': 'single', 'value': 9e99},
    {'year': 2025, 'MARS': 'mjoint', 'value': 9e99},
    {'year': 2025, 'MARS': 'mseparate', 'value': 9e99},
    {'year': 2025, 'MARS': 'headhh', 'value': 9e99},
    {'year': 2025, 'MARS': 'widow', 'value': 9e99},

    {'year': 2026, 'MARS': 'single', 'value': 9e99},
    {'year': 2026, 'MARS': 'mjoint', 'value': 9e99},
    {'year': 2026, 'MARS': 'mseparate', 'value': 9e99},
    {'year': 2026, 'MARS': 'headhh', 'value': 9e99},
    {'year': 2026, 'MARS': 'widow', 'value': 9e99},
]
LIST_SCALAR_ZERO = [
    {'year': 2023, 'value': 0.0},

    {'year': 2024, 'value': 0.0},

    {'year': 2025, 'value': 0.0},

    {'year': 2026, 'value': 0.0},
]
NEW_KNOWN_ITEMS = {
    # PAYROLL TAX PARAMETER SOURCES:
    # - SSA Office of the Chief Actuary: Contribution and Benefit Base
    #       https://www.ssa.gov/OACT/COLA/cbb.html
    'SS_Earnings_c': [
        {'year': 2023, 'value': 160200.0},

        {'year': 2024, 'value': 168600.0},

        {'year': 2025, 'value': 176100.0},

        {'year': 2026, 'value': 184500.0},
    ],
    # INCOME TAX PARAMETER SOURCES:
    # - IRS Rev. Proc. 2022-38 containing 2023 policy parameter values is at:
    #       https://www.irs.gov/pub/irs-drop/rp-22-38.pdf
    # - IRS Rev. Proc. 2023-34 containing 2024 policy parameter values is at:
    #       https://www.irs.gov/pub/irs-drop/rp-23-34.pdf
    # - IRS Rev. Proc. 2024-40 containing 2025 policy parameter values is at:
    #       https://www.irs.gov/pub/irs-drop/rp-24-40.pdf
    # - IRS Rev. Proc. 2025-32 containing 2026 policy parameter values is at:
    #       https://www.irs.gov/pub/irs-drop/rp-25-32.pdf
    #   Note that rp-25-32.pdf also includes 2025 values for OBBBA parameters
    'II_brk1': [
        {'year': 2023, 'MARS': 'single', 'value': 11000.0},
        {'year': 2023, 'MARS': 'mjoint', 'value': 22000.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 11000.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 15700.0},
        {'year': 2023, 'MARS': 'widow', 'value': 22000.0},

        {'year': 2024, 'MARS': 'single', 'value': 11600.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 23200.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 11600.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 16550.0},
        {'year': 2024, 'MARS': 'widow', 'value': 23200.0},

        {'year': 2025, 'MARS': 'single', 'value': 11925.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 23850.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 11925.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 17000.0},
        {'year': 2025, 'MARS': 'widow', 'value': 23850.0},

        {'year': 2026, 'MARS': 'single', 'value': 12400.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 24800.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 12400.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 17700.0},
        {'year': 2026, 'MARS': 'widow', 'value': 24800.0},
    ],
    'II_brk2': [
        {'year': 2023, 'MARS': 'single', 'value': 44725.},
        {'year': 2023, 'MARS': 'mjoint', 'value': 89450.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 44725.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 59850.0},
        {'year': 2023, 'MARS': 'widow', 'value': 89450.0},

        {'year': 2024, 'MARS': 'single', 'value': 47150.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 94300.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 47150.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 63100.0},
        {'year': 2024, 'MARS': 'widow', 'value': 94300.0},

        {'year': 2025, 'MARS': 'single', 'value': 48475.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 96950.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 48475.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 64850.0},
        {'year': 2025, 'MARS': 'widow', 'value': 96950.0},

        {'year': 2026, 'MARS': 'single', 'value': 50400.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 100800.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 50400.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 67450.0},
        {'year': 2026, 'MARS': 'widow', 'value': 100800.0},
    ],
    'II_brk3': [
        {'year': 2023, 'MARS': 'single', 'value': 95375.0},
        {'year': 2023, 'MARS': 'mjoint', 'value': 190750.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 95375.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 95350.0},
        {'year': 2023, 'MARS': 'widow', 'value': 190750.0},

        {'year': 2024, 'MARS': 'single', 'value': 100525.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 201050.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 100525.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 100500.0},
        {'year': 2024, 'MARS': 'widow', 'value': 201050.0},

        {'year': 2025, 'MARS': 'single', 'value': 103350.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 206700.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 103350.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 103350.0},
        {'year': 2025, 'MARS': 'widow', 'value': 206700.0},

        {'year': 2026, 'MARS': 'single', 'value': 105700.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 211400.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 105700.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 105700.0},
        {'year': 2026, 'MARS': 'widow', 'value': 211400.0},
    ],
    'II_brk4': [
        {'year': 2023, 'MARS': 'single', 'value': 182100.0},
        {'year': 2023, 'MARS': 'mjoint', 'value': 364200.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 182100.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 182100.0},
        {'year': 2023, 'MARS': 'widow', 'value': 364200.0},

        {'year': 2024, 'MARS': 'single', 'value': 191950.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 383900.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 191950.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 191950.0},
        {'year': 2024, 'MARS': 'widow', 'value': 383900.0},

        {'year': 2025, 'MARS': 'single', 'value': 197300.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 394600.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 197300.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 197300.0},
        {'year': 2025, 'MARS': 'widow', 'value': 394600.0},

        {'year': 2026, 'MARS': 'single', 'value': 201775.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 403550.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 201775.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 201750.0},
        {'year': 2026, 'MARS': 'widow', 'value': 403550.0},
    ],
    'II_brk5': [
        {'year': 2023, 'MARS': 'single', 'value': 231250.0},
        {'year': 2023, 'MARS': 'mjoint', 'value': 462500.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 231250.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 231250.0},
        {'year': 2023, 'MARS': 'widow', 'value': 462500.0},

        {'year': 2024, 'MARS': 'single', 'value': 243725.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 487450.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 243725.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 243700.0},
        {'year': 2024, 'MARS': 'widow', 'value': 487450.0},

        {'year': 2025, 'MARS': 'single', 'value': 250525.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 501050.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 250525.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 250500.0},
        {'year': 2025, 'MARS': 'widow', 'value': 501050.0},

        {'year': 2026, 'MARS': 'single', 'value': 256225.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 512450.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 256225.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 256200.0},
        {'year': 2026, 'MARS': 'widow', 'value': 512450.0},
    ],
    'II_brk6': [
        {'year': 2023, 'MARS': 'single', 'value': 578125.0},
        {'year': 2023, 'MARS': 'mjoint', 'value': 693750.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 578125.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 578100.0},
        {'year': 2023, 'MARS': 'widow', 'value': 693750.0},

        {'year': 2024, 'MARS': 'single', 'value': 609350.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 731200.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 365600.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 609350.0},
        {'year': 2024, 'MARS': 'widow', 'value': 731200.0},

        {'year': 2025, 'MARS': 'single', 'value': 626350.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 751600.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 375800.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 626350.0},
        {'year': 2025, 'MARS': 'widow', 'value': 751600.0},

        {'year': 2026, 'MARS': 'single', 'value': 640600.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 768700.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 384350.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 640600.0},
        {'year': 2026, 'MARS': 'widow', 'value': 768700.0},
    ],
    'II_brk7': [
        {'year': 2023, 'MARS': 'single', 'value': 9e99},
        {'year': 2023, 'MARS': 'mjoint', 'value': 9e99},
        {'year': 2023, 'MARS': 'mseparate', 'value': 9e99},
        {'year': 2023, 'MARS': 'headhh', 'value': 9e99},
        {'year': 2023, 'MARS': 'widow', 'value': 9e99},

        {'year': 2024, 'MARS': 'single', 'value': 9e99},
        {'year': 2024, 'MARS': 'mjoint', 'value': 9e99},
        {'year': 2024, 'MARS': 'mseparate', 'value': 9e99},
        {'year': 2024, 'MARS': 'headhh', 'value': 9e99},
        {'year': 2024, 'MARS': 'widow', 'value': 9e99},

        {'year': 2025, 'MARS': 'single', 'value': 9e99},
        {'year': 2025, 'MARS': 'mjoint', 'value': 9e99},
        {'year': 2025, 'MARS': 'mseparate', 'value': 9e99},
        {'year': 2025, 'MARS': 'headhh', 'value': 9e99},
        {'year': 2025, 'MARS': 'widow', 'value': 9e99},

        {'year': 2026, 'MARS': 'single', 'value': 9e99},
        {'year': 2026, 'MARS': 'mjoint', 'value': 9e99},
        {'year': 2026, 'MARS': 'mseparate', 'value': 9e99},
        {'year': 2026, 'MARS': 'headhh', 'value': 9e99},
        {'year': 2026, 'MARS': 'widow', 'value': 9e99},
    ],
    'CG_brk1': [
        {'year': 2023, 'MARS': 'single', 'value': 44625.0},
        {'year': 2023, 'MARS': 'mjoint', 'value': 89250.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 44625.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 59750.0},
        {'year': 2023, 'MARS': 'widow', 'value': 89250.0},

        {'year': 2024, 'MARS': 'single', 'value': 47025.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 94050.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 47025.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 63000.0},
        {'year': 2024, 'MARS': 'widow', 'value': 94050.0},

        {'year': 2025, 'MARS': 'single', 'value': 48350.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 96700.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 48350.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 64750.0},
        {'year': 2025, 'MARS': 'widow', 'value': 96700.0},

        {'year': 2026, 'MARS': 'single', 'value': 49450.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 98900.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 49450.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 66200.0},
        {'year': 2026, 'MARS': 'widow', 'value': 98900.0},
    ],
    'CG_brk2': [
        {'year': 2023, 'MARS': 'single', 'value': 492300.0},
        {'year': 2023, 'MARS': 'mjoint', 'value': 553850.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 276900.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 523050.0},
        {'year': 2023, 'MARS': 'widow', 'value': 553850.0},

        {'year': 2024, 'MARS': 'single', 'value': 518900.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 583750.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 291850.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 551350.0},
        {'year': 2024, 'MARS': 'widow', 'value': 583750.0},

        {'year': 2025, 'MARS': 'single', 'value': 533400.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 600050.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 300000.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 566700.0},
        {'year': 2025, 'MARS': 'widow', 'value': 600050.0},

        {'year': 2026, 'MARS': 'single', 'value': 545500.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 613700.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 306850.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 579600.0},
        {'year': 2026, 'MARS': 'widow', 'value': 613700.0},
    ],
    'CG_brk3': [
        {'year': 2023, 'MARS': 'single', 'value': 9e99},
        {'year': 2023, 'MARS': 'mjoint', 'value': 9e99},
        {'year': 2023, 'MARS': 'mseparate', 'value': 9e99},
        {'year': 2023, 'MARS': 'headhh', 'value': 9e99},
        {'year': 2023, 'MARS': 'widow', 'value': 9e99},

        {'year': 2024, 'MARS': 'single', 'value': 9e99},
        {'year': 2024, 'MARS': 'mjoint', 'value': 9e99},
        {'year': 2024, 'MARS': 'mseparate', 'value': 9e99},
        {'year': 2024, 'MARS': 'headhh', 'value': 9e99},
        {'year': 2024, 'MARS': 'widow', 'value': 9e99},

        {'year': 2025, 'MARS': 'single', 'value': 9e99},
        {'year': 2025, 'MARS': 'mjoint', 'value': 9e99},
        {'year': 2025, 'MARS': 'mseparate', 'value': 9e99},
        {'year': 2025, 'MARS': 'headhh', 'value': 9e99},
        {'year': 2025, 'MARS': 'widow', 'value': 9e99},
    ],
    'EITC_c': [
        {'year': 2023, 'EIC': '0kids', 'value': 600.0},
        {'year': 2023, 'EIC': '1kid', 'value': 3995.0},
        {'year': 2023, 'EIC': '2kids', 'value': 6604.0},
        {'year': 2023, 'EIC': '3+kids', 'value': 7430.0},

        {'year': 2024, 'EIC': '0kids', 'value': 632.0},
        {'year': 2024, 'EIC': '1kid', 'value': 4213.0},
        {'year': 2024, 'EIC': '2kids', 'value': 6960.0},
        {'year': 2024, 'EIC': '3+kids', 'value': 7830.0},

        {'year': 2025, 'EIC': '0kids', 'value': 649.0},
        {'year': 2025, 'EIC': '1kid', 'value': 4328.0},
        {'year': 2025, 'EIC': '2kids', 'value': 7152.0},
        {'year': 2025, 'EIC': '3+kids', 'value': 8046.0},

        {'year': 2026, 'EIC': '0kids', 'value': 664.0},
        {'year': 2026, 'EIC': '1kid', 'value': 4427.0},
        {'year': 2026, 'EIC': '2kids', 'value': 7316.0},
        {'year': 2026, 'EIC': '3+kids', 'value': 8231.0},
    ],
    'EITC_ps': [
        {'year': 2023, 'EIC': '0kids', 'value': 9800.0},
        {'year': 2023, 'EIC': '1kid', 'value': 21560.0},
        {'year': 2023, 'EIC': '2kids', 'value': 21560.0},
        {'year': 2023, 'EIC': '3+kids', 'value': 21560.0},

        {'year': 2024, 'EIC': '0kids', 'value': 10330.0},
        {'year': 2024, 'EIC': '1kid', 'value': 22720.0},
        {'year': 2024, 'EIC': '2kids', 'value': 22720.0},
        {'year': 2024, 'EIC': '3+kids', 'value': 22720.0},

        {'year': 2025, 'EIC': '0kids', 'value': 10620.0},
        {'year': 2025, 'EIC': '1kid', 'value': 23350.0},
        {'year': 2025, 'EIC': '2kids', 'value': 23350.0},
        {'year': 2025, 'EIC': '3+kids', 'value': 23350.0},

        {'year': 2026, 'EIC': '0kids', 'value': 10860.0},
        {'year': 2026, 'EIC': '1kid', 'value': 23890.0},
        {'year': 2026, 'EIC': '2kids', 'value': 23890.0},
        {'year': 2026, 'EIC': '3+kids', 'value': 23890.0},
    ],
    'EITC_ps_addon_MarriedJ': [
        {'year': 2023, 'EIC': '0kids', 'value': 6570.0},
        {'year': 2023, 'EIC': '1kid', 'value': 6560.0},
        {'year': 2023, 'EIC': '2kids', 'value': 6560.0},
        {'year': 2023, 'EIC': '3+kids', 'value': 6560.0},

        {'year': 2024, 'EIC': '0kids', 'value': 6920.0},
        {'year': 2024, 'EIC': '1kid', 'value': 6920.0},
        {'year': 2024, 'EIC': '2kids', 'value': 6920.0},
        {'year': 2024, 'EIC': '3+kids', 'value': 6920.0},

        {'year': 2025, 'EIC': '0kids', 'value': 7110.0},
        {'year': 2025, 'EIC': '1kid', 'value': 7120.0},
        {'year': 2025, 'EIC': '2kids', 'value': 7120.0},
        {'year': 2025, 'EIC': '3+kids', 'value': 7120.0},

        {'year': 2026, 'EIC': '0kids', 'value': 7280.0},
        {'year': 2026, 'EIC': '1kid', 'value': 7270.0},
        {'year': 2026, 'EIC': '2kids', 'value': 7270.0},
        {'year': 2026, 'EIC': '3+kids', 'value': 7270.0},
    ],
    'EITC_InvestIncome_c': [
        {'year': 2023, 'value': 11000.0},

        {'year': 2024, 'value': 11600.0},

        {'year': 2025, 'value': 11950.0},

        {'year': 2026, 'value': 12200.0},
    ],
    'AMT_brk1': [
        {'year': 2023, 'MARS': 'single', 'value': 220700.0},
        {'year': 2023, 'MARS': 'mjoint', 'value': 220700.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 110350.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 220700.0},
        {'year': 2023, 'MARS': 'widow', 'value': 220700.0},

        {'year': 2024, 'MARS': 'single', 'value': 232600.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 232600.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 116300.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 232600.0},
        {'year': 2024, 'MARS': 'widow', 'value': 232600.0},

        {'year': 2025, 'MARS': 'single', 'value': 239100.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 239100.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 119550.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 239100.0},
        {'year': 2025, 'MARS': 'widow', 'value': 239100.0},

        {'year': 2026, 'MARS': 'single', 'value': 244500.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 244500.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 122250.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 244500.0},
        {'year': 2026, 'MARS': 'widow', 'value': 244500.0},
    ],
    'AMT_em': [
        {'year': 2023, 'MARS': 'single', 'value': 81300.0},
        {'year': 2023, 'MARS': 'mjoint', 'value': 126500.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 63250.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 81300.0},
        {'year': 2023, 'MARS': 'widow', 'value': 126500.0},

        {'year': 2024, 'MARS': 'single', 'value': 85700.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 133300.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 66650.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 85700.0},
        {'year': 2024, 'MARS': 'widow', 'value': 133300.0},

        {'year': 2025, 'MARS': 'single', 'value': 88100.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 137000.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 68500.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 88100.0},
        {'year': 2025, 'MARS': 'widow', 'value': 137000.0},

        {'year': 2026, 'MARS': 'single', 'value': 90100.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 140200.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 70100.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 90100.0},
        {'year': 2026, 'MARS': 'widow', 'value': 140200.0},
    ],
    'AMT_em_ps': [
        {'year': 2023, 'MARS': 'single', 'value': 578150.0},
        {'year': 2023, 'MARS': 'mjoint', 'value': 1156300.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 578150.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 578150.0},
        {'year': 2023, 'MARS': 'widow', 'value': 1156300.0},

        {'year': 2024, 'MARS': 'single', 'value': 609350.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 1218700.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 609350.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 609350.0},
        {'year': 2024, 'MARS': 'widow', 'value': 1218700.0},

        {'year': 2025, 'MARS': 'single', 'value': 626350.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 1252700.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 626350.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 626350.0},
        {'year': 2025, 'MARS': 'widow', 'value': 1252700.0},

        {'year': 2026, 'MARS': 'single', 'value': 500000.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 1000000.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 500000.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 500000.0},
        {'year': 2026, 'MARS': 'widow', 'value': 1000000.0},
    ],
    'AMT_em_pe': [
        {'year': 2023, 'value': 831150.0},

        {'year': 2024, 'value': 875950.0},

        {'year': 2025, 'value': 900350.0},

        {'year': 2026, 'value': 639200.0},
    ],
    'AMT_child_em': [
        {'year': 2023, 'value': 8800.0},

        {'year': 2024, 'value': 9250.0},

        {'year': 2025, 'value': 9550.0},

        {'year': 2026, 'value': 9750.0},
    ],
    'STD': [
        {'year': 2023, 'MARS': 'single', 'value': 13850.0},
        {'year': 2023, 'MARS': 'mjoint', 'value': 27700.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 13850.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 20800.0},
        {'year': 2023, 'MARS': 'widow', 'value': 27700.0},

        {'year': 2024, 'MARS': 'single', 'value': 14600.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 29200.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 14600.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 21900.0},
        {'year': 2024, 'MARS': 'widow', 'value': 29200.0},

        {'year': 2025, 'MARS': 'single', 'value': 15750.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 31500.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 15750.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 23625.0},
        {'year': 2025, 'MARS': 'widow', 'value': 31500.0},

        {'year': 2026, 'MARS': 'single', 'value': 16100.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 32200.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 16100.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 24150.0},
        {'year': 2026, 'MARS': 'widow', 'value': 32200.0},
    ],
    'STD_Dep': [
        {'year': 2023, 'value': 1250.0},

        {'year': 2024, 'value': 1300.0},

        {'year': 2025, 'value': 1350.0},

        {'year': 2026, 'value': 1350.0},
    ],
    'STD_Aged': [
        {'year': 2023, 'MARS': 'single', 'value': 1800.0},
        {'year': 2023, 'MARS': 'mjoint', 'value': 1500.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 1500.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 1800.0},
        {'year': 2023, 'MARS': 'widow', 'value': 1800.0},

        {'year': 2024, 'MARS': 'single', 'value': 1950.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 1550.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 1550.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 1950.0},
        {'year': 2024, 'MARS': 'widow', 'value': 1950.0},

        {'year': 2025, 'MARS': 'single', 'value': 2000.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 1600.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 1600.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 2000.0},
        {'year': 2025, 'MARS': 'widow', 'value': 1600.0},

        {'year': 2026, 'MARS': 'single', 'value': 2050.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 1650.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 1650.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 2050.0},
        {'year': 2026, 'MARS': 'widow', 'value': 1650.0},
    ],
    'ID_AllTaxes_c_ps': [
        {'year': 2025, 'MARS': 'single', 'value': 500000},
        {'year': 2025, 'MARS': 'mjoint', 'value': 500000},
        {'year': 2025, 'MARS': 'mseparate', 'value': 250000},
        {'year': 2025, 'MARS': 'headhh', 'value': 500000},
        {'year': 2025, 'MARS': 'widow', 'value': 500000},

        {'year': 2030, 'MARS': 'single', 'value': 9e+99},
        {'year': 2030, 'MARS': 'mjoint', 'value': 9e+99},
        {'year': 2030, 'MARS': 'mseparate', 'value': 9e+99},
        {'year': 2030, 'MARS': 'headhh', 'value': 9e+99},
        {'year': 2030, 'MARS': 'widow', 'value': 9e+99},
    ],
    'PT_qbid_taxinc_thd': [
        {'year': 2023, 'MARS': 'single', 'value': 182100.0},
        {'year': 2023, 'MARS': 'mjoint', 'value': 364200.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 182100.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 182100.0},
        {'year': 2023, 'MARS': 'widow', 'value': 182100.0},

        {'year': 2024, 'MARS': 'single', 'value': 191950.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 383900.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 191950.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 191950.0},
        {'year': 2024, 'MARS': 'widow', 'value': 191950.0},

        {'year': 2025, 'MARS': 'single', 'value': 197300.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 394600.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 197300.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 197300.0},
        {'year': 2025, 'MARS': 'widow', 'value': 197300.0},

        {'year': 2026, 'MARS': 'single', 'value': 201750.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 403500.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 201775.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 201750.0},
        {'year': 2026, 'MARS': 'widow', 'value': 201750.0},
    ],
    'PT_qbid_min_ded': [
        {'year': 2026, 'value': 400},
    ],
    'PT_qbid_min_qbi': [
        {'year': 2026, 'value': 1000},
    ],
    'ALD_BusinessLosses_c': [
        {'year': 2023, 'MARS': 'single', 'value': 289000.0},
        {'year': 2023, 'MARS': 'mjoint', 'value': 578000.0},
        {'year': 2023, 'MARS': 'mseparate', 'value': 289000.0},
        {'year': 2023, 'MARS': 'headhh', 'value': 289000.0},
        {'year': 2023, 'MARS': 'widow', 'value': 578000.0},

        {'year': 2024, 'MARS': 'single', 'value': 305000.0},
        {'year': 2024, 'MARS': 'mjoint', 'value': 610000.0},
        {'year': 2024, 'MARS': 'mseparate', 'value': 305000.0},
        {'year': 2024, 'MARS': 'headhh', 'value': 305000.0},
        {'year': 2024, 'MARS': 'widow', 'value': 610000.0},

        {'year': 2025, 'MARS': 'single', 'value': 313000.0},
        {'year': 2025, 'MARS': 'mjoint', 'value': 626000.0},
        {'year': 2025, 'MARS': 'mseparate', 'value': 313000.0},
        {'year': 2025, 'MARS': 'headhh', 'value': 313000.0},
        {'year': 2025, 'MARS': 'widow', 'value': 626000.0},

        {'year': 2026, 'MARS': 'single', 'value': 256000.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 512000.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 256000.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 256000.0},
        {'year': 2026, 'MARS': 'widow', 'value': 512000.0},
    ],
    'CTC_c': [
        {'year': 2023, 'value': 2000.0},

        {'year': 2024, 'value': 2000.0},

        {'year': 2025, 'value': 2200.0},

        {'year': 2026, 'value': 2200.0},
    ],
    'ACTC_c': [
        {'year': 2023, 'value': 1600.0},

        {'year': 2024, 'value': 1700.0},

        {'year': 2025, 'value': 1700.0},

        {'year': 2026, 'value': 1700.0},
    ],
    # OTHER PARAMS THAT ARE NOT INDEXED:
    'ALD_Dependents_Child_c': LIST_SCALAR_ZERO,
    'ALD_Dependents_Elder_c': LIST_SCALAR_ZERO,
    'II_em': LIST_SCALAR_ZERO,
    'II_em_ps': LIST_MARS_INF,
    'II_credit': LIST_MARS_ZERO,
    'II_credit_ps': LIST_MARS_ZERO,
    'II_credit_nr': LIST_MARS_ZERO,
    'II_credit_nr_ps': LIST_MARS_ZERO,
    'ID_Medical_c': LIST_MARS_INF,
    'ID_StateLocalTax_c': LIST_MARS_INF,
    'ID_RealEstate_c': LIST_MARS_INF,
    'ID_InterestPaid_c': LIST_MARS_INF,
    'ID_Charity_c': LIST_MARS_INF,
    'ID_Casualty_c': LIST_MARS_INF,
    'ID_Miscellaneous_c': LIST_MARS_INF,
    'ID_ps': LIST_MARS_INF,
    'ID_c': LIST_MARS_INF,
    'CG_ec': LIST_SCALAR_ZERO,
    'PT_qbid_ps': LIST_MARS_INF,
    'RPTC_c': LIST_SCALAR_ZERO,
    'CTC_new_ps': LIST_MARS_ZERO,
    'AGI_surtax_thd': LIST_MARS_INF,
    'UBI_u18': LIST_SCALAR_ZERO,
    'UBI_1820': LIST_SCALAR_ZERO,
    'UBI_21': LIST_SCALAR_ZERO,
}
for num in range(1, 3 + 1):
    NEW_KNOWN_ITEMS[f'AMT_CG_brk{num}'] = NEW_KNOWN_ITEMS[f'CG_brk{num}']


def main():
    """
    High-level script logic.
    """
    # read existing policy_current_law.json into pdict dictionary
    fname = os.path.join('taxcalc', 'policy_current_law.json')
    with open(fname, 'r', encoding='utf-8') as jfile:
        pdict = json.load(jfile)

    # update indexed parameter values in pdict dictionary using NEW_KNOWN_ITEMS
    num_indexed_params = 0
    for pname, pinfo in pdict.items():
        if pname == 'schema':
            continue
        if not pinfo.get('indexed', False):
            continue
        num_indexed_params += 1
        if pname not in NEW_KNOWN_ITEMS:
            print(f'NO NEW_KNOWN_ITEMS FOR INDEXED PARAMETER {pname}')
            continue
        # specify plist as policy_current_law.json value list
        plist = pdict[pname]['value']
        # specify new list and its first_new_year in NEW_KNOWN_ITEMS
        newlist = NEW_KNOWN_ITEMS[pname]
        first_new_year = newlist[0]['year']
        # remove plist items for years no less than first_new_year
        while True:
            if plist[-1]['year'] >= first_new_year:
                del plist[-1]
            else:
                break  # out of while loop
        # add newlist to end of plist
        pdict[pname]['value'] = plist + newlist
    print('NUMBER OF INDEXED PARAMETERS =', num_indexed_params)

    # write updated pdict dictionary to pcl.json file
    with open('pcl.json', 'w', encoding='utf-8') as jfile:
        jfile.write(json.dumps(pdict, indent=4) + '\n')

    # return no-error exit code
    return 0
# end main function code


if __name__ == '__main__':
    sys.exit(main())
