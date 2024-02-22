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


def run(fname=utils.GAF_GENE_LIST, gaf=utils.GAF_REF_DATA, json_obo=utils.OBO_JSON, top=10, verbose=False, match='', minc=1):
    stream1 = gzip.open(gaf, mode="rt", encoding="UTF-8")
    stream1 = filter(lambda x: not x.startswith("!"), stream1)
    stream1 = map(lambda x: x.strip(), stream1)
    stream1 = map(lambda x: x.split("\t"), stream1)

    ann = {}
    for row in stream1:
        pname, gname, goid = row[1], row[2], row[4]
        ann.setdefault(pname, []).append(goid)
        ann.setdefault(gname, []).append(goid)

    stream2 = utils.get_stream(fname)
    stream2 = map(lambda x: x.upper(), stream2)
    stream2 = list(stream2)
    miss, coll = [], []

    for elem in stream2:
        if elem not in ann:
            miss.append(elem)
        else:
            coll.extend(set(ann[elem]))

    if miss:
        utils.warn(f"missing {len(miss)} ids")
    if verbose:
        utils.warn(f"missing ids: {miss} ")

    stream = gzip.open(json_obo, mode="rt", encoding="UTF-8")
    terms = json.load(stream)

    # Map the GO categories to their names
    go2func = dict(
            (x.get("id", "id?"), x.get("name", "name?")) for x in terms
    )


    # Build the counter.
    count = Counter(coll)

    # Keep the sort stable.
    elems = count.most_common()

    # Fill in the function names.
    elems = map(lambda x: (x[0], x[1], go2func.get(x[0], "?")), elems)

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

    # Opent the output stream.
    write = csv.writer(sys.stdout)

    # Write the header.
    write.writerow([GOID, "count", "size", LABEL, "function"])

    # The size of the original collection.
    size = len(stream2)

    # Print the results.
    for goid, cnt, func in elems:
        if match and re.search(match, func) is None:
            continue
        label = f"{cnt}/{size}"
        write.writerow([goid, cnt, size, f"{label}", func])

    if len(elems) != n_found:
        utils.info(f"there are {n_found-len(elems)} additional terms not shown")


if __name__ == "__main__":

    run()

