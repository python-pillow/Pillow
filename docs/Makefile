# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
PYTHON        = python3
SPHINXOPTS    =
SPHINXBUILD   = $(PYTHON) -m sphinx.cmd.build
PAPER         =
BUILDDIR      = _build

# Internal variables.
PAPEROPT_a4     = --define latex_paper_size=a4
PAPEROPT_letter = --define latex_paper_size=letter
ALLSPHINXOPTS   = --doctree-dir $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

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
	$(SPHINXBUILD) --builder html --fail-on-warning --keep-going $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

.PHONY: dirhtml
dirhtml:
	$(MAKE) install-sphinx
	$(SPHINXBUILD) --builder dirhtml $(ALLSPHINXOPTS) $(BUILDDIR)/dirhtml
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/dirhtml."

.PHONY: singlehtml
singlehtml:
	$(MAKE) install-sphinx
	$(SPHINXBUILD) --builder singlehtml $(ALLSPHINXOPTS) $(BUILDDIR)/singlehtml
	@echo
	@echo "Build finished. The HTML page is in $(BUILDDIR)/singlehtml."

.PHONY: linkcheck
linkcheck:
	$(MAKE) install-sphinx
	$(SPHINXBUILD) --builder linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck -j auto
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in $(BUILDDIR)/linkcheck/output.txt."

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
