# GeneScape: Gene Function Visualization

**GeneScape** is a software tool for visualizing gene functions. Users enter a list of genes, the software then draws a subgraph of the Gene Ontology (GO) terms associated with the genes.

![GeneScape Tree][tree]

[tree]: https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/interface-tree.png

**GeneScape** is a Python-based [Shiny][pyshiny] application that be run both at the command line and also via a graphical user interface.

## Quickstart

The public version of the software can be accessed at:

* https://biostar.shinyapps.io/genescape/

[pyshiny]: https://shiny.posit.co/py/

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

## Command line use

The program is distributed as an executable called `genescape` with the following subcommands:

* `genescape tree` draws informative Gene Ontology (GO) subgraphs
* `genescape annotate` annotates a list of genes with GO functions
* `genescape web` provides a web interface for the `tree` command

After installation, users launch the graphical user interface with:

The user interface is browser-based via the URL:

* [http://localhost:8000][local]

The page you see should look similar to the image below:

![GeneScape interface][iface1]

[iface1]: https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/interface-empty.png

Once you are done running with the program, you will need to close the terminal that started the program or press CTRL+C to stop the program from running.

## Using the interface

Fill in the text box with a list of genes names or GO terms or gene names and click the `Draw Tree` button to visualize the relationships between the GO terms.

![GeneScape interface][iface2]

[iface2]: https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/interface-help.png

The program will generate a tree visualization of the functional elements of the gene names that are inputted.

![GeneScape][tree]

**GeneScape** works the following way:

1. It first reads genes from an **Input List** 
1. Then extracts the **Annotations** associated with the input genes 
1. Finally it builds and visualizes the functional subtree tree based on these Annotations. 

> **Note**: Even short lists of genes (under ten genes) can create large trees. Filter by minimum counts (how many genes share the function) or functional patterns (functions that match a pattern). 

## Node Labeling 

The labels in the graph carry additional information on the number of genes in the input that carry that function as well as an indicator for the specificity of the function in the organism. For example, the label:

```
      GO:0004866
    endopeptidase
  inhibitor activity [39]
        (1/5)
```

Indicates that the function `endopeptidase inhibitor activity` was seen as an annotation to `39` of *all genes* in the original association file (for the human there are over 19K gene symbols). Thus, the `[39]` is a characteristic of annotation of the organism.

The `(1/5)` means that  `1` out of `5` genes in the input list carry this annotation. Thus the value is a characteristic of the input list. The `mincount` filter is applied to the count value to filter out functions that are under a threshold.

It is possible to compute a p-value to determine whether an observed enrichment difference is statistically significant. We'll just note that assigning p-values to enrichment counts is fraught with several challenges. In our opinion, GO annotations are neither complete, nor independent, nor precise enough to satisfy mathematical requirements. In addition, appropriate selection of the background (aka the `19000` above) to correct p-values for multiple comparisons also presents many challenges. For these reasons, we do not compute p-values in our application.

## Node Coloring

The colors in the tree carry additional meaning:

- Light green nodes represent functions that are in the input list.
- Dark green nodes are functions present in the input and are leaf nodes in the terminology, the most granular annotation possible 

A dark green means that the ontology has no terms that would be even more specific than that specific annotation. A light green means there are more specific annotations, but none of the genes were annotated as such. In both cases, the green color indicates that the function was present in the input list.

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

1. a pattern that matches the **function** columns
2. a minimum number of genes that carry that function
3. the GO subtree shown in the **root** column

Filters are applied during the annotation step and will filter the GO terms derived from the gene list.

In the Shiny interface use the **Mincount** filter to remove functions that are not well represented in the input list. Recall that `mincount` represents the number of genes in the input list that carry that function. You can see the counts for each annotation in the **Function Annotations** box as the first column.

## Command line requirements

To generate images from command line the `graphviz` software must be installed. You can install it via `conda`

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

## genescape tree

We packaged test data with the software so you can test it like so:

```console
genescape tree --test
```

Which will generate a tree visualization of the test data.

![GeneScape output][out1]

[out1]: https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/genescape-output1.png

## Reducing the graph size

We can pass the tree visualizer a list of genes or a list of GO ids, or even a mix of both. Here is an example.

```
Cyp1a1
Sphk2
Sptlc2
```

We run the `tree` command to visualize the relationships between the GO terms 

```console
genescape tree genes.txt
```

Note that we had only three genes in the input yet even that produces a huge tree of terms.

![GeneScape output][out2]

[out2]: https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/genescape-output2.png

We can narrow down the visualization in multiple ways, for example, we can select only terms that match the word `lipid` :

```console
genescape tree -m lipid genes.txt 
```

When filtered as shown above, the output is much more manageable:

![GeneScape output][out3]


[out3]: https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/genescape-output3.png

## genetrack annotation

The annotator operates on gene names. Suppose you have a list of gene names in the format:

```
Cyp1a1
Sphk2
Sptlc2
Smpd3
```

The command:

```console
genescape annotate --test 
```

will produce the output:

```
coverage,function,node_id,source,size,ann_count,ann_total,desc_count
1,endopeptidase inhibitor activity,GO:0004866,C3P1,4,39,199,5
1,GTPase activator activity,GO:0005096,GRTP1,4,274,274,0
1,extracellular space,GO:0005615,C3P1,4,1669,1669,0
1,cytoplasm,GO:0005737,BCAS4,4,5118,5452,44
1,membrane,GO:0016020,ABTB3,4,3268,20199,360
1,PDZ domain binding,GO:0030165,ABTB3,4,86,86,0
1,BLOC-1 complex,GO:0031083,BCAS4,4,15,15,0
1,"synaptic transmission, glutamatergic",GO:0035249,ABTB3,4,42,42,0
1,exploration behavior,GO:0035640,ABTB3,4,19,35,1
1,protein heterodimerization activity,GO:0046982,ABTB3,4,319,319,0
1,protein stabilization,GO:0050821,ABTB3,4,219,219,0
1,activation of GTPase activity,GO:0090630,GRTP1,4,100,100,0
1,glutamatergic synapse,GO:0098978,ABTB3,4,412,428,3
```

## genescape build

The software is currently packaged with a human and a mouse genome derived data index.

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

## Odds and ends

It is possible to mix gene and ontology terms. The following is a valid input:

```console
GO:0005488
GO:0005515
Cyp1a1
Sphk2
Sptlc2
```

Listing the same gene or GO term multiple times will count it multiple times.

## Testing

Tests are run via a `Makefile` as:

```console
make test
```

## Additional customizations

The software can be customized by creating a copy of the `config.toml` file and settings the `GENESCAPE_CONFIG` environment variable to point to the new configuration file.

* [config.toml](src/genescape/data/config.toml)

In this file the lines that have an `index` type will be used to build the dropdown menu in the web interface.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to contribute to the development of GeneScape.

## License

`genescape` is distributed under the terms of the MIT license. 
