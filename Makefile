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
serve:
	python src/genescape/server.py

# Performs the testing.
test:
	(cd test && make test)

# Runs a linter.
lint:
	hatch run lint:style

# Fix linting errors.
fix:
	hatch run lint:fmt

push:
	git commit -am 'saving work' && git push


exe:
	pyinstaller src/genescape/server.py --add-data=src/genescape/data:genescape/data -y --onefile

clean:
	rm -f src/genescape/web/static/tmp/image*

realclean: clean
	rm -rf build dist

build:
	hatch build 

pypi:
	hatch run publish

$(OBO):
	mkdir -p $(dir $(OBO))
	curl -L $(URL) > $(OBO)

get: $(OBO)
	@ls -l $(OBO)

.PHONY: test lint fix push demo clean realclean build pypi get
