#
# Need the hatch tool to run this Makefile.
#
# pipx install hatch
#

# Default OBO file.
OBO_URL = http://current.geneontology.org/ontology/go-basic.obo
OBO_FILE = obo/go-basic.obo

# The gene association file.
GAF_URL = https://current.geneontology.org/annotations/goa_human.gaf.gz
GAF_FILE = obo/goa_human.gaf.gz

# The index file.
IDX_FILE = obo/genescape.index.gz

# Makefile customizations
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# Usage information.
usage:
	@echo "#"
	@echo "# Use the source, Luke!"
	@echo "#"

# Performs the testing.
web:
	shiny run --reload genescape.web:app

# Tag and push to repository.
tag: test
	python src/genescape/exe.py --tag

# Build the executable.
exe: test
	python src/genescape/exe.py --build

shiny: test
	pip install rsconnect
	rsconnect deploy shiny src/genescape --name biostar --title GeneScape

# Generate images for the documentation
docimg:
	genescape tree -o docs/images/genescape-output1a.png src/genescape/data/test_genes.txt
	genescape tree -o docs/images/genescape-output2a.png src/genescape/data/test_goids.txt
	genescape tree -m lipid -o docs/images/genescape-output3a.png src/genescape/data/test_goids.txt

# Runs a linter.
lint:
	hatch run lint:style

# Fix linting errors.
fix:
	hatch run lint:fmt

# Save work.
push:
	git commit -am 'saving work' && git push



build: clean
	rm -rf build dist
	hatch build 
	ls -lh dist

publish: build
	hatch publish

# Download the gene ontology file
${OBO_FILE}:
	mkdir -p $(dir ${OBO_FILE})
	curl -L ${OBO_URL} > ${OBO_FILE}

${GAF_FILE}:
	mkdir -p $(dir ${GAF_FILE})
	curl -L ${GAF_URL} > ${GAF_FILE}

${IDX_FILE}: ${OBO_FILE} ${GAF_FILE}
	hatch run genescape build --obo ${OBO_FILE} --gaf ${GAF_FILE} --index ${IDX_FILE}

obo: ${OBO_FILE}
	ls -lh ${OBO_FILE}

gaf: ${GAF_FILE}
	ls -lh ${GAF_FILE}

index: ${IDX_FILE}
	ls -lh ${IDX_FILE}

# Performs a python-only test.
test:
	hatch run test

# A full test with file generation.
testall: test
	(cd test && make testall)

clean:
	rm -rf build dist ${IDX_FILE}

env:
	conda create -n genescape python=3.11 shiny rsconnect graphviz

.PHONY: test lint fix push clean build publish obo docimg web
