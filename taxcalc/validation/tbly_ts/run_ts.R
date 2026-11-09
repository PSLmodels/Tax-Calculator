# Runs the Tax-Simulator federal calculator on a TAXSIM-35 input sample
# (the R part of step 2 of the validation; called by run_ts.py).
#
# USAGE: Rscript --vanilla run_ts.R TSDIR INFILE OUTFILE INDEXES OVERRIDES
#
#   TSDIR      Tax-Simulator clone at the commit pinned in ts_pin.json
#   INFILE     TAXSIM-35 input sample (csv or csv.gz) for a single year
#   OUTFILE    TAXSIM-format output csv to write
#   INDEXES    ts_indexes.csv (series, year, growth)
#   OVERRIDES  ts_law_overrides.csv (year, filing_status, variable,
#              value, ts_value)
#
# The translation of TAXSIM input into Tax-Simulator tax units and of
# Tax-Simulator output into TAXSIM output follows VARIABLES.md.
# Tax-Simulator code is sourced but never modified.

args = commandArgs(trailingOnly = TRUE)
if (length(args) != 5) {
  stop('usage: Rscript --vanilla run_ts.R ',
       'TSDIR INFILE OUTFILE INDEXES OVERRIDES')
}
ts_dir    = normalizePath(args[1], mustWork = TRUE)
infile    = normalizePath(args[2], mustWork = TRUE)
outfile   = file.path(normalizePath(dirname(args[3]), mustWork = TRUE),
                      basename(args[3]))
idx_file  = normalizePath(args[4], mustWork = TRUE)
ovr_file  = normalizePath(args[5], mustWork = TRUE)

suppressPackageStartupMessages({
  for (pkg in c('tidyverse', 'magrittr', 'rlang', 'yaml', 'data.table')) {
    library(pkg, character.only = TRUE)
  }
})
options(warn = 2)  # treat warnings as errors


#--------------------------------------------------------------------
# Load the minimal Tax-Simulator source set (see ts_pin.json); TS uses
# paths relative to the top of its repository
#--------------------------------------------------------------------
setwd(ts_dir)
return_vars = list()
ts_sources = c(list.files('src/calc', recursive = TRUE,
                          pattern = '\\.[Rr]$', full.names = TRUE),
               'src/data/tax_law.R', 'src/misc/utils.R')
ts_sources = ts_sources[!grepl('^src/calc/state/', ts_sources)]
for (src in ts_sources) source(src)


#--------------------------------------------------------------------
# Read and check the TAXSIM-35 input sample
#--------------------------------------------------------------------
smpl = read_csv(infile, show_col_types = FALSE, progress = FALSE)
year = unique(smpl$year)
errors = c()
require_that = function(condition, msg) {
  if (!isTRUE(condition)) errors <<- c(errors, msg)
}
require_that(length(year) == 1, 'sample contains more than one year')
require_that(all(smpl$state == 0), 'state not always zero')
require_that(all(smpl$mstat %in% c(1, 2, 6)), 'mstat not always 1, 2, or 6')
require_that(all(smpl$depx >= 0 & smpl$depx <= 3), 'depx not in [0,3]')
require_that(!any(smpl$mstat == 6 & smpl$depx > 0),
             'mstat 6 with dependents')
# TAXSIM inputs that have no Tax-Simulator translation (VARIABLES.md)
must_be_zero = c('nonprop', 'transfers', 'rentpaid', 'pprofinc',
                 'sprofinc', 'age4', 'age5')
for (var in must_be_zero) {
  require_that(all(smpl[[var]] == 0),
               paste0('nonzero values of untranslated ', var))
}
# spouse variables must be zero for non-joint units
for (var in c('sage', 'swages', 'ssemp', 'sbusinc', 'sui')) {
  require_that(all(smpl[[var]][smpl$mstat != 2] == 0),
               paste0('nonzero ', var, ' for non-joint unit'))
}
require_that(!anyNA(smpl), 'missing values in sample')
if (length(errors) > 0) {
  stop('TAXSIM input check failed: ', paste(errors, collapse = '; '))
}


#--------------------------------------------------------------------
# Build the tax law for YEAR and apply the published-value overrides
#--------------------------------------------------------------------
indexes = read_csv(idx_file, show_col_types = FALSE, progress = FALSE)
law = build_tax_law_from_id('default', year, indexes)
overrides = read_csv(ovr_file, show_col_types = FALSE, progress = FALSE) %>%
  filter(year == !!year)
for (i in seq_len(nrow(overrides))) {
  ovr = overrides[i, ]
  if (!(ovr$variable %in% names(law))) {
    stop('override variable ', ovr$variable, ' is not a TS law column')
  }
  row = which(law$year == ovr$year & law$filing_status == ovr$filing_status)
  if (length(row) != 1) {
    stop('no unique law row for override ', ovr$variable)
  }
  # the TS value must be the one recorded when the override was made,
  # so that a change in the pin or in ts_indexes.csv is not hidden
  if (law[[ovr$variable]][row] != ovr$ts_value) {
    stop('TS value of ', ovr$variable, ' for ', ovr$year, ' filing status ',
         ovr$filing_status, ' is ', law[[ovr$variable]][row],
         ' but ts_law_overrides.csv has ts_value ', ovr$ts_value)
  }
  law[[ovr$variable]][row] = ovr$value
}


#--------------------------------------------------------------------
# Translate the sample into Tax-Simulator tax units (VARIABLES.md)
#--------------------------------------------------------------------

# dependent ages, youngest first, NA for absent dependents
ages = as.matrix(smpl[, c('age1', 'age2', 'age3')])
ages[col(ages) > smpl$depx] = NA
ages = t(apply(ages, 1, function(a) sort(a, na.last = TRUE)))
present = !is.na(ages)
joint = smpl$mstat == 2

units = tibble(
  id             = smpl$taxsimid,
  year           = smpl$year,
  filing_status  = case_when(joint ~ 2,
                             smpl$mstat == 6 ~ 3,
                             smpl$depx > 0 ~ 4,
                             TRUE ~ 1),
  filer          = 1,
  dep_status     = 0,
  age1           = smpl$page,
  age2           = if_else(joint, smpl$sage, NA_real_),
  blind1         = 0,
  blind2         = if_else(joint, 0, NA_real_),
  n_dep          = smpl$depx,
  dep_age1       = ages[, 1],
  dep_age2       = ages[, 2],
  dep_age3       = ages[, 3],
  dep_ctc1       = if_else(present[, 1], 1, NA_real_),
  dep_ctc2       = if_else(present[, 2], 1, NA_real_),
  dep_ctc3       = if_else(present[, 3], 1, NA_real_),
  dep_ssn1       = dep_ctc1,
  dep_ssn2       = dep_ctc2,
  dep_ssn3       = dep_ctc3,
  n_dep_eitc     = rowSums(present & ages < 19, na.rm = TRUE),
  wages1         = smpl$pwages,
  wages2         = smpl$swages,
  wages          = wages1 + wages2,
  sole_prop1     = smpl$psemp + smpl$pbusinc,
  sole_prop2     = smpl$ssemp + smpl$sbusinc,
  sole_prop      = sole_prop1 + sole_prop2,
  scorp_active   = smpl$scorp,
  rent           = smpl$otherprop,
  div_pref       = smpl$dividends,
  div_ord        = 0,
  txbl_int       = smpl$intrec,
  kg_st          = smpl$stcg,
  kg_lt          = smpl$ltcg,
  txbl_pens_dist = smpl$pensions,
  gross_pens_dist = smpl$pensions,
  txbl_ira_dist  = 0,
  gross_ss       = smpl$gssi,
  ui             = smpl$pui + smpl$sui,
  salt_prop      = smpl$proptax,
  salt_inc_sales = 0,
  salt_pers      = 0,
  # fully deductible, outside the SALT cap, no AMT add-back (VARIABLES.md)
  other_item_exp = smpl$mortgage + smpl$otheritem,
  care_exp       = smpl$childcare,
  # random draws: zero means full CDCTC take-up and no EITC
  # pre-certification check (set explicitly, not by zero-fill)
  r.bus_loss     = 0,
  r.new_car      = 0,
  r.cdctc_takeup = 0,
  r.eitc_precert = 0,
  salt_workaround_part  = 0,
  salt_workaround_scorp = 0
)

# all other exogenous Tax-Simulator inputs are zero
zero_vars = c(
  'alimony', 'alimony_exp', 'amt_ftc', 'amt_nols', 'aoc_exp',
  'auto_int_exp', 'caregiver_exp1', 'caregiver_exp2', 'casualty_exp',
  'char_cash', 'char_noncash', 'divorce_year', 'dpad', 'early_penalty',
  'ed_exp', 'ei_prior_yr', 'estate', 'estate_loss', 'excess_ptc',
  'exempt_int', 'farm', 'farm1', 'farm2', 'first_mort_bal',
  'first_mort_int', 'first_mort_year', 'ftc', 'gbc', 'hsa_contr',
  'inv_int_exp', 'ira_penalty', 'job_exp', 'keogh_contr', 'kg_1250',
  'kg_collect', 'kg_lt_basis', 'kg_lt_cpi_ratio', 'kg_lt_years_held',
  'llc_exp', 'med_exp', 'net_ptc', 'old_cred', 'ot1', 'ot2',
  'other_above_ded', 'other_gains', 'other_inc', 'other_misc_exp',
  'other_nonref', 'part_179', 'part_active', 'part_active_loss',
  'part_passive', 'part_passive_loss', 'part_se1', 'part_se2',
  'prior_yr_cred', 'recapture_tax', 'rent_loss', 'res_energy_cred',
  'savers_cred', 'scorp_179', 'scorp_active_loss', 'scorp_passive',
  'scorp_passive_loss', 'se_health', 'second_mort_bal',
  'second_mort_int', 'second_mort_year', 'sl_int_ded', 'sstb_farm',
  'sstb_part', 'sstb_scorp', 'sstb_sole_prop', 'state_ref',
  'tax_prep_exp', 'tips1', 'tips2', 'tips_lh1', 'tips_lh2',
  'trad_contr_er1', 'trad_contr_er2', 'trad_contr_ira', 'tuition_ded',
  'wagebill_farm', 'wagebill_part', 'wagebill_scorp',
  'wagebill_sole_prop'
)
for (var in zero_vars) units[[var]] = 0

tax_units = units %>% left_join(law, by = c('year', 'filing_status'))
if (anyNA(tax_units$ord.rates1)) stop('tax-law join failed')


#--------------------------------------------------------------------
# Calculate taxes and write TAXSIM-format output (VARIABLES.md)
#--------------------------------------------------------------------
# estate and wealth taxes are not income or payroll taxes, so skip them
res = do_taxes(tax_units, NULL, fed_calc_vars(incl_payroll = FALSE),
               return_vars$calc_pr,
               calc_estate_flag = FALSE, calc_wealth_flag = FALSE)
if (nrow(res) != nrow(tax_units) || !identical(res$id, tax_units$id)) {
  stop('do_taxes output rows differ from input rows')
}

out = tibble(
  taxsimid = res$id,
  year     = res$year,
  fiitax   = res$liab_iit_net,
  fica     = res$liab_pr,
  tfica    = res$liab_pr - res$liab_fica_er1 - res$liab_fica_er2,
  addmed   = res$liab_add_med,
  v44      = tax_units$pr.hi_ee_rates * tax_units$wages + res$liab_add_med,
  v10      = res$agi,
  v11      = tax_units$ui,
  v12      = res$txbl_ss,
  v13      = res$std_ded,
  v14      = res$pe_ded,
  v17      = res$item_ded,
  qbid     = res$qbi_ded,
  v18      = res$txbl_inc,
  v19      = res$liab_ord,
  v28      = res$liab,
  v26      = res$amt_gross_inc,
  v27      = res$liab_amt,
  niit     = res$liab_niit,
  v22      = res$ctc_nonref,
  actc     = res$ctc_ref,
  v24      = res$cdctc_nonref + res$cdctc_ref,
  v25      = res$eitc,
  cares    = res$rebate
)
if (anyNA(out)) {
  bad = names(out)[colSums(is.na(out)) > 0]
  stop('missing values in output columns: ', paste(bad, collapse = ' '))
}
write_csv(out, outfile)
