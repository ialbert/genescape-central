# GeneScape

The `genescape` suite is planned to become a collection of tools used to visualize the results of functional genome analysis. Various new tools may be implemented in the future.

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
...
```

You can run the `tree` command in the following way:

```console
genescape tree -o demo.pdf goids.txt 
```

The above command generates the following output:

![demo](docs/images/demo.png)

The image displays the GO subtree that contains all the input GO terms. Here's what each color means:

* Green nodes: These are the GO terms from your list.
* Light blue nodes: These are leaf nodes (the end points of the tree) representing the most granular annotation possible.
* White nodes: These connect the green nodes, forming the tree's structure. These represent the minimal ancestral nodes needed to interconnect your GO terms.

The first number indicates the count of nodes in the subtree starting from that node.

The second number shows the total number of nodes of the original, complete annotation tree that this subtree is a part of. 

For example, a node labeled "16/11235" indicates there are 16 nodes in the subtree beginning at that node. 

In the larger tree before filtering to your specific GO terms, this node's subtree had 11,235 nodes. 

These numbers and colors are meant to help you understand the level of detail and the specificity of the functional terms you visualize.

Customizing the labels. The last line of numbers may be replaced with custom labels read from the second column of the comma separated input file. For example, the following input file:

```
GO:0005488,A
GO:0005515,B
GO:0048029,C
GO:0005537,D
GO:0003824,E
...
```

Would generate `A`, `B`, `C`, `D`, and `E` instead of the `X/Y` numbers.

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
