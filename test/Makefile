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
	# Link the test data into this directory
	ln -sf ../src/genescape/data inp

	genescape annotate --test > out/test1.json
	genescape annotate --test --csv > out/test1.csv
	
	genescape tree --test -o out/test1.pdf
	genescape tree --test -o out/test1.png
	genescape tree --test -o out/test1.dot
	
	genescape annotate inp/test_goids.txt | genescape tree -o out/test2.pdf
	genescape annotate inp/test_goids.txt --csv | genescape tree -o out/test3.pdf
	
	genescape annotate inp/test_genes.txt | genescape tree -c 2 -o out/test4.pdf
	genescape tree -c 2 -o out/test5.pdf inp/test_genes.txt
	
	genescape tree inp/test_genes.txt -o out/test6.pdf
	genescape tree inp/test_goids.txt -o out/test7.pdf

	genescape annotate --test --csv  -m golgi | genescape tree -o out/test8.pdf
	genescape tree -m golgi inp/test_genes.txt -o out/test9.pdf


clean:
	rm -f out/*.*

.PHONY: test clean
