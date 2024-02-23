"""
Annotates a list of genes with functions based on the GO graph
"""
import csv
import gzip
import sys,json,re
from collections import Counter
from itertools import *
from pprint import pprint

from genescape import utils
from genescape.utils import GOID, LABEL


def run(fname=utils.GENE_LIST, index=utils.INDEX, top=10, verbose=False, match='', minc=1):

    # Open the index stream
    idx_stream = gzip.open(index, mode="rt", encoding="UTF-8")

    # Load the full index.
    data = json.load(idx_stream)

    # Read the genelist
    stream = utils.get_stream(fname)
    stream = map(lambda x: x.upper(), stream)
    stream = list(stream)

    valid_ids = set(list(data[utils.IDX_gene2go].keys()) + list(data[utils.IDX_prot2go].keys()))

    # Fetch functions stored for genes or proteins
    def get(elem):
        return set(data[utils.IDX_gene2go].get(elem, []) + data[utils.IDX_prot2go].get(elem, []))

    miss, coll = [], []

    for elem in stream:

        if elem not in valid_ids:
            miss.append(elem)
        else:
            coll.extend(get(elem))

    if miss:
        utils.warn(f"missing {len(miss)} ids: {','.join(miss[:10])} ... ")
    if verbose:
        utils.warn(f"all missing ids: {miss} ")

    def go2func(goid):
        return data[utils.IDX_OBO][goid]["name"]

    # Build the counter.
    count = Counter(coll)

    # Keep the sort stable.
    elems = count.most_common()

    # Fill in the function names.
    elems = map(lambda x: (x[0], x[1], go2func(x[0])), elems)

    # Apply the regex filter
    elems = filter(lambda x: re.search(match, x[2]), elems) if match else elems

    # Apply the minimum count filter
    elems = filter(lambda x: x[1] >= minc, elems)

    # Sort the remaining elements by count.
    elems = sorted(elems, key=lambda x: (x[1], x[0]), reverse=True)

    # The number of hits found.
    n_found = len(list(elems))

    # Take the top N elements.
    elems = elems[:top] if top > 0 else elems

    # The size of the original collection.
    size = len(stream)

    # Create the data object
    result = []
    fields_long = [utils.GOID, "count", "size", utils.LABEL, "function"]
    for goid, cnt, func in elems:
        if match and re.search(match, func) is None:
            continue
        label = f"{cnt}"
        elem = dict(zip(fields_long, [goid, cnt, size, label, func]))

        result.append(elem)

    # The CSV file has fewer fields
    fields_short = fields_long
    write = csv.DictWriter(sys.stdout, fieldnames=fields_short)
    write.writeheader()
    write.writerows(result)

    # Final notification if needed.
    if len(elems) != n_found:
        utils.info(f"{len(elems)} out of {n_found} shown")


if __name__ == "__main__":

    run()

