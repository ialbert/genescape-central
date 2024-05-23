# GeneScape: Gene Function Visualization

**GeneScape** is a software tool for visualizing gene functions. Users enter a list of genes, the software then draws a subgraph of the Gene Ontology (GO) terms associated with the genes.

**GeneScape** is a Python-based [Shiny][pyshiny] application that be run both at the command line and also via a graphical user interface.

![GeneScape Tree][interface]

[interface]: https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/gs_web_interface.png

The Shiny version of the software can be accessed at:

* https://biostar.shinyapps.io/genescape/

Usage limits may apply to the public interface. For unlimited use, install and run the software locally.

[pyshiny]: https://shiny.posit.co/py/

### Local installation

Users can also run the program on their system by installing the software via `pip`:

```console
pip install genescape
```

After installation, the Shiny interface can be started via:

```console
genescape web
``` 

Visit the [http://localhost:8000][local] URL in your browser to see the interface.

[local]: http://localhost:8000

Once you are done running the web interface, press CTRL+C to stop the program from running.

### Command line use

The program can also be used at the command line to generate images or annotations:

* `genescape tree` draws informative Gene Ontology (GO) subgraphs
* `genescape annotate` annotates a list of genes with GO functions
* `genescape web` provides a web interface for the `tree` command

### What does GeneScape do?

**GeneScape** works the following way:

1. It first reads genes from an **Input List** 
1. Then extracts the **Annotations** associated with the input genes 
1. Finally it builds and visualizes the functional subtree tree based on these Annotations. 

**Note**: Even short lists of genes (under ten genes) can create large trees. Filter by minimum coverage (how many genes share the function) or functional patterns (functions that match a pattern). 

GeneScape will try to find a reasonable coverage coverage threshold when that threshold is not explicitly specified.

### Node Labeling 

The labels in the graph carry additional information on the number of genes in the input that carry that function and an indicator for the specificity of the function in the organism. For example, the label:

```
      GO:0004866
    endopeptidase
  inhibitor activity [39]
        (1/5)
```

Indicates that the function `endopeptidase inhibitor activity` was seen as an annotation to `39` of *all genes* in the original association file (for the human there are over 19K gene symbols). Thus, the `[39]` is a characteristic of annotation of the organism.

The `(1/5)` means that  `1` out of `5` genes in the input list carry this annotation. Thus the value is a characteristic of the input list. The `mincount` filter is applied to the count value to filter out functions that are under a threshold.

### Node Coloring

The colors in the tree carry additional meaning:

- Light green nodes represent functions that are in the input list.
- Dark green nodes are functions present in the input and are leaf nodes in the terminology, the most granular annotation possible 

A dark green means that the term is a leaf node, the most specific annotation possible. In both cases, the green color indicates that the function was present in the input list.

Each subtree in a different GO category has a different color:
  - Biological Process (BP)
  - Molecular Function (MF)
  - Cellular Component (CC)

The subtree coloring is meant to help you understand the level of detail and the specificity of the functional terms you visualize.

Numbers such as 1/4 mean how many genes in the input carry that function.

## Reducing the tree size

The trees can get huge, even for a small number of genes. 

Users can greatly reduce the size of the graph by removing functions that are not well represented in the input list or by focusing the graph to contain only functions that match a pattern.

Just by setting the `mincount` to 2 or higher is often enough to simplify the graph to a manageable size.

The filtering conditions that users can apply are:

1. a pattern that matches the **Function** columns
1. a minimum **Coverage** that means the minimum number of genes that carry that function
1. a GO subtree 

Filters are applied during the annotation step and will filter the GO terms derived from the gene list.

In the Shiny interface use the **coverage** filter to remove functions that are not well represented in the input list. Recall that `coverage` represents the number of genes in the input list that carry that function. You can see the counts for each annotation in the **Function Annotations** box as the first column.

### Command line requirements

To generate images from the command line, the `graphviz` software must be installed. You can install it via `conda`

```console
conda install graphviz
```

or via `apt` or `brew`.

Those unable to install the `graphviz` package can save the output as a `.dot` file:

```console
genescape tree --test -o output.dot 
```

Then use an online tool like [viz-js][viz] to visualize the graph.

[viz]: https://viz-js.com/ 

### genescape tree

We packaged test data with the software so you can test it like so:

```console
genescape tree --test
```

Which will generate a tree visualization of the test data.

![GeneScape output][out1]

[out1]: https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/gs_output_1.png

### Reducing the graph size

We can pass the tree visualizer a list of genes or a list of GO IDs, or even a mix of both. 

We run the `tree` command to visualize the relationships between the GO terms that include all coverages:

```console
genescape tree genes.txt --mincov 1 
```

For many (most) gene lists resulting functional graph might be huge. If no coverage is specified, the software will try to find a reasonable coverage threshold for the input genes.

![GeneScape output][out2]

[out2]: https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/gs_output_2.png

We can narrow down the visualization in multiple ways, for example, we can select only terms that match the word `lipid` :

```console
genescape tree -m repair genes.txt 
```

When filtered as shown above, the output is much more manageable:

![GeneScape output][out3]

[out3]: https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/gs_output_3.png

### genetrack annotation

The annotator operates on gene names. Suppose you have a list of gene names in the format:

```
Cyp1a1
Sphk2
Sptlc2
Smpd3
```

The command:

```console
genescape annotate genelist.txt
```

will produce the output:

```
Coverage,Function,GO,Genes
3,protein binding,GO:0005515,CYP1A1|SMPD3|SPHK2
2,cytoplasm,GO:0005737,SMPD3|SPHK2
2,mitochondrial inner membrane,GO:0005743,CYP1A1|SPHK2
2,endoplasmic reticulum membrane,GO:0005789,CYP1A1|SPTLC2
2,sphingolipid biosynthetic process,GO:0030148,SPHK2|SPTLC2
2,intracellular membrane-bounded organelle,GO:0043231,CYP1A1|SPHK2
2,sphingosine biosynthetic process,GO:0046512,SPHK2|SPTLC2
```

### genescape build

The software is currently packaged indices for a number of organisms.

To build an index for a different organism, download the GAF association file from the Gene Ontology website. 

* https://geneontology.org/docs/download-go-annotations/

To build the new index use:

```console
genescape build --gaf mydata.gaf.gz --obo go.basic.gz -i mydata.index.gz 
```

To use the custom index, pass the `-i` (`--index`) option to any of the commands, `web`, `tree` and `annotate` like so:

```console
genescape web --index mydata.index.gz
```

See the `--help` for more options.

### Odds and ends

It is possible to mix gene and ontology terms. The following is a valid input:

```console
GO:0005488
GO:0005515
Cyp1a1
Sphk2
Sptlc2
```

### Testing

Tests are run via a `Makefile` as:

```console
make test
```

### Additional customizations

The software can be customized by creating a copy of the `config.toml` file and settings the `GENESCAPE_CONFIG` environment variable to point to the new configuration file.

* [config.toml](src/genescape/data/config.toml)

In this file the lines that have an `index` type will be used to build the dropdown menu in the web interface.

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to contribute to the development of GeneScape.

### License

`genescape` is distributed under the terms of the MIT license. 
