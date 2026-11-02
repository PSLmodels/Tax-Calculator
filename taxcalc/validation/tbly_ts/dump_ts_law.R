# Writes the Tax-Simulator baseline tax law for one year, before any
# ts_law_overrides.csv replacements, in long form (called by
# build_overrides.py).
#
# USAGE: Rscript --vanilla dump_ts_law.R TSDIR YEAR INDEXES OUTFILE
#
#   TSDIR      Tax-Simulator clone at the commit pinned in ts_pin.json
#   YEAR       tax year
#   INDEXES    ts_indexes.csv (series, year, growth)
#   OUTFILE    csv to write, with columns year, filing_status,
#              variable, and ts_value, containing every numeric
#              Tax-Simulator law column
#
# The law is built exactly as in run_ts.R.  Tax-Simulator code is
# sourced but never modified.

args = commandArgs(trailingOnly = TRUE)
if (length(args) != 4) {
  stop('usage: Rscript --vanilla dump_ts_law.R TSDIR YEAR INDEXES OUTFILE')
}
ts_dir    = normalizePath(args[1], mustWork = TRUE)
year      = as.integer(args[2])
idx_file  = normalizePath(args[3], mustWork = TRUE)
outfile   = file.path(normalizePath(dirname(args[4]), mustWork = TRUE),
                      basename(args[4]))

suppressPackageStartupMessages({
  for (pkg in c('tidyverse', 'magrittr', 'rlang', 'yaml', 'data.table')) {
    library(pkg, character.only = TRUE)
  }
})
options(warn = 2)  # treat warnings as errors

# load the same Tax-Simulator source set as run_ts.R
setwd(ts_dir)
return_vars = list()
ts_sources = c(list.files('src/calc', recursive = TRUE,
                          pattern = '\\.[Rr]$', full.names = TRUE),
               'src/data/tax_law.R', 'src/misc/utils.R')
ts_sources = ts_sources[!grepl('^src/calc/state/', ts_sources)]
for (src in ts_sources) source(src)

indexes = read_csv(idx_file, show_col_types = FALSE, progress = FALSE)
law = build_tax_law_from_id('baseline', year, indexes)
law %>%
  filter(year == !!year) %>%
  select(year, filing_status, where(is.numeric)) %>%
  pivot_longer(-c(year, filing_status),
               names_to = 'variable', values_to = 'ts_value') %>%
  arrange(variable, filing_status) %>%
  write_csv(outfile)
