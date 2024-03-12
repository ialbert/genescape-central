import os
import textwrap

import pydot
import networkx as nx
from networkx import DiGraph

from genescape import utils
from genescape.utils import GOID, LABEL, DEGREE, COUNT_DESC, INPUT


# Parse GO Ontology file from fname into a networkx graph
def build_graph(index):
    graph = nx.DiGraph()

    data = utils.get_json(index)

    # The term section of the index.
    terms = data[utils.IDX_OBO]

    # Add all nodes to Graph
    for name, node in terms.items():
        oid = node["id"]
        name = node["name"]
        text = textwrap.fill(name, width=20)
        label = f"{oid}\n{text}"
        namespace = utils.NAMESPACE_MAP.get(node["namespace"], "?")
        graph.add_node(oid, id=oid, name=name, namespace=namespace, label=label, **utils.NODE_ATTRS)

    # Add all edges to Graph
    for name, node in terms.items():
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
def make(annot: dict[str, dict[str]], graph: DiGraph()) -> DiGraph():

    # The nodes in the graph.
    nodes = set(annot.keys())

    # Get all the valid nodes.
    nodes = list(filter(lambda x: graph.has_node(x), nodes))

    # Print information messages.
    utils.info(f"valid ids: {len(nodes)}")
    utils.debug(f"valid nodes: {nodes}")

    # Write information on missing nodes.
    miss = list(set(annot.keys()) - set(nodes))
    if miss:
        utils.warn(f"missing {len(miss)} ids like: {', '.join(miss[:10])} ... ")
        utils.debug(f"missing nodes: {miss}")

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

        # Keeps track of wether the node was in the input list.
        tree.nodes[node][INPUT] = node in inp_nodes

    # Print information messages.
    utils.info(f"subtree {len(tree.nodes())} nodes and {len(tree.edges())} edges")

    return tree



# Count all nodes reachable from start, also counting start.
def count_descendants(graph, start):
    return len(nx.descendants(graph, start)) + 1

def pydot_graph(annot, tree: DiGraph) -> pydot.Dot :
    """
    Adds additional information to the tree nodes.
    """

    # Create the pydot graph.
    pg = pydot.Dot("genescape", graph_type="digraph")

    # Iterate over the nodes
    for node in tree.nodes():
        # Get the annotations for the node if these exist.
        ann = annot.get(node, {}).get("label")

        # Fetch the label for the node
        label = tree.nodes[node]["label"]

        # Fill with additional information for the label
        label = f"{label}\n{ann}" if ann else label

        # Properly quote the label
        label = fix(label)

        # Fill the nodes with the appropriate color
        if tree.nodes[node][COUNT_DESC] == 1:
            fillcolor = utils.LF_COLOR
        elif node in annot:
            fillcolor = utils.FG_COLOR
        else:
            fillcolor = utils.BG_COLOR

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
    value = size/WIDTH
    return value

def write(pg, out, imgsize=2048):
    """
    Save the tree to a file.
    """

    pg.set_graph_defaults(size=f"{WIDTH},{HEIGHT}", dpi=dpi(imgsize))

    pg.write_raw(f"{out}.dot")


    # Write the graph to a file.
    utils.info(f"output: {out}")
    if out.endswith(".pdf"):
        pg.write_pdf(out, prog="dot")
    elif out.endswith(".png"):
        pg.write_png(out, prog="dot")
    elif out.endswith(".dot"):
        pg.write_raw(out)
    else:
        utils.stop(f"Unknown output format: {out}")


def run(annot, index=utils.INDEX, out="output.pdf", ann=None, verbose=False):

    # Build graph from JSON file
    graph = build_graph(index)

    # Generate the tree from the graph.
    tree = make(annot=annot, graph=graph)

    # Decorate the tree with additional information.
    pg = pydot_graph(annot, tree)

    # Write the tree to a file.
    write(pg, out)

    return tree

# dot -Tpdf output_raw.dot -o output.pdf

if __name__ == "__main__":
    out = os.path.join("genescape.pdf")
    annot = utils.parse_terms(utils.GO_LIST)
    run(annot=annot, index=utils.INDEX, out=out)
