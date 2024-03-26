"""
Annotates a list of genes with functions based on the GO graph
"""
import csv, io
import gzip
import sys, json, re
from collections import Counter
from itertools import *
from pathlib import Path
from genescape import utils, resources


def run(data, index, pattern='', mincount=1, root=utils.NS_ALL, csvout=False):
    # Collect the run status into this list.
    status = {
        utils.CODE_FIELD: 0,
        utils.INVALID_FIELD: []
    }

    # Checking the input
    if not index:
        utils.stop(f"Index file is not set index={index}")

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
            ids = [name]
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

    def go2ns(goid):
        return idx[utils.IDX_OBO][goid]["namespace"]

    # Build the counter.
    counter = Counter(coll)

    # Keep the sort stable.
    counts = counter.most_common()

    # Fill in the function names.
    counts = map(lambda x: (x[0], x[1], go2func(x[0])), counts)

    # Apply the regex filter
    counts = filter(lambda x: re.search(pattern, x[2], re.IGNORECASE), counts) if pattern else counts

    # Apply the minimum count filter
    counts = filter(lambda x: x[1] >= mincount, counts)

    # Sort the remaining elements by count.
    counts = sorted(counts, key=lambda x: (x[1], x[0]), reverse=True)

    # The number of hits found.
    n_size = len(list(names)) - len(miss)

    # Create the data object
    res = []
    data_fields = [utils.GID, "root", "count", "function", utils.SOURCE, "count", "size", utils.LABEL]



    for goid, cnt, func in counts:
        label = f"({cnt}/{n_size})"
        funcs = func2name.get(goid, [])
        name_space = go2ns(goid)

        root_code = utils.NAMESPACE_MAP.get(name_space, "?")

        # Filter by root codes
        if root != utils.NS_ALL and root != root_code:
            continue

        name = dict(zip(data_fields, [goid, root_code, cnt,func, funcs, cnt, n_size, label]))

        res.append(name)

    json_data = {utils.DATA_FIELD: res, utils.STATUS_FIELD: status}

    if csvout:
        out = ann2csv(json_data)
    else:
        out = json.dumps(json_data, indent=2)

    return out


def ann2csv(ann):
    text = ''
    data = ann.get(utils.DATA_FIELD, [])
    if data:
        fields = data[0].keys()
        stream = io.StringIO()
        write = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        write.writeheader()
        for row in data:
            row = dict(row)
            row[utils.SOURCE] = ";".join(row.get(utils.SOURCE, []))
            write.writerow(row)
        text = stream.getvalue()

    return text


if __name__ == "__main__":
    # Initialize the resources
    res = resources.init()

    inp = res.TEST_GENES
    index = res.INDEX

    # Read the genelist
    stream = utils.get_stream(inp=inp)

    data = utils.parse_terms(iterable=stream)

    out = run(data=data, index=index, csvout=True)

    print(out)
