# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
PYTHON        = python3
SPHINXBUILD   = $(PYTHON) -m sphinx.cmd.build
SPHINXOPTS    = --fail-on-warning
BUILDDIR      = _build
BUILDER       = html
JOBS          = auto
PAPER         =

# Internal variables.
PAPEROPT_a4     = --define latex_paper_size=a4
PAPEROPT_letter = --define latex_paper_size=letter

ALLSPHINXOPTS   = --builder $(BUILDER) \
                  --doctree-dir $(BUILDDIR)/doctrees \
                  --jobs $(JOBS) \
                  $(PAPEROPT_$(PAPER)) \
                  $(SPHINXOPTS) \
                  . $(BUILDDIR)/$(BUILDER)

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"
	@echo "  htmlview   to open the index page built by the html target in your browser"
	@echo "  htmllive   to rebuild and reload HTML files in your browser"
	@echo "  serve      to start a local server for viewing docs"
	@echo "  dirhtml    to make HTML files named index.html in directories"
	@echo "  singlehtml to make a single large HTML file"
	@echo "  linkcheck  to check all external links for integrity"

.PHONY: clean
clean:
	-rm -rf $(BUILDDIR)/*

install-sphinx:
	$(PYTHON) -m pip install -e ..[docs]

.PHONY: html
html:
	$(MAKE) install-sphinx
	$(SPHINXBUILD) $(ALLSPHINXOPTS)

.PHONY: dirhtml
dirhtml: BUILDER = dirhtml
dirhtml: html

.PHONY: singlehtml
singlehtml: BUILDER = singlehtml
singlehtml: html

.PHONY: linkcheck
linkcheck: BUILDER = linkcheck
linkcheck: html

.PHONY: htmlview
htmlview: html
	$(PYTHON) -c "import os, webbrowser; webbrowser.open('file://' + os.path.realpath('$(BUILDDIR)/html/index.html'))"

.PHONY: htmllive
htmllive: SPHINXBUILD = $(PYTHON) -m sphinx_autobuild
htmllive: SPHINXOPTS = --open-browser --delay 0
htmllive: html

.PHONY: serve
serve:
	cd $(BUILDDIR)/html; $(PYTHON) -m http.server
