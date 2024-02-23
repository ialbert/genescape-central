import csv
import gzip
import json
import os
import textwrap
from itertools import tee
import pydot
import networkx as nx

from genescape import utils
from genescape.utils import GOID, LABEL


# Parse GO Ontology file from fname into a networkx graph
def build_graph(json_obo):
    graph = nx.DiGraph()

    stream = gzip.open(json_obo, mode="rt", encoding="UTF-8")
    terms = json.load(stream)

    # Add all nodes to Graph
    for node in terms:
        oid = node["id"]
        name = node["name"]
        text = textwrap.fill(name, width=20)
        label = f"{oid}\n{text}"
        namespace = utils.NAMESPACE_MAP.get(node["namespace"], "?")
        graph.add_node(oid, id=oid, name=name, namespace=namespace, label=label, **utils.NODE_ATTRS)

    # Add all edges to Graph
    for node in terms:
        for parent in node.get("is_a", []):
            if graph.has_node(parent):
                graph.add_edge(parent, node["id"])
            else:
                utils.warn(f"# Missing parent: {parent} for {node}")

    return graph

# Apply the quoting.
def fix(text):
    return f'"{text}"'

def run(fname, json_obo=utils.OBO_JSON, out="output.pdf", ann=None, verbose=False):

    # Build graph from JSON file
    graph = build_graph(json_obo=json_obo)

    def count_descendants(graph, start_node):
        # Count all nodes reachable from start_node, excluding start_node itself
        return len(nx.descendants(graph, start_node)) + 1

    # Get the stream from the file
    stream = utils.get_stream(fname)

    # Split the stream to allow detecting the header
    stream1, stream2 = tee(csv.reader(stream), 2)

    # Detect whether the file is header delimiter CSV or not
    headers = next(stream1)

    if GOID in headers and LABEL in headers:
        # Has headers, read the specified columns
        utils.debug("reading annotations")
        idx1, idx2 = headers.index(GOID), headers.index(LABEL)
        ann = dict((r[idx1], r[idx2]) for r in stream1)
        terms = list(ann.keys())
    else:
        # No headers, read the first column.
        utils.debug("reading first column")
        ann = {}
        terms = list( r[0] for r in stream2)

    # Select subtree from ancestors
    anc = set()

    miss = list(filter(lambda x: graph.has_node(x) is False, terms))
    if miss:
        utils.warn(f"unknown ids: {len(miss)}")
        utils.debug(f"unknown: {miss}")

    # Keep only valid nodes
    nodes = list(filter(lambda x: graph.has_node(x), terms))

    # Print the valid ids
    utils.info(f"valid ids: {len(nodes)}")
    utils.debug(f"valid: {nodes}")

    selection = set(nodes)

    # Get all ancestors and mark the ones that are terms.
    for node in nodes:
        graph.nodes[node]["fillcolor"] = utils.FG_COLOR
        anc = anc.union(nx.ancestors(graph, node))

    # Add the original nodes as well.
    total = anc.union(nodes)

    # Subset the graph to the ancestors only.
    tree = graph.subgraph(total)

    # Generate the expected and observed counts.
    #exp_counts = {node: count_descendants(graph, node) for node in graph.nodes()}
    #obs_counts = {node: count_descendants(tree, node) for node in tree.nodes()}

    # Add the observed and expected counts to the labels.
    for node in tree.nodes():

        # Get the annotations for the node.
        annot = str(ann.get(node, ""))

        # Fill with additional information for the label
        label = graph.nodes[node]["label"]
        label = f"{label}\n{annot}" if annot else label
        graph.nodes[node]["label"] = fix(label)

        # Insert additional information on each node
        graph.nodes[node]["degree"] = graph.degree(node)
        graph.nodes[node]["count_desc"] = count_descendants(graph, node)

        #graph.nodes[node]["fillcolor"] = utils.LF_COLOR

    # Print information on the subgraph.
    utils.info(f"subgraph: {len(tree.nodes())} nodes and {len(tree.edges())} edges")

    utils.info(f"output: {out}")

    # Stop here if the output is dot
    if out.endswith(".dot"):
        nx.nx_agraph.write_dot(tree, path=f"{out}")
        return



    # Create the pydot graph.
    pgraph = pydot.Dot("genescape", graph_type="digraph")
    for node in tree.nodes():

        # Fetch the label for the node.
        label = tree.nodes[node]["label"]

        # Fill the nodes with the appropriate color
        if count_descendants(graph, node) == 1:
            fillcolor = utils.LF_COLOR
        elif  node in selection:
            fillcolor = utils.FG_COLOR
        else:
            fillcolor = utils.BG_COLOR

        # Need to quote the node name
        nodex = fix(node)

        # Add the node to the graph
        pnode = pydot.Node(nodex, label=label, fillcolor=fillcolor, shape=utils.SHAPE, style="filled")
        pgraph.add_node(pnode)

    # Add the edges to the graph
    for edge in tree.edges():
        edge1 = fix(edge[0])
        edge2 = fix(edge[1])
        pedge = pydot.Edge(edge1, edge2)
        pgraph.add_edge(pedge)

    fname_dot = f"{out.split('.')[0]}.dot"
    pgraph.write_raw(fname_dot)
    pgraph.write_pdf(out, prog="dot")

# dot -Tpdf output_raw.dot -o output.pdf

if __name__ == "__main__":
    out = os.path.join("output.pdf")
    run(fname=utils.DEMO_DATA, json_obo=utils.OBO_JSON, out=out)
