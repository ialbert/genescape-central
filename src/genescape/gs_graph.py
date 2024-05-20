from genescape import utils, resources
from genescape import gs_index
import networkx as nx
import pandas as pd
import re, textwrap
import pydot

ATTR_KEY = 'attr'

class NodeAttr:
    """
    Represents additional attributes for a node in the graph.
    """
    def __init__(self):
        self.is_input = False
        self.sources = []
        self.descendants = []
        self.sources_all = []

    @property
    def src_len(self):
        return len(self.sources)

    @property
    def src_all_len(self):
        return len(self.sources_all)

    @property
    def desc_count(self):
        return len(self.descendants)

class Run:

    def __init__(self, idg, targets=[], root=utils.NS_ALL, mincount=1, pattern=''):

        # Collects errors
        self.errors = []

        # The index object
        self.idx = idg.idx

        self.graph = idg.graph

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

        # Remove duplicates
        self.goids = set(self.goids)

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
        self.valid_goids = set(filter(lambda x: len(self.go2inp[x]) >= mincount, self.valid_goids))

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
            sources = self.go2inp.get(node_id, [])
            attr = NodeAttr()
            attr.is_input = node_id in self.valid_goids
            attr.sources = list(sources)
            node[ATTR_KEY] = attr

        # Travers and update the cumulative totals
        def traverse(tree, node_id, store):

            store[node_id] = [node_id]

            for child_id in tree.successors(node_id):
                if child_id not in store:
                    traverse(tree, child_id, store)
                    store[node_id].extend(store[child_id])

            # Add up the totals from the subtree.
            totals = []
            for parent_id in store[node_id]:
                totals += tree.nodes[parent_id][ATTR_KEY].sources

            # Shortcut to the node
            node = tree.nodes[node_id]

            # Store the descendants from the subtree only.
            node[ATTR_KEY].descendants = set(store[node_id])

            # Add the cumulative totals
            node[ATTR_KEY].sources_all = list(set(totals))

        roots = filter(lambda x: tree.in_degree(x) == 0, tree.nodes())
        for root in roots:
            store = dict()
            traverse(tree, root, store=store)

        # Need a sorted tree for stability.
        self.tree = nx.DiGraph()
        self.tree.add_nodes_from(sorted(tree.nodes(data=True)))
        self.tree.add_edges_from(tree.edges(data=True))

    def as_pydot(self):

        # Create the pydot graph.
        pg = pydot.Dot("genescape", graph_type="digraph")

        # Create a custom node for each node in the tree.
        for goid in self.tree.nodes():
            node = self.tree.nodes[goid]
            attr = node[ATTR_KEY]

            name = node["name"]

            ns = node[self.idx.NAMESPACE]

            # Get the fillcolor.
            fillcolor = utils.NAMESPACE_COLORS.get(ns, utils.BG_COLOR)

            node_id = fix_text(goid)
            text = textwrap.fill(name, width=20)

            ann_count = human_readable(node[self.idx.ANNO_COUNT])
            ann_total = human_readable(node[self.idx.ANNO_TOTAL])
            desc_count = human_readable(attr.desc_count)

            # The lenght of the input targets.
            input_size = len(self.valid_targets)

            label = f"{goid}\n{text} [{ann_count}]"

            # Change the label for input nodes.
            if attr.is_input:
                # Check if the original node is a leaf.
                is_leaf = (self.graph.out_degree(goid) == 0)
                fillcolor = utils.LEAF_COLOR if is_leaf else utils.INPUT_COLOR
                label = f"{label}\n({attr.src_all_len}/{input_size})"

            label = fix_text(label)
            pn = pydot.Node(node_id, label=label, fillcolor=fillcolor, shape="box", style="filled")
            pg.add_node(pn)

        # Fill in the edges.
        for edge in self.tree.edges():
            edge1 = fix_text(edge[0])
            edge2 = fix_text(edge[1])
            pe = pydot.Edge(edge1, edge2)
            pg.add_edge(pe)

        return pg

    def as_df(self):

        # Find the input nodes
        nodes = filter(lambda x: self.tree.nodes[x][ATTR_KEY].is_input, self.tree.nodes())

        inp_size = len(self.valid_targets)

        rows = []
        for node_id in nodes:
            node = self.tree.nodes[node_id]
            attr = node[ATTR_KEY]
            func_name = node["name"]
            source = "|".join(sorted(attr.sources))
            count = attr.src_len
            ann_count = node[self.idx.ANNO_COUNT]
            ann_total = node[self.idx.ANNO_TOTAL]
            desc_count = node[self.idx.DESC_COUNT]

            data = dict(coverage=count, function=func_name,
                        node_id=node_id,
                        source=source,
                        size=inp_size,
                        ann_count=ann_count,
                        ann_total=ann_total,
                        desc_count=desc_count
                        )
            rows.append(data)

        df = pd.DataFrame(rows)

        # Sort the results.
        if not df.empty:
            df = df.sort_values(by='coverage', ascending=False)

        return df

WIDTH = 16.9
HEIGHT = 6.0

def dpi(size, width):
    value = size / width
    return value

def save_graph(pg, fname, imgsize=2048, width=WIDTH):
    """
    Saves the pydot graph to a file
    """
    utils.info(f"file: {fname}")

    pg.set_graph_defaults()

    if fname.endswith(".dot"):
        pg.write_raw(f"{fname}")
    elif fname.endswith(".pdf"):
        pg.write_pdf(fname)
    elif fname.endswith(".png"):
        pg.set_graph_defaults(size=f"{WIDTH},{HEIGHT}", dpi=dpi(imgsize, width=width))
        pg.write_png(fname)
    else:
        utils.warn(f"Unknown output format: {fname}")

# Double quote text for dot
def fix_text(text):
    return f'"{text}"'

# Convert a number to a human readable format.
def human_readable(value, digits=0):
    try:
        newval = int(round(float(value) / 1000, digits))
    except ValueError:
        newval = 0
    newval = f"{newval:d}K" if newval > 1 else value
    return newval

@utils.memoize
def load_index_graph(fname):
    """
    Loads and index and initializes the graph.
    """
    # Load the index.
    idx = gs_index.load_index(fname)

    # Produce the index graph
    idx = gs_index.IndexGraph(idx)

    return idx

def subgraph(idx_fname, targets, root=utils.NS_ALL, mincount=1, pattern=''):
    idg = load_index_graph(idx_fname)
    utils.info(str(idg.idx))
    res = Run(idg=idg, targets=targets, root=root, mincount=mincount, pattern=pattern)
    return res


def demo():
    # Initialize the graph datastructure.
    from genescape import resources
    res = resources.init()
    idx_fname = res.INDEX_FILE

    idg = load_index_graph(idx_fname)

    targets = "ABTB3 BCAS4 C3P1 GRTP1".split()

    res = Run(idg=idg, targets=targets)

    #pg = res.as_pydot()

    df = res.as_df()

    print(df)




if __name__ == "__main__":
    demo()
