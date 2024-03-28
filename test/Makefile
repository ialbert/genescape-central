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
	@echo "# make test"
	@echo "#"

# Generates various outputs
test:
	# Make the output directory.
	mkdir -p out

	genescape annotate --test > out/test.json
	genescape annotate --test --csv > out/test.csv
	
	genescape tree --test -o out/test.pdf
	genescape tree --test -o out/test.png
	genescape tree --test -o out/test.dot
	
	genescape annotate files/hs_genes1.txt | genescape tree -o out/hs_genes1.pdf
	genescape annotate files/hs_goids1.txt --csv | genescape tree -o out/hs_goids1.pdf

	genescape tree -c 2 -o out/hs_gene1-mincount-2.pdf files/hs_genes1.txt

	genescape annotate --csv -m golgi files/hs_genes1.txt > out/hs_gene1-golgi.json

	genescape tree -m golgi files/hs_genes1.txt -o out/hs_gene1-golgi.pdf

	genescape tree files/hs_genes2.txt > out/hs_genes2.pdf

	genescape build -i out/genescape.json.gz


clean:
	rm -f out/*.*

.PHONY: test clean
