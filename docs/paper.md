---
title: 'GeneScape: A Python package for gene ontology analysis'
tags:
  - Python
  - biology
  - bioinformatics
  - functional analysis
authors:
  - name: Istvan Albert
    orcid: 0000-0001-8366-984X
    equal-contrib: true
    affiliation: 1 

affiliations:
 - name: Biochemistry and Molecular Biology, Pennsylvania State University, USA
   index: 1

date: 30 March 2024
bibliography: docs/paper.bib
---

# Summary

Gene Ontologies (GOs)  [@Asburner2000], [@GO2023] are standardized and structured vocabulary that describes gene products in the context of their associated biological processes, cellular components, and molecular functions. The ontologies take the form of a graph structure in the form of a directed tree, where each node defines a term, and each edge represents a hierarchical relationship between the words of the vocabulary.

For example, in the GO data, `GO:0090630` is a word defined as *activation of GTPase activity* and is a child of `GO:0043547`, which is defined as *positive regulation of GTPase activity* that in turn is a child of `GO:0051345` *positive regulation of hydrolase activity* and so on. 

Gene association files (GAF) are text files used to annotate an organism's gene products with Gene Ontology terms, thereby associating a function with a gene product. Scientists may obtain gene association files from the Gene Ontology Consortium or from other sources. For example, a GAF file connects a gene product label such as `ZC3H11B` with typically multiple GO terms, such as `GO:0046872` or `GO:0016973`. 

The Gene Ontology Consortium maintains GAF files for various organisms. These GO and GAF datasets are used by all processes that interpret genomic data in a functional context.  Typical data analysis steps generate gene lists, gene enrichment tools such as `g:profiler`, and `enrichr` output lists of GO terms that must be placed into a functional context.

# Statement of need

The most annotated gene for the human genome (`HTT1` had 1098 annotations at the time of writing this document). Typically, even small lists of genes will have many annotations and represent large subtrees of functions. There is a need to visualize these subtrees in an informative and relatively easy way.

GeneScape is a Python package that allows end users to visualize a list of gene products in terms of the functional context as represented by the Gene Ontology. The package provides both a browser-based visual interface and a command-line interface to assist users with different levels of computational expertise. From a gene list such as: 

```
ABTB3 
BCAS4
C3P1
GRTP1
```

GeneScape first transforms this gene input list into a GO term list:

```
GO:0090630,BP,1,activation of GTPase activity,GRTP1,4,(1/4)
GO:0046982,MF,1,protein heterodimerization activity,ABTB3,4,(1/4)
GO:0031083,CC,1,BLOC-1 complex,BCAS4,4,(1/4)
GO:0016020,CC,1,membrane,ABTB3,4,(1/4)
GO:0005737,CC,1,cytoplasm,BCAS4,4,(1/4)
GO:0005615,CC,1,extracellular space,C3P1,4,(1/4)
GO:0005096,MF,1,GTPase activator activity,GRTP1,4,(1/4)
GO:0004866,MF,1,endopeptidase inhibitor activity,C3P1,4,(1/4)
```

Then, the GO term list is visualized as a graph structure that represents the functional context of the genes. 

![GeneScape interface \label{fig:interface}](images/interface-tree.png)

GeneScape provides reactive interface elements that allow users to filter the resulting outputs by:

1. Word patterns that match the function definitions
2. A minimum number of genes share the function 
3. A specific GO subtree: Biological Process, Molecular Function, Cellular Component

In addition, users can zoom in and out of the tree. The software's command-line version supports generating outputs in various formats, such as PDF or PNG.

The software's main purpose is to allows users to assess the functional depth of genes and to identify commonalities and differences in the functional context of these genes.

# Acknowledgements

We acknowledge support from the Huck Institutes for the Life Sciences at the Pennsylvania State University.

# References
