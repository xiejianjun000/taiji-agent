# govmcp Sphinx Documentation Makefile

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build
APIDOCDIR     = source/api

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

html: api-docs
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

html-noplot: Makefile
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

dirhtml:
	@$(SPHINXBUILD) -b dirhtml "$(SOURCEDIR)" "$(BUILDDIR)/dirhtml" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/dirhtml."

singlehtml:
	@$(SPHINXBUILD) -b singlehtml "$(SOURCEDIR)" "$(BUILDDIR)/singlehtml" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The HTML page is in $(BUILDDIR)/singlehtml."

pickle:
	@$(SPHINXBUILD) -b pickle "$(SOURCEDIR)" "$(BUILDDIR)/pickle" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished; now you can process the pickle files."

json:
	@$(SPHINXBUILD) -b json "$(SOURCEDIR)" "$(BUILDDIR)/json" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished; now you can process the JSON files."

htmlhelp:
	@$(SPHINXBUILD) -b htmlhelp "$(SOURCEDIR)" "$(BUILDDIR)/htmlhelp" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished; now you can run HTML Help Workshop with the" \
	      ".hhp project file in $(BUILDDIR)/htmlhelp."

qthelp:
	@$(SPHINXBUILD) -b qthelp "$(SOURCEDIR)" "$(BUILDDIR)/qthelp" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished; now you can run "qcollectiongenerator" with the" \
	      ".qhcp project file in $(BUILDDIR)/qthelp, like this:"
	@echo "# qcollectiongenerator $(BUILDDIR)/qthelp/govmcp.qhcp"
	@echo "# To view the help file:"
	@echo "# assistant -collectionFile $(BUILDDIR)/qthelp/govmcp.qhcp"

devhelp:
	@$(SPHINXBUILD) -b devhelp "$(SOURCEDIR)" "$(BUILDDIR)/devhelp" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished."
	@echo
	@echo "To view the help file you must install "make-devhelp"."
	@echo "# apt-get install sphinx-doc"

epub:
	@$(SPHINXBUILD) -b epub "$(SOURCEDIR)" "$(BUILDDIR)/epub" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The epub files are in $(BUILDDIR)/epub."

latex:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished; the LaTeX files are in $(BUILDDIR)/latex."
	@echo "Run \`make all-pdf\` or \`make all-ps\` in that directory to" \
	      "produce various PDF documents."

latexpdf:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex" $(SPHINXOPTS) $(O)
	@echo "Running LaTeX files through pdflatex..."
	$(MAKE) -C "$(BUILDDIR)/latex" all-pdf
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex."

latexpdfja:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex" $(SPHINXOPTS) $(O)
	@echo "Running LaTeX files through platex and dvipdfmx..."
	$(MAKE) -C "$(BUILDDIR)/latex" all-pdf-ja
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex."

text:
	@$(SPHINXBUILD) -b text "$(SOURCEDIR)" "$(BUILDDIR)/text" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The text files are in $(BUILDDIR)/text."

man:
	@$(SPHINXBUILD) -b man "$(SOURCEDIR)" "$(BUILDDIR)/man" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The manual pages are in $(BUILDDIR)/man."

texinfo:
	@$(SPHINXBUILD) -b texinfo "$(SOURCEDIR)" "$(BUILDDIR)/texinfo" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The Texinfo files are in $(BUILDDIR)/texinfo."
	@echo "Run \`make\' in that directory to produce the info file."

info:
	@$(SPHINXBUILD) -b texinfo "$(SOURCEDIR)" "$(BUILDDIR)/texinfo" $(SPHINXOPTS) $(O)
	@echo "Running TeXinfo files through makeinfo..."
	make -C "$(BUILDDIR)/texinfo" info
	@echo "makeinfo finished; the Info files are in $(BUILDDIR)/texinfo."

gettext:
	@$(SPHINXBUILD) -b gettext "$(SOURCEDIR)" "$(BUILDDIR)/gettext" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The message catalogs are in $(BUILDDIR)/gettext."

changes:
	@$(SPHINXBUILD) -b changes "$(SOURCEDIR)" "$(BUILDDIR)/changes" $(SPHINXOPTS) $(O)
	@echo
	@echo "The overview file is in $(BUILDDIR)/changes."

linkcheck:
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS) $(O)
	@echo
	@echo "Link check complete. Look at $(BUILDDIR)/linkcheck/output.txt."

doctest:
	@$(SPHINXBUILD) -b doctest "$(SOURCEDIR)" "$(BUILDDIR)/doctest" $(SPHINXOPTS) $(O)
	@echo
	@echo "Testing of doctests in the sources finished, look at the" \
	      "renderer output in $(BUILDDIR)/doctest/output.txt."

xml:
	@$(SPHINXBUILD) -b xml "$(SOURCEDIR)" "$(BUILDDIR)/xml" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The XML files are in $(BUILDDIR)/xml."

pseudoepub:
	@$(SPHINXBUILD) -b pseudoepub "$(SOURCEDIR)" "$(BUILDDIR)/pseudoepub" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The pseudo-epub files are in $(BUILDDIR)/pseudoepub."

clean:
	rm -rf $(BUILDDIR)/*

clean-api:
	rm -rf $(APIDOCDIR)/*

api-docs: clean-api
	@echo "Generating API documentation..."
	@python -m sphinx.ext.apidoc -f -o $(APIDOCDIR) ../govmcp

build: api-docs html

serve:
	@python -m http.server 8000 -b 127.0.0.1 -d $(BUILDDIR)/html

livehtml:
	@sphinx-autobuild -b html $(SOURCEDIR) $(BUILDDIR)/html $(SPHINXOPTS)

.DEFAULT_GOAL := html
