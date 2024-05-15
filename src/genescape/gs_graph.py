from genescape import utils, resources
from genescape import gs_index

@utils.memoize
def load_graph(fname):
    """
    Loads and index and initializes the graph.
    """
    # Load the index.
    idx = gs_index.load_index(fname)

    # Initialize the graph datastructure.
    idx.init_graph()

    print(idx)

    return idx



def main():
    fname = "../../genescape.index.gz"

    load_graph(fname=fname)


if __name__ == "__main__":
    main()
