# GeneScape

[![PyPI - Version](https://img.shields.io/pypi/v/genescape.svg)](https://pypi.org/project/genescape)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/genescape.svg)](https://pypi.org/project/genescape)

The `genescape` suite is meant to be a collection of tools used to visualize gene ontology and the results of functional analysis. 

* `tree` draws informative gene ontology (GO) graphs based on GO terms.

## genescape tree

Starting with a file that contains GO terms (see [goids.txt](src/genescape/data/goids.txt) for the complete file)
:

```
GO:0005488
GO:0005515
GO:0048029
GO:0005537
GO:0003824
```

run the `tree` command in the following way:

```console
genescape tree -o demo.pdf goids.txt 
```

to generate the following graph:

![demo](docs/images/demo.png)

The image displays a subtree with various colored nodes representing different types of Gene Ontology (GO) terms from a provided list. Here's what each color means:

* Green nodes: These are the GO terms from your list.
* Light blue nodes: These are leaf nodes (the end points of the tree) representing the most granular annotation possible.
* White nodes: These connect the green nodes, forming the tree's structure. These represent the minimal ancestral nodes needed to interconnect your GO terms.

Additionally, each node shows two numbers:

The first number indicates the count of nodes in the subtree starting from that node.

The second number shows the total number of nodes in the original, larger tree that this subtree is a part of. 

For example, a node labeled "16/11235" means there are 16 nodes in the subtree beginning at that node. In the larger tree before filtering to your specific GO terms, this node's subtree had 11,235 nodes. These numbers help you understand the level of detail or specificity in the functional annotation.


## Installation

You can install `genescape` via `pip` or `pipx`.

Since the software is meant to be used as a command line tool, [pipx][pipx] is recommended.

```bash
pipx install genescape
```

[pipx]: https://pipx.pypa.io/stable/

To run the tool, you will also need to have the `dot` command from [Graphviz](https://graphviz.org/) installed and available on your `PATH`. You can install Graphviz via your package manager or via `conda` with:

```console  
conda install graphviz
```

## License

`genescape` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
