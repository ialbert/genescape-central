# GeneScape: gene function visualization

![GeneScape Tree][tree]

[tree]: https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/interface-tree.png

**GeneScape** is a software tool for visualizing gene functions. 

**GeneScape** is distributed as a standalone executable that can be run on Windows or MacOS.

The software can also operate in command line mode on any platform where Python 3.10 or above is available and can be installed with `pip install genescape` When executed from the command line:

* `genescape tree` draws informative Gene Ontology (GO) subgraphs
* `genescape annotate` annotates a list of genes with GO functions
* `genescape web` provides a web interface for the `tree` command

More details in [Install](#installation) section below.

## Quick start

Download the latest binary release for your platform

* [GeneScape Releases][releases]

[releases]: https://www.github.com/ialbert/genescape-central/releases

**Windows**: unzip then double-click the executable to start the program.

**MacOS** The first time you run the tool on MacOS you have to unzip, right-click and select **open**. You then again have to agree to run the software. Once you do so the program runs, and in the future you can double-click the executable to start the program.

Visit the localhost address in your browser:

* [http://localhost:8000](http://localhost:8000)

the page you see should look like this:

![GeneScape interface][iface1]

[iface1]: https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/interface-empty.png

Fill in the text box with a list of genes names or GO terms or gene names and click the `Draw Tree` button to visualize the relationships between the GO terms.

![GeneScape interface][iface2]

[iface2]: https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/interface-help.png

The program will generate a tree visualization of the functional elements of the gene names that are inputted.

![GeneScape][tree]

**GeneScape** does the following:

1. Reads genes from an **Input list** 
1. Extracts the **Functional Annotations** associated with the input genes 
1. Builds and visualizes a tree based on these GO terms 

## Node labeling 

The labels in the graph carry additional information on the number of genes in the input that carry that function as well as an indicator for the specificity of the function in the organism. For example, the label:

```
   GO:0098978
  glutamatergic
  synapse: 2.1%
      (1/2)
```

Indicates that the function `glutamatergic synapse` was seen as an annotation to 2.1% of *all genes* in the original association file. Thus it is characteristic of the annotation of the organism.

When it comes to the input file, 1 out of 2 genes carry this function. 

Thus we are observing a function that appears in 2.1% of all genes of the organism and a 1/2=50% fraction of the input genes. 

You are welcome to apply a p-value to this difference to determine whether it is statistically significant. Note that assigning p-value to enrichment counts is fraught with challenges, as in our opinion, GO annotations are neither complete, nor independent nor accurate enough to make such determination.

## Node coloring

The colors in the tree carry additional meaning:

- Light green nodes represent functions that are in the input list.
- Dark green nodes are functions present in the input and are leaf nodes in the terminology, the most granular annotation possible 

Each subtree in a different GO category has a different color:
  - Biological Process (BP)
  - Molecular Function (MF)
  - Cellular Component (CC)

The subtree coloring is meant to help you understand the level of detail and the specificity of the functional terms you visualize.

Numbers such as 1/4 mean how many genes in the input carry that function.

## Reducing the tree size

The trees can get huge, even for a small number of genes. 

Note the information in the box titles **Function Annotations** you can filter the terms in that box by:

1. a pattern that matches the **function** columns
2. a minimum number of genes that carry that function shown in the **count** column
3. the GO subtree shown in the **root** column

Note the options available in the interface:

![GeneScape bar][bar]

[bar]: 
https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/interface-bar.png

All of these elements are applied during the annotation step and will filter the GO terms derived from the gene list.

## Command line usage

To start the web interface type:

```console
genescape web
```

A web browser will start with the interface above.

## genescape tree

You can also use GeneScape completely from the command line with no web interface.

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
genescape tree genes.txt -o output.pdf
```

Note that we had only three genes in the input yet even that produces a huge tree of terms.

![GeneScape output][out2]

[out2]: https://raw.githubusercontent.com/ialbert/genescape-central/main/docs/images/genescape-output2.png

We can narrow down the visualization in multiple ways, for example, we can select only terms that match the word `lipid` :

```console
genescape tree -m lipid genes.txt -o output.pdf
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
genescape annotate -t --csv
```

will produce the output:

```
gid,root,count,function,source,size,label
GO:0090630,BP,1,activation of GTPase activity,GRTP1,4,(1/4)
GO:0046982,MF,1,protein heterodimerization activity,ABTB3,4,(1/4)
GO:0031083,CC,1,BLOC-1 complex,BCAS4,4,(1/4)
GO:0016020,CC,1,membrane,ABTB3,4,(1/4)
GO:0005737,CC,1,cytoplasm,BCAS4,4,(1/4)
GO:0005615,CC,1,extracellular space,C3P1,4,(1/4)
GO:0005096,MF,1,GTPase activator activity,GRTP1,4,(1/4)
GO:0004866,MF,1,endopeptidase inhibitor activity,C3P1,4,(1/4)
```

## genescape build

The software is currently packaged with a human and a mouse genome derived data index.

To build an index for a different organism, download the GAF association file from the Gene Ontology website. 

* https://geneontology.org/docs/download-go-annotations/

To build the new index use:

```console
genescape build --gaf mydata.gaf -i mydata.index.gz 
```

You can also load up a different version of the OBO ontology. See the `--help` for more options.

## Installation

For a standalone executable Windows or MacOS executable, download the latest release from the [releases page][releases]. 

When installed from the command line, the software requires Python 3.10 or above.  You can install `genescape` via `pip` or `pipx`.

```console
pip install genescape
```

No other software installation is needed if you want to use of the web interface via 

```console
genescape web
```

If you want to generate PDF or PNG images from the command line without a web browser, you will need to have the `graphviz` software from [Graphviz](https://graphviz.org/) installed and available on your `PATH`. The simplest way to install Graphviz via your package manager `apt`, `brew` or via `conda`:

```console  
conda install graphviz
```

If you are unable to install the `graphviz` package you can save the output as a `.dot` file. 

```console
genescape tree --test -o output.dot 
```

Then use an online tool like [viz-js][viz] to visualize the graph.

[viz]: https://viz-js.com/ 

## Testing

Tests are run via a `Makefile` as:

```console
make test
```

Tests require that `graphviz` is installed and available on the `PATH`.

Due to the nondeterministic way that the images are created, we are unable to test for exact outputs the tests are limited to running the software and checking for runtime errors.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to contribute to the development of GeneScape.

## License

`genescape` is distributed under the terms of the MIT license. 
