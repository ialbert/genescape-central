"""
Annotates a list of genes with functions based on the GO graph
"""
import gzip, csv, sys
from itertools import *
from collections import Counter
from genescape import utils
from pprint import pprint
from genescape.utils import GOIDS, LABELS

def run(fname=utils.GAF_GENE_LIST, gaf=utils.GAF_REF_DATA, top=10):
    gaf = utils.GAF_REF_DATA
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
        utils.warn(f"missing {len(miss)} genes {miss}")

    count = Counter(coll)


    write = csv.writer(sys.stdout)
    write.writerow([GOIDS, LABELS])

    # Find the most common GO terms
    size = len(stream2)

    for goid, cnt in count.most_common(top):
        label = f"{cnt}/{size}"
        write.writerow([goid, label])

if __name__ == "__main__":

    run()

