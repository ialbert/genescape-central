# Genescape `tree`

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

run the `tree` command to visualize the relationships between the GO terms:

```console
genescape tree -o output.pdf goids.txt 
```

The command generates the following output:

![Example output](images/demo.png)

The image displays the GO subtree that contains all the input GO terms. Here's what each color means:

* Green nodes: These are the GO terms from your list.
* Light blue nodes: These are leaf nodes (the end points of the tree) representing the most granular annotation possible.
* White nodes: These connect the green nodes, forming the tree's structure. These represent the minimal ancestral nodes needed to interconnect your GO terms.

### Default labels

When labels are not explicitly provided, an automatic node labeling will take place where the number is the total number of nodes in the complete annotation tree. 

For example, a node labeled `51` indicates there are `51` nodes in the subtree beginning at that node even though it may only show you a few of its descendants. A blue node should have the number `1` indicating that it is a leaf node.

The numbers and colors are meant to assist in understanding the level of detail and the specificity of the functional terms you visualize.

### Custom labels

The input may also take the form of a CSV file with headers. In that case the content of the columns `goids` and `labels` will be processed. Example:

```
goids,labels
GO:0005488,A
GO:0005515,B
GO:0048029,C
GO:0005537,D
...
```

Would generate `A`, `B`, `C`, `D`, and `E` instead of the `X/Y` numbers.  


![Example output with labels](images/demo-labels.png)

When the input is in CSV format, only the green nodes (nodes in the input list) will be labeled.
