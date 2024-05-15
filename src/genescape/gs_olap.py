from genescape import nexus, resources
from pathlib import Path


def run(names1, names2, root=None, match=None, count=0, oname="output.pdf"):

    res = resources.init()
    idx_fname = res.INDEX_FILE

    idx, dot1, tree1, ann1, status1 = nexus.run(genes=names1, idx_fname=idx_fname,
                                                root=root, pattern=match, mincount=count)

    idx, dot2, tree2, ann2, status2 = nexus.run(genes=names2, idx_fname=idx_fname,
                                                root=root, pattern=match, mincount=count)

    # The common nodes between the two trees
    nodes1 = set(tree1.nodes())
    nodes2 = set(tree2.nodes())
    common = nodes1 & nodes2

    jaccard = len(common) / len(nodes1 | nodes2)
    oc = len(common) / min(len(nodes1), len(nodes2))

    tree = tree1.subgraph(common)

    dot = nexus.make_pydot(tree, status1)

    print(f"Jaccard: {jaccard:.2f}")
    print(f"Overlap Coefficient: {oc:.2f}")
    print(tree)


    #print(dot)


if __name__ == '__main__':
    res = resources.init()

    names1 = "BCAS4 Cyp1a1".split()
    names2 = "GRTP1 Sphk2".split()

    run(names1, names2)
