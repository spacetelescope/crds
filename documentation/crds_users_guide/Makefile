# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = python -msphinx
SPHINXPROJ    = CRDS
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

tarhtml: html
	mv $(BUILDDIR)/html  users_guide
	tar zcf users_guide.tar.gz users_guide
	rm -rf users_guide

 serverhtml: tarhtml
	mv users_guide.tar.gz ../../../CRDS_server/sources/static
	cd ../../../CRDS_server/sources/static; \
	tar zxf users_guide.tar.gz; \
	rm users_guide.tar.gz

