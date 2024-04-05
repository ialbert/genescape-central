#
# Need the hatch tool to run this Makefile.
#
# pipx install hatch
#

# Default OBO file.
OBO_URL = http://current.geneontology.org/ontology/go-basic.obo
OBO_FILE = tmp/go-basic.obo

# The gene association file.
GAF_URL = https://current.geneontology.org/annotations/goa_human.gaf.gz
GAF_FILE = tmp/goa_human.gaf.gz

# Usage information.
usage:
	@echo "#"
	@echo "# Use the source, Luke!"
	@echo "#"

# Download the gene ontology file
${OBO_FILE}:
	mkdir -p $(dir ${OBO_FILE})
	curl -L ${OBO_URL} > ${OBO_FILE}

${GAF_FILE}:
	mkdir -p $(dir ${GAF_FILE})
	curl -L ${GAF_URL} > ${GAF_FILE}

index: ${OBO_FILE} ${GAF_FILE}
	genescape build --obo ${OBO_FILE} --gaf ${GAF_FILE} --index ${GAF_FILE}.index.gz

# Performs the testing.
web:
	python src/genescape/server.py

# Push a tag to the repository.
tag:
	pytest
	python src/genescape/dist.py --tag

# Performs a python-only test.
test:
	hatch run test

# A full test with file generation.
testall: test
	(cd test && make test)

# Runs a linter.
lint:
	hatch run lint:style

# Generate images for the documentation
docimg:
	genescape tree -o docs/images/genescape-output1.png src/genescape/data/test_genes.txt 
	genescape tree -o docs/images/genescape-output2.png src/genescape/data/test_goids.txt 
	genescape tree -m lipid -o docs/images/genescape-output3.png src/genescape/data/test_goids.txt 

# Fix linting errors.
fix:
	hatch run lint:fmt

push:
	git commit -am 'saving work' && git push

zip:
	python src/genescape/dist.py

clean:
	rm -f src/genescape/web/static/tmp/image*

realclean: clean
	rm -rf build dist

build: test
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
