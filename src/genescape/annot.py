"""
Annotates a list of genes with functions based on the GO graph
"""
import csv
import gzip
import sys,json,re
from collections import Counter
from itertools import *

from genescape import utils

def run(names, index=utils.INDEX, top=10, verbose=False, match='', minc=1, output=sys.stdout):

    # Open the index stream
    idx_stream = gzip.open(index, mode="rt", encoding="UTF-8")

    # Load the full index.
    data = json.load(idx_stream)

    # Remap the names to upper case.
    names = map(lambda x: x.upper(), names)
    names = list(names)

    # The valid ids are the unqiue gene and protein ids.
    valid_ids = set(list(data[utils.IDX_gene2go].keys()) + list(data[utils.IDX_prot2go].keys()))

    # Fetch GO functions for a given gene or protein id.
    def get_func(name):
        ids = set(data[utils.IDX_gene2go].get(name, []) + data[utils.IDX_prot2go].get(name, []))
        return ids

    # The missing and collected gene names.
    miss, coll, func2name = [], [], {}

    # Collect the missing elements.
    for name in names:
        if name not in valid_ids:
            miss.append(name)
        else:
            funcs = get_func(name)
            # Collect genes that match a function.
            for func in funcs:
                func2name.setdefault(func, []).append(name)
            coll.extend(funcs)

    # The missing ids.
    if miss:
        utils.warn(f"missing {len(miss)} ids: {','.join(miss[:10])} ... ")

    # Print all missing elements if verbose.
    if verbose:
        utils.warn(f"all missing ids: {miss} ")

    # Get the elements for a go id.
    def go2func(goid):
        return data[utils.IDX_OBO][goid]["name"]

    # Build the counter.
    counter = Counter(coll)

    # Keep the sort stable.
    counts = counter.most_common()

    # Fill in the function names.
    counts = map(lambda x: (x[0], x[1], go2func(x[0])), counts)

    # Apply the regex filter
    counts = filter(lambda x: re.search(match, x[2], re.IGNORECASE), counts) if match else counts

    # Apply the minimum count filter
    counts = filter(lambda x: x[1] >= minc, counts)

    # Sort the remaining elements by count.
    counts = sorted(counts, key=lambda x: (x[1], x[0]), reverse=True)

    # The number of hits found.
    n_found = len(list(counts))

    # Take the top N elements.
    counts = counts[:top] if top > 0 else counts

    # The size of the original collection.
    n_size = len(names)

    # Create the data object
    res = []
    data_fields = [utils.GOID, "count", "size", utils.LABEL, "function", "genes"]
    for goid, cnt, func in counts:
        label = f"({cnt}/{n_size})"
        funcs = func2name.get(goid, [])
        name = dict(zip(data_fields, [goid, cnt, n_size, label, func, funcs]))
        res.append(name)

    # The CSV file has fewer fields
    if output is not None:
        csv_field = data_fields[:-1]
        write = csv.DictWriter(output, fieldnames=csv_field, extrasaction='ignore')
        write.writeheader()
        write.writerows(res)

    # Final notification if needed.
    if len(counts) != n_found:
        utils.info(f"showing top {len(counts)} out of {n_found}")

    return res


if __name__ == "__main__":
    # Read the genelist
    names = utils.get_lines(fname=utils.GENE_LIST)
    run(names=names)

