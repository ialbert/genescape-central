# GeneScape: gene function visualization

![GeneScape Tree][tree]

[tree]: https://github.com/ialbert/genescape-central/blob/main/docs/images/interface-tree.png

**GeneScape** is a software tool for visualizing gene functions. 

**GeneScape** is distributed as a standalone executable that can be run on Windows or MacOS.

The software can also operate in command line mode on any platform where Python 3.10 or above is available and can be installed with `pip install genescape` When executed from the command line:

* `genescape tree` draws informative Gene Ontology (GO) subgraphs
* `genescape annotate` annotates a list of genes with GO functions
* `genescape web` provides a web interface for the `tree` command

See more detailes in [Install](#installation) section below.

## Quick start

Download the latest binary release for your platform

* [GeneScape Releases][releases]

[releases]: https://github.com/ialbert/genescape-central/releases

**Windows**: unzip then double-click the executable to start the program.

**MacOS** The first time you run the tool on MacOS you have to unzip, right-click and select **open**. You then again have to agree to run the software. Once you do so the program runs, and in the future you can double-click the executable to start the program.

After a few seconds, a new browser window will pop and you will get an interface that looks like this:

![GeneScape interface][iface1]

[iface1]: https://github.com/ialbert/genescape-central/blob/main/docs/images/interface-empty.png

Fill in the text box with a list of genes names or GO terms or gene names and click the `Draw Tree` button to visualize the relationships between the GO terms.

![GeneScape interface][iface2]

[iface2]: https://github.com/ialbert/genescape-central/blob/main/docs/images/interface-help.png

The program will generate a tree visualization of the functional elements of the gene names that are inputted.

![GeneScape][tree]

**GeneScape** does the following:

1. Reads genes from an **Input list** 
1. Extracts the **Functional Annotations** associated with the input genes 
1. Builds and visualizes a tree based on these GO terms 

## Color scheme

The colors in the tree carry additional meaning:

- Light Green nodes represent functions that are in the input list.
- Dark green nodes are functions present in the input and are leaf nodes in the terminology, the most granular annotation possible 

Each subtree in a different GO category has a different color:
  - Biological Process (BP)
  - Molecular Function (MF)
  - Cellular Component (CC)

The subtree coloring is meant to help you understand the level of detail and the specificity of the functional terms you visualize.

Numbers such as 1/4 mean how many genes in the input carry that function.


## Reducing the tree size

The tree can get huge, even for a small number of genes. 

You can reduce the size of the tree by filtering for a pattern in the functions or by visualizing functions that occur in a minimum number of genes.

Note all the options available in the interface:

![GeneScape bar][bar]

[bar]: https://github.com/ialbert/genescape-central/blob/main/docs/images/interface-bar.png

All of these elements are applied during the first and will filter the GO terms derived from the gene list.

## Command line usage

See the installation below on how to get the command line version.

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

[out1]: https://github.com/ialbert/genescape-central/blob/main/docs/images/genescape-output1.png

You can pass to the tree visualizer a list of genes or a list of GO ids, or even a mix of both. Here is an example.

```
Cyp1a1
Sphk2
Sptlc2
```

run the `tree` command to visualize the relationships between the GO terms 

```console
genescape tree genes.txt -o output.pdf
```

You only had three genes in the input yet even that produces a large tree of terms.

![GeneScape output]

[out2]: https://github.com/ialbert/genescape-central/blob/main/docs/images/genescape-output2.png

You can narrow down the visualization in multiple ways, for example, you can select only terms that match the word `lipid` :

```console
genescape tree -m lipid genes.txt -o output.pdf
```

When filtered as shown above the output is much more manageable:

![GeneScape output][out3]

[out3]: https://github.com/ialbert/genescape-central/blob/main/docs/images/genescape-output3.png

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

## License

`genescape` is distributed under the terms of the MIT license. 
