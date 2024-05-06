#
# Need the hatch tool to run this Makefile.
#
# pipx install hatch
#

# Default OBO file.
OBO_URL = http://current.geneontology.org/ontology/go-basic.obo
OBO = obo/go-basic.obo.gz

# The gene association file.
GAF_URL = https://current.geneontology.org/annotations/goa_human.gaf.gz
GAF = obo/goa_human.gaf.gz

# The index file.
IDX = genescape.index.gz

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
	shiny run --reload genescape.shiny.app:app

# Tag and push to repository.
tag: test
	python src/genescape/exe.py --tag

# Build the executable.
exe: test
	python src/genescape/exe.py --build


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
${OBO}:
	mkdir -p $(dir ${OBO})
	curl -L ${OBO_URL} | gzip -c > ${OBO}

${GAF}:
	mkdir -p $(dir ${GAF})
	curl -L ${GAF_URL} > ${GAF}

${IDX}: ${OBO} ${GAF}
	hatch run genescape build --obo ${OBO} --gaf ${GAF} --index ${IDX}

obo: ${OBO}
	ls -lh ${OBO}

gaf: ${GAF}
	ls -lh ${GAF}

index: ${IDX}
	ls -lh ${IDX}
	genescape build -s --index ${IDX}

# Performs a python-only test.
test:
	hatch run test 

clean:
	rm -rf build dist ${IDX}

env:
	micromamba create -n shiny python=3.11 rsconnect-python graphviz make -y

shiny:
	#pip install rsconnect-python
	rsconnect deploy shiny src/genescape/shiny --name biostar --title GeneScape

.PHONY: test lint fix push clean build publish obo docimg web
