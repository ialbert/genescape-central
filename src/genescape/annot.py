"""
Annotates a list of genes with functions based on the GO graph
"""
import csv, io
import gzip
import sys,json,re
from collections import Counter
from itertools import *

from genescape import utils

def run(data, index=utils.INDEX, pattern='', minc=1, csvout=False, verbose=False,):

    # Collect the run status into this list.
    status = {
        utils.CODE_FIELD:0,
        utils.INVALID_FIELD:[]
    }

    # Open the index stream
    idx_stream = gzip.open(index, mode="rt", encoding="UTF-8")

    # Load the full index.
    idx = json.load(idx_stream)

    # Extract the gene names from the data
    names = map(lambda x: x[utils.GID], data[utils.DATA_FIELD])

    # Remap the names to upper case.
    names = map(lambda x: x.upper(), names)
    names = list(names)

    # The known and valid inputs
    gene2go = idx[utils.IDX_gene2go]
    prot2go = idx[utils.IDX_prot2go]
    go = idx[utils.IDX_OBO]

    # The valid ids are the unqiue gene and protein ids.
    valid_ids = set(gene2go) | set(prot2go) | set(go)

    # Fetch GO functions for a given gene or protein id.
    def get_func(name):
        if name in go:
            ids = [ name ]
        else:
            ids = set(gene2go.get(name, []) + prot2go.get(name, []))
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
        status[utils.CODE_FIELD] = 1
        status[utils.INVALID_FIELD] = (list(miss))
        utils.warn(f"{status}")

    # Get the elements for a go id.
    def go2func(goid):
        return idx[utils.IDX_OBO][goid]["name"]

    # Build the counter.
    counter = Counter(coll)

    # Keep the sort stable.
    counts = counter.most_common()

    # Fill in the function names.
    counts = map(lambda x: (x[0], x[1], go2func(x[0])), counts)

    # Apply the regex filter
    counts = filter(lambda x: re.search(pattern, x[2], re.IGNORECASE), counts) if pattern else counts

    # Apply the minimum count filter
    counts = filter(lambda x: x[1] >= minc, counts)

    # Sort the remaining elements by count.
    counts = sorted(counts, key=lambda x: (x[1], x[0]), reverse=True)

    # The number of hits found.
    n_size = len(list(names)) - len(miss)

    # Create the data object
    res = []
    data_fields = [utils.GID, "count", "size", utils.LABEL, "function", utils.SOURCE]
    for goid, cnt, func in counts:
        label = f"({cnt}/{n_size})"
        funcs = func2name.get(goid, [])
        name = dict(zip(data_fields, [goid, cnt, n_size, label, func, funcs]))
        res.append(name)

    json_data = {utils.DATA_FIELD:res, utils.STATUS_FIELD:status}

    # The CSV file has fewer fields
    if csvout:
        csv_field = data_fields
        stream = io.StringIO()
        write = csv.DictWriter(stream, fieldnames=csv_field, extrasaction='ignore')
        write.writeheader()
        for row in res:
            row = dict(row)
            row[utils.SOURCE] = ";".join(row[utils.SOURCE])
            write.writerow(row)
        out = stream.getvalue()

    else:
        out = json.dumps(json_data, indent=2)

    return out


if __name__ == "__main__":

    # Read the genelist
    iter = utils.get_stream(inp=utils.GENE_LIST)

    data = utils.parse_terms(iter=iter)

    out = run(data=data, csvout=True)

    print (out)

