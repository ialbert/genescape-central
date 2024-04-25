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

NODE_ATTRS = {OUT_DEGREE: 0}

HEADER_KEY = "header"
TERMS_KEY = "terms"
TYPEDEFS_KEY = "typedefs"
INPUT_LIST = "input_list"
GENE_LIST = "gene_list"
GENE_LEN = "gene_len"
TOTAL_COUNT = "total_count"

SINGLE_VALUE = {"id", "name", "namespace", "comment"}
MULTI_VALUE = {"alt_id", "subset", "replaced_by", "consider"}

SYM2GO, GO2SYM, GO2NAME = "sym2go", "go2sym", "go2name"


@utils.timer
def build_graph(data):
    # The complete ontology graph
    graph = nx.DiGraph()
    terms = data[TERMS_KEY]

    nodes = filter(lambda x: not x.get("is_obsolete"), terms.values())
    # nodes = islice(nodes, 100)
    nodes = list(nodes)

    # Add individual nodes to the
    for node in nodes:
        oid = node["id"]
        name = node["name"]
        namespace = utils.NAMESPACE_MAP.get(node[NAMESPACE], "?")
        graph.add_node(oid, id=oid, name=name, namespace=namespace, **utils.NODE_ATTRS)

    for node in nodes:
        child = node["id"]
        for elem in node.get("is_a", []):
            parent = elem["target"]
            if graph.has_node(parent):
                graph.add_edge(parent, child)
            else:
                utils.warn(f"# Missing parent: {parent} for {node}")

    # Add the degree to the nodes
    for node in graph.nodes():
        out_degree = graph.out_degree(node)
        in_degree = graph.in_degree(node)
        graph.nodes[node][OUT_DEGREE] = out_degree
        graph.nodes[node][IN_DEGREE] = in_degree

    # save with cpickle
    with open("../../graph.pkl", "wb") as fp:
        pickle.dump(graph, fp)


@utils.timer
def parse_gaf(fname):
    stream = gzip.open(fname, mode="rt", encoding="UTF-8")
    stream = filter(lambda x: not x.startswith("!"), stream)
    stream = map(lambda x: x.strip(), stream)
    stream = csv.reader(stream, delimiter="\t")
    # stream = islice(stream, 1000)
    sym2go, go2sym, go2name = {}, {}, {}
    for row in stream:
        name, symb, goid, synon = row[1], row[2], row[4], row[10]

        sym2go.setdefault(symb, []).append(goid)
        sym2go.setdefault(name, []).append(goid)

        go2sym.setdefault(goid, []).append(symb)
        go2name.setdefault(goid, []).append(name)

    # Remove duplicates in case these exists.
    for key in sym2go:
        sym2go[key] = list(set(sym2go[key]))

    for key in go2sym:
        go2sym[key] = list(set(go2sym[key]))
        go2name[key] = list(set(go2name[key]))

    data = {
        SYM2GO: sym2go,
        GO2SYM: go2sym,
        GO2NAME: go2name,
    }

    # Save data as json in a gzip
    with gzip.open("../../gaf.json.gz", "wb") as fp:
        text = json.dumps(data, indent=4)
        fp.write(text.encode('utf-8'))


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
    subs = dict()
    terms = dict()
    typedefs = []

    data = {HEADER_KEY: head, TERMS_KEY: terms, TYPEDEFS_KEY: typedefs}

    for elems in head_stream:
        code = elems[0].strip(":")
        if code == "subsetdef":
            subs[elems[1]] = elems[2]
        else:
            head[code] = elems[1]

    # Add the subsetdef
    head["subsetdef"] = subs

    term = {}
    for elems in term_stream:

        code = elems[0].strip(":")

        # Exit this loop at the typedef stanza
        if code == "[Typedef]":
            break

        # Term stanza
        if code == "[Term]":
            # Yield the term if it exists
            if term:
                term["is_obsolete"] = term.get("is_obsolete", False)
                terms[term["id"]] = term
                term = {}
            continue

        if code == "is_a":
            target = elems[1]
            label = " ".join(elems[3:])
            term.setdefault("is_a", []).append(dict(target=target, label=label))
            continue

        if code in SINGLE_VALUE:
            term[code] = " ".join(elems[1:])
            continue

        if code == "def":
            text = elems[1]
            refs = parse_refs(elems[2])
            term[code] = dict(text=text, refs=refs)
            continue

        if code == "synonym":
            text = elems[1]
            scope = elems[2]
            refs = parse_refs(elems[3])
            term.setdefault(code, []).append(dict(text=text, scope=scope, refs=refs))
            continue

        if code in MULTI_VALUE:
            value = elems[1]
            term.setdefault(code, []).append(value)
            continue

        if code == "is_obsolete":
            term["is_obsolete"] = True
            continue

        if code == "relationship":
            key = elems[1]
            target = elems[2]
            label = " ".join(elems[4:])
            term.setdefault(code, []).append(dict(target=target, type=key, label=label))
            continue

    # Parse the typdefs
    term_stream = chain([["[Typedef]"]], term_stream)

    type_obj = dict()
    for elems in term_stream:
        code = elems[0].strip(":")
        if code == "[Typedef]":
            if type_obj:
                typedefs.append(type_obj)
            type_obj = {}
            continue

        if code in ("id", "namespace"):
            type_obj[code] = elems[1]
            continue

        if code == "is_a":
            target = elems[1]
            label = " ".join(elems[3:])
            type_obj.setdefault(code, []).append(dict(target=target, label=label))
            continue

        if code == "name":
            type_obj[code] = " ".join(elems[1:])
            continue

        if code.startswith("is_"):
            type_obj[code] = elems[1] == 'true'
            continue

    return data


@utils.timer
def save_json(obo_name, json_name):
    stream = utils.get_stream(obo_name)

    data = parse_obo(stream)

    text = json.dumps(data, indent=4)

    with gzip.open(json_name, "wb") as fp:
        fp.write(text.encode('utf-8'))


@utils.timer
def load_json(json_name):
    with gzip.open(json_name, "rb") as fp:
        text = fp.read().decode('utf-8')
        data = json.loads(text)

    return data


@utils.timer
def read_graph():
    with open("../../graph.pkl", "rb") as fp:
        obo = pickle.load(fp)

    with gzip.open("../../gaf.json.gz", "rb") as fp:
        text = fp.read().decode('utf-8')
        gaf = json.loads(text)

    tgt = "ABTB3 BCAS4 C3P1 GRTP1 SPOP ABCA2 PSMD3".split()

    tgt2set = set(tgt)

    sym2go = gaf[SYM2GO]

    miss2sym = set(filter(lambda x: x not in sym2go, tgt))
    valid2sym = list(filter(lambda x: x in sym2go, tgt))

    goids = map(sym2go.get, valid2sym)
    goids = chain.from_iterable(goids)
    goids = list(set(goids))

    # Check GOIds not found in the BOB
    miss2go = set(filter(lambda x: x not in obo.nodes, goids))
    valid2go = list(filter(lambda x: x in obo.nodes, goids))

    anc = set()
    for node in valid2go:
        anc = anc.union(nx.ancestors(obo, node))
    anc = anc.union(valid2go)

    # Subset the graph to the ancestors only.
    tree = obo.subgraph(anc)

    # Initialize the subtree
    for goid in tree.nodes():
        node = tree.nodes[goid]
        node[TOTAL_COUNT] = len(gaf[GO2SYM].get(goid, []))
        node[INPUT_LIST] = False
        node[GENE_LIST] = set()

    # Update the subtree with the gene list
    for goid in valid2go:
        node = tree.nodes[goid]
        symbs = set(gaf[GO2SYM].get(goid, []) + gaf[GO2NAME].get(goid, []))
        annot = tgt2set & symbs
        node[INPUT_LIST] = True
        node[GENE_LIST] = annot

    # The leaf nodes of the subtree.
    leaf = list(filter(lambda x: tree.out_degree(x) == 0, valid2go))

    for goid in leaf:
        node = tree.nodes[goid]
        genes = node[GENE_LIST]
        anc = nx.ancestors(tree, goid)
        for anc_id in anc:
            anc_node = tree.nodes[anc_id]
            anc_node[GENE_LIST] = anc_node[GENE_LIST] | genes

    # Annotate subtree with gene counts
    for goid in tree.nodes():
        node = tree.nodes[goid]
        node[GENE_LEN] = len(node[GENE_LIST])

    # Sort the graph nodes to make the output deterministic.

    # Sort nodes
    s_nodes = sorted(tree.nodes(data=True))

    # Sort edges (not yet)
    s_edges = tree.edges(data=True)

    s_tree = nx.DiGraph()
    s_tree.add_nodes_from(s_nodes)
    s_tree.add_edges_from(s_edges)

    return s_tree

def fix_text(text):
    return f'"{text}"'

def human_readable(value, digits=0):
    try:
        newval = int(round(float(value)/1000, digits))
    except ValueError:
        newval = 0
    newval = f"{newval:d}K" if newval > 1 else value
    return newval

def run():
    res = resources.init()
    obo_name = res.OBO_FILE
    json_name = "../../data.json.gz"

    # save_json(obo_name, json_name)

    # data = load_json(json_name)

    # build_graph(data)

    gaf_fname = res.GAF_FILE

    # parse_gaf(gaf_fname)

    tree = read_graph()

    # Create the pydot graph.
    pg = pydot.Dot("genescape", graph_type="digraph")
    for goid in tree.nodes():
        node = tree.nodes[goid]
        name = node["name"]
        if node[OUT_DEGREE] == 0:
            fillcolor = utils.LEAF_COLOR
        elif node[INPUT_LIST]:
            fillcolor = utils.INPUT_COLOR
        else:
            key = node[NAMESPACE]
            fillcolor = utils.NAMESPACE_COLORS.get(key, utils.BG_COLOR)

        node_id = fix_text(goid)
        text = textwrap.fill(name, width=20)
        t_count = human_readable(node[TOTAL_COUNT])
        g_count = len(node[GENE_LIST])
        if node[INPUT_LIST]:
            label = f"{goid}\n{text} [{t_count}]\n({g_count}/100)"
        else:
            label = f"{goid}\n{text} [{t_count}]"
        label = fix_text(label)
        pnode = pydot.Node(node_id, label=label, fillcolor=fillcolor, shape="box", style="filled")
        pg.add_node(pnode)

    for edge in tree.edges():
        edge1 = fix_text(edge[0])
        edge2 = fix_text(edge[1])
        pedge = pydot.Edge(edge1, edge2)
        pg.add_edge(pedge)

    print(pg)

    pg.set_graph_defaults()
    pg.set_node_defaults(shape="box", style="filled")
    pg.write_pdf("../../output.pdf")




if __name__ == '__main__':
    run()
