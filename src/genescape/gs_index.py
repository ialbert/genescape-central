"""
Represents a GeneScape index.
"""
import csv, gzip, json, os
from pathlib import Path
from itertools import tee, takewhile, dropwhile, islice
from genescape import utils
import networkx as nx

class Index:
    INFO_KEY = "info"
    OBO_KEY = "obo"
    ANNO_COUNT = "anno_count"
    ANNO_TOTAL = "anno_total"
    DESC_COUNT = "desc_count"
    NAMESPACE = "namespace"

    SYM2GO, GO2SYM, NAME2SYM = "sym2go", "go2sym", "name2sym"

    def __init__(self, data=None):
        # The data storage.
        self.data = data or dict()

        # Information on the index.
        self.info = self.data.get(self.INFO_KEY) or dict()

        # The OBO data.
        self.obo = self.data.get(self.OBO_KEY) or dict()

        # Maps symbols to GO terms.
        self.sym2go = self.data.get(self.SYM2GO) or dict()

        # Maps GO terms to symbols.
        self.go2sym = self.data.get(self.GO2SYM) or dict()

        # Maps names to symbols (synonyms).
        self.name2sym = self.data.get(self.NAME2SYM) or dict()

        # The graph representation of the ontology.
        self.graph = nx.DiGraph()

    def init_graph(self):
        self.graph = build_graph(self)

    def stats(self):
        map_count = 0
        for value in self.go2sym.values():
            map_count += len(list(set(value)))
        sym_count = len(self.sym2go)
        go_count = len(self.go2sym)

        return map_count, sym_count, go_count

    def __str__(self):
        map_count, sym_count, go_count = self.stats()
        source = self.info.get("gaf_fname", "unknown")
        return f"Index: {map_count:,d} associations of {sym_count:,d} genes over {go_count:,d} GO terms ({source})"


class IndexGraph:
    """
    Represents a GeneScape index with a graph.
    """
    def __init__(self, idx):

        # Store the index.
        self.idx = idx

        # Generate the graph.
        self.graph = build_graph(idx)


# Parse a stream to an OBO file and for
@utils.timer
def parse_obo(obo_fname, idx):

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

    # Shortcut to the info object.
    info = idx.info

    # Shortcut to the OBO object.
    obo = idx.obo

    # Read the obo file
    info['obo_fname'] = Path(obo_fname).name

    INCLUDE = ["format-version", "data-version", "ontology"]
    INCLUDE = set(INCLUDE)

    # Fill the headers
    for elems in head_stream:
        code = elems[0].strip(":")
        if code in INCLUDE:
            info[code] = elems[1]

    # Read each individual OBO term.
    term = {}
    for elems in term_stream:
        code = elems[0].strip(":")

        # Exit this loop at the typedef stanza
        if code == "[Typedef]":
            break

        if code == "[Term]" and term:
            is_obsolete = term.get("is_obsolete", False)
            if not is_obsolete:
                obo[term["id"]] = term
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
    obo[term["id"]] = term

    return idx

@utils.timer
def parse_gaf(fname, idx):

    # Open the file
    info = idx.info

    stream = gzip.open(fname, mode="rt", encoding="UTF-8")

    stream, header = tee(stream, 2)

    # Parse the headers
    header = takewhile(lambda x: x.startswith("!"), header)
    header = map(lambda x: x.strip("!"), header)
    header = map(lambda x: x.strip(""), header)
    header = filter(None, header)
    header = csv.reader(header, delimiter=" ")
    header = filter(lambda x: len(x)>1, header)
    info ['gaf_fname'] = Path(fname).name
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
    #stream = islice(stream, 1000)
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

    # Update the index storage.
    idx.sym2go.update(sym2go)
    idx.go2sym.update(go2sym)
    idx.name2sym.update(name2sym)

    obo = idx.obo
    # Fill in annotation counts
    for node_id in obo:
        values = idx.go2sym.get(node_id, [])
        obo[node_id][idx.ANNO_COUNT] = len(values)
        obo[node_id][idx.ANNO_TOTAL] = len(values)

    return idx

@utils.memoize
def load_index(path):
    if not isinstance(path, Path):
        path = Path(path)

    # Print error if path does not exist
    if not path.exists():
        utils.stop(f"file not found: {path}")

    stream = gzip.open(path, "rb") if path.name.endswith(".gz") else open(path, "rt")
    with stream as fp:
        text = fp.read().decode('utf-8')
        data = json.loads(text)

    idx = Index(data=data)
    return idx

@utils.timer
def save_index(idx, path):
    if not isinstance(path, Path):
        path = Path(path)
    stream = gzip.open(path, "wb") if path.name.endswith(".gz") else open(path, "wb")
    with stream as fp:
        text = json.dumps(idx.data, indent=4)
        fp.write(text.encode('utf-8'))

    # print file size in megabyites
    size = path.stat().st_size / 1024 / 1024
    utils.info(f"Index: {path} ({size:.2f} MB)")


def build_graph(idx):
    """
    Build an ontology graph from a JSON data structure.
    """
    # The complete ontology graph
    graph = nx.DiGraph()

    # Remove obsolete terms.
    nodes = filter(lambda x: not x.get("is_obsolete"), idx.obo.values())

    # nodes = islice(nodes, 100)
    nodes = list(nodes)

    # Add individual nodes to the
    for row in nodes:
        oid = row["id"]
        name = row["name"]
        namespace = utils.NAMESPACE_MAP.get(row[idx.NAMESPACE], "?")
        anno_count = row.get(idx.ANNO_COUNT, -1)
        anno_total = row.get(idx.ANNO_TOTAL, -1)
        desc_count = row.get(idx.DESC_COUNT, -1)
        kwargs = {idx.DESC_COUNT: desc_count, idx.ANNO_COUNT: anno_count, idx.ANNO_TOTAL: anno_total}

        graph.add_node(oid, id=oid, name=name, namespace=namespace, **kwargs)

    for row in nodes:
        child = row["id"]
        for parent in row.get("is_a", []):
            if graph.has_node(parent):
                graph.add_edge(parent, child)
            else:
                utils.warn(f"# Missing parent: {parent} for {row}")

    return graph

def finalize_index(idx):
    """
    Modify the index with additional information.
    """
    # Build the initial graph
    gs = IndexGraph(idx=idx)

    # Build the initial graph
    graph = gs.graph

    # Shortcut to the OBO object.
    obo = idx.obo

    # Add the degree to the nodes
    for node_id in graph.nodes():
        obo[node_id][idx.DESC_COUNT] = graph.out_degree(node_id)

    # Update annotations for each node
    topo_nodes = list(nx.topological_sort(graph))

    for node_id in reversed(topo_nodes):
        total = obo[node_id][idx.ANNO_TOTAL]
        desc_count = obo[node_id][idx.DESC_COUNT]
        for pre in graph.predecessors(node_id):
            obo[pre][idx.ANNO_TOTAL] += total
            obo[pre][idx.DESC_COUNT] += desc_count

    return idx


def build_index():
    from genescape import resources

    res = resources.init()
    obo_fname = res.OBO_FILE
    gaf_fname = res.GAF_FILE

    fname = "../../genescape.index.gz"

    if 0:
        idx = Index()
        idx = parse_obo(obo_fname, idx=idx)
        idx = parse_gaf(gaf_fname, idx=idx)
        idx = finalize_index(idx)
        save_index(idx=idx, path=fname)

    idx = load_index(fname)
    print (idx)

    print (idx.name2sym)


if __name__ == '__main__':
    build_index()
