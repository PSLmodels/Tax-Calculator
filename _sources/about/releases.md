Release history
===============
Go [here](https://github.com/PSLmodels/Tax-Calculator/pulls?q=is%3Apr+is%3Aclosed)
for a complete commit history.


2025-07-23 Release 5.1.0
------------------------
(last merged pull request is
[#2933](https://github.com/PSLmodels/Tax-Calculator/pull/2933))

**This is an enhancement release.**

**API Changes**

**New Features**
- Add `PT_qbid_limited` policy parameter and associated logic
[[#2923](https://github.com/PSLmodels/Tax-Calculator/pull/2923) by Martin Holmer]
- Refactor tax-calculation function logic to reduce model execution time
[[#2924](https://github.com/PSLmodels/Tax-Calculator/pull/2924) by Martin Holmer]
- OBBBA-enhancement PRs 2927-2933 described in [issue 2926](https://github.com/PSLmodels/Tax-Calculator/issues/2926) by Martin Holmer

**Bug Fixes**


2025-07-02 Release 5.0.0
------------------------
(last merged pull request is
[#2920](https://github.com/PSLmodels/Tax-Calculator/pull/2920))

**This is a major release with changes that make Tax-Calculator incompatible with earlier releases.**

**API Changes**
- Rename two OASDI benefit taxation policy parameters
[[#2918](https://github.com/PSLmodels/Tax-Calculator/pull/2918) by Martin Holmer]
- Remove `PT_rt?` and `PT_brk?` and four associated `PT_*` parameters
[[#2919](https://github.com/PSLmodels/Tax-Calculator/pull/2919) by Martin Holmer]
- Remove several, but not all, policy parameters that limit itemized deductions
[[#2920](https://github.com/PSLmodels/Tax-Calculator/pull/2920) by Martin Holmer]

**New Features**

**Bug Fixes**


2025-06-13 Release 4.6.3
------------------------
(last merged pull request is
[#2915](https://github.com/PSLmodels/Tax-Calculator/pull/2915))

**This is a minor enhancement release.**

**API Changes**

**New Features**
- Update CLI documentation
[[#2907](https://github.com/PSLmodels/Tax-Calculator/pull/2907) by Martin Holmer]
- Add deprecation warnings for planned Tax-Calculator 5.0.0 changes, add two tests, and remove one obsolete test
[[#2908](https://github.com/PSLmodels/Tax-Calculator/pull/2908),
 [#2909](https://github.com/PSLmodels/Tax-Calculator/pull/2909), and
 [#2910](https://github.com/PSLmodels/Tax-Calculator/pull/2910) by Martin Holmer]
- Add optional `--runid N` CLI option that simplifies output file names
[[#2912](https://github.com/PSLmodels/Tax-Calculator/pull/2912) by Martin Holmer]
- Add a default `income_group` definition to the CLI --dumpdb output
[[#2913](https://github.com/PSLmodels/Tax-Calculator/pull/2913) and
 [#2914](https://github.com/PSLmodels/Tax-Calculator/pull/2914) by Martin Holmer]
- Standardize CLI output file name extensions
[[#2915](https://github.com/PSLmodels/Tax-Calculator/pull/2915) by Martin Holmer]

**Bug Fixes**


2025-05-16 Release 4.6.2
------------------------
(last merged pull request is
[#2905](https://github.com/PSLmodels/Tax-Calculator/pull/2905))

**This is a bug-fix release.**

**API Changes**

**New Features**

**Bug Fixes**
- Work around multiple-indexing-change limitations in `parameters.py` code
[[#2904](https://github.com/PSLmodels/Tax-Calculator/pull/2904) by Martin Holmer]
- Require `paramtools` 0.20.0 that works with the current `marshmallow` 4.0.0
[[#2905](https://github.com/PSLmodels/Tax-Calculator/pull/2905) by Martin Holmer]


2025-05-09 Release 4.6.1
------------------------
(last merged pull request is
[#2900](https://github.com/PSLmodels/Tax-Calculator/pull/2900))

**This is a minor enhancement and bug-fix release.**

**API Changes**

**New Features**
- Add ability to specify compound reforms when using the CLI tool's
`--baseline` option
[[#2896](https://github.com/PSLmodels/Tax-Calculator/pull/2896) by Martin Holmer]
- Improve documentation of the `parameter_indexing_CPI_offset` policy parameter
[[#2897](https://github.com/PSLmodels/Tax-Calculator/pull/2897) by Martin Holmer]
- Add CLI `--numyears N` option that allows faster multiple-year runs with `tc`
[[#2900](https://github.com/PSLmodels/Tax-Calculator/pull/2900) by Martin Holmer]

**Bug Fixes**
- Remove redundant Parameters class property
[[#2898](https://github.com/PSLmodels/Tax-Calculator/pull/2898) by Martin Holmer]


2025-04-30 Release 4.6.0
------------------------
(last merged pull request is
[#2893](https://github.com/PSLmodels/Tax-Calculator/pull/2893))

**This is an enhancement and bug-fix release.**

**API Changes**

**New Features**
- Several enhancements to Tax-Calculator CLI program, `tc`
[PRs [#2886](https://github.com/PSLmodels/Tax-Calculator/pull/2886), [#2888](https://github.com/PSLmodels/Tax-Calculator/pull/2888), [#2889](https://github.com/PSLmodels/Tax-Calculator/pull/2889), [#2890](https://github.com/PSLmodels/Tax-Calculator/pull/2890), [#2891](https://github.com/PSLmodels/Tax-Calculator/pull/2891), and [#2893](https://github.com/PSLmodels/Tax-Calculator/pull/2893) by Martin Holmer]

**Bug Fixes**
- Update required `bokeh` version
[[#2882](https://github.com/PSLmodels/Tax-Calculator/pull/2882) by Bodi Yang]
- Make ACTC_c parameter be inflation indexed in the TCJA-extension reform
[[#2883](https://github.com/PSLmodels/Tax-Calculator/pull/2883) by Martin Holmer]
- Avoid `marshmallow` version 4.0.0 until `paramtools` is fixed
[[#2885](https://github.com/PSLmodels/Tax-Calculator/pull/2885) by Martin Holmer]


2025-03-11 Release 4.5.0
------------------------
(last merged pull request is
[#2878](https://github.com/PSLmodels/Tax-Calculator/pull/2878))

**This is an enhancement release.**

**API Changes**

**New Features**
- Updates for CBO January 2025 baseline projection
[[#2874](https://github.com/PSLmodels/Tax-Calculator/pull/2874) by Bodi Yang]
- Fixes to deprecation and code style warnings [PRs [#2876](https://github.com/PSLmodels/Tax-Calculator/pull/2876), [#2877](https://github.com/PSLmodels/Tax-Calculator/pull/2877), [#2878](https://github.com/PSLmodels/Tax-Calculator/pull/2878), by Martin Holmer]


2025-02-13 Release 4.4.1
------------------------
(last merged pull request is
[#2872](https://github.com/PSLmodels/Tax-Calculator/pull/2872))

**This is a minor enhancement release.**

**API Changes**

**New Features**
- Cosmetic code changes so that "make cstest" produces no warnings
- New tests added so that "make coverage" produces 100% code coverage
- Add c32800 to list of calc variables in records_variables.json file
[[#2872](https://github.com/PSLmodels/Tax-Calculator/pull/2872) by Martin Holmer]


2024-12-19 Release 4.4.0
------------------------
(last merged pull request is
[#2856](https://github.com/PSLmodels/Tax-Calculator/pull/2856))

**This is an enhancement release.**

**API Changes**

**New Features**
- Make a Policy object's last budget year be flexible
[[#2856](https://github.com/PSLmodels/Tax-Calculator/pull/2856) by Jason DeBacker with minor assistance from Martin Holmer]


2024-12-16 Release 4.3.5
------------------------
(last merged pull request is
[#2854](https://github.com/PSLmodels/Tax-Calculator/pull/2854))

**This is a minor enhancement and bug-fix release.**

**API Changes**

**New Features**
- Update PUF and CPS input data using CBO June 2024 baseline projection
[[#2831](https://github.com/PSLmodels/Tax-Calculator/pull/2831) by Bodi Yang]
- Generalize tmd_constructor in both Records and Policy classes
[[#2850](https://github.com/PSLmodels/Tax-Calculator/pull/2850) by Martin Holmer]
- Add changes that should have been included in PR #2831
[[#2854](https://github.com/PSLmodels/Tax-Calculator/pull/2854) by Martin Holmer]

**Bug Fixes**
- Fix several broken documentation links
[[#2847](https://github.com/PSLmodels/Tax-Calculator/pull/2847) by Martin Holmer and
[#2849](https://github.com/PSLmodels/Tax-Calculator/pull/2849) by Martin Holmer]
- Remove incorrect use of GrowFactors() in Policy and Parameters classes
[[#2852](https://github.com/PSLmodels/Tax-Calculator/pull/2852) by Martin Holmer]


2024-11-30 Release 4.3.4
------------------------
(last merged pull request is
[#2844](https://github.com/PSLmodels/Tax-Calculator/pull/2844))

**This is a bug-fix release.**

**API Changes**

**New Features**

**Bug Fixes**
- Fix deprecation warning when using pip to install an editable package
[[#2840](https://github.com/PSLmodels/Tax-Calculator/pull/2840) by Jason DeBacker]
- Fix weights precision in output file when using CLI tool with TMD input data
[[#2841](https://github.com/PSLmodels/Tax-Calculator/pull/2841) by Martin Holmer]
- Fix categorization of self-employment tax and additional Medicare tax
[[#2844](https://github.com/PSLmodels/Tax-Calculator/pull/2844) by Martin Holmer]


2024-11-14 Release 4.3.3
------------------------
(last merged pull request is
[#2837](https://github.com/PSLmodels/Tax-Calculator/pull/2837))

**This is a minor enhancement release.**

**API Changes**

**New Features**
- Clarify TCJA-after-2025 documentation
[[#2836](https://github.com/PSLmodels/Tax-Calculator/pull/2836) by Martin Holmer]
- Add known values of 2025 policy parameters
[[#2837](https://github.com/PSLmodels/Tax-Calculator/pull/2837) by Martin Holmer]


2024-11-08 Release 4.3.2
------------------------
(last merged pull request is
[#2834](https://github.com/PSLmodels/Tax-Calculator/pull/2834))

**This is a bug-fix release.**

**API Changes**

**New Features**
- Add Policy.tmd_constructor() static method for convenience when using Python API
[[#2834](https://github.com/PSLmodels/Tax-Calculator/pull/2834) by Martin Holmer]

**Bug Fixes**
- Fix handling of tmd_growfactors.csv file
[[#2832](https://github.com/PSLmodels/Tax-Calculator/pull/2832) by Martin Holmer]
- Fix `tc` reform documentation output
[[#2833](https://github.com/PSLmodels/Tax-Calculator/pull/2833) by Martin Holmer]


2024-10-28 Release 4.3.1
------------------------
(last merged pull request is
[#2828](https://github.com/PSLmodels/Tax-Calculator/pull/2828))

**This is a minor enhancement release.**

**API Changes**

**New Features**
- Remove PT_qbid_limit_switch parameter and it's assocated False code
[[#2823](https://github.com/PSLmodels/Tax-Calculator/pull/2823) by Martin Holmer]
- Add checking of Python version to the CLI tool, tc
[[#2827](https://github.com/PSLmodels/Tax-Calculator/pull/2827) by Martin Holmer]
- Add weights_scale attribute to the Records and Data classes
[[#2828](https://github.com/PSLmodels/Tax-Calculator/pull/2828) by Martin Holmer]


2024-10-02 Release 4.3.0
------------------------
(last merged pull request is
[#2819](https://github.com/PSLmodels/Tax-Calculator/pull/2819))

**This is an enhancement and bug-fix release.**

**API Changes**

**New Features**
- Add known values of inflation-indexed policy parameters for 2023 [[#2806](https://github.com/PSLmodels/Tax-Calculator/pull/2806) by Martin Holmer]
- Enhance `Records.tmd_constructor` static method [[#2809](https://github.com/PSLmodels/Tax-Calculator/pull/2809) by Martin Holmer]
- Remove TMD data files from Tax-Calculator repository [[#2810](https://github.com/PSLmodels/Tax-Calculator/pull/2810) by Martin Holmer]
- Add known values of inflation-indexed policy parameters for 2024 [[#2816](https://github.com/PSLmodels/Tax-Calculator/pull/2816) by Martin Holmer]
- Enhance `extend_tcja.py` and update `reforms/ext.json` [[#2817](https://github.com/PSLmodels/Tax-Calculator/pull/2817) by Martin Holmer]
- Enhance `ppp.py` script [[#2819](https://github.com/PSLmodels/Tax-Calculator/pull/2819) by Martin Holmer]

**Bug Fixes**
- Fix specification of domestic production deduction under TCJA [[#2807](https://github.com/PSLmodels/Tax-Calculator/pull/2807) by Martin Holmer]
- Fix `ALD_BusinessLosses_c` parameter values after 2025 [[#2818](https://github.com/PSLmodels/Tax-Calculator/pull/2818) by Martin Holmer]


2024-09-14 Release 4.2.2
------------------------
(last merged pull request is
[#2801](https://github.com/PSLmodels/Tax-Calculator/pull/2801))

**This is a bug-fix release.**

**API Changes**

**New Features**
- Non-substantive, cosmetic changes to `policy_current_law.json` file [[#2791](https://github.com/PSLmodels/Tax-Calculator/pull/2791) by Martin Holmer]
- Update `tmd_growfactors.csv` and `tmd_weights.csv.gz` files [[#2797](https://github.com/PSLmodels/Tax-Calculator/pull/2797) by Martin Holmer]

**Bug Fixes**
- Add missing pre-2022 values for indexed policy parameters [[#2789](https://github.com/PSLmodels/Tax-Calculator/pull/2789) by Martin Holmer]
- Fix education tax credit phase-out parameters [[#2790](https://github.com/PSLmodels/Tax-Calculator/pull/2790) by Martin Holmer]
- Several PRs with updates for dependency versions and other minor changes by Martin Holmer and Jason DeBacker


2024-07-30 Release 4.2.1
------------------------
(last merged pull request is
[#2786](https://github.com/PSLmodels/Tax-Calculator/pull/2786))

**This is a bug-fix release.**

**API Changes**

**New Features**

**Bug Fixes**
- Add custom `reforms/growfactors_ext.json` file to use in dynamic analysis of the `reforms/ext.json` extend-TCJA-beyond-2025 reform [[#2770](https://github.com/PSLmodels/Tax-Calculator/pull/2777) by Jason DeBacker]
- Fix CDCC phase-out calculations [[#2779](https://github.com/PSLmodels/Tax-Calculator/pull/2779) by Martin Holmer]
- Fix CARES charity deduction for nonitemizers [[#2781](https://github.com/PSLmodels/Tax-Calculator/pull/2781) by Martin Holmer]
- Fix four 2020 PT_rt? parameter values [[#2783](https://github.com/PSLmodels/Tax-Calculator/pull/2783) by Martin Holmer]
- Correct AMT taxable income calculation to handle QBID correctly [[#2784](https://github.com/PSLmodels/Tax-Calculator/pull/2784) by Martin Holmer]
- Fix qualified business income calculation [[#2785](https://github.com/PSLmodels/Tax-Calculator/pull/2785) by Martin Holmer]
- Add `ctc_nonrefundable` variable [[#2786](https://github.com/PSLmodels/Tax-Calculator/pull/2786) by Martin Holmer]


2024-07-21 Release 4.2.0
------------------------
(last merged pull request is
[#2774](https://github.com/PSLmodels/Tax-Calculator/pull/2774))

**This is an enhancement release.**

**API Changes**

**New Features**
- Add final Phase3 version of tmd input files [[#2774](https://github.com/PSLmodels/Tax-Calculator/pull/2774) by Martin Holmer]
- Update the `thru74` branch to include final Phase3 tmd input files [[#2755](https://github.com/PSLmodels/Tax-Calculator/pull/2755) by Martin Holmer]


2024-07-11 Release 4.1.0
------------------------
(last merged pull request is
[#2772](https://github.com/PSLmodels/Tax-Calculator/pull/2772))

**This is an enhancement and bug-fix release.**

**API Changes**

**New Features**
- Add ability to use from the Python API custom growfactors files [[#2757](https://github.com/PSLmodels/Tax-Calculator/pull/2757) and [#2771](https://github.com/PSLmodels/Tax-Calculator/pull/2771) by Martin Holmer]
- Add `tmd_growfactors.csv` file for use with the tmd.csv input file [[#2758](https://github.com/PSLmodels/Tax-Calculator/pull/2758) by Martin Holmer]
- Add ability to run Tax-Calculator under Python 3.12 [[#2763](https://github.com/PSLmodels/Tax-Calculator/pull/2763) by Martin Holmer]
- Add `ctc_total` and `ctc_refundable` output variables [[#2765](https://github.com/PSLmodels/Tax-Calculator/pull/2765) and [#2766](https://github.com/PSLmodels/Tax-Calculator/pull/2766) by Martin Holmer]
- Add exact calculation logic to the `CTC_new` function [[#2769](https://github.com/PSLmodels/Tax-Calculator/pull/2769) by Martin Holmer]

**Bug Fixes**
- Fix 2018 and 2021 EITC phase-out start parameter values [[#2768](https://github.com/PSLmodels/Tax-Calculator/pull/2768) and [#2770](https://github.com/PSLmodels/Tax-Calculator/pull/2770) by Martin Holmer]


2024-06-01 Release 4.0.0
------------------------
(last merged pull request is
[#2752](https://github.com/PSLmodels/Tax-Calculator/pull/2752))

**This is a major release with changes that make Tax-Calculator incompatible with earlier releases.**

**API Changes**
- Apply a new framework for the payroll tax policy parameters: Payroll tax parameters are split into the employer side and employee side ~ `FICA_mc_trt`, `FICA_ss_trt` are replaced by `FICA_mc_trt_employer`, `FICA_mc_trt_employee`, `FICA_ss_trt_employer` and `FICA_ss_trt_employee`. [[#2669](https://github.com/PSLmodels/Tax-Calculator/pull/2669) by Bodi Yang]
- CDCC rate scale (`CDCC_crt`, `CDCC_frt`) changed from 0~1 to 0~100. [[#2628](https://github.com/PSLmodels/Tax-Calculator/pull/2628) by Duncan Hobbs and [#2671](https://github.com/PSLmodels/Tax-Calculator/pull/2671) by Jason DeBacker]

**New Features**
- Ablility to perform payroll tax reform upon either employer side or employee side. [by Bodi Yang]


2024-05-10 Release 3.6.0
------------------------
(last merged pull request is
[#2743](https://github.com/PSLmodels/Tax-Calculator/pull/2743))

**This is an enhancement release.**

**API Changes**

**New Features**
- Add capabilites to handle `tmd*` files from the tax-microdata repository [[#2740](https://github.com/PSLmodels/Tax-Calculator/pull/2740) by Martin Holmer]
- Minor updates to documentation, testing, and environment by Martin Holmer and Jason DeBacker in various PRs

2024-04-04 Release 3.5.3
------------------------
(last merged pull request is
[#2732](https://github.com/PSLmodels/Tax-Calculator/pull/2732))

**This is an enhancement and bug-fix release.**

**API Changes**

**New Features**
- Updates `growfactors.csv` and PUF and CPS weights files for new `taxdata` reflecting the February 2024 CBO economic projections [[#2729](https://github.com/PSLmodels/Tax-Calculator/pull/2729) by Bodi Yang]
- Simplification of how tax parameters are indexed [[#2732](https://github.com/PSLmodels/Tax-Calculator/pull/2732) by Martin Holmer]

**Bug Fixes**
- Correct historical parameter values [[#2730](https://github.com/PSLmodels/Tax-Calculator/pull/2730) by Martin Holmer]


2024-03-18 Release 3.5.2
------------------------
(last merged pull request is
[#2725](https://github.com/PSLmodels/Tax-Calculator/pull/2725))

**This is an enhancement and bug-fix release.**

**API Changes**

**New Features**
- Complete works of TAXSIM-35 validation, in several PRS by Bodi Yang and Jason DeBacker

**Bug Fixes**
- Fix bugs in `ppp.py` script  [[#2725](https://github.com/PSLmodels/Tax-Calculator/pull/2725) by Martin Holmer]

2024-02-27 Release 3.5.1
------------------------
(last merged pull request is
[#2722](https://github.com/PSLmodels/Tax-Calculator/pull/2722))

**This is an enhancement and bug-fix release.**

**API Changes**

**New Features**


**Bug Fixes**
- Includes `paramtools` in required packages for installation [[#2721](https://github.com/PSLmodels/Tax-Calculator/pull/2721) by Jason DeBacker]



2024-02-10 Release 3.5.0
------------------------
(last merged pull request is
[#2715](https://github.com/PSLmodels/Tax-Calculator/pull/2715))

**This is an enhancement and bug-fix release.**

**API Changes**

**New Features**
- Add baseline table output to `cli` command [[#2714](https://github.com/PSLmodels/Tax-Calculator/pull/2714) by Martin Holmer]
- Additional TAXSIM-35 validation tools, several PRS by Bodi Yang and Jason DeBacker

**Bug Fixes**
- Avoid Pandas deprecation warnings[[#2715](https://github.com/PSLmodels/Tax-Calculator/pull/2785) by Martin Holmer]
- Correctly account for the `odc` variable as refundable in 2021 [[#2703](https://github.com/PSLmodels/Tax-Calculator/pull/2704) by Bodi Yang]
- Fix incorrect value for `EITC_ps_MarriedJ` in 2020 [[#2699](https://github.com/PSLmodels/Tax-Calculator/pull/2699) by Bodi Yang]
- Fix incorrect value for ACTC amount for 2023-2025 to reflect inflation adjustment [[#2691](https://github.com/PSLmodels/Tax-Calculator/pull/2691) by Jason DeBacker]



2023-06-20 Release 3.4.1
------------------------
(last merged pull request is
[#2686](https://github.com/PSLmodels/Tax-Calculator/pull/2686))

**This is an enhancement and bug-fix release.**

**API Changes**

**New Features**
- Update documentation of use cases [[#2686](https://github.com/PSLmodels/Tax-Calculator/pull/2686) by Jason Debacker]
- Update the last budget year to 2033 ~ also extend the projections to 2033 [[#2682](https://github.com/PSLmodels/Tax-Calculator/pull/2682) by Bodi Yang]

**Bug Fixes**
- Reweight PUF data for the year 2033, to fix the odd PUF weightings, PUF ratios and odd projections [[#2685](https://github.com/PSLmodels/Tax-Calculator/pull/2685) by Bodi Yang], with primary work in [[TaxData PR #429](https://github.com/PSLmodels/taxdata/pull/429)by Bodi Yang]
- Fix incorrect value for EITC_c in 2020 [[#2684](https://github.com/PSLmodels/Tax-Calculator/pull/2684) by Matt Jensen]


2023-05-05 Release 3.4.0
------------------------
(last merged pull request is
[#2677](https://github.com/PSLmodels/Tax-Calculator/pull/2677))

**This is an enhancement and bug-fix release.**

**API Changes**

**New Features**
- Tax-Calculator baseline update for CBO economic projections, published in May, "The Budget and Economic Outlook: 2023 to 2033" [[#2676](https://github.com/PSLmodels/Tax-Calculator/pull/2676) by Bodi Yang], with primary work in [[TaxData PR #421](https://github.com/PSLmodels/taxdata/pull/421)by Bodi Yang]

**Bug Fixes**
- Replacement of the deprecated Pandas `.append()` method in the model [[#2676](https://github.com/PSLmodels/Tax-Calculator/pull/2676) by Bodi Yang]
- Fix calculaton of 2021 child and other dependent credit [[#2677](https://github.com/PSLmodels/Tax-Calculator/pull/2677) by Matt Jensen]
- Fix exemption of UI from AGI for EITC in certain years [[#2675](https://github.com/PSLmodels/Tax-Calculator/pull/2675) by Jason Debacker]
- Fix incorrect value for max EITC in 2022 [[#2673](https://github.com/PSLmodels/Tax-Calculator/pull/2673) by Jason Debacker]

2022-12-16 Release 3.3.0
------------------------
(last merged pull request is
[#2662](https://github.com/PSLmodels/Tax-Calculator/pull/2662))

**This is an enhancement and bug-fix release.**

**API Changes**

**New Features**
- Tax-Calculator baseline update for CBO economic projections, published in May, "The Budget and Economic Outlook: 2022 to 2032" [[#2662](https://github.com/PSLmodels/Tax-Calculator/pull/2662) by Bodi Yang], with primary work in [[TaxData PR #412](https://github.com/PSLmodels/taxdata/pull/412)by Bodi Yang]
- Add parameters for threshold for self-employment income exempt from SECA taxes [[#2659](https://github.com/PSLmodels/Tax-Calculator/pull/2659) by Jason Debacker]
- Update calculation of child number when CTC_include17 [[#2644](https://github.com/PSLmodels/Tax-Calculator/pull/2644) by Matt Jensen]
- Add Python 3.10 to test matrix [[#2646](https://github.com/PSLmodels/Tax-Calculator/pull/2646) by Jason Debacker]
- Inflation adjustment of the year 2020, 2021, 2022, for IRS tax forms and tax law inflation adjustments documents [[#2633](https://github.com/PSLmodels/Tax-Calculator/pull/2633) by Bodi Yang]

**Bug Fixes**
- Fix Parameter error parsing in taxcalcio module [[#2625](https://github.com/PSLmodels/Tax-Calculator/pull/2625/commits) by Hank Doupe]

2021-08-06 Release 3.2.1
------------------------
(last merged pull request is
[#2615](https://github.com/PSLmodels/Tax-Calculator/pull/2615))

**This is bug-fix release.**

**API Changes**

**New Features**

**Bug Fixes**
Correct an error in the value of the `CTC_new_c_under6_bonus` for the year 2021. [[#2609](https://github.com/PSLmodels/Tax-Calculator/pull/2609) by Jason DeBacker]


2021-07-17 Release 3.2.0
------------------------
(last merged pull request is
[#2604](https://github.com/PSLmodels/Tax-Calculator/pull/2604))

**This is an enhancement and bug-fix release.**

**API Changes**

**New Features**
- Updates the current law baseline to include the CARES Act (#2586), the the Consolidated Appropriations Act of 2021, and the American Rescue Plan Act, (PRs #2573 and #2588), and the Consolidated Appropriations Act of 2021 (PR #2593) as well as updates to EITC parameters (PR #2593). This ends a transition period for users to model these changes as reforms to the former baseline. [[#2586](https://github.com/PSLmodels/tax-calculator/pull/2586), [#2593](https://github.com/PSLmodels/tax-calculator/pull/2593), [#2573](https://github.com/PSLmodels/tax-calculator/pull/2573), [#2588](https://github.com/PSLmodels/tax-calculator/pull/2588), [#2593](https://github.com/PSLmodels/tax-calculator/pull/2593) with contributions from Angela Shoulders, Cody Kallen, Matt Jensen, and Jason DeBacker]
- Updates growfactors and weights for the PUF and CPS data to reflect updates to `taxdata`, including new CBO forecasts. [[#2599](https://github.com/PSLmodels/tax-calculator/pull/2599) by Anderson Frailey]
- Add profiling to testing [[#2570](https://github.com/PSLmodels/tax-calculator/pull/2570), [#2577](https://github.com/PSLmodels/tax-calculator/pull/2577), [#2587](https://github.com/PSLmodels/tax-calculator/pull/2587) by Jacob Chuslo]
- Allow for non-taxed UI eligibility. [[#2579](https://github.com/PSLmodels/tax-calculator/pull/2579) by Max Ghenis]
- Additional unit tests for `calcfunctions.py`. [[#2572](https://github.com/PSLmodels/tax-calculator/pull/2572) by Angela Shoulders]

**Bug Fixes**


2021-03-01 Release 3.1.0
------------------------
(last merged pull request is
[#2566](https://github.com/PSLmodels/Tax-Calculator/pull/2566))

**This is an enhancement and bug-fix release.**

**API Changes**

**New Features**
- Package for Python 3.9. [[#2522](https://github.com/PSLmodels/tax-calculator/pull/2522) by Max Ghenis]
- Parameters for QBI deduction phaseout. [[#2508](https://github.com/PSLmodels/tax-calculator/pull/2508) by Peter Metz]
- Switch for QBI deduction wage and capital limitations. [[#2497(https://github.com/PSLmodels/tax-calculator/pull/2497) by Peter Metz]
- Interaction with `calcfunctions.py` functions and unit tests without `@jit` decorator. [[#2515](https://github.com/PSLmodels/tax-calculator/pull/2515) by Jacob Chuslo]

**Bug Fixes**
- Fix default parameter value for deduction for blind and aged widowed taxpayers. [[#2537](https://github.com/PSLmodels/tax-calculator/pull/2537) by Jacob Chuslo, reported by Jason DeBacker]
- Include self-employment tax in calculation of partnership-specific marginal tax rates. [[#2486](https://github.com/PSLmodels/tax-calculator/pull/2486) by Cody Kallen]
- Fix stacking of an optional capital gains tax bracket. [[#2500](https://github.com/PSLmodels/tax-calculator/pull/2500) by Peter Metz]
- Fix bug caused by adjusting the indexed status of a parameter while also adjusting the parameter's value and a related parameter's value. [[#2532](https://github.com/PSLmodels/tax-calculator/pull/2532) by Hank Doupe]

2020-08-24 Release 3.0.0
------------------------
(last merged pull request is
[#2474](https://github.com/PSLmodels/Tax-Calculator/pull/2474))

**This is a major release with changes that make Tax-Calculator incompatible with earlier releases.**

**API Changes**
- Adopt the [ParamTools library](https://github.com/PSLmodels/ParamTools) for parameter processing and validation, allowing easier integration with other projects that rely on ParamTools, less code for the Tax-Calculator project to maintain, and other benefits for Tax-Calculator users. Backwards compatibiltiy was maintained except for a minor API change: The parameter values that are accessible as instance attributes (e.g. pol.II_em) are not casted down into a lower dimension. So, if the year is 2017, then pol.II_em returns [4050.0] instead of 4050.0. [[#2401](https://github.com/PSLmodels/Tax-Calculator/pull/2401) by Hank Doupe]
- CPI_offset was replaced by parameter_indexing_CPI_offset, which has slightly different behavior: When parameter_indexing_CPI_offset is specified in a reform, that value is no longer added to the existing parameter_indexing_CPI_offset as was the case with CPI_offset. Rather, the specified value becomes the offset from the baseline unchained CPI. This new behavior is consistent with what is expected from all other Tax-Calculator parameters. [[#2413](https://github.com/PSLmodels/Tax-Calculator/pull/2413) by Peter Metz]
- Replace the variable reporting the number of dependents under 5 years old (nu05) with the number under 6 years old (nu06) to support recent policy proposals. [[#2443](https://github.com/PSLmodels/Tax-Calculator/pull/2443) by Peter Metz, with primary work in [TaxData PR #329](https://github.com/PSLmodels/taxdata/pull/329) by Anderson Frailey]
- Remove the changes.md file to consolidate version reporting in this file, releases.md. [[#2474](https://github.com/PSLmodels/Tax-Calculator/pull/2474) by Matt Jensen]

**New Features**
- Enable Windows users to convert TAXSIM input files to the interface required by Tax-Calculator's tc Command Line Interface by replacing validation script taxcalc.sh with taxcalc.py [[#2408](https://github.com/PSLmodels/Tax-Calculator/pull/2408) by Peter Metz based on feedback from Ernie Tedeschi]
- Add automated testing for Python 3.8 to ensure a bug-free experience for users on the latest version of Python. [[#2414](https://github.com/PSLmodels/Tax-Calculator/pull/2414) by Hank Doupe]
- Include UBI amounts, when introduced by user reforms, to variables that report total benefits. [[#2418](https://github.com/PSLmodels/Tax-Calculator/pull/2418) by Jason DeBacker]
- Improve [documentation site](https://pslmodels.github.io/Tax-Calculator/) with [Jupyter Book](https://jupyterbook.org/intro.html) [[#2420](https://github.com/PSLmodels/Tax-Calculator/pull/2420) by Max Ghenis with auxiliary PRs by Jason DeBacker]
- Add documentation for the Tax-Calculator API to the docs site. [[#2441](https://github.com/PSLmodels/Tax-Calculator/pull/2441) by Jason DeBacker]
- Add documentation for Tax-Calculator parameters to the docs site. [[#2450](https://github.com/PSLmodels/Tax-Calculator/pull/2450) by Hank Doupe]
- Port from SAS to Python the creation of the CPS tax unit file that is packaged with Tax-Calculator. [[#2444](https://github.com/PSLmodels/Tax-Calculator/pull/2444) by Peter Metz, with primary work in [TaxData PR #314](https://github.com/PSLmodels/taxdata/pull/314) by Anderson Frailey]
- Update the Tax-Calculator baseline for the CBO's July 2 report, "An Update to the Economic Outlook: 2020-2030." [[#2462](https://github.com/PSLmodels/Tax-Calculator/pull/2462) by Peter Metz, with primary work in [TaxData PR #332](https://github.com/PSLmodels/taxdata/pull/314) by Jacob Chuslo]

**Bug Fixes**
- Adjustments to the CPI_offset set under current law previously  overwrite the scheduled expiration of TCJA tax cut for parameters that are inflation indexed. The adoption of the new parameter_indexing_CPI_offset fixes this bug. We are unware of any users encountering this issue. [[#2413](https://github.com/PSLmodels/Tax-Calculator/pull/2413) by Peter Metz]

2020-03-18 Release 2.9.0
------------------------
(last merged pull request is
[#2405](https://github.com/PSLmodels/Tax-Calculator/pull/2405))

**This is an enhancement and bug-fix release.**

**API Changes**
- None

**New Features**
- Update to January 2020 CBO economic projections [[#2403](https://github.com/PSLmodels/Tax-Calculator/pull/2403) by Peter Metz]

**Bug Fixes**
- Reinstate personal exemption phaseout (PEP) in 2026 [[#2402](https://github.com/PSLmodels/Tax-Calculator/pull/2402)
  by Peter Metz and identified by Peter Metz]

2020-02-28 Release 2.8.0
------------------------
(last merged pull request is
[#2400](https://github.com/PSLmodels/Tax-Calculator/pull/2400))

**This is an enhancement release.**

**API Changes**
- None

**New Features**
- Allows users a greater range when modifying input data with Tax-Calculator's growdiff capabilities [[#2397](https://github.com/PSLmodels/Tax-Calculator/pull/2397) by Peter Metz]
- Update 2019 policy parameters with IRS published values [[#2399](https://github.com/PSLmodels/Tax-Calculator/pull/2399)
  by Peter Metz]

**Bug Fixes**
-None

2019-12-13 Release 2.7.0
------------------------
(last merged pull request is
[#2395](https://github.com/PSLmodels/Tax-Calculator/pull/2395))

**This is an enhancement and bug-fix release.**

**API Changes**
- None

**New Features**
- Versioning improved to facilitate pip installation [[#2390](https://github.com/PSLmodels/Tax-Calculator/pull/2390)
  by Matt Jensen as requested by Max Ghenis]
- New notification and documentation about when data extrapolation are not conducted by Tax-Calculator on startup [[#2394](https://github.com/PSLmodels/Tax-Calculator/pull/2394) by Matt Jensen as requested by Don Boyd]

**Bug Fixes**

- Fix for CPI_offsets when applied in 2018 and later [[#2381](https://github.com/PSLmodels/Tax-Calculator/pull/2381)
  by Hank Doupe, who also identified the bug]
- Ceiling on SALT taxes no longer incorrectly indexed for inflation [[#2388](https://github.com/PSLmodels/Tax-Calculator/pull/2388)
  by Max Ghenis with bug reported by Tyler Evilsizer]

2019-10-31 Release 2.6.0
------------------------
(last merged pull request is
[#2379](https://github.com/PSLmodels/Tax-Calculator/pull/2379))

**This is an enhancement release.**

**API Changes**
- None

**New Features**
- Add a version of recipe04 for Pandas users [[#2373](https://github.com/PSLmodels/Tax-Calculator/pull/2373)
  by Max Ghenis]

**Bug Fixes**
- None

2019-08-06 Release 2.5.0
------------------------
(last merged pull request is
[#2370](https://github.com/PSLmodels/Tax-Calculator/pull/2370))

**This is an enhancement and bug-fix release.**

**API Changes**
- None

**New Features**
- Add to the income tax a refundable payroll tax credit (RPTC) that can be used to emulate a payroll tax exemption
  [[#2366](https://github.com/PSLmodels/Tax-Calculator/pull/2366)
  by Peter Metz, Matt Jensen and Martin Holmer]

**Bug Fixes**
- Allow reforms that specify a `CPI_offset` change in the same year as a tax policy parameter's indexing status is changed
  [[#2364](https://github.com/PSLmodels/Tax-Calculator/pull/2364)
  by Anderson Frailey]


2019-06-28 Release 2.4.2
------------------------
(last merged pull request is
[#2352](https://github.com/PSLmodels/Tax-Calculator/pull/2352))

**This is a bug-fix release.**

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Add farm income to qualified business income
  [[#2352](https://github.com/PSLmodels/Tax-Calculator/pull/2352)
  by Martin Holmer]


2019-06-26 Release 2.4.1
------------------------
(last merged pull request is
[#2348](https://github.com/PSLmodels/Tax-Calculator/pull/2348))

**This is a bug-fix release.**

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Add taxable-income cap to qualified business income deduction logic
  [[#2348](https://github.com/PSLmodels/Tax-Calculator/pull/2348)
  by Martin Holmer]


2019-06-25 Release 2.4.0
------------------------
(last merged pull request is
[#2345](https://github.com/PSLmodels/Tax-Calculator/pull/2345))

**This is an enhancement release.**

**API Changes**
- None

**New Features**
- Improve calculation of qualified business income deduction
  [[#2345](https://github.com/PSLmodels/Tax-Calculator/pull/2345)
  by Martin Holmer]

**Bug Fixes**
- None


2019-06-08 Release 2.3.0
------------------------
(last merged pull request is
[#2337](https://github.com/PSLmodels/Tax-Calculator/pull/2337))

**This is an enhancement release.**

**API Changes**
- None

**New Features**
- Redo validation tests using newest version of TAXSIM-27
  [[#2336](https://github.com/PSLmodels/Tax-Calculator/pull/2336)
  by Martin Holmer with assistance from Dan Feenberg]
- Simplify Records class internal logic by adding generic Data class
  [[#2337](https://github.com/PSLmodels/Tax-Calculator/pull/2337)
  by Martin Holmer based on ideas from Cody Kallen]

**Bug Fixes**
- None


2019-05-20 Release 2.2.0
------------------------
(last merged pull request is
[#2327](https://github.com/PSLmodels/Tax-Calculator/pull/2327))

**This is an enhancement and bug-fix release.**

**API Changes**
- None

**New Features**
- Add "Redefining Expanded Income" cookbook recipe
  [[#2321](https://github.com/PSLmodels/Tax-Calculator/pull/2321)
  by Martin Holmer responding to request by Max Ghenis]
- Add option to specify table and graph quantiles that have equal numbers of people (rather than filing units)
  [[#2322](https://github.com/PSLmodels/Tax-Calculator/pull/2322)
  by Martin Holmer responding to request by Max Ghenis]
- Add "Analyzing a Non-Parametric Reform" cookbook recipe
  [[#2327](https://github.com/PSLmodels/Tax-Calculator/pull/2327)
  by Martin Holmer]

**Bug Fixes**
- Correct treatment of tuition and fees deduction in 2018 and subsequent years
  [[#2319](https://github.com/PSLmodels/Tax-Calculator/pull/2319)
  by Anderson Frailey with bug reported by Alan Viard and Erin Melly]


2019-05-09 Release 2.1.0
------------------------
(last merged pull request is
[#2316](https://github.com/PSLmodels/Tax-Calculator/pull/2316))

**This is an enhancement release.**

**API Changes**
- None

**New Features**
- Provide option to specify simpler JSON reform files
  [[#2312](https://github.com/PSLmodels/Tax-Calculator/pull/2312)
  by Martin Holmer]
- Streamline GrowDiff.apply_to and Records._extrapolate code
  [[#2314](https://github.com/PSLmodels/Tax-Calculator/pull/2314)
  by Martin Holmer]
- Reorganize Tax-Calculator documentation
  [[#2315](https://github.com/PSLmodels/Tax-Calculator/pull/2315)
  by Martin Holmer]

**Bug Fixes**
- None


2019-04-17 Release 2.0.1
------------------------
(last merged pull request is
[#2306](https://github.com/PSLmodels/Tax-Calculator/pull/2306))

**This is a bug-fix release.**

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Fix minor flaw in definition of EITC investment income
  [[#2306](https://github.com/PSLmodels/Tax-Calculator/pull/2306)
  by Martin Holmer]


2019-04-15 Release 2.0.0
------------------------
(last merged pull request is
[#2297](https://github.com/PSLmodels/Tax-Calculator/pull/2297))

**This is a major release with changes that make Tax-Calculator incompatible with earlier releases.**

Read [this document](UPGRADING.md#upgrading-to-tax-calculator-20) to understand what you need to do before using Tax-Calculator 2.0.

**API Changes**
- Simplify and standardize the way that policy reforms (and assumption changes) are specified in both JSON files and Python dictionaies
  [[#2292](https://github.com/PSLmodels/Tax-Calculator/pull/2292)
  by Martin Holmer]

**New Features**
- Revise Tax-Calculator versus TASIM-27 validation test logic
  [[#2278](https://github.com/PSLmodels/Tax-Calculator/pull/2278)
  by Martin Holmer]
- Update Tax-Calculator versus TASIM-27 validation test results
  [[#2279](https://github.com/PSLmodels/Tax-Calculator/pull/2279)
  by Martin Holmer]

**Bug Fixes**
- Fix Windows-related bug in `docs/cookbook/test_recipes.py` that generated FAIL messages when there were only whitespace differences
  [[#2280](https://github.com/PSLmodels/Tax-Calculator/pull/2280)
  by Martin Holmer with bug reported by Robert Orr and fix tested on Windows by Duncan Hobbs]


2019-03-24 Release 1.2.0
------------------------
(last merged pull request is
[#2269](https://github.com/PSLmodels/Tax-Calculator/pull/2269))

**This is an enhancement and bug-fix release.**

**API Changes**
- None

**New Features**
- Add JSON reform file for tax provisions in Sanders-DeFazio "Social Security Expansion Act"
  [[#2266](https://github.com/PSLmodels/Tax-Calculator/pull/2266)
  by Duncan Hobbs]
- Add ability to handle larger values of integer parameters in Parameter class
  [[#2269](https://github.com/PSLmodels/Tax-Calculator/pull/2269)
  by Martin Holmer]

**Bug Fixes**
- Fix minor bugs related to the `_SS_Earnings_thd` policy parameter added in [#2222](https://github.com/PSLmodels/Tax-Calculator/pull/2222)
  [[#2267](https://github.com/PSLmodels/Tax-Calculator/pull/2267)
  by Martin Holmer]


2019-03-17 Release 1.1.0
------------------------
(last merged pull request is
[#2261](https://github.com/PSLmodels/Tax-Calculator/pull/2261))

**This is an enhancement release.**

**API Changes**
- None

**New Features**
- Provide more flexibility in specifying structural EITC reforms that make the credit more individualized
  [[#2254](https://github.com/PSLmodels/Tax-Calculator/pull/2254)
  by Matt Jensen]
- Use new data input files from [taxdata pull request 307](https://github.com/PSLmodels/taxdata/pull/307#issue-257784078) that are generated using January 2019 CBO economic projection; extend budget years through 2029
  [[#2255](https://github.com/PSLmodels/Tax-Calculator/pull/2255)
  by Martin Holmer using data files produced by Anderson Frailey]
- Add error messages that stop use of file names (or strings beginning with 'http') in `Calculator.read_json_param_objects` method that do not end in '.json'
  [[#2261](https://github.com/PSLmodels/Tax-Calculator/pull/2261)
  by Martin Holmer based on report by Max Ghenis]

**Bug Fixes**
- None


2019-02-26 Release 1.0.1
------------------------
(last merged pull request is
[#2243](https://github.com/PSLmodels/Tax-Calculator/pull/2243))

**This is a bug-fix release.**

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Make the six components of total itemized deductions add up to pre-limitation total itemized deductions
  [[#2243](https://github.com/PSLmodels/Tax-Calculator/pull/2243)
  by Martin Holmer with bug reported by Erin Melly]


2019-02-22 Release 1.0.0
------------------------
(last merged pull request is
[#2241](https://github.com/PSLmodels/Tax-Calculator/pull/2241))

**This is a major release with changes that make Tax-Calculator
incompatible with earlier releases.**

**API Changes**
- Remove from Tax-Calculator the Behavior class; same capabilities now in Behavioral-Responses
  [[#2182](https://github.com/PSLmodels/Tax-Calculator/pull/2182)
  by Martin Holmer]
- Redefine the meaning of the `_CTC_c` policy parameter and remove five old reform parameters that are incompatible with current law
  [[#2223](https://github.com/PSLmodels/Tax-Calculator/pull/2223)
  by Martin Holmer with the assistance of Cody Kallen]
- Remove from Tax-Calculator the `quantity_response` function, which is now in Behavioral-Responses
  [[#2233](https://github.com/PSLmodels/Tax-Calculator/pull/2233)
  by Martin Holmer]

**New Features**
- Add `ppp.py` developer-only script and create FAQ issue #2183 to describe its use
  [[#2181](https://github.com/PSLmodels/Tax-Calculator/pull/2181)
  by Martin Holmer]
- Move read-the-docs documentation into several Tax-Calculator/*.md files
  [[#2184](https://github.com/PSLmodels/Tax-Calculator/pull/2184)
  by Martin Holmer]
- Incorporate slightly different CPS and PUF input data files
  [[#2185](https://github.com/PSLmodels/Tax-Calculator/pull/2185)
  by Martin Holmer with data from Anderson Frailey], which requires new `puf.csv` input file (see [taxdata pull request 296](https://github.com/PSLmodels/taxdata/pull/296) for details) with this information:
  * Byte size: 56415704
  * MD5 checksum: 4aa15435c319bf5e4d3427faf52384c0
- Add new data files generated in [taxdata pull request 297](https://github.com/PSLmodels/taxdata/pull/297) using the August-2018 CBO ten-year projection
  [[#2196](https://github.com/PSLmodels/Tax-Calculator/pull/2196)
  by Martin Holmer with data from Anderson Frailey]
- Add actual 2018 values for all policy parameters
  [[#2212](https://github.com/PSLmodels/Tax-Calculator/pull/2212)
  by Peter Metz]
- Revise specification of `2017_law.json` and `TCJA.json` reform files to work when last known parameter values are for 2018
  [[#2218](https://github.com/PSLmodels/Tax-Calculator/pull/2218)
  by Martin Holmer]
- Add policy parameter that allows specification of the payroll tax aspects of the Larson "Social Security 2100 Act"
  [[#2222](https://github.com/PSLmodels/Tax-Calculator/pull/2222)
  by Anderson Frailey]

**Bug Fixes**
- Fix negative/zero/positive split of bottom decile in distribution and difference tables
  [[#2192](https://github.com/PSLmodels/Tax-Calculator/pull/2192)
  by Martin Holmer]
- Fix CTC+ODC logic for 2018+
  [[#2211](https://github.com/PSLmodels/Tax-Calculator/pull/2211)
   [#2205](https://github.com/PSLmodels/Tax-Calculator/pull/2205)
  by Martin Holmer with need pointed out by Peter Metz]


2018-12-14 Release 0.24.0
-------------------------
(last merged pull request is
[#2176](https://github.com/PSLmodels/Tax-Calculator/pull/2176))

**API Changes**
- None

**New Features**
- Make taxcalc packages available for Python 3.7 as well as for Python 3.6
  [[#2176](https://github.com/PSLmodels/Tax-Calculator/pull/2176)
  by Martin Holmer]

**Bug Fixes**
- None


2018-12-13 Release 0.23.4
-------------------------
(last merged pull request is
[#2170](https://github.com/PSLmodels/Tax-Calculator/pull/2170))

**API Changes**
- None

**New Features**
- Add new EITC policy parameter to aid in [validation work](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/validation/taxsim/README.md#validation-of-tax-calculator-against-internet-taxsim-version-27)
  [[#2164](https://github.com/PSLmodels/Tax-Calculator/pull/2164)
  by Martin Holmer]

**Bug Fixes**
- Fix obscure bug regarding rules for determining eligibility for the child AMT exemption that was discovered during [validation work](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/validation/taxsim/README.md#validation-of-tax-calculator-against-internet-taxsim-version-27)
  [[#2162](https://github.com/PSLmodels/Tax-Calculator/pull/2162)
  by Martin Holmer]


2018-12-05 Release 0.23.3
-------------------------
(last merged pull request is
[#2150](https://github.com/PSLmodels/Tax-Calculator/pull/2150))

**API Changes**
- None

**New Features**
- Revise taxcalc/validation/taxsim logic to work with new TAXSIM version 27
  [[#2140](https://github.com/PSLmodels/Tax-Calculator/pull/2140)
  by Martin Holmer]
- Use `tc --dump` in validation work, which allows removal of `simtax.py` and its class and tests
  [[#2142](https://github.com/PSLmodels/Tax-Calculator/pull/2142)
  by Martin Holmer]
- Add test to Makefile that detects previously undetected bugs in `calcfunctions.py`
  [[#2144](https://github.com/PSLmodels/Tax-Calculator/pull/2144)
  by Martin Holmer]
- Eliminate Tax-Calculator dependency on the `toolz` package
  [[#2148](https://github.com/PSLmodels/Tax-Calculator/pull/2148)
  by Martin Holmer]

**Bug Fixes**
- Change the age range for those using the special child AMT-exemption rules
  [[#2141](https://github.com/PSLmodels/Tax-Calculator/pull/2141)
  by Martin Holmer]


2018-11-22 Release 0.23.2
-------------------------
(last merged pull request is
[#2126](https://github.com/PSLmodels/Tax-Calculator/pull/2126))

**API Changes**
- None

**New Features**
- Refactor `create_diagnostic_table` utility function to work better when using the Behavioral-Repsonses `behresp` package
  [[#2126](https://github.com/PSLmodels/Tax-Calculator/pull/2126)
  by Martin Holmer responding to question from Ernie Tedeschi]

**Bug Fixes**
- None


2018-11-20 Release 0.23.1
-------------------------
(last merged pull request is
[#2123](https://github.com/PSLmodels/Tax-Calculator/pull/2123))

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Replace buggy Parameters.default_data() with Policy.metadata() method
  [[#2119](https://github.com/PSLmodels/Tax-Calculator/pull/2119)
  by Martin Holmer with bug reported by Hank Doupe]
- Add ability to pass Pandas DataFrame as the `adjust_ratios` argument to Records class constructor
  [[#2121](https://github.com/PSLmodels/Tax-Calculator/pull/2121)
  by Martin Holmer with bug reported by Anderson Frailey]
- Revise cookbook recipe 1 to show easier way to access reform files on website
  [[#2122](https://github.com/PSLmodels/Tax-Calculator/pull/2122)
  by Martin Holmer]


2018-11-13 Release 0.23.0
-------------------------
(last merged pull request is
[#2111](https://github.com/PSLmodels/Tax-Calculator/pull/2111))

**API Changes**
- Remove confusing `filer` variable from list of usable input variables
  [[#2102](https://github.com/PSLmodels/Tax-Calculator/pull/2102)
  by Martin Holmer]
- Remove useless `start_year` and `num_years` arguments of constructor for the Policy, Consumption, and GrowDiff classes
  [[#2103](https://github.com/PSLmodels/Tax-Calculator/pull/2103)
  by Martin Holmer]
- Add deprecated warning to Behavior class constructor and documentation because Behavior class will be removed from Tax-Calculator in a future release
  [[#2105](https://github.com/PSLmodels/Tax-Calculator/pull/2105)
  by Martin Holmer]
- Remove `versioneer.py` and `taxcalc/_version.py` and related code now that Package-Builder is handling version specification
  [[#2111](https://github.com/PSLmodels/Tax-Calculator/pull/2111)
  by Martin Holmer]

**New Features**
- Revise cookbook recipe 2 to show use of new Behavioral-Responses behresp package as alternative to deprecated Behavior class
  [[#2107](https://github.com/PSLmodels/Tax-Calculator/pull/2107)
  by Martin Holmer]

**Bug Fixes**
- None


2018-10-26 Release 0.22.2
-------------------------
(last merged pull request is
[#2094](https://github.com/PSLmodels/Tax-Calculator/pull/2094))

**API Changes**
- None

**New Features**
- Add _EITC_basic_frac policy parameter so that an Earned and Basic Income Tax Credit (EBITC) reform can be analyzed
  [[#2094](https://github.com/PSLmodels/Tax-Calculator/pull/2094)
  by Martin Holmer]

**Bug Fixes**
- None


2018-10-25 Release 0.22.1
-------------------------
(last merged pull request is
[#2091](https://github.com/PSLmodels/Tax-Calculator/pull/2091))

**API Changes**
- None

**New Features**
- Add Records.read_cps_data static method to make it easier to test other models in the Policy Simulation Library collection of USA tax models
  [[#2090](https://github.com/PSLmodels/Tax-Calculator/pull/2090)
  by Martin Holmer]

**Bug Fixes**
- None


2018-10-24 Release 0.22.0
-------------------------
(last merged pull request is
[#2087](https://github.com/PSLmodels/Tax-Calculator/pull/2087))

**API Changes**
- Refactor `tbi` functions so that other models in the Policy Simulation Library (PSL) collection of USA tax models can easily produce the tables expected by TaxBrain
  [[#2087](https://github.com/PSLmodels/Tax-Calculator/pull/2087)
  by Martin Holmer]

**New Features**
- Add more detailed pull-request work-flow documentation
  [[#2071](https://github.com/PSLmodels/Tax-Calculator/pull/2071)
  by Martin Holmer]
- Add Travis-CI-build badge to `README.md` file
  [[#2078](https://github.com/PSLmodels/Tax-Calculator/pull/2078)
  by Philipp Kats]
- Add ability to read online JSON reform/assumption files located at URLs beginning with `http`
  [[#2079](https://github.com/PSLmodels/Tax-Calculator/pull/2079)
  by Anderson Frailey]
- Add Python-version and code-coverage badges to `README.md` file
  [[#2080](https://github.com/PSLmodels/Tax-Calculator/pull/2080)
  by Martin Holmer]

**Bug Fixes**
- Fix syntax error in `gitpr.bat` Windows batch script
  [[#2084](https://github.com/PSLmodels/Tax-Calculator/pull/2084)
  by Martin Holmer]
- Fix bug in create_difference_table utility function that affected the `ubi` and `benefit_*_total` variables
  [[#2087](https://github.com/PSLmodels/Tax-Calculator/pull/2087)
  by Martin Holmer]


2018-09-11 Release 0.21.0 : first release compatible only with Python 3.6
-------------------------------------------------------------------------
(last merged pull request is
[#2058](https://github.com/PSLmodels/Tax-Calculator/pull/2058))

**API Changes**
- Require Python 3.6 to run Tax-Calculator source code or conda package
  [[#2058](https://github.com/PSLmodels/Tax-Calculator/pull/2058)
  by Martin Holmer], which requires new `puf.csv` input file (see [taxdata pull request 283](https://github.com/PSLmodels/taxdata/pull/283) for details) with this information:
  * Byte size: 56415698
  * MD5 checksum: 3f1c7c2b16b6394a9148779db992bed1

**New Features**
- None

**Bug Fixes**
- None


2018-09-06 Release 0.20.3 : LAST RELEASE COMPATIBLE WITH PYTHON 2.7
-------------------------------------------------------------------
(last merged pull request is
[#2056](https://github.com/PSLmodels/Tax-Calculator/pull/2056))

**API Changes**
- None

**New Features**
- Incorporate new PUF input data that include imputed values of itemizeable expenses for non-itemizers
  [[#2052](https://github.com/PSLmodels/Tax-Calculator/pull/2052)
  by Martin Holmer], which requires new `puf.csv` input file with this information:
  * Byte size: 55104059
  * MD5 checksum: 9929a03b2d93a628d5057cc17d032e52
- Incorporate new CPS input data that include different `other_ben` values
  [[#2055](https://github.com/PSLmodels/Tax-Calculator/pull/2055)
  by Martin Holmer]
- Incorporate new PUF input data that include imputed values of pension contributions
  [[#2056](https://github.com/PSLmodels/Tax-Calculator/pull/2056)
  by Martin Holmer], which requires new `puf.csv` input file with this information:
  * Byte size: 56415698
  * MD5 checksum: a10091a770472254c50f8985d8839162

**Bug Fixes**
- None


2018-08-10 Release 0.20.2
-------------------------
(last merged pull request is
[#2048](https://github.com/PSLmodels/Tax-Calculator/pull/2048))

**API Changes**
- None

**New Features**
- Add Calculator.n65() method that uses new `elderly_dependents` input variable
  [[#2029](https://github.com/PSLmodels/Tax-Calculator/pull/2029)
  by Martin Holmer at request of Max Ghenis]
- Incorporate updated CPS and PUF input data
  [[#2032](https://github.com/PSLmodels/Tax-Calculator/pull/2032)
  by Martin Holmer and Anderson Frailey]
- Add policy parameters that allow many changes in tax treatment of charitable giving
  [[#2037](https://github.com/PSLmodels/Tax-Calculator/pull/2037)
  by Derrick Choe]
- Extrapolate CPS benefit variables in the same way as other dollar variables are extrapolated to future years
  [[#2041](https://github.com/PSLmodels/Tax-Calculator/pull/2041)
  by Martin Holmer]
- Incorporate most recent PUF input data fixing problem mentioned in [#2032](https://github.com/PSLmodels/Tax-Calculator/pull/2032)
  [[#2047](https://github.com/PSLmodels/Tax-Calculator/pull/2047)
  by Martin Holmer and Anderson Frailey], which requires new `puf.csv`
  input file with this information:
  * Byte size: 54341028
  * MD5 checksum: b64b90884406dfcff85f2ac9ba79f9bf
- Incorporate most recent CPS input data containing actuarial value of health insurance benefits
  [[#2048](https://github.com/PSLmodels/Tax-Calculator/pull/2048)
  by Martin Holmer and Anderson Frailey]

**Bug Fixes**
- Fix incorrect aging of `e00900` variable
  [[#2027](https://github.com/PSLmodels/Tax-Calculator/pull/2027)
  by Martin Holmer with bug reported by Max Ghenis]


2018-05-21 Release 0.20.1
-------------------------
(last merged pull request is
[#2005](https://github.com/PSLmodels/Tax-Calculator/pull/2005))

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Fix warning logic to exclude CPS data and to fix handling of changes in standard deduction amounts
  [[#2005](https://github.com/PSLmodels/Tax-Calculator/pull/2005)
  by Martin Holmer]


2018-05-18 Release 0.20.0
-------------------------
(last merged pull request is
[#2003](https://github.com/PSLmodels/Tax-Calculator/pull/2003))

**API Changes**
- Simplify table-creation Calculator methods and related utility functions
  [[#1984](https://github.com/PSLmodels/Tax-Calculator/pull/1984)
  by Martin Holmer]
- Rename `Growfactors` class as `GrowFactors` and rename `Growdiff` class as `GrowDiff`
  [[#1996](https://github.com/PSLmodels/Tax-Calculator/pull/1996)
  by Martin Holmer]
- Add `quantity_response` utility function and remove obsolete charity and earnings response logic from Behavior class
  [[#1997](https://github.com/PSLmodels/Tax-Calculator/pull/1997)
  by Martin Holmer]
- Add empty shell of `GrowModel` class that will eventually contain a simple macroeconomic growth model with annual feedback to the microeconomic simulation
  [[#1998](https://github.com/PSLmodels/Tax-Calculator/pull/1998)
  by Martin Holmer]

**New Features**
- Streamline logic that prevents disclosure of details of PUF filing units
  [[#1979](https://github.com/PSLmodels/Tax-Calculator/pull/1979)
  by Martin Holmer]
- Add option to not include benefits in a Records object that uses CPS data
  [[#1985](https://github.com/PSLmodels/Tax-Calculator/pull/1985)
  and
  [[#1988](https://github.com/PSLmodels/Tax-Calculator/pull/1988)
  by Martin Holmer]
- Update CODING and TESTING documentation to reflect recommended usage of `pycodestyle` in place of `pep8`
  [[#1989](https://github.com/PSLmodels/Tax-Calculator/pull/1989)
  by Martin Holmer]
- Add validity checking for non-behavior assumption parameters
  [[#1992](https://github.com/PSLmodels/Tax-Calculator/pull/1992)
  by Martin Holmer]
- Add Tax-Calculator cookbook recipe using Behavior class and its `response` method
  [[#1993](https://github.com/PSLmodels/Tax-Calculator/pull/1993)
  by Martin Holmer]
- Add Tax-Calculator cookbook recipe showing how to create a custom table
  [[#1994](https://github.com/PSLmodels/Tax-Calculator/pull/1994)
  by Martin Holmer]
- Add Tax-Calculator cookbook recipe showing how to use new `quantity_response` utility function
  [[#2002](https://github.com/PSLmodels/Tax-Calculator/pull/2002)
  by Martin Holmer]

**Bug Fixes**
- Fix mishandling of boolean policy parameters
  [[#1982](https://github.com/PSLmodels/Tax-Calculator/pull/1982)
  by Hank Doupe]


2018-04-19 Release 0.19.0
-------------------------
(last merged pull request is
[#1977](https://github.com/PSLmodels/Tax-Calculator/pull/1977))

**API Changes**
- Improve data quality of several CPS age variables, which causes changes in CPS tax results
  [[#1962](https://github.com/PSLmodels/Tax-Calculator/pull/1962)
  by Anderson Frailey and Martin Holmer based on bug reported by Max Ghenis]

**New Features**
- Add validity checking for revised values of behavioral response parameters
  [[#1952](https://github.com/PSLmodels/Tax-Calculator/pull/1952)
  by Hank Doupe]
- Strengthen logic that prevents disclosure of details of filing units in PUF
  [[#1972](https://github.com/PSLmodels/Tax-Calculator/pull/1972)
   [#1973](https://github.com/PSLmodels/Tax-Calculator/pull/1973)
   [#1976](https://github.com/PSLmodels/Tax-Calculator/pull/1976)
  by Martin Holmer]

**Bug Fixes**
- Fix loose checking of the data type of parameters in reform dictionaries passed to the Policy class `implement_reform` method
  [[#1960](https://github.com/PSLmodels/Tax-Calculator/pull/1960)
  by Martin Holmer based on bug reported by Hank Doupe]
- Fix diagnostic and distribution tables so that itemizers plus standard-deduction takers equals total returns
  [[#1964](https://github.com/PSLmodels/Tax-Calculator/pull/1964)
  by Martin Holmer]
- Fix confusing documentation of the data type of parameters
  [[#1970](https://github.com/PSLmodels/Tax-Calculator/pull/1970)
  by Martin Holmer as suggested by Hank Doupe]
- Fix bug in TCJA tax calculations for those with large business losses
  [[#1977](https://github.com/PSLmodels/Tax-Calculator/pull/1977)
  by Martin Holmer based on bug report by Ernie Tedeschi]


2018-03-30 Release 0.18.0
-------------------------
(last merged pull request is
[#1942](https://github.com/PSLmodels/Tax-Calculator/pull/1942))

**API Changes**
- Remove redundant `_DependentCredit_c` policy parameter and fix dependent credit phase-out logic
  [[#1937](https://github.com/PSLmodels/Tax-Calculator/pull/1937)
  by Martin Holmer]

**New Features**
- Add memory management logic to reduce memory usage
  [[#1942](https://github.com/PSLmodels/Tax-Calculator/pull/1942)
  by Martin Holmer]

**Bug Fixes**
- Replace monthly housing benefits with annual housing benefits in CPS data
  [[#1941](https://github.com/PSLmodels/Tax-Calculator/pull/1941)
  by Anderson Frailey]


2018-03-16 Release 0.17.0
-------------------------
(last merged pull request is
[#1926](https://github.com/PSLmodels/Tax-Calculator/pull/1926))

**API Changes**
- Make `run_nth_year_tax_calc_model` function return tables with all rows
  [[#1914](https://github.com/PSLmodels/Tax-Calculator/pull/1914)
  by Martin Holmer]
- Rename Calculator class `param` method as `policy_param`
  [[#1915](https://github.com/PSLmodels/Tax-Calculator/pull/1915)
  by Martin Holmer]
- Add notice of end of Python 2.7 support beginning in 2019
  [[#1923](https://github.com/PSLmodels/Tax-Calculator/pull/1923)
  by Martin Holmer]

**New Features**
- Add row names to distribution and difference tables
  [[#1913](https://github.com/PSLmodels/Tax-Calculator/pull/1913)
  by Martin Holmer]
- Add row for those with zero income in distribution and difference tables
  [[#1917](https://github.com/PSLmodels/Tax-Calculator/pull/1917)
  by Martin Holmer]
- Revise Calculator class decile_graph method to provide option for including those with zero income and/or those with negative income in the bottom decile
  [[#1918](https://github.com/PSLmodels/Tax-Calculator/pull/1918)
  by Martin Holmer]
- Add UBI benefits statistic to distribution and difference tables
  [[#1919](https://github.com/PSLmodels/Tax-Calculator/pull/1919)
  by Killian Pinkelman]
- Add two benefits statistics to distribution and difference tables
  [[#1925](https://github.com/PSLmodels/Tax-Calculator/pull/1925)
  by Anderson Frailey]

**Bug Fixes**
- None


2018-03-09 Release 0.16.2
-------------------------
(last merged pull request is
[#1911](https://github.com/PSLmodels/Tax-Calculator/pull/1911))

**API Changes**
- None

**New Features**
- Add graph of percentage change in after-tax expanded income by baseline expanded-income percentile and include it in `tc --graphs` output and in the cookbook's basic recipe
  [[#1890](https://github.com/PSLmodels/Tax-Calculator/pull/1890)
  by Martin Holmer]
- Improve handling of those with negative or zero `expanded_income` in tables and graphs
  [[#1902](https://github.com/PSLmodels/Tax-Calculator/pull/1902)
  by Martin Holmer]
- Add three new benefits and improve imputation of interest, dividend, and pension income in CPS data
  [[#1911](https://github.com/PSLmodels/Tax-Calculator/pull/1911)
  by Anderson Frailey and Martin Holmer]

**Bug Fixes**
- Correct bottom bin name in distribution/difference tables exported to TaxBrain
  [[#1889](https://github.com/PSLmodels/Tax-Calculator/pull/1889)
  by Martin Holmer]
- Add missing check of equality of `BEN_*_value` parameters in baseline and reform Calculator objects when using `expanded_income` in tables or graphs
  [[#1894](https://github.com/PSLmodels/Tax-Calculator/pull/1894)
  by Martin Holmer]
- Correct and simplify calculation of `expanded_income`
  [[#1897](https://github.com/PSLmodels/Tax-Calculator/pull/1897)
   [#1899](https://github.com/PSLmodels/Tax-Calculator/pull/1899)
   [#1900](https://github.com/PSLmodels/Tax-Calculator/pull/1900)
   [#1901](https://github.com/PSLmodels/Tax-Calculator/pull/1901)
  by Martin Holmer and Anderson Frailey], which requires new `puf.csv`
  input file with this information:
  * Byte size: 54718219
  * MD5 checksum: e22429702920a0d927a36ea1103ba067
- Correct AGI concept used in EITC phase-out logic
  [[#1907](https://github.com/PSLmodels/Tax-Calculator/pull/1907)
  by Martin Holmer as reported by Max Ghenis]


2018-02-16 Release 0.16.1
-------------------------
(last merged pull request is
[#1886](https://github.com/PSLmodels/Tax-Calculator/pull/1886))

**API Changes**
- None

**New Features**
- Add graph of percentage change in after-tax expanded income by baseline expanded-income quintiles
  [[#1880](https://github.com/PSLmodels/Tax-Calculator/pull/1880)
  by Martin Holmer]
- Improve consistency of UBI-related head-count-by-age values in the CPS data
  [[#1882](https://github.com/PSLmodels/Tax-Calculator/pull/1882)
  by Anderson Frailey]
- Add variable to `cps.csv.gz` that facilitates matching CPS data to Tax-Calculator filing units
  [[#1885](https://github.com/PSLmodels/Tax-Calculator/pull/1885)
  by Anderson Frailey]

**Bug Fixes**
- Fix lack of calculation of `benefit_cost_total` variable
  [[#1886](https://github.com/PSLmodels/Tax-Calculator/pull/1886)
  by Anderson Frailey]


2018-02-13 Release 0.16.0
-------------------------
(last merged pull request is
[#1871](https://github.com/PSLmodels/Tax-Calculator/pull/1871))

**API Changes**
- Improve data quality of several existing CPS variables, which causes changes in CPS tax results
  [[#1853](https://github.com/PSLmodels/Tax-Calculator/pull/1853)
  by Anderson Frailey with assistance from Martin Holmer]
- Use 2011 PUF data (rather than the older 2009 PUF data), which causes changes in PUF tax results
  [[#1871](https://github.com/PSLmodels/Tax-Calculator/pull/1871)
  by Anderson Frailey and Martin Holmer], which requires new `puf.csv` input file with this information:
  * Byte size: 54714632
  * MD5 checksum: de4a59c9bce0a7d5e6c3110172237c9b

**New Features**
- Add ability to extrapolate imputed benefits and benefit-related policy parameters
  [[#1719](https://github.com/PSLmodels/Tax-Calculator/pull/1719)
  by Anderson Frailey]
- Add ability to specify the consumption value of in-kind benefits to be less than the government cost of providing in-kind benefits
  [[#1863](https://github.com/PSLmodels/Tax-Calculator/pull/1863)
  by Anderson Frailey]

**Bug Fixes**
- Improve handling of very high marginal tax rates in the `Behavior.response` method
  [[#1858](https://github.com/PSLmodels/Tax-Calculator/pull/1858)
  by Martin Holmer with assistance from Matt Jensen]


2018-01-30 Release 0.15.2
-------------------------
(last merged pull request is
[#1851](https://github.com/PSLmodels/Tax-Calculator/pull/1851))

**API Changes**
- None

**New Features**
- Add ability to specify a compound reform in the tc `--reform` option
  [[#1842](https://github.com/PSLmodels/Tax-Calculator/pull/1842)
  by Martin Holmer as requested by Ernie Tedeschi]
- Add compatible-data information for each policy parameter to user guide
  [[#1844](https://github.com/PSLmodels/Tax-Calculator/pull/1844)
  by Martin Holmer as requested by Matt Jensen]
- Add tc `--baseline BASELINE` option that sets baseline policy equal to that specified in BASELINE reform file (rather than baseline policy being current-law poliy)
  [[#1851](https://github.com/PSLmodels/Tax-Calculator/pull/1851)
  by Martin Holmer as requested by Matt Jensen and Ernie Tedeschi]

**Bug Fixes**
- Add error checking for Calculator misuse in presence of behavioral responses
  [[#1848](https://github.com/PSLmodels/Tax-Calculator/pull/1848)
  by Martin Holmer]
- Add error checking for diagnostic_table misuse in presence of behavioral responses
  [[#1849](https://github.com/PSLmodels/Tax-Calculator/pull/1849)
  by Martin Holmer]


2018-01-20 Release 0.15.1
-------------------------
(last merged pull request is
[#1838](https://github.com/PSLmodels/Tax-Calculator/pull/1838))

**API Changes**
- None

**New Features**
- Add `cpi_inflatable` field for each parameter in the four JSON parameter files
  [[#1838](https://github.com/PSLmodels/Tax-Calculator/pull/1838)
  by Martin Holmer as requested by Hank Doupe]

**Bug Fixes**
- None


2018-01-18 Release 0.15.0
-------------------------
(last merged pull request is
[#1834](https://github.com/PSLmodels/Tax-Calculator/pull/1834))

**API Changes**
- Make objects embedded in a Calculator object private and provide Calculator class access methods to manipulate the embedded objects
  [[#1791](https://github.com/PSLmodels/Tax-Calculator/pull/1791)
  by Martin Holmer]
- Rename three UBI policy parameters to be more descriptive
  [[#1813](https://github.com/PSLmodels/Tax-Calculator/pull/1813)
  by Martin Holmer as suggested by Max Ghenis]

**New Features**
- Add validity testing of compatible_data information in `current_law_policy.json`
  [[#1614](https://github.com/PSLmodels/Tax-Calculator/pull/1614)
  by Matt Jensen with assistance from Hank Doupe]
- Add `--outdir` option to command-line `tc` tool
  [[#1801](https://github.com/PSLmodels/Tax-Calculator/pull/1801)
  by Martin Holmer as suggested by Reuben Fischer-Baum]
- Make TCJA policy current-law policy
  [[#1803](https://github.com/PSLmodels/Tax-Calculator/pull/1803)
  by Martin Holmer with assistance from Cody Kallen]
- Change minimum required pandas version from 0.21.0 to 0.22.0 and remove zsum() pandas work-around
  [[#1805](https://github.com/PSLmodels/Tax-Calculator/pull/1805)
  by Martin Holmer]
- Add policy parameter and logic needed to represent TCJA treatment of alimony received
  [[#1818](https://github.com/PSLmodels/Tax-Calculator/pull/1818)
  by Martin Holmer and Cody Kallen]
- Add policy parameters and logic needed to represent TCJA limits on pass-through income and business losses
  [[#1819](https://github.com/PSLmodels/Tax-Calculator/pull/1819)
  by Cody Kallen]
- Revise user guide and Tax-Calculator cookbook recipes to reflect TCJA as current-law policy
  [[#1832](https://github.com/PSLmodels/Tax-Calculator/pull/1832)
  by Martin Holmer]

**Bug Fixes**
- Fix column order in distribution table
  [[#1834](https://github.com/PSLmodels/Tax-Calculator/pull/1834)
  by Martin Holmer and Hank Doupe]


2017-12-24 Release 0.14.3
-------------------------
(last merged pull request is
[#1796](https://github.com/PSLmodels/Tax-Calculator/pull/1796))

**API Changes**
- None

**New Features**
- Change minimum required pandas version from 0.20.1 to 0.21.0
  [[#1781](https://github.com/PSLmodels/Tax-Calculator/pull/1781)
  by Martin Holmer]
- Generalize validation of boolean policy parameter values in reforms
  [[#1782](https://github.com/PSLmodels/Tax-Calculator/pull/1782)
  by Martin Holmer as requested by Hank Doupe]
- Handle small numerical differences in test results generated under Python 3.6
  [[#1795](https://github.com/PSLmodels/Tax-Calculator/pull/1795)
  by Martin Holmer with need pointed out by Matt Jensen]
- Make the `_cpi_offset` policy parameter work like other policy parameters
  [[#1796](https://github.com/PSLmodels/Tax-Calculator/pull/1796)
  by Martin Holmer with need pointed out by Matt Jensen and Hank Doupe]

**Bug Fixes**
- None


2017-12-19 Release 0.14.2
-------------------------
(last merged pull request is
[#1775](https://github.com/PSLmodels/Tax-Calculator/pull/1775))

**API Changes**
- None

**New Features**
- Add two policy parameters that can be used to cap itemized SALT deductions as a fraction of AGI
  [[#1711](https://github.com/PSLmodels/Tax-Calculator/pull/1711)
  by Derrick Choe with assistance from Cody Kallen and Hank Doupe]
- Update "notes" in `current_law_policy.json` for policy parameters first introduced in TCJA bills
  [[#1765](https://github.com/PSLmodels/Tax-Calculator/pull/1765)
  by Max Ghenis]

**Bug Fixes**
- Standardize format of ValueError messages raised by Policy.implement_reform method
  [[#1775](https://github.com/PSLmodels/Tax-Calculator/pull/1775)
  by Martin Holmer, reported by Max Ghenis and diagnosed by Hank Doupe]


2017-12-15 Release 0.14.1
-------------------------
(last merged pull request is
[#1759](https://github.com/PSLmodels/Tax-Calculator/pull/1759))

**API Changes**
- None

**New Features**
- Add policy parameter that can cap the combined state and local income/sales and real-estate deductions
  [[#1756](https://github.com/PSLmodels/Tax-Calculator/pull/1756)
  by Cody Kallen with helpful discussion from Ernie Tedeschi and Matt Jensen]
- Add percentage change in income by income decile graph to `tc --graphs` output
  [[#1758](https://github.com/PSLmodels/Tax-Calculator/pull/1758)
  by Martin Holmer]
- Add JSON reform file for TCJA conference bill
  [[#1759](https://github.com/PSLmodels/Tax-Calculator/pull/1759)
  by Cody Kallen with review by Matt Jensen and Sean Wang]

**Bug Fixes**
- None


2017-12-11 Release 0.14.0
-------------------------
(last merged pull request is
[#1742](https://github.com/PSLmodels/Tax-Calculator/pull/1742))

**API Changes**
- Add several Calculator table methods and revise table utilities to not use Calculator object(s)
  [[#1718](https://github.com/PSLmodels/Tax-Calculator/pull/1718)
  by Martin Holmer]
- Add several Calculator graph methods and revise graph utilities to not use Calculator objects
  [[#1722](https://github.com/PSLmodels/Tax-Calculator/pull/1722)
  by Martin Holmer]
- Add Calculator ce_aftertax_income method and revise corresponding utility to not use Calculator object
  [[#1723](https://github.com/PSLmodels/Tax-Calculator/pull/1723)
  by Martin Holmer]

**New Features**
- Add new policy parameter for refunding the new CTC against all payroll taxes
  [[#1716](https://github.com/PSLmodels/Tax-Calculator/pull/1716)
  by Matt Jensen as suggested by Ernie Tedeschi]
- Remove calculation of AGI tables from the TaxBrain Interface, tbi
  [[#1724](https://github.com/PSLmodels/Tax-Calculator/pull/1724)
  by Martin Holmer as suggested by Matt Jensen and Hank Doupe]
- Add ability to specify partial customized CLI `tc --dump` output
  [[#1735](https://github.com/PSLmodels/Tax-Calculator/pull/1735)
  by Martin Holmer as suggested by Sean Wang]
- Add *Cookbook of Tested Recipes for Python Programming with Tax-Calculator*
  [[#1740](https://github.com/PSLmodels/Tax-Calculator/pull/1740)
  by Martin Holmer]
- Add calculation of two values on the ALL row of the difference table
  [[#1741](https://github.com/PSLmodels/Tax-Calculator/pull/1741)
  by Martin Holmer]

**Bug Fixes**
- Fix Behavior.response method to handle very high marginal tax rates
  [[#1698](https://github.com/PSLmodels/Tax-Calculator/pull/1698)
  by Martin Holmer, reported by Richard Evans and Jason DeBacker]
- Fix `create_distribution_table` to generate correct details for the top decile
  [[#1712](https://github.com/PSLmodels/Tax-Calculator/pull/1712)
  by Martin Holmer]


2017-11-17 Release 0.13.2
-------------------------
(last merged pull request is
[#1680](https://github.com/PSLmodels/Tax-Calculator/pull/1680))

**API Changes**
- None

**New Features**
- Add TCJA_House_Amended JSON policy reform file
  [[#1664](https://github.com/PSLmodels/Tax-Calculator/pull/1664)
  by Cody Kallen and Matt Jensen]
- Add `_cpi_offset` policy parameter that can be used to specify chained CPI indexing reforms
  [[#1667](https://github.com/PSLmodels/Tax-Calculator/pull/1667)
  by Martin Holmer]
- Add new policy parameter that changes the stacking order of child/dependent credits
  [[#1676](https://github.com/PSLmodels/Tax-Calculator/pull/1676)
  by Matt Jensen as suggested by Cody Kallen with need identified by Joint Economic Committee staff]
- Add to several TCJA reform files the provision for chained CPI indexing
  [[#1680](https://github.com/PSLmodels/Tax-Calculator/pull/1680)
  by Matt Jensen]

**Bug Fixes**
- Fix `_ACTC_ChildNum` policy parameter documentation and logic
  [[#1666](https://github.com/PSLmodels/Tax-Calculator/pull/1666)
  by Martin Holmer, reported by Ernie Tedeschi]
- Fix documentation for mis-named `n1821` input variable
  [[#1672](https://github.com/PSLmodels/Tax-Calculator/pull/1672)
  by Martin Holmer, reported by Max Ghenis]
- Fix logic of run_nth_year_gdp_elast_model function in the TaxBrainInterface
  [[#1677](https://github.com/PSLmodels/Tax-Calculator/pull/1677)
  by Martin Holmer, reported by Hank Doupe]


2017-11-10 Release 0.13.1
-------------------------
(last merged pull request is
[#1655](https://github.com/PSLmodels/Tax-Calculator/pull/1655))

**API Changes**
- None

**New Features**
- Add household and family identifiers from the CPS for the cps.csv.gz file that ships with taxcalc
  [[#1635](https://github.com/PSLmodels/Tax-Calculator/pull/1635)
  by Anderson Frailey]
- Improved documentation for the cps.csv.gz file that ships with taxcalc
  [[#1648](https://github.com/PSLmodels/Tax-Calculator/pull/1648)
  by Martin Holmer]
- Add parameter for the business income exclusion in the Senate TCJA Chairman's mark
  [[#1651](https://github.com/PSLmodels/Tax-Calculator/pull/1648)
  by Cody Kallen]
- Add TCJA reform file for the Senate Chairman's mark
  [[#1652](https://github.com/PSLmodels/Tax-Calculator/pull/1652)
  by Cody Kallen]
- Add FIPS state codes to the cps.csv.gz file that ships with taxcalc
  [[#1653](https://github.com/PSLmodels/Tax-Calculator/pull/1653)
  by Anderson Frailey]

**Bug Fixes**
- Fix an edge case related to new pass-through parameters that caused some extreme MTRs
  [[#1645](https://github.com/PSLmodels/Tax-Calculator/pull/1645)
  by Cody Kallen, reported by Richard Evans]


2017-11-07 Release 0.13.0
-------------------------
(last merged pull request is
[#1632](https://github.com/PSLmodels/Tax-Calculator/pull/1632))

**API Changes**
- Add new statistics and top-decile detail to distribution and difference tables
  [[#1605](https://github.com/PSLmodels/Tax-Calculator/pull/1605)
  by Martin Holmer]

**New Features**
- Add expanded_income and aftertax_income to distribution table
  [[#1602](https://github.com/PSLmodels/Tax-Calculator/pull/1602)
  by Martin Holmer]
- Add utility functions that generate a change-in-aftertax-income-by-decile graph
  [[#1606](https://github.com/PSLmodels/Tax-Calculator/pull/1606)
  by Martin Holmer]
- Add new dependent credits for children and non-children dependents
  [[#1615](https://github.com/PSLmodels/Tax-Calculator/pull/1615)
  by Cody Kallen]
- Add new non-refundable credit for filer and spouse
  [[#1618](https://github.com/PSLmodels/Tax-Calculator/pull/1618)
  by Cody Kallen]
- Add capability to model pass-through tax rate eligiblity rules in TCJA
  [[#1620](https://github.com/PSLmodels/Tax-Calculator/pull/1620)
  by Cody Kallen]
- Make several Personal Nonrefundable Credit parameters available to external applications like TaxBrain
  [[#1622](https://github.com/PSLmodels/Tax-Calculator/pull/1622)
  by Matt Jensen]
- Extend extrapolation to 2027 and update to June 2017 CBO baseline
  [[#1624](https://github.com/PSLmodels/Tax-Calculator/pull/1624)
  by Anderson Frailey]
- Add new reform JSON file for the Tax Cuts and Jobs Act
  [[#1625](https://github.com/PSLmodels/Tax-Calculator/pull/1625)
  by Cody Kallen]

**Bug Fixes**
- Resolve compatibility issues with Pandas 0.21.0
  [[#1629](https://github.com/PSLmodels/Tax-Calculator/pull/1629)
  by Hank Doupe]
- Cleaner solution to compatibility issues with Pandas 0.21.0
  [[#1634](https://github.com/PSLmodels/Tax-Calculator/pull/1634)
  by Hank Doupe]


2017-10-20 Release 0.12.0
-------------------------
(last merged pull request is
[#1600](https://github.com/PSLmodels/Tax-Calculator/pull/1600))

**API Changes**
- Rename read_json_param_files as read_json_param_objects
  [[#1563](https://github.com/PSLmodels/Tax-Calculator/pull/1563)
  by Martin Holmer]
- Remove arrays_not_lists argument from read_json_param_objects
  [[#1568](https://github.com/PSLmodels/Tax-Calculator/pull/1568)
  by Martin Holmer]
- Rename dropq as tbi (taxbrain interface) and refactor run_nth_year_*_model functions so that either puf.csv or cps.csv can be used as input data
  [[#1577](https://github.com/PSLmodels/Tax-Calculator/pull/1577)
  by Martin Holmer]
- Change Calculator class constructor so that it makes a deep copy of each specified object for internal use
  [[#1582](https://github.com/PSLmodels/Tax-Calculator/pull/1582)
  by Martin Holmer]
- Rename and reorder difference table columns
  [[#1584](https://github.com/PSLmodels/Tax-Calculator/pull/1584)
  by Martin Holmer]

**New Features**
- Add Calculator.reform_documentation that generates plain text documentation of a reform
  [[#1564](https://github.com/PSLmodels/Tax-Calculator/pull/1564)
  by Martin Holmer]
- Enhance stats_summary.py script and its output
  [[#1566](https://github.com/PSLmodels/Tax-Calculator/pull/1566)
  by Amy Xu]
- Add reform documentation as standard output from Tax-Calculator CLI, tc
  [[#1567](https://github.com/PSLmodels/Tax-Calculator/pull/1567)
  by Martin Holmer]
- Add parameter type checking to Policy.implement_reform method
  [[#1585](https://github.com/PSLmodels/Tax-Calculator/pull/1585)
  by Martin Holmer]
- Add `_CTC_new_for_all` policy parameter to allow credits for those with negative AGI
  [[#1595](https://github.com/PSLmodels/Tax-Calculator/pull/1595)
  by Martin Holmer]
- Narrow range of legal values for `_CDCC_c` policy parameter
  [[#1597](https://github.com/PSLmodels/Tax-Calculator/pull/1597)
  by Matt Jensen]
- Make several UBI policy parameters available to external applications like TaxBrain
  [[#1599](https://github.com/PSLmodels/Tax-Calculator/pull/1599)
  by Matt Jensen]

**Bug Fixes**
- Relax _STD and _STD_Dep minimum value warning logic
  [[#1578](https://github.com/PSLmodels/Tax-Calculator/pull/1578)
  by Martin Holmer]
- Fix macro-elasticity model logic so that GDP change in year t depends on tax rate changes in year t-1
  [[#1579](https://github.com/PSLmodels/Tax-Calculator/pull/1579)
  by Martin Holmer]
- Fix bugs in automatic generation of reform documentation having to do with policy parameters that are boolean scalars
  [[#1596](https://github.com/PSLmodels/Tax-Calculator/pull/1596)
  by Martin Holmer]


2017-09-21 Release 0.11.0
-------------------------
(last merged pull request is
[#1555](https://github.com/PSLmodels/Tax-Calculator/pull/1555))

**API Changes**
- Revise dropq distribution and difference tables used by TaxBrain
  [[#1537](https://github.com/PSLmodels/Tax-Calculator/pull/1537)
  by Anderson Frailey and Martin Holmer]
- Make dropq run_nth_year_tax_calc_model return a dictionary of results
  [[#1543](https://github.com/PSLmodels/Tax-Calculator/pull/1543)
  by Martin Holmer]

**New Features**
- Add option to cap the amount of gross itemized deductions allowed as a decimal fraction of AGI
  [[#1542](https://github.com/PSLmodels/Tax-Calculator/pull/1542)
  by Matt Jensen]
- Add dropq tables using AGI as income measure for TaxBrain use
  [[#1544](https://github.com/PSLmodels/Tax-Calculator/pull/1544)
  by Martin Holmer]
- Add JSON reform file for Brown-Khanna GAIN Act that expands the EITC
  [[#1555](https://github.com/PSLmodels/Tax-Calculator/pull/1555)
  by Matt Jensen and Martin Holmer]

**Bug Fixes**
- None


2017-09-13 Release 0.10.2
-------------------------

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Allow policy parameter suffix logic to work even when there are reform errors
  [[34561ff](https://github.com/PSLmodels/Tax-Calculator/commit/34561ffdeb23c632e248d760c0e34417df0b41f3)
  by Martin Holmer]


2017-09-08 Release 0.10.1
-------------------------

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Fix vagueness of error/warning messages for non-scalar policy parameters
  [[5536792](https://github.com/PSLmodels/Tax-Calculator/commit/5536792538c3f3e687cccc9e38b20949ac68cb9a)
  by Martin Holmer]


2017-08-28 Release 0.10.0
-------------------------
(last merged pull request is
[#1531](https://github.com/PSLmodels/Tax-Calculator/pull/1531))

**API Changes**
- Add dropq function that returns reform warnings and errors
  [[#1524](https://github.com/PSLmodels/Tax-Calculator/pull/1524)
  by Martin Holmer]

**New Features**
- Add option to use policy parameter suffixes in JSON reform files
  [[#1505](https://github.com/PSLmodels/Tax-Calculator/pull/1505)
  by Martin Holmer] and
  [[#1520](https://github.com/PSLmodels/Tax-Calculator/pull/1520)
  by Martin Holmer]
- Add rounding of wage-inflated or price-inflated parameter values to nearest cent
  [[#1506](https://github.com/PSLmodels/Tax-Calculator/pull/1506)
  by Martin Holmer]
- Add extensive checking of reform policy parameter names and values
  [[#1524](https://github.com/PSLmodels/Tax-Calculator/pull/1524)
  by Martin Holmer]

**Bug Fixes**
- None


2017-07-26 Release 0.9.2
------------------------
(last merged pull request is
[#1490](https://github.com/PSLmodels/Tax-Calculator/pull/1490))

**API Changes**
- None

**New Features**
- Add several taxcalc/reforms/earnings_shifting.* files that analyze the revenue implications of high-paid workers forming personal LLCs to contract with their former employers under the Trump2017.json reform
  [[#1464](https://github.com/PSLmodels/Tax-Calculator/pull/1464)
  by Martin Holmer]
- Add ability to read and calculate taxes with new CPS input data for 2014 and subsequent years
  [[#1484](https://github.com/PSLmodels/Tax-Calculator/pull/1484)
  by Martin Holmer]
- Add tests of ability to calculate taxes with new CPS input data
  [[#1490](https://github.com/PSLmodels/Tax-Calculator/pull/1490)
  by Martin Holmer]

**Bug Fixes**
- Fix decorators bug that appeared when numpy 1.13.1, and pandas 0.20.2 that uses numpy 1.13, recently became available
  [[#1470](https://github.com/PSLmodels/Tax-Calculator/pull/1470)
  by T.J. Alumbaugh]
- Fix records bug that appeared when numpy 1.13.1, and pandas 0.20.2 that uses numpy 1.13, recently became available
  [[#1473](https://github.com/PSLmodels/Tax-Calculator/pull/1473)
  by Martin Holmer]


2017-07-06 Release 0.9.1
------------------------
(last merged pull request is
[#1438](https://github.com/PSLmodels/Tax-Calculator/pull/1438))

**API Changes**
- None

**New Features**
- Add Form 1065 Schedule K-1 self-employment earnings to calculation of self-employment payroll taxes
  [[#1438](https://github.com/PSLmodels/Tax-Calculator/pull/1438)
  by Martin Holmer],
  which requires new `puf.csv` input file with this information:
  * Byte size: 53743252
  * MD5 checksum: ca0ad8bbb05ee15b1cbefc7f1fa1f965
- Improve calculation of sub-sample weights
  [[#1441](https://github.com/PSLmodels/Tax-Calculator/pull/1441)
  by Hank Doupe]

**Bug Fixes**
- Fix personal refundable credit bug and personal nonrefundable credit bug
  [[#1450](https://github.com/PSLmodels/Tax-Calculator/pull/1450)
  by Martin Holmer]


2017-06-14 Release 0.9.0
------------------------
(last merged pull request is
[#1431](https://github.com/PSLmodels/Tax-Calculator/pull/1431))

**API Changes**
- Initial specification of public API removes several unused utility
  functions and makes private several Tax-Calculator members whose
  only role is to support public members
  [[#1424](https://github.com/PSLmodels/Tax-Calculator/pull/1424)
  by Martin Holmer]

**New Features**
- Add nonrefundable personal credit reform options
  [[#1427](https://github.com/PSLmodels/Tax-Calculator/pull/1427)
  by William Ensor]

- Add repeal personal exemptions for dependents under age 18 reform option
  [[#1428](https://github.com/PSLmodels/Tax-Calculator/pull/1428)
  by Hank Doupe]

- Switch to use of new improved `puf.csv` input file that causes small
  changes in tax results
  [[#1429](https://github.com/PSLmodels/Tax-Calculator/pull/1429)
  by Martin Holmer],
  which requires new `puf.csv` input file with this information:
  * Byte size: 52486351
  * MD5 checksum: d56b649c92049e32501b2d2fc5c36c92

**Bug Fixes**
- Fix logic of gross casualty loss calculation by moving it out of
  Tax-Calculator and into the taxdata repository
  [[#1426](https://github.com/PSLmodels/Tax-Calculator/pull/1426)
  by Martin Holmer]


2017-06-08 Release 0.8.5
------------------------
(last merged pull request is
[#1416](https://github.com/PSLmodels/Tax-Calculator/pull/1416))

**API Changes**
- None

**New Features**
- Add column to differences table to show the change in tax liability
  as percentage of pre-reform after tax income
  [[#1375](https://github.com/PSLmodels/Tax-Calculator/pull/1375)
  by Anderson Frailey]
- Add policy reform file for the Renacci reform
  [[#1376](https://github.com/PSLmodels/Tax-Calculator/pull/1376),
  [#1383](https://github.com/PSLmodels/Tax-Calculator/pull/1383)
  and
  [#1385](https://github.com/PSLmodels/Tax-Calculator/pull/1385)
  by Hank Doupe]
- Add separate ceiling for each itemized deduction parameter
  [[#1385](https://github.com/PSLmodels/Tax-Calculator/pull/1385)
  by Hank Doupe]

**Bug Fixes**
- Fix bug in add_weighted_income_bins utility function
  [[#1387](https://github.com/PSLmodels/Tax-Calculator/pull/1387)
  by Martin Holmer]


2017-05-12 Release 0.8.4
------------------------
(last merged pull request is
[#1363](https://github.com/PSLmodels/Tax-Calculator/pull/1363))

**API Changes**
- None

**New Features**
- Add economic response assumption file template to documentation
  [[#1332](https://github.com/PSLmodels/Tax-Calculator/pull/1332)
  by Cody Kallen]
- Complete process of creating [user
  guide](https://PSLmodels.github.io/Tax-Calculator/)
  [[#1355](https://github.com/PSLmodels/Tax-Calculator/pull/1355)
  by Martin Holmer]
- Add Tax-Calculator conda package for Python 3.6
  [[#1361](https://github.com/PSLmodels/Tax-Calculator/pull/1361)
  by Martin Holmer]

**Bug Fixes**
- None


2017-05-01 Release 0.8.3
------------------------
(last merged pull request is
[#1328](https://github.com/PSLmodels/Tax-Calculator/pull/1328))

**API Changes**
- None

**New Features**
- Add --test installation option to Tax-Calculator CLI
  [[#1306](https://github.com/PSLmodels/Tax-Calculator/pull/1306)
  by Martin Holmer]
- Add --sqldb SQLite3 database dump output option to CLI
  [[#1312](https://github.com/PSLmodels/Tax-Calculator/pull/1312)
  by Martin Holmer]
- Add a reform preset for the April 2017 Trump tax plan
  [[#1323](https://github.com/PSLmodels/Tax-Calculator/pull/1323)
  by Cody Kallen]
- Add Other Taxes to tables and clarify documentation
  [[#1328](https://github.com/PSLmodels/Tax-Calculator/pull/1328)
  by Martin Holmer]

**Bug Fixes**
- None


2017-04-13 Release 0.8.2
------------------------
(last merged pull request is
[#1295](https://github.com/PSLmodels/Tax-Calculator/pull/1295))

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Minor edits to comments in Trump/Clinton policy reform files
  [[#1295](https://github.com/PSLmodels/Tax-Calculator/pull/1295)
  by Matt Jensen]


2017-04-13 Release 0.8.1
------------------------
(last merged pull request is
[#1293](https://github.com/PSLmodels/Tax-Calculator/pull/1293))

**API Changes**
- None

**New Features**
- Add testing for notebooks, starting with the behavior_example and
  10-minute notebooks
  [[#1198](https://github.com/PSLmodels/Tax-Calculator/pull/1198)
  by Peter Steinberg]
- Add MTR with respect to spouse earnings
  [[#1257](https://github.com/PSLmodels/Tax-Calculator/pull/1257)
  by Anderson Frailey]
- Add tax differences table to Tax-Calculator CLI --tables output
  [[#1265](https://github.com/PSLmodels/Tax-Calculator/pull/1265)
  by Martin Holmer]
- Update Jupyter Notebooks to demonstrate the latest Python API
  [[#1277](https://github.com/PSLmodels/Tax-Calculator/pull/1277)
  by Matt Jensen]
- Enable the charitable givings elasticity to vary by AGI value
  [[#1278](https://github.com/PSLmodels/Tax-Calculator/pull/1278)
  by Matt Jensen]
- Introduce records_variables.json to serve as a single source of
  truth for Records variables
  [[#1179](https://github.com/PSLmodels/Tax-Calculator/pull/1179)
  and
  [#1285](https://github.com/PSLmodels/Tax-Calculator/pull/1285)
  by Zach Risher]

**Bug Fixes**
- None


2017-03-24 Release 0.8.0
------------------------
(last merged pull request is
[#1260](https://github.com/PSLmodels/Tax-Calculator/pull/1260))

**API Changes**
- None

**New Features**
- Add ability to calculate, and possibly tax, UBI benefits
  [[#1235](https://github.com/PSLmodels/Tax-Calculator/pull/1235)
  by Anderson Frailey]
- Add additional deduction and credit haircut policy parameters
  [[#1247](https://github.com/PSLmodels/Tax-Calculator/pull/1247)
  by Anderson Frailey]
- Add constant charitable giving elasticities to behavioral response
  [[#1246](https://github.com/PSLmodels/Tax-Calculator/pull/1246)
  by Matt Jensen]
- Add another credit haircut policy parameter
  [[#1252](https://github.com/PSLmodels/Tax-Calculator/pull/1252)
  by Anderson Frailey]
- Make Tax-Calculator CLI an entry point to the taxcalc package
  [[#1253](https://github.com/PSLmodels/Tax-Calculator/pull/1253)
  by Martin Holmer]
- Add --tables option to Tax-Calculator CLI
  [[#1258](https://github.com/PSLmodels/Tax-Calculator/pull/1258)
  by Martin Holmer]

**Bug Fixes**
- None


2017-03-08 Release 0.7.9
------------------------
(last merged pull request is
[#1228](https://github.com/PSLmodels/Tax-Calculator/pull/1228))

**API Changes**
- Move simtax.py to taxcalc/validation/taxsim directory
  [[#1288](https://github.com/PSLmodels/Tax-Calculator/pull/1288)
  by Martin Holmer]

**New Features**
- Make import style more consistent
  [[#1288](https://github.com/PSLmodels/Tax-Calculator/pull/1288)
  by Martin Holmer]

**Bug Fixes**
- Add growdiff.json to MANIFEST.in
  [[#1217](https://github.com/PSLmodels/Tax-Calculator/pull/1217)
  and
  [#1219](https://github.com/PSLmodels/Tax-Calculator/pull/1219)
  by Peter Steinberg]


2017-03-01 Release 0.7.8
------------------------
(last merged pull request is
[#1206](https://github.com/PSLmodels/Tax-Calculator/pull/1206))

**API Changes**
- Redesign Growth class to support more realistic growth responses
  [[#1199](https://github.com/PSLmodels/Tax-Calculator/pull/1199)
  by Martin Holmer]

**New Features**
- Add a policy reform file for key provisions of the Ryan-Brady Better
  Way tax plan
  [[#1204](https://github.com/PSLmodels/Tax-Calculator/pull/1204)
  by Cody Kallen]
- Add a policy reform file for select provisions of the Clinton 2016
  campaign tax plan
  [[#1206](https://github.com/PSLmodels/Tax-Calculator/pull/1206)
  by Cody Kallen]

**Bug Fixes**
- None


2017-02-16 Release 0.7.7
------------------------
(last merged pull request is
[#1197](https://github.com/PSLmodels/Tax-Calculator/pull/1197))

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Add name of new Stage3 adjustment-ratios file to MANIFEST.in
  [[#1197](https://github.com/PSLmodels/Tax-Calculator/pull/1197)
  by Anderson Frailey]


2017-02-15 Release 0.7.6
------------------------
(last merged pull request is
[#1192](https://github.com/PSLmodels/Tax-Calculator/pull/1192))

**API Changes**
- Add Stage3 adjustment ratios to target IRS-SOI data on the
  distribution of interest income
  [[#1193](https://github.com/PSLmodels/Tax-Calculator/pull/1193)
  by Anderson Frailey],
  which requires new `puf.csv` input file with this information:
  * Byte size: 51470450
  * MD5 checksum: 3a02e9909399ba85d0a7cf5e98149b90

**New Features**
- Add to diagnostic table the number of tax units with non-positive
  income and combined tax liability
  [[#1170](https://github.com/PSLmodels/Tax-Calculator/pull/1170)
  by Anderson Frailey]

**Bug Fixes**
- Correct Policy wage growth rates to agree with CBO projection
  [[#1171](https://github.com/PSLmodels/Tax-Calculator/pull/1171)
  by Martin Holmer]


2017-01-31 Release 0.7.5
------------------------
(last merged pull request is
[#1169](https://github.com/PSLmodels/Tax-Calculator/pull/1169))

**API Changes**
- None

**New Features**
- Add a Trump 2016 policy reform JSON file
  [[#1135](https://github.com/PSLmodels/Tax-Calculator/pull/1135)
  by Matt Jensen]
- Reduce size of input file by rounding weights
  [[#1158](https://github.com/PSLmodels/Tax-Calculator/pull/1158)
  by Anderson Frailey]
- Update current-law policy parameters to 2017 IRS values
  [[#1169](https://github.com/PSLmodels/Tax-Calculator/pull/1169)
  by Anderson Frailey]

**Bug Fixes**
- Index EITC investment income cap to inflation
  [[#1169](https://github.com/PSLmodels/Tax-Calculator/pull/1169)
  by Anderson Frailey]


2017-01-24 Release 0.7.4
------------------------
(last merged pull request is
[#1152](https://github.com/PSLmodels/Tax-Calculator/pull/1152))

**API Changes**
- Separate policy reforms and response assumptions into two separate
  JSON files
  [[#1148](https://github.com/PSLmodels/Tax-Calculator/pull/1148)
  by Martin Holmer]

**New Features**
- New JSON reform file examples and capabilities
  [[#1123](https://github.com/PSLmodels/Tax-Calculator/pull/1123)-[#1131](https://github.com/PSLmodels/Tax-Calculator/pull/1131)
  by Martin Holmer]

**Bug Fixes**
- Fix bugs in 10-minute notebook
  [[#1152](https://github.com/PSLmodels/Tax-Calculator/pull/1152)
  by Matt Jensen]


2017-01-24 Release 0.7.3
------------------------
(last merged pull request is
[#1113](https://github.com/PSLmodels/Tax-Calculator/pull/1113))

**API Changes**
- None

**New Features**
- Add ability to use an expression to specify a policy parameter
  [[#1081](https://github.com/PSLmodels/Tax-Calculator/pull/1081)
  by Martin Holmer]
- Expand scope of JSON reform file to include non-policy parameters
  [[#1083](https://github.com/PSLmodels/Tax-Calculator/pull/1083)
  by Martin Holmer]
- Add ability to conduct normative expected-utility analysis
  [[#1098](https://github.com/PSLmodels/Tax-Calculator/pull/1098)
  by Martin Holmer]
- Add ability to compute MTR with respect to charitable cash
  contributions
  [[#1104](https://github.com/PSLmodels/Tax-Calculator/pull/1104)
  by Cody Kallen]
- Unify environment definition by removing requirements.txt
  [[#1094](https://github.com/PSLmodels/Tax-Calculator/pull/1094)
  by Zach Risher]
- Reorganize current_law_policy.json and add section headers
  [[#1109](https://github.com/PSLmodels/Tax-Calculator/pull/1109)
  by Matt Jensen]
- Add dollar limit on itemized deductions
  [[#1084](https://github.com/PSLmodels/Tax-Calculator/pull/1084)
  by Cody Kallen]
- Add testing for Windows with Appveyor
  [[#1111](https://github.com/PSLmodels/Tax-Calculator/pull/1111)
  by T.J. Alumbaugh]

**Bug Fixes**
- Fix capital-gains-reform bug reported by Cody Kallen
  [[#1088](https://github.com/PSLmodels/Tax-Calculator/pull/1088)
  by Martin Holmer]
- Provide Pandas 0.19.1 compatibility by fixing DataFrame.to_csv()
  usage
  [[#1092](https://github.com/PSLmodels/Tax-Calculator/pull/1092)
  by Zach Risher]


2016-12-05 Release 0.7.2
------------------------
(last merged pull request is
[#1082](https://github.com/PSLmodels/Tax-Calculator/pull/1082))

**API Changes**
- None

**New Features**
- Add ability to simulate non-refundable dependent credit
  [[#1069](https://github.com/PSLmodels/Tax-Calculator/pull/1069)
  by Cody Kallen]
- Add ability to narrow investment income exclusion base
  [[#1072](https://github.com/PSLmodels/Tax-Calculator/pull/1072)
  by Martin Holmer]
- Replace use of two cmbtp_* variables with a single cmbtp variable
  [[#1077](https://github.com/PSLmodels/Tax-Calculator/pull/1077)
  by Martin Holmer],
  which requires new `puf.csv` input file with this information:
  * Byte size: 50953138
  * MD5 checksum: acbf905c8b7d29fd4b06b13e1cc8a60c

**Bug Fixes**
- None


2016-11-15 Release 0.7.1
------------------------
(last merged pull request is
[#1060](https://github.com/PSLmodels/Tax-Calculator/pull/1060))

**API Changes**
- Rename policy parameters for consistency
  [[#1051](https://github.com/PSLmodels/Tax-Calculator/pull/1051)
  by Martin Holmer]

**New Features**
- Add ability to simulate broader range of refundable CTC reforms
  [[#1055](https://github.com/PSLmodels/Tax-Calculator/pull/1055)
  by Matt Jensen]
- Add more income items into expanded_income variable
  [[#1057](https://github.com/PSLmodels/Tax-Calculator/pull/1057)
  by Martin Holmer]

**Bug Fixes**
- None


2016-11-09 Release 0.7.0
------------------------
(last merged pull request is
[#1044](https://github.com/PSLmodels/Tax-Calculator/pull/1044))

**API Changes**
- Rename and refactor old add_weighted_decile_bins utility function
  [[#1043](https://github.com/PSLmodels/Tax-Calculator/pull/1043)
  by Martin Holmer]

**New Features**
- None

**Bug Fixes**
- Remove unused argument from means_and_comparisons utility function
  [[#1044](https://github.com/PSLmodels/Tax-Calculator/pull/1044)
  by Martin Holmer]


2016-11-09 Release 0.6.9
------------------------
(last merged pull request is
[#1039](https://github.com/PSLmodels/Tax-Calculator/pull/1039))

**API Changes**
- None

**New Features**
- Add calculation of MTR wrt e26270, partnership & S-corp income
  [[#987](https://github.com/PSLmodels/Tax-Calculator/pull/987)
  by Cody Kallen]
- Add utility function that plots marginal tax rates by percentile
  [[#948](https://github.com/PSLmodels/Tax-Calculator/pull/948)
  by Sean Wang]
- Add ability to simulate Trump-style dependent care credit
  [[#999](https://github.com/PSLmodels/Tax-Calculator/pull/999)
  by Anderson Frailey]
- Add ability to simulate Clinton-style NIIT reform
  [[#1012](https://github.com/PSLmodels/Tax-Calculator/pull/1012)
  by Martin Holmer]
- Add ability to simulate Clinton-style CTC expansion
  [[#1039](https://github.com/PSLmodels/Tax-Calculator/pull/1039)
  by Matt Jensen]

**Bug Fixes**
- Fix bug in TaxGains function
  [[#981](https://github.com/PSLmodels/Tax-Calculator/pull/981)
  by Cody Kallen]
- Fix bug in multiyear_diagnostic_table utility function
  [[#988](https://github.com/PSLmodels/Tax-Calculator/pull/988)
  by Matt Jensen]
- Fix AMT bug that ignored value of AMT_CG_rt1 parameter
  [[#1000](https://github.com/PSLmodels/Tax-Calculator/pull/1000)
  by Martin Holmer]
- Fix several other minor AMT CG bugs
  [[#1001](https://github.com/PSLmodels/Tax-Calculator/pull/1001)
  by Martin Holmer]
- Move self-employment tax from income tax total to payroll tax total
  [[#1021](https://github.com/PSLmodels/Tax-Calculator/pull/1021)
  by Martin Holmer]
- Add half of self-employment tax to expanded income
  [[#1032](https://github.com/PSLmodels/Tax-Calculator/pull/1032)
  by Martin Holmer]


2016-10-07 Release 0.6.8
------------------------
(last merged pull request is
[#970](https://github.com/PSLmodels/Tax-Calculator/pull/970))

**API Changes**
- None

**New Features**
- Add ability to simulate reforms that limit benefit of itemized
  deductions
  [[#867](https://github.com/PSLmodels/Tax-Calculator/pull/867)
  by Matt Jensen]
- Add investment income exclusion policy parameter
  [[#972](https://github.com/PSLmodels/Tax-Calculator/pull/972)
  by Cody Kallen]
- Add ability to eliminate differential tax treatment of LTCG+QDIV
  income
  [[#973](https://github.com/PSLmodels/Tax-Calculator/pull/973)
  by Martin Holmer]

**Bug Fixes**
- None


2016-09-29 Release 0.6.7
------------------------
(last merged pull request is
[#945](https://github.com/PSLmodels/Tax-Calculator/pull/945))

**API Changes**
- None

**New Features**
- Add extra income tax brackets and rates
  [[#858](https://github.com/PSLmodels/Tax-Calculator/pull/858),
  Sean Wang]
- Add ability to simulate Fair Share Tax, or Buffet Rule, reforms
  [[#904](https://github.com/PSLmodels/Tax-Calculator/pull/904)
  by Anderson Frailey]
- Add ability to tax pass-through income at different rates
  [[#913](https://github.com/PSLmodels/Tax-Calculator/pull/913)
  by Sean Wang]
- Add itemized-deduction surtax exemption policy parameter
  [[#926](https://github.com/PSLmodels/Tax-Calculator/pull/926)
  by Matt Jensen]
- Add ability to simulate high-AGI surtax reforms
  [[#939](https://github.com/PSLmodels/Tax-Calculator/pull/939)
  by Sean Wang]

**Bug Fixes**
- Correct Net Investment Income Tax (NIIT) calculation
  [[#874](https://github.com/PSLmodels/Tax-Calculator/pull/874)
  by Martin Holmer]
- Correct Schedule R credit calculation
  [[#898](https://github.com/PSLmodels/Tax-Calculator/pull/898)
  by Martin Holmer]
- Remove logic for expired First-Time Homebuyer Credit
  [[#914](https://github.com/PSLmodels/Tax-Calculator/pull/914)
  by Martin Holmer]


2016-08-13 Release 0.6.6
------------------------
(last merged pull request is
[#844](https://github.com/PSLmodels/Tax-Calculator/pull/844))

**API Changes**
- None

**New Features**
- Revise code to use smaller `puf.csv` input file and make changes to
  create that input file
- Remove debugging variables from functions.py reducing execution time
  by 42 percent
  [[#833](https://github.com/PSLmodels/Tax-Calculator/pull/833)]
- Add comments to show one way to use Python debugger to trace
  Tax-Calculator code
  [[#835](https://github.com/PSLmodels/Tax-Calculator/pull/835)]
- Add tests that confirm zeroing-out CALCULATED_VARS at start leaves
  results unchanged
  [[#837](https://github.com/PSLmodels/Tax-Calculator/pull/837)]
- Revise logic used to estimate behavioral responses to policy reforms
  [[#846](https://github.com/PSLmodels/Tax-Calculator/pull/846),
  [#854](https://github.com/PSLmodels/Tax-Calculator/pull/854)
  and
  [#857](https://github.com/PSLmodels/Tax-Calculator/pull/857)]

**Bug Fixes**
- Make 2013-2016 medical deduction threshold for elderly be 7.5% of
  AGI (not 10%)
  [[#839](https://github.com/PSLmodels/Tax-Calculator/pull/839)]
- Fix typo so that two ways of limiting itemized deductions produce
  the same results
  [[#842](https://github.com/PSLmodels/Tax-Calculator/pull/842)]


2016-07-12 Release 0.6.5
------------------------
(last merged pull request is
[#820](https://github.com/PSLmodels/Tax-Calculator/pull/820))

**API Changes**
- None

**New Features**
- Add --exact option to simtax.py and inctax.py scripts
- Add calculation of Schedule R credit
- Remove _cmp variable from functions.py code

**Bug Fixes**
- Fix itemized deduction logic for charity
- Remove Numba dependency


2016-06-17 Release 0.6.4
------------------------
(last merged pull request is
[#794](https://github.com/PSLmodels/Tax-Calculator/pull/794))

**API Changes**
- Create Consumption class used to compute "effective" marginal tax rates

**New Features**
- Revise Behavior class logic
- Add unit tests to increase code coverage to 98 percent
- Add scripts to version and release

**Bug Fixes**
- Test TaxBrain handling of delayed reforms
- Move cmbtp calculation and earnings splitting logic from Records
  class to `puf.csv` file preparation
- Update Numpy and Pandas dependencies to latest versions to avoid a
  bug in the Windows conda package for Pandas 0.16.2


2016-05-09 Release 0.6.3
------------------------
(last merged pull request is
[#727](https://github.com/PSLmodels/Tax-Calculator/pull/727))

**API Changes**
- None

**New Features**
- Add --records option to simtax.py
- Add --csvdump option to inctax.py
- Add three "d" samples to Tax-Calculator versus Internet-TAXSIM comparisons
- Add first set of Tax-Calculator versus TaxBrain comparisons
- Add data and logic to implement EITC age-eligibility rules
- Update and fix 10_minutes_to_Tax-Calculator.ipynb
- Update files in taxcalc/comparison

**Bug Fixes**
- Fix Child Care Expense logic
- Exclude dependents from EITC eligibility


Before Release 0.6.2
--------------------
See commit history for pull requests before
[#650](https://github.com/PSLmodels/Tax-Calculator/pull/650)
