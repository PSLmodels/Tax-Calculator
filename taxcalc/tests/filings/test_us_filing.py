from taxcalc.filings import USFiling
from taxcalc.records import Records


def test_us_filing():
    generated = USFiling.rvars_generated_with_forms(2015)
    used = USFiling.rvars_used_with_forms(2015)

    # TODO: reduce the size of these sets
    not_yet_generated = {
        'f6251', 'nu05', 'e00900s', 'e00200p',
        'cmbtp', 'elderly_dependent', 'e02100s', 'e00900p', 'e02100p',
        'age_spouse', 'n24', 'nu13', 'e00200s', 'filer', 'age_head'
    }
    not_yet_used = {
        '_combined',
        '_earned', '_earned_p', '_earned_s',
        '_eitc', '_exact', '_expanded_income',
        '_num',
        '_payrolltax',
        '_refund',
        '_sep', '_sey', '_standard', '_surtax',
        '_taxbc',
        'c01000', 'c02900_in_ei', 'c03260',
        'c04470', 'c04600', 'c04800', 'c05200', 'c05700', 'c05800',
        'c07100', 'c07180', 'c07200', 'c07220', 'c07230', 'c07240',
        'c07260', 'c07300', 'c07400', 'c07600',
        'c08000', 'c09200', 'c09600',
        'c10960', 'c11070', 'c19700',
        'c21040', 'c21060', 'c23650', 'c59660', 'c62100', 'c87668',
        'care_deduction', 'ctc_new',
        'dep_credit', 'dwks10', 'dwks13', 'dwks14', 'dwks19',
        'fstax',
        'ID_Casualty_frt_in_pufcsv_year', 'invinc_agi_ec', 'invinc_ec_base',
        'lumpsum_tax',
        'NIIT',
        'personal_credit',
        'pre_c04600', 'prectc', 'ptax_amc', 'ptax_oasdi', 'ptax_was',
        'setax',
        'ymod', 'ymod1',
    }

    assert generated == Records.USABLE_READ_VARS - not_yet_generated
    assert used == Records.CALCULATED_VARS - not_yet_used
