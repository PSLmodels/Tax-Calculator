# Minimal makefile for Jupinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    = -c "./"
SPHINXBUILD   = python -msphinx
SOURCEDIR     = source
BUILDDIR      = _build
BUILDWEBSITE  = _build/website
BUILDCOVERAGE = _build/coverage
BUILDPDF      = _build/pdf
PORT          = 8888
FILES         = 

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(FILES) $(SPHINXOPTS) $(O)

.PHONY: help Makefile

preview:
ifneq (,$(filter $(target),website Website))
	cd $(BUILDWEBSITE)/jupyter_html && python -m http.server $(PORT)
else
ifdef lecture
	cd $(BUILDDIR)/jupyter/ && jupyter notebook --port $(PORT) --port-retries=0 $(basename $(lecture)).ipynb
else
	cd $(BUILDDIR)/jupyter/ && jupyter notebook --port $(PORT) --port-retries=0
endif
endif

coverage:
ifneq ($(strip $(parallel)),)
	@$(SPHINXBUILD) -M jupyter "$(SOURCEDIR)" "$(BUILDCOVERAGE)" $(FILES) $(SPHINXOPTS) $(O) -D jupyter_make_coverage=1 -D jupyter_execute_notebooks=1 -D jupyter_ignore_skip_test=0 -D jupyter_number_workers=$(parallel) 
else
	@$(SPHINXBUILD) -M jupyter "$(SOURCEDIR)" "$(BUILDCOVERAGE)" $(FILES) $(SPHINXOPTS) $(O) -D jupyter_make_coverage=1 -D jupyter_execute_notebooks=1 -D jupyter_ignore_skip_test=0
endif

website:
ifneq ($(strip $(parallel)),)
	@$(SPHINXBUILD) -M jupyter "$(SOURCEDIR)" "$(BUILDWEBSITE)" $(FILES) $(SPHINXOPTS) $(O) -D jupyter_make_site=1 -D jupyter_generate_html=1 -D jupyter_download_nb=1 -D jupyter_execute_notebooks=1 -D jupyter_target_html=1 -D jupyter_images_markdown=0 -D jupyter_html_template="html.tpl" -D jupyter_coverage_dir=$(BUILDCOVERAGE) -D jupyter_number_workers=$(parallel)
else
	@$(SPHINXBUILD) -M jupyter "$(SOURCEDIR)" "$(BUILDWEBSITE)" $(FILES) $(SPHINXOPTS) $(O) -D jupyter_make_site=1 -D jupyter_generate_html=1 -D jupyter_download_nb=1 -D jupyter_execute_notebooks=1 -D jupyter_target_html=1 -D jupyter_images_markdown=0 -D jupyter_html_template="html.tpl" -D jupyter_coverage_dir=$(BUILDCOVERAGE)
endif

pdf:
ifneq ($(strip $(parallel)),)
	@$(SPHINXBUILD) -M jupyterpdf "$(SOURCEDIR)" "$(BUILDDIR)" $(FILES) $(SPHINXOPTS) $(O) -D jupyter_latex_template="latex.tpl" -D jupyter_images_markdown=1 -D jupyter_execute_notebooks=1 -D jupyter_target_pdf=1 -D jupyter_number_workers=$(parallel)
else
	@$(SPHINXBUILD) -M jupyterpdf "$(SOURCEDIR)" "$(BUILDDIR)" $(FILES) $(SPHINXOPTS) $(O) -D jupyter_latex_template="latex.tpl" -D jupyter_images_markdown=1 -D jupyter_execute_notebooks=1 -D jupyter_target_pdf=1
endif

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(FILES) $(SPHINXOPTS) $(O)
