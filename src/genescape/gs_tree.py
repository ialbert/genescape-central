import gzip
import json
import os
import csv
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
        oid = node["id"]
        name = node["name"]
        text = textwrap.fill(name, width=20)
        label = f"{node['id']}\n{text}"
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


def run(fname, json_obo=utils.OBO_JSON, out="output.pdf", ann=None):

    # Build graph from JSON file
    graph = build_graph(json_obo=json_obo)

    def count_descendants(graph, start_node):
        # Count all nodes reachable from start_node, excluding start_node itself
        return len(nx.descendants(graph, start_node)) + 1

    # Expected counts
    exp_counts = {node: count_descendants(graph, node) for node in graph.nodes()}

    # Print the input file name.

    # Get the stream from the file
    stream = utils.get_stream(fname)
    stream = map(lambda x: x.strip(), stream)
    stream = filter(lambda x: x, stream)
    stream = filter(lambda x: not x.startswith("#"), stream)

    # Turn into a CSV reader

    ann = dict()
    stream = csv.reader(stream)
    terms = []
    for elems in stream:
        terms.append(elems[0])
        if len(elems) > 1:
            ann[elems[0]] = elems[1]

    # Select subtree from ancestors
    anc = set()

    miss = list(filter(lambda x: graph.has_node(x) is False, terms))
    if miss:
        utils.info(f"unknown ids: {len(miss)}")
        utils.debug(f"unknown: {miss}")

    # Keep only valid nodes
    nodes = list(filter(lambda x: graph.has_node(x), terms))

    # Print the valid ids
    utils.info(f"valid ids: {len(nodes)}")
    utils.debug(f"valid: {nodes}")

    # Get all ancestors and mark the ones that are terms.
    for node in nodes:
        graph.nodes[node]["fillcolor"] = utils.FG_COLOR
        anc = anc.union(nx.ancestors(graph, node))

    # Add the original nodes as well.
    total = anc.union(nodes)

    # Subset the graph to the ancestors only.
    tree = graph.subgraph(total)

    # Create the observed counts.
    obs_counts = {node: count_descendants(tree, node) for node in tree.nodes()}

    # Add the observed and expected counts to the labels.
    for node, obs_value in obs_counts.items():
        exp_value = exp_counts[node]

        # Annotations may be generated or pulled in from the file
        if ann:
            value = ann.get(node, "")
        else:
            value = f"{obs_value}/{exp_value}"

        # Fill in only if there is a value.
        if value:
            label = graph.nodes[node]["label"]
            graph.nodes[node]["label"] = f"{label}\n{value}"

        if exp_value == 1:
            graph.nodes[node]["fillcolor"] = "lightblue"

    # Print information on the subgraph.
    utils.info(f"subgraph: {len(tree.nodes())} nodes and {len(tree.edges())} edges")

    # Exit here on windows but continue on Linux
    if os.name == "nt":
        utils.stop("skipping plotting on Windows")

    # Convert to AGraph
    tree = nx.nx_agraph.to_agraph(tree)

    # Set the plot orientation
    # tree.graph_attr['rankdir'] = 'LR'

    # Layout the graph
    tree.layout("dot")

    # Render and save the graph
    tree.draw(out)

    # Print the output file name.
    utils.info(f"output: {out}")


if __name__ == "__main__":
    out = os.path.join("output.pdf")
    run(fname=utils.DEMO_DATA, json_obo=utils.OBO_JSON, out=out)
