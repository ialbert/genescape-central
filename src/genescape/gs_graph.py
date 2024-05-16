from genescape import utils, resources
from genescape import gs_index
import networkx as nx
import re

class NodeAttr:
    """
    Additional node attributes.
    """
    def __init__(self):
        self.inp_flag = False
        self.inp_sym = []
        self.inp_len = 0
        self.inp_sym_tot = []
        self.inp_len_tot = 0
        self.desc_list = []

class Result:

    def __init__(self, idx, targets=[], root=utils.NS_ALL, mincount=1, pattern=''):

        # Collects errors
        self.errors = []

        # The index object
        self.idx = idx
        self.graph = idx.graph

        # The input targets
        self.targets = set(map(lambda x: x.upper(), targets))

        # The missing targets
        self.missing_targets = list(filter(lambda x: x not in self.idx.sym2go and x not in self.idx.obo, self.targets))

        # Store the missing targets
        if self.missing_targets:
            msg = f"Missing symbols: {','.join(self.missing_targets)}"
            self.errors.append(msg)

        # The valid targets.
        self.valid_targets = list(filter(lambda x: x in self.idx.sym2go or x in self.idx.obo, self.targets))

        # Maps GO ids to input target symbols.
        self.go2inp = dict()

        # GO terms for the input targets.
        self.goids = []

        # Populate the mappings.
        for target in self.valid_targets:
            values = self.idx.sym2go.get(target, []) or [target]
            for goid in values:
                self.go2inp.setdefault(goid, []).append(target)
                self.goids.append(goid)

        # Normally the list should be empty. Sanity check.
        self.missing_goids = list(filter(lambda x: x not in self.idx.obo, self.goids))

        if self.missing_goids:
            msg = f"Missing GO terms: {','.join(self.missing_goids)}"
            self.errors.append(msg)

        # Nodes to build the subgraph from.
        self.valid_goids = filter(lambda x: x in self.graph.nodes, self.goids)

        # Apply the root filter.
        if root != utils.NS_ALL:
            self.valid_goids = filter(lambda x: self.graph.nodes[x][utils.NAMESPACE] == root, self.valid_goids)

        # Apply the pattern filter.
        if pattern:
            try:
                patt = re.compile(pattern, re.IGNORECASE)
                self.valid_goids = filter(lambda x: re.search(patt, self.idx.graph.nodes[x]["name"]), self.valid_goids)
            except re.error:
                msg = f"Invalid pattern: {pattern}"
                self.errors.append(msg)

        # Apply mincount filter.
        self.valid_goids = filter(lambda x: len(self.go2inp[x]) >= mincount, self.valid_goids)

        # Check for input.
        if not self.valid_goids:
            msg = "No GO terms pass all conditions."
            self.errors.append(msg)

        # Find the ancestors for each node.
        anc = set()
        for node in self.valid_goids:
            anc = anc.union(nx.ancestors(self.graph, node))

        # Add the original nodes basck well.
        anc = anc.union(self.valid_goids)

        # Subset the graph to the ancestors only.
        tree = self.graph.subgraph(anc)

        # Initialize the subtree
        for node_id in tree.nodes():
            node = tree.nodes[node_id]
            sources = go2inp.get(node_id, [])
            node[INP_FLAG] = node_id in valid2tgt
            node[INP_SYM] = list(sources)
            node[INP_LEN] = len(sources)


@utils.memoize
def load_graph(fname):
    """
    Loads and index and initializes the graph.
    """
    # Load the index.
    idx = gs_index.load_index(fname)

    # initialize the graph
    idx.init_graph()

    return idx

def main(idx):
    # Initialize the graph datastructure.
    gs = Result(idx=idx)

    return gs


def get_subgraph(idx, targets, root=utils.NS_ALL, mincount=1, pattern=''):
    gs = GS_Graph(idx=idx, targets=targets)

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


def run():
    fname = "../../genescape.index.gz"

    idx = load_graph(fname=fname)
    main(idx=idx)


if __name__ == "__main__":
    run()
