import os, json
import textwrap

import pydot
import networkx as nx
from networkx import DiGraph

from genescape import utils, annot
from genescape.utils import GID, LABEL, DEGREE, COUNT_DESC, INPUT


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
def make_tree(terms: list, info:dict, graph: DiGraph()) -> DiGraph():

    # The nodes in the graph.
    nodes = set(terms)

    # Get all the valid nodes.
    nodes = list(filter(lambda x: graph.has_node(x), nodes))

    # Print information messages.
    utils.info(f"valid ids: {len(nodes)}")
    utils.debug(f"valid nodes: {nodes}")

    # Write information on missing nodes.
    miss = list(set(terms) - set(nodes))
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

def pydot_graph(info, tree: DiGraph) -> pydot.Dot :
    """
    Adds additional information to the tree nodes.
    """

    # Create the pydot graph.
    pg = pydot.Dot("genescape", graph_type="digraph")

    # Iterate over the nodes
    for node in tree.nodes():
        # Get the annotations for the node if these exist.
        ann = info.get(node, {}).get("label")

        # Fetch the label for the node
        label = tree.nodes[node]["label"]

        # Fill with additional information for the label
        label = f"{label}\n{ann}" if ann else label

        # Properly quote the label
        label = fix(label)

        # Fill the nodes with the appropriate color
        if tree.nodes[node][COUNT_DESC] == 1:
            fillcolor = utils.LF_COLOR
        elif tree.nodes[node][utils.INPUT]:
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

def write(pg, out=None, imgsize=2048):
    """
    Save the tree to a file.
    """

    # No output requested
    if out is None:
        return

    # Write the graph to a file.
    utils.info(f"output: {out}")

    pg.set_graph_defaults()

    if out.endswith(".dot"):
        print (f"writing to {out}")
        pg.write_raw(f"{out}")
    elif out.endswith(".pdf"):
        pg.write_pdf(out, prog=utils.DOT_EXE)
    elif out.endswith(".png"):
        pg.set_graph_defaults(size=f"{WIDTH},{HEIGHT}", dpi=dpi(imgsize))
        pg.write_png(out, prog=utils.DOT_EXE)
    else:
        utils.stop(f"Unknown output format: {out}")

def run(data, index=utils.INDEX, out="output.pdf",  pattern=None, verbose=False):

    # The field that contains the data
    DF = utils.DATA_FIELD

    # GO ids and Gene ids
    go_data = {DF: []}
    gn_data = {DF: []}

    # Split the data into GO and Gene ids
    for row in data[DF]:
        if row[utils.GID].startswith("GO:"):
            go_data[DF].append(row)
        else:
            gn_data[DF].append(row)



    # Fill in the GO terms obtained from Genes.
    if gn_data[DF]:
        gn_res = annot.run(data=gn_data, index=utils.INDEX, pattern=pattern)
        gn_res = json.loads(gn_res)
        go_data[DF].extend(gn_res[DF])

    print(go_data)
    print(gn_data)
    1 / 0

    # Build graph from JSON file
    graph = build_graph(index)

    # Generate the tree from the graph.
    tree = make_tree(terms=terms, info=info, graph=graph)

    # Decorate the tree with additional information.
    pg = pydot_graph(info, tree)

    # Write the tree to a file.
    write(pg, out)

    return tree

# dot -Tpdf output_raw.dot -o output.pdf

if __name__ == "__main__":
    out = os.path.join("genescape.pdf")

    iter = utils.get_stream(inp=utils.GO_LIST)

    data = utils.parse_terms(iter=iter)

    print(data)

    run(data=data, index=utils.INDEX, out=out)
