#
# Need the hatch tool to run this Makefile.
#
# pipx install hatch
#

# Default OBO file.
URL = http://current.geneontology.org/ontology/go-basic.obo
OBO = tmp/go-basic.obo

# Usage information.
usage:
	@echo "#"
	@echo "# Use the source, Luke!"
	@echo "#"

# Performs the testing.
web:
	python src/genescape/server.py

# Performs the testing.
test:
	(cd test && make test)

# Runs a linter.
lint:
	hatch run lint:style

docs:
	genescape tree -o docs/images/genescape-output1.png src/genescape/data/test_genes.txt 
	genescape tree -o docs/images/genescape-output2.png src/genescape/data/test_goids.txt 
	genescape tree -m lipid -o docs/images/genescape-output3.png src/genescape/data/test_goids.txt 
# Fix linting errors.
fix:
	hatch run lint:fmt

push:
	git commit -am 'saving work' && git push

VERSION ?= $(shell grep '__version__' src/genescape/__about__.py | sed "s/__version__ = \"\\(.*\\)\"/\1/" | tr -d '.')

NAME ?= GeneScape-${VERSION}

mac:

	# Example of generating a tag file with the version
	@echo "VERSION=${VERSION}"

	rm -rf build dist
	pyinstaller src/genescape/server.py \
		--add-data=src/genescape/data:genescape/data \
		-i docs/images/logo.ico -n ${NAME} -y --onefile
	(cd dist && zip ${NAME}-MacOS.zip ${NAME} && rm -f ${NAME})


clean:
	rm -f src/genescape/web/static/tmp/image*

realclean: clean
	rm -rf build dist

build:
	rm -rf build dist
	hatch build 
	ls -lh dist

pypi: build
	hatch publish

$(OBO):
	mkdir -p $(dir $(OBO))
	curl -L $(URL) > $(OBO)

get: $(OBO)
	@ls -l $(OBO)

.PHONY: test docs lint fix push demo clean realclean build pypi get
