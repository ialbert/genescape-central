"""
Graph representation of an ontology
"""
import io
import itertools
from pathlib import Path
import gzip, sys, re, json, csv, textwrap, pickle
from genescape import resources, utils
from itertools import islice, takewhile, dropwhile, tee, chain
import networkx as nx
import pydot
from pprint import pprint
from genescape.__about__ import __version__
import pandas as pd

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
INFO_KEY = "info"

# Ontology key.
OBO_KEY = "obo"

# Symbol to GO, GO to symbol, and name to symbol mappings.
SYM2GO, GO2SYM, NAME2SYM = "sym2go", "go2sym", "name2sym"

# True for a GO term that is present in the input data.
INP_FLAG = "inp_flag"

# A list that stores the symbols that support a GO term.
INP_SYM = "inp_sym"

# The length of the INP_SYMB list.
INP_LEN = "inp_len"

# A list that stores all the of a GO subtree.
INP_SYM_TOT = "inp_sym_tot"

# The lenght of the INP_SYMB_TOT list.
INP_LEN_TOT = "inp_len_tot"

# The list of descendant nodes for the GO term.
DESC_LIST = "desc_list"

# The number of descendants for the GO term.
DESC_COUNT = "desc_count"

# The number of annotations for the GO term.
ANNO_COUNT = "ann_count"

# The cumulative sum of annotations for GO term.
ANNO_TOTAL = "ann_total"

# Status keys
SYM_VALID = "sym_valid"
SYM_MISS = "sym_miss"
GO_VALID = "go_valid"
GO_MISS = "go_miss"

# Node attributes
NODE_ATTRS = {OUT_DEGREE: 0, DESC_COUNT: 0, ANNO_COUNT: 0, ANNO_TOTAL: 0}

WIDTH = 16.9
HEIGHT = 6.0


def dpi(size):
    value = size / WIDTH
    return value


def build_graph(data):
    """
    Build an ontology graph from a JSON data structure.
    """
    # The complete ontology graph
    graph = nx.DiGraph()
    obo = data[OBO_KEY]

    # Remove obsolete terms.
    obo = filter(lambda x: not x.get("is_obsolete"), obo.values())

    # nodes = islice(nodes, 100)
    obo = list(obo)

    # Add individual nodes to the
    for row in obo:
        oid = row["id"]
        name = row["name"]
        namespace = utils.NAMESPACE_MAP.get(row[NAMESPACE], "?")
        anno_count = row.get(ANNO_COUNT, -1)
        anno_total = row.get(ANNO_TOTAL, -1)
        desc_count = row.get(DESC_COUNT, -1)
        out_degree = row.get(OUT_DEGREE, -1)
        in_degree = row.get(IN_DEGREE, -1)
        kwargs = {OUT_DEGREE: out_degree, IN_DEGREE: in_degree, DESC_COUNT: desc_count, ANNO_COUNT: anno_count,
                  ANNO_TOTAL: anno_total}
        graph.add_node(oid, id=oid, name=name, namespace=namespace, **kwargs)

    for row in obo:
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

    stream, header = itertools.tee(stream, 2)

    # Parse the headers
    header = takewhile(lambda x: x.startswith("!"), header)
    header = map(lambda x: x.strip("!"), header)
    header = map(lambda x: x.strip(""), header)
    header = filter(None, header)
    header = csv.reader(header, delimiter=" ")
    header = filter(lambda x: len(x)>1, header)
    info = dict(gaf_fname=Path(fname).name)
    for row in header:
        key = row[0].strip(":")
        if key == "gaf-version" or key == "go-version":
            info[key] = row[1]
        elif key == "generated-by" or key == "date-generated":
            info.setdefault(key, []).append(row[1])

    # Iterate over the body
    stream = dropwhile(lambda x: x.startswith("!"), stream)
    stream = map(lambda x: x.strip(), stream)
    stream = csv.reader(stream, delimiter="\t")
    # stream = islice(stream, 1000)
    sym2go, go2sym, name2sym = {}, {}, {}
    for row in stream:
        name, symb, goid, synon = row[1], row[2], row[4], row[10]

        # Convert to uppercase.
        name = name.upper()
        symb = symb.upper()
        goid = goid.upper()

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

    return gaf, info


def parse_refs(text):
    text = text.strip('[').strip(']').strip()
    refs = [ref for ref in text.split(",") if ref]
    return refs


# Parse a stream to an OBO file and for
@utils.timer
def parse_obo(obo_fname):

    # Open the file
    stream = utils.get_stream(obo_fname)

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

    info = dict(obo_fname=Path(obo_fname).name)
    terms = dict()

    data = {OBO_KEY: terms}

    INCLUDE = ["format-version", "data-version", "ontology"]
    INCLUDE = set(INCLUDE)

    # Fill the headers
    for elems in head_stream:
        code = elems[0].strip(":")
        if code in INCLUDE:
            info[code] = elems[1]

    term = {}
    for elems in term_stream:
        code = elems[0].strip(":")

        # Exit this loop at the typedef stanza
        if code == "[Typedef]":
            break

        if code == "[Term]" and term:
            is_obsolete = term.get("is_obsolete", False)
            if not is_obsolete:
                terms[term["id"]] = term
            term = {}
            continue

        if code == "is_a":
            target = elems[1]
            term.setdefault("is_a", []).append(target)
            continue

        if code == "name":
            term[code] = " ".join(elems[1:])
            continue

        if code == "id" or code == "namespace":
            term[code] = elems[1]
            continue

        if code == "is_obsolete":
            term["is_obsolete"] = True
            continue

        continue

    # Last term needs to be added
    terms[term["id"]] = term

    return data, info


def make_graph(idx, graph, targets, root=NS_ALL, mincount=1, pattern=''):
    # Better defaults
    targets = targets or []

    # Inputs must be unique.
    targets = set(map(lambda x: x.upper(), targets))

    obo = idx[OBO_KEY]
    sym2go = idx[SYM2GO]

    # Symbols not found in the association file.
    sym_miss = set(filter(lambda x: x not in sym2go and x not in obo, targets))

    # Print notification on missing symbols.
    if sym_miss:
        utils.warn(f"Missing symbols: {sym_miss}")

    # Symbols found in the association file.
    sym_valid = list(filter(lambda x: x in sym2go or x in obo, targets))

    # A list of GO terms in the input list.
    goids = []

    # Maps GO ids to input target symbols.
    go2inp = dict()

    # Build the symbol mappings.
    for sym in sym_valid:
        values = sym2go.get(sym, []) or [sym]
        for goid in values:
            go2inp.setdefault(goid, []).append(sym)
            goids.append(goid)

    # Terms not found in the OBO
    go_miss = list(filter(lambda x: x not in graph.nodes, goids))

    # Missing GO terms.
    if go_miss:
        utils.warn(f"Missing GO terms: {go_miss}")

    # Subselect the valid GO terms
    go_valid = filter(lambda x: x in graph.nodes, goids)

    # Apply the filtering if a root is given.
    if root != NS_ALL:
        go_valid = filter(lambda x: graph.nodes[x][NAMESPACE] == root, go_valid)

    # Apply the pattern filter
    if pattern:
        try:
            patt = re.compile(pattern, re.IGNORECASE)
            go_valid = filter(lambda x: re.search(patt, graph.nodes[x]["name"]), go_valid)
        except re.error:
            utils.error(f"Invalid pattern: {pattern}", stop=False)

    # Filter by minimum count
    go_valid = filter(lambda x: len(go2inp[x]) >= mincount, go_valid)

    # Convert to a list
    go_valid = list(go_valid)

    # Provides a quick lookup for the valid GO terms.
    valid2tgt = set(go_valid)

    # Find the ancestors for each node.
    anc = set()
    for node in go_valid:
        anc = anc.union(nx.ancestors(graph, node))

    # Add the original nodes as well.
    anc = anc.union(go_valid)

    # Subset the graph to the ancestors only.
    tree = graph.subgraph(anc)

    # Initialize the subtree
    for node_id in tree.nodes():
        node = tree.nodes[node_id]
        sources = go2inp.get(node_id, [])
        node[INP_FLAG] = node_id in valid2tgt
        node[INP_SYM] = list(sources)
        node[INP_LEN] = len(sources)

    # Travers and update the cumulative totals
    def traverse(tree, node_id, store):

        store[node_id] = [node_id]

        for child_id in tree.successors(node_id):
            if child_id not in store:
                traverse(tree, child_id, store)
                store[node_id].extend(store[child_id])

        inp_sym = []
        for parent_id in store[node_id]:
            inp_sym += tree.nodes[parent_id][INP_SYM]

        # Shortcut to the node
        node = tree.nodes[node_id]

        # Store the descendants of the subtree only
        node[DESC_LIST] = store[node_id]
        node[INP_SYM_TOT] = list(set(inp_sym))
        node[INP_LEN_TOT] = len(inp_sym)

    roots = filter(lambda x: tree.in_degree(x) == 0, tree.nodes())
    for root in roots:
        store = dict()
        traverse(tree, root, store=store)

    # Sort nodes
    s_nodes = sorted(tree.nodes(data=True))

    # Sort edges (not yet)
    s_edges = tree.edges(data=True)

    s_tree = nx.DiGraph()
    s_tree.add_nodes_from(s_nodes)
    s_tree.add_edges_from(s_edges)

    # Populate the status
    status = {
        SYM_VALID: sym_valid,
        SYM_MISS: sym_miss,
        GO_VALID: go_valid,
        GO_MISS: go_miss,
    }

    utils.info(f"graph: {len(s_tree.nodes)} nodes and {len(s_tree.edges)} edges")


    return s_tree, status


def make_pydot(tree, status):
    # Pull the status information
    sym_valid = status[SYM_VALID]

    # Create the pydot graph.
    pg = pydot.Dot("genescape", graph_type="digraph")
    for goid in tree.nodes():
        node = tree.nodes[goid]
        name = node["name"]
        out_degree = node[OUT_DEGREE]
        is_input = node[INP_FLAG]
        is_leaf = out_degree == 0

        key = node[NAMESPACE]
        fillcolor = utils.NAMESPACE_COLORS.get(key, utils.BG_COLOR)

        node_id = fix_text(goid)
        text = textwrap.fill(name, width=20)
        ann_count = human_readable(node[ANNO_COUNT])
        ann_total = human_readable(node[ANNO_TOTAL])
        desc_count = human_readable(node[DESC_COUNT])
        out_degree = node[OUT_DEGREE]
        src_sym = node[INP_SYM]
        src_tot = node[INP_LEN_TOT]

        valid_len = len(sym_valid)
        label = f"{goid}\n{text} [{ann_count}]"
        if is_input:
            fillcolor = utils.LEAF_COLOR if is_leaf else utils.INPUT_COLOR
            label = f"{label}\n({src_tot}/{valid_len})"

        label = fix_text(label)
        pnode = pydot.Node(node_id, label=label, fillcolor=fillcolor, shape="box", style="filled")
        pg.add_node(pnode)

    for edge in tree.edges():
        edge1 = fix_text(edge[0])
        edge2 = fix_text(edge[1])
        pedge = pydot.Edge(edge1, edge2)
        pg.add_edge(pedge)

    return pg

def fix_text(text):
    return f'"{text}"'


def human_readable(value, digits=0):
    try:
        newval = int(round(float(value) / 1000, digits))
    except ValueError:
        newval = 0
    newval = f"{newval:d}K" if newval > 1 else value
    return newval


@utils.memoize
def load_json(path):
    if not isinstance(path, Path):
        path = Path(path)

    # Print error if path does not exist
    if not path.exists():
        utils.stop(f"file not found: {path}")

    stream = gzip.open(path, "rb") if path.name.endswith(".gz") else open(path, "rt")
    with stream as fp:
        text = fp.read().decode('utf-8')
        data = json.loads(text)

    return data


@utils.timer
def save_json(data, path):
    if not isinstance(path, Path):
        path = Path(path)
    stream = gzip.open(path, "wb") if path.name.endswith(".gz") else open(path, "wb")
    with stream as fp:
        text = json.dumps(data, indent=4)
        fp.write(text.encode('utf-8'))





def load_index(fname):
    idx = load_json(fname)
    return idx


@utils.memoize
def load_graph(fname):
    idx = load_json(fname)
    graph = build_graph(idx)
    return idx, graph


def stats(idx=None):
    if isinstance(idx, str):
        utils.stop("index must be an object not string")
    map_count, sym_count, go_count = idx_stats(idx)
    source = idx.get(INFO_KEY, {}).get("gaf_fname", "unknown")
    msg = f"index: {map_count:,} mappings,  {sym_count:,} symbols, {go_count:,} terms ({source})"
    utils.info(msg)
    return map_count, sym_count, go_count


def idx_stats(idx):
    go2sym = idx[GO2SYM]
    sym2go = idx[SYM2GO]

    map_count = 0
    for value in go2sym.values():
        map_count += len(list(set(value)))
    sym_count = len(sym2go)
    go_count = len(go2sym)

    return map_count, sym_count, go_count


def build_index(obo_fname, gaf_fname, idx_fname):
    """
    Builds an index from an OBO and GAF file.
    """

    obo_obj, info1 = parse_obo(obo_fname)
    gaf_obj, info2 = parse_gaf(gaf_fname)

    # Shortcut to the obo dictionary.
    obo = obo_obj[OBO_KEY]

    # Fill in annotation counts
    for node_id in obo_obj[OBO_KEY]:
        values = gaf_obj[GO2SYM].get(node_id, [])
        obo[node_id][ANNO_COUNT] = len(values)
        obo[node_id][ANNO_TOTAL] = len(values)

    # Create the info dictionary
    info = { "genescape-version": __version__ }
    info.update(info1)
    info.update(info2)

    # Merge the two dictionaries.
    idx = { INFO_KEY:info }
    idx.update(obo_obj)
    idx.update(gaf_obj)

    # Fill missing graph measures.
    fill_graph(idx=idx)

    # Print database stats.
    stats(idx=idx)

    # Save the index to the file.
    save_json(idx, idx_fname)


@utils.timer
def fill_graph(idx):
    """
    Fills the index with additional information
    """

    # Build an incomplete graph from the index.
    graph = build_graph(idx)

    obo = idx[OBO_KEY]
    gaf = idx[GO2SYM]

    # Add the degree to the nodes
    for node_id in graph.nodes():
        out_degree = graph.out_degree(node_id)
        in_degree = graph.in_degree(node_id)
        obo[node_id][OUT_DEGREE] = out_degree
        obo[node_id][IN_DEGREE] = in_degree
        obo[node_id][DESC_COUNT] = out_degree

    # Update annotations for each node
    topo_nodes = list(nx.topological_sort(graph))

    for node_id in reversed(topo_nodes):
        total = obo[node_id][ANNO_TOTAL]
        desc_count = obo[node_id][DESC_COUNT]
        for predecessor in graph.predecessors(node_id):
            obo[predecessor][ANNO_TOTAL] += total
            obo[predecessor][DESC_COUNT] += desc_count

    return obo

def annotate(tree, status, nodes=None):
    sym_valid = status[SYM_VALID]
    sym_size = len(sym_valid)

    inp_nodes = filter(lambda x: tree.nodes[x][INP_FLAG], tree.nodes())

    rows = []
    for node_id in inp_nodes:
        node = tree.nodes[node_id]
        func_name = node["name"]
        source = "|".join(sorted(node[INP_SYM]))
        count = node[INP_LEN]
        ann_count = node[ANNO_COUNT]
        ann_total = node[ANNO_TOTAL]
        desc_count = node[DESC_COUNT]

        data = dict(coverage=count, function=func_name,
                    node_id=node_id,
                    source=source,
                    size=sym_size,
                    ann_count=ann_count,
                    ann_total=ann_total,
                    desc_count=desc_count
                    )
        rows.append(data)

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(by='coverage', ascending=False)

    return df


def save_graph(pgraph, fname, imgsize=2048):
    """
    Saves the pydot graph to a file
    """
    utils.info(f"file: {fname}")

    pgraph.set_graph_defaults()

    if fname.endswith(".dot"):
        pgraph.write_raw(f"{fname}")
    elif fname.endswith(".pdf"):
        pgraph.write_pdf(fname)
    elif fname.endswith(".png"):
        pgraph.set_graph_defaults(size=f"{WIDTH},{HEIGHT}", dpi=dpi(imgsize))
        pgraph.write_png(fname)
    else:
        utils.warn(f"Unknown output format: {fname}")


def run(idx_fname, genes, root=utils.NS_ALL,  pattern="", mincount=1):
    """
    Creates a tree and an annotation
    """

    utils.info(f"index: {idx_fname}")

    # build_index(obo_fname=obo_fname, gaf_fname=gaf_fname, idx_fname=idx_fname)
    idx, graph = load_graph(idx_fname)

    # Print the statistics
    stats(idx)

    # Select the subgraph
    tree, status = make_graph(targets=genes, idx=idx, graph=graph, root=root, mincount=mincount, pattern=pattern)

    # Generate the annotations.
    ann = annotate(tree=tree, status=status)

    # Transform the tree into a pydot graph
    dot = make_pydot(tree, status)

    return idx, dot, tree, ann, status

def build_test():
    res = resources.init()

    obo_fname = res.OBO_FILE
    gaf_fname = res.GAF_FILE
    idx_fname = "demo.json.gz"

    build_index(obo_fname=obo_fname, gaf_fname=gaf_fname, idx_fname=idx_fname)

if __name__ == '__main__':

    #build_test()

    #sys.exit()

    genes = "GO:0035639 GO:0097159  ".split()

    res = resources.init()
    obo_fname = res.OBO_FILE
    gaf_fname = res.GAF_FILE
    idx_fname = res.INDEX_FILE

    pattern = ""
    mincount = 1
    root = utils.NS_ALL

    dot, tree, ann = run(genes=genes, idx_fname=idx_fname,  root=root, pattern=pattern, mincount=mincount)

    #save_graph(dot, fname="output.pdf", imgsize=2048)

    text = ann.to_csv(index=False)

    print(text)
