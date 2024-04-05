import csv
import io
import json
import os
import textwrap

import networkx as nx
import pydot
from networkx import DiGraph

from genescape import annot, resources, utils
from genescape.utils import COUNT_DESC, DEGREE, GID, INPUT, LABEL, NAMESPACE

def human_readable(value, digits=0):
    """
    Converts a size in bytes to a human readable format.
    """
    try:
        value = int(round(float(value), digits))
    except ValueError:
        return value
    if value >= 1000:
        value = int(round(float(value)/1000, digits))
        value = f"{value:d}K"
    else:
        value = f"{value:d}"
    return value

# Parse GO Ontology file from fname into a networkx graph
def build_onto_graph(index):

    # The complete ontology graph
    graph = nx.DiGraph()

    # Gets the JSON data from the index file.
    data = resources.get_json(index)

    # The term section of the index.
    terms = data[utils.IDX_OBO]

    # Add all nodes to Graph
    for node in terms.values():
        oid = node["id"]
        name = node["name"]
        text = textwrap.fill(name, width=20)
        label = f"{oid}\n{text}"
        #gperc = node.get(utils.GO2GENE_PERC, 0)
        gcount = node.get(utils.GO2GENE_COUNT, 0)
        gcount = human_readable(gcount)
        label += f" [{gcount}]"

        namespace = utils.NAMESPACE_MAP.get(node["namespace"], "?")
        graph.add_node(oid, id=oid, name=name, namespace=namespace, label=label, **utils.NODE_ATTRS)


    # Add all edges to Graph
    for node in terms.values():
        for parent in node.get("is_a", []):
            if graph.has_node(parent):
                graph.add_edge(parent, node["id"])
            else:
                utils.warn(f"# Missing parent: {parent} for {node}")

    return graph


# Apply the quoting.
def fix(text):
    return f'"{text}"'


# Generates a tree from the graph.
def make_tree(ann, graph):

    terms = dict()
    for key in ann[utils.DATA_FIELD]:
        terms[key[utils.GID]] = key

    # The nodes in the graph.
    nodes = set(terms)

    # Keep only valid nodes.
    nodes = list(filter(lambda x: graph.has_node(x), nodes))

    # Collect the ancestors for each node.
    anc = set()
    for node in nodes:
        anc = anc.union(nx.ancestors(graph, node))

    # Add the original nodes as well.
    anc = anc.union(nodes)

    # Subset the graph to the ancestors only.
    tree = graph.subgraph(anc)

    # Input nodes
    inp_nodes = set(nodes)

    # Decorate the tree with additional information.
    for node in tree.nodes():

        # Keeps track of the degree of the node.
        tree.nodes[node][DEGREE] = graph.degree(node)

        # Keeps track of the number of descendants of the node.
        tree.nodes[node][COUNT_DESC] = count_descendants(graph, node)

        # Keeps track of whether the node was in the input list.
        tree.nodes[node][INPUT] = node in inp_nodes

        # Set the namespace for the node.
        tree.nodes[node][NAMESPACE] = tree.nodes[node].get("namespace", "?")

    # Print information messages.
    utils.info(f"subtree {len(tree.nodes())} nodes and {len(tree.edges())} edges")

    # Sort nodes and edges (Example: By node label)
    s_nodes = sorted(tree.nodes(data=True))
    s_edges = list(tree.edges(data=True))

    # Attempt to sort the graph nodes and edges to make the output deterministic.
    s_tree = nx.DiGraph()
    s_tree.add_nodes_from(s_nodes)
    s_tree.add_edges_from(s_edges)

    return s_tree


# Count all nodes reachable from start, also counting start.
def count_descendants(graph, start):
    return len(nx.descendants(graph, start)) + 1


def pydot_graph(extra, tree):
    """
    Adds additional information to the tree nodes.
    """

    # Create a dictionary of the annotations.
    info = dict(map(lambda x: (x[utils.GID], x), extra[utils.DATA_FIELD]))

    # Create the pydot graph.
    pg = pydot.Dot("genescape", graph_type="digraph")

    # Iterate over the nodes
    for node in tree.nodes():
        # Get the annotations for the node if these exist.
        extra = info.get(node, {}).get("label")

        # Fetch the label for the node
        label = tree.nodes[node]["label"]

        # Fill with additional information for the label
        label = f"{label}\n{extra}" if extra else label

        # Properly quote the label
        label = fix(label)

        # Fill the nodes with the appropriate color
        if tree.nodes[node][COUNT_DESC] == 1:
            fillcolor = utils.LEAF_COLOR
        elif tree.nodes[node][utils.INPUT]:
            fillcolor = utils.INPUT_COLOR
        else:
            key = tree.nodes[node][NAMESPACE]
            fillcolor = utils.NAMESPACE_COLORS.get(key, utils.BG_COLOR)

        # Need to quote the node name
        nodex = fix(node)

        # Add the node to the graph
        pnode = pydot.Node(nodex, label=label, fillcolor=fillcolor, shape=utils.SHAPE, style="filled")
        pg.add_node(pnode)

    # Add the edges to the graph
    for edge in tree.edges():
        edge1 = fix(edge[0])
        edge2 = fix(edge[1])
        pedge = pydot.Edge(edge1, edge2)
        pg.add_edge(pedge)

    return pg


WIDTH = 16.9
HEIGHT = 6.0


def dpi(size):
    value = size / WIDTH
    return value


def write(pg, out=None, imgsize=2048):
    """
    Save the tree to a file.
    """

    # Turn the graph into a DOT string.
    text = pg.to_string()

    # No output requested
    if out is None:
        return text

    # Write the graph to a file.
    utils.info(f"output: {out}")

    pg.set_graph_defaults()

    if out.endswith(".dot"):
        utils.debug(f"writing to {out}")
        pg.write_raw(f"{out}")
    elif out.endswith(".pdf"):
        pg.write_pdf(out)
    elif out.endswith(".png"):
        pg.set_graph_defaults(size=f"{WIDTH},{HEIGHT}", dpi=dpi(imgsize))
        pg.write_png(out)
    else:
        utils.stop(f"Unknown output format: {out}")

    return text


def build_tree(ann, index):

    # Speed up the process by caching the graph.
    def build():
        graph = build_onto_graph(index)
        return graph

    key = f"graph_{index}"
    graph = resources.cache(key, func=build)

    # Generate the tree from the graph.
    tree = make_tree(ann=ann, graph=graph)

    return tree


def write_tree(tree, ann, out=None):

    # Transform the tree into a pydot graph.
    pg = pydot_graph(extra=ann, tree=tree)

    # Write the tree to a file.
    text = write(pg, out)

    return text


def parse_input(inp, index, pattern=None, root=utils.NS_ALL, mincount=1):
    """
    Parses an input and generates a tree and an annotation object.
    """

    utils.info(f"index: {index}")

    # Get the input stream.
    it = utils.get_stream(inp=inp)

    # Parse the input into a dictionary.
    data = utils.parse_terms(iterable=it)

    # Run the annotation command
    ann = annot.run(data, index=index, mincount=mincount, pattern=pattern, root=root)

    # Turn the JSON string into an object.
    ann = json.loads(ann)

    # Run the tree command.
    tree = build_tree(ann=ann, index=index)

    # Return the tree
    return tree, ann


if __name__ == "__main__":
    cnf = resources.get_config()
    res = resources.init(cnf)

    ind = res.INDEX
    inp = res.TEST_GENES
    out = os.path.join("genescape.pdf")
    tree, ann = parse_input(inp=inp, index=ind, mincount=1, root=utils.NS_CC)
    text = write_tree(tree, ann, out=out)
