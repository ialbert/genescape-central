"""
Graph representation of an ontology
"""

import gzip, sys, re, json, csv, textwrap, pickle
from genescape import resources, utils
from itertools import islice, takewhile, dropwhile, tee, chain
import networkx as nx
import pydot

# Namespace categories
NS_BP, NS_MF, NS_CC, NS_ALL = "BP", "MF", "CC", "ALL"

# Additional fields
OUT_DEGREE = "out_degree"
IN_DEGREE = "in_degree"
NAMESPACE = "namespace"

# Map the GO categories namespaces.
NAMESPACE_MAP = {
    "biological_process": NS_BP,
    "molecular_function": NS_MF,
    "cellular_component": NS_CC,
}

# Set the default attributes for the nodes
# NODE_ATTRS = dict(fillcolor=BG_COLOR, shape=SHAPE, style="filled")


# Data keys in the index.
HEADER_KEY = "info"

# Ontology key.
OBO_KEY = "obo"

# Mapping keys.
SYM2GO, GO2SYM, NAME2SYM = "sym2go", "go2sym", "name2sym"


INPUT_LIST = "input_list"
SOURCE_SYM = "sources"
SOURCE_LEN = "src_len"

# The number of descendants for the GO term.
DESC_COUNT = "desc_count"

# The number of annotation for the GO term.
ANNO_COUNT = "anno_count"

# The cumulative sum of annotations for GO term.
ANNO_TOTAL = "anno_total"

# Node attributes
NODE_ATTRS = {OUT_DEGREE: 0, DESC_COUNT: 0, ANNO_COUNT: 0, ANNO_TOTAL: 0}

@utils.timer
def build_graph(data):
    """
    Build an ontology graph from a JSON data structure.
    """
    # The complete ontology graph
    graph = nx.DiGraph()
    terms = data[OBO_KEY]

    terms = filter(lambda x: not x.get("is_obsolete"), terms.values())
    # nodes = islice(nodes, 100)
    terms = list(terms)

    # Add individual nodes to the
    for row in terms:
        oid = row["id"]
        name = row["name"]
        namespace = utils.NAMESPACE_MAP.get(row[NAMESPACE], "?")
        anno_count = row.get(ANNO_COUNT, -1)
        anno_total = row.get(ANNO_TOTAL, -1)
        desc_count = row.get(DESC_COUNT, -1)
        out_degree = row.get(OUT_DEGREE, -1)
        in_degree = row.get(IN_DEGREE, -1)
        kwargs = {OUT_DEGREE: out_degree, IN_DEGREE: in_degree, DESC_COUNT: desc_count, ANNO_COUNT: anno_count, ANNO_TOTAL: anno_total}
        graph.add_node(oid, id=oid, name=name, namespace=namespace, **kwargs)

    for row in terms:
        child = row["id"]
        for parent in row.get("is_a", []):
            if graph.has_node(parent):
                graph.add_edge(parent, child)
            else:
                utils.warn(f"# Missing parent: {parent} for {row}")

    return graph

@utils.timer
def parse_gaf(fname):
    stream = gzip.open(fname, mode="rt", encoding="UTF-8")
    stream = filter(lambda x: not x.startswith("!"), stream)
    stream = map(lambda x: x.strip(), stream)
    stream = csv.reader(stream, delimiter="\t")
    # stream = islice(stream, 1000)
    sym2go, go2sym, name2sym = {}, {}, {}
    for row in stream:
        name, symb, goid, synon = row[1], row[2], row[4], row[10]

        sym2go.setdefault(symb, []).append(goid)
        sym2go.setdefault(name, []).append(goid)

        go2sym.setdefault(goid, []).append(symb)
        name2sym[name] = symb

    # Remove duplicates in case these exists.
    for key in sym2go:
        sym2go[key] = list(set(sym2go[key]))

    for key in go2sym:
        go2sym[key] = list(set(go2sym[key]))

    gaf = {
        SYM2GO: sym2go,
        GO2SYM: go2sym,
        NAME2SYM: name2sym
    }

    return gaf

def parse_refs(text):
    text = text.strip('[').strip(']').strip()
    refs = [ref for ref in text.split(",") if ref]
    return refs


# Parse a stream to an OBO file and for
@utils.timer
def parse_obo(stream):
    # Remove empty rows
    stream = filter(None, stream)

    # Turn the stream into a CSV reader
    stream = csv.reader(stream, delimiter=" ")

    # Split the stream into three streams
    head_stream, term_stream = tee(stream, 2)

    # Up the reaching the first term
    head_stream = takewhile(lambda x: x[0] != "[Term]", head_stream)

    # Drop until you reach term and take until you reach the typedef
    term_stream = dropwhile(lambda x: x[0] != "[Term]", term_stream)

    head = dict()
    terms = dict()

    data = {HEADER_KEY: head, OBO_KEY: terms}

    INCLUDE = [ "format-version", "data-version", "ontology" ]
    INCLUDE = set(INCLUDE)

    # Fill the headers
    for elems in head_stream:
        code = elems[0].strip(":")
        if code in INCLUDE:
            head[code] = elems[1]

    term = {}
    for elems in term_stream:
        code = elems[0].strip(":")

        # Exit this loop at the typedef stanza
        if code == "[Typedef]":
            break

        if code == "[Term]" and term:
            term["is_obsolete"] = term.get("is_obsolete", False)
            terms[term["id"]] = term
            term = {}
            continue

        if code == "is_a":
            target = elems[1]
            term.setdefault("is_a", []).append(target)
            continue

        if code == "id" or code == "name" or code == "namespace":
            term[code] = elems[1]
            continue

        if code == "is_obsolete":
            term["is_obsolete"] = True
            continue

        continue

    # Last term needs to be added
    terms[term["id"]] = term

    return data



@utils.timer
def make_subgraph(idx, graph, tgt=None, root=NS_MF):

    tgt = tgt or "ABTB3 BCAS4 C3P1 GRTP1 SPOP ABCA2 PSMD3 GO:0046983 GO:1901265".split()

    # Unique targets
    tgt2set = set(tgt)

    obo = idx[OBO_KEY]
    sym2go = idx[SYM2GO]
    go2sym = idx[GO2SYM]

    # Symbols not found in the association file.
    miss2sym = set(filter(lambda x: x not in sym2go, tgt))

    # Symbols found in the association file.
    valid2sym = list(filter(lambda x: x in sym2go or x in obo, tgt))

    # Map the symbols to GO terms
    goids = map(lambda x: sym2go.get(x, [x]), valid2sym)
    goids = chain.from_iterable(goids)
    goids = list(set(goids))

    # Terms not found in the OBO
    miss2go = set(filter(lambda x: x not in graph.nodes, goids))

    # Valid GO terms
    valid2go = filter(lambda x: x in graph.nodes, goids)

    # Keep only terms where the root is the same as the namespace
    if root:
        valid2go = filter(lambda x: graph.nodes[x][NAMESPACE] == root, valid2go)

    valid2go = list(valid2go)
    valid2tgt = set(valid2go)

    anc = set()
    for node in valid2go:
        anc = anc.union(nx.ancestors(graph, node))
    anc = anc.union(valid2go)

    # Subset the graph to the ancestors only.
    tree = graph.subgraph(anc)

    # Initialize the subtree
    for node_id in tree.nodes():
        node = tree.nodes[node_id]
        is_input = node_id in valid2tgt
        if is_input:
            sources = list(set(go2sym.get(node_id, [])) & tgt2set)
        else:
            sources = []
        node[INPUT_LIST] = is_input
        node[SOURCE_SYM] = sources
        node[SOURCE_LEN] = len(sources)

    # Sort nodes
    s_nodes = sorted(tree.nodes(data=True))

    # Sort edges (not yet)
    s_edges = tree.edges(data=True)

    s_tree = nx.DiGraph()
    s_tree.add_nodes_from(s_nodes)
    s_tree.add_edges_from(s_edges)

    return s_tree, valid2sym


def fix_text(text):
    return f'"{text}"'


def human_readable(value, digits=0):
    try:
        newval = int(round(float(value) / 1000, digits))
    except ValueError:
        newval = 0
    newval = f"{newval:d}K" if newval > 1 else value
    return newval

@utils.timer
def load_json(fname):
    stream = gzip.open(fname, "rb") if fname.endswith(".gz") else open(fname, "rt")
    with stream as fp:
        text = fp.read().decode('utf-8')
        data = json.loads(text)

    return data

@utils.timer
def save_json(data, fname):
    stream = gzip.open(fname, "wb") if fname.endswith(".gz") else open(fname, "wb")
    with stream as fp:
        text = json.dumps(data, indent=4)
        fp.write(text.encode('utf-8'))

@utils.timer
def compute_graph_measures(idx):
    """
    Fills the index with additional information
    """

    graph = build_graph(idx)

    obo = idx[OBO_KEY]

    # Add the degree to the nodes
    for node_id in graph.nodes():
        out_degree = graph.out_degree(node_id)
        in_degree = graph.in_degree(node_id)
        obo[node_id][OUT_DEGREE] = out_degree
        obo[node_id][IN_DEGREE] = in_degree

    def traverse(tree, node_id, store):
        desc_total = 0
        anno_total = obo[node_id][ANNO_COUNT]
        for child in tree.successors(node_id):
            if child not in store:
                traverse(tree, child, store)
            desc_total += store[child] + 1
            anno_total += obo[child][ANNO_COUNT]
        store[node_id] = desc_total
        obo[node_id][DESC_COUNT] = desc_total
        obo[node_id][ANNO_TOTAL] = anno_total

    # From the roots backfill graph measures
    roots = filter(lambda x: graph.in_degree(x) == 0, graph.nodes())
    for root in roots:
        store = dict()
        traverse(graph, root, store=store)

    return obo

@utils.memoize
def load_index(fname):
    idx = load_json(fname)
    return idx

@utils.memoize
def load_graph(fname):
    idx = load_json(fname)
    graph = build_graph(idx)
    return idx, graph

def run(cnf=None, obo_fname=None, gaf_fname=None):

    res = resources.init(cnf)
    obo_fname = obo_fname or res.OBO_FILE
    gaf_fname = gaf_fname or res.GAF_FILE

    obo_json = "../../tmp/obo.json.gz"
    gaf_json = "../../tmp/gaf.json.gz"
    idx_json = "../../tmp/index.json.gz"

    if 0:
        stream = utils.get_stream(obo_fname)

        obo = parse_obo(stream)
        gaf = parse_gaf(gaf_fname)

        # Fill in annotation counts
        for node_id in obo[OBO_KEY]:
            values = gaf[GO2SYM].get(node_id, [])
            obo[OBO_KEY][node_id][ANNO_COUNT] = len(values)

        idx = dict(obo)
        idx.update(gaf)

        compute_graph_measures(idx=idx)

        save_json(idx, idx_json)

    idx, graph = load_graph(idx_json)

    idx, graph = load_graph(idx_json)

    tree, valid2sym = make_subgraph(idx=idx, graph=graph)


    # Create the pydot graph.
    pg = pydot.Dot("genescape", graph_type="digraph")
    for goid in tree.nodes():
        node = tree.nodes[goid]
        name = node["name"]
        out_degree = node[OUT_DEGREE]
        is_input = node[INPUT_LIST]
        is_leaf = out_degree == 0

        key = node[NAMESPACE]
        fillcolor = utils.NAMESPACE_COLORS.get(key, utils.BG_COLOR)

        node_id = fix_text(goid)
        text = textwrap.fill(name, width=20)
        ann_count = human_readable(node[ANNO_COUNT])
        ann_total = human_readable(node[ANNO_TOTAL])
        desc_count = human_readable(node[DESC_COUNT])
        out_degree = node[OUT_DEGREE]

        src_count = node[SOURCE_LEN]
        valid_len = len(valid2sym)
        label = f"{goid}\n{text} [{ann_count}]"
        if is_input:
            fillcolor = utils.LEAF_COLOR if is_leaf else utils.INPUT_COLOR
            label = f"{label}\n({src_count}/{valid_len})"

        label = fix_text(label)
        pnode = pydot.Node(node_id, label=label, fillcolor=fillcolor, shape="box", style="filled")
        pg.add_node(pnode)

    for edge in tree.edges():
        edge1 = fix_text(edge[0])
        edge2 = fix_text(edge[1])
        pedge = pydot.Edge(edge1, edge2)
        pg.add_edge(pedge)

    #print(pg)

    pg.set_graph_defaults()
    pg.set_node_defaults(shape="box", style="filled")
    pg.write_pdf("../../output.pdf")


if __name__ == '__main__':
    run()
