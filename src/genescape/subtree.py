import gzip
import json
import os
import re
import textwrap

import networkx as nx

from genescape import utils


# Parse GO Ontology file from fname into a networkx graph
def build_graph(json_obo):
    graph = nx.DiGraph()

    stream = gzip.open(json_obo, mode="rt", encoding="UTF-8")
    terms = json.load(stream)

    # Add all nodes to Graph
    for node in terms:
        name = textwrap.fill(node["name"], width=20)
        label = f"{node['id']}\n{name}"
        graph.add_node(node["id"], label=label, **utils.NODE_ATTRS)

    # Add all edges to Graph
    for node in terms:
        for parent in node.get("is_a", []):
            if graph.has_node(parent):
                graph.add_edge(parent, node["id"])
            else:
                utils.warn(f"# Missing parent: {parent} for {node}")

    return graph


def run(fname, json_obo=utils.OBO, mcol="category", mval="GO:MF", pcol="pval", pval=0.05, out="output.pdf"):
    # Build graph from JSON file
    graph = build_graph(json_obo=json_obo)

    # Stores GO terms
    terms = []

    from genescape.plugins.gprofiler import get_csv, relabel

    # Get the stream from the file
    stream = get_csv(fname)

    # Filter by p-value
    if pcol and pval:
        stream = filter(lambda x: float(x[pcol]) < pval, stream)

    # Filter by regular exprssion
    if mcol and mval:
        stream = filter(lambda x: re.search(x[mcol], mval), stream)

    # Dictionary keyed by GO terms
    terms, g2d = [], {}
    for row in stream:
        goid = row["goid"]
        terms.append(goid)
        g2d[goid] = row

    # Select subtree from ancestors
    anc = set()

    miss = list(filter(lambda x: graph.has_node(x) is False, terms))
    if miss:
        utils.warn(f"# unknown ids: {','.join(miss)}")

    # Keep only valid nodes
    nodes = list(filter(lambda x: graph.has_node(x), terms))

    # Print the valid ids
    utils.info(f"valid ids: {len(nodes)}")

    # Get all ancestors and mark the ones that are terms.
    for node in nodes:
        graph.nodes[node]["fillcolor"] = utils.FG_COLOR
        graph.nodes[node]["label"] = relabel(graph=graph, g2d=g2d, node=node)
        anc = anc.union(nx.ancestors(graph, node))

    # Add the original nodes as well.
    total = anc.union(nodes)

    # Subset the graph to the ancestors only.
    tree = graph.subgraph(total)

    # Print information on the subgraph.
    utils.info(f"subgraph has {len(tree.nodes())} nodes and {len(tree.edges())} edges.")

    # Exit here on windows but continue on Linux
    if os.name == "nt":
        utils.stop("skipping plotting on Windows")

    # Convert to AGraph
    tree = nx.nx_agraph.to_agraph(tree)

    # Set the plot orientation
    # tree.graph_attr['rankdir'] = 'LR'

    # Create the legend
    legend = tree.add_subgraph(name="legend", label="Legend", rank="sink")
    legend.add_node(
        "x",
        label="Legend: \n 88 / 2.5x = 88 observered counts / 2.5x fold enrichment.\n "
        "Green indicates GO term observed in data",
        shape="box",
        color="white",
    )

    # Layout the graph
    tree.layout("dot")

    # Render and save the graph
    tree.draw(out)

    utils.info(f"output: {out}")


if __name__ == "__main__":
    run(fname=utils.CSV, json_obo=utils.OBO)
