#
# Parse an OBO and produces a GZIPed JSON file
#
import gzip, os
import json
import csv
from itertools import *

from genescape import utils

def parse_line(text, sep):
    text = text.strip()
    elem = text.split(sep)[1].strip().strip('"')
    return elem


# Parse a stream to an OBO file and for
def parse_obo(stream):
    term = {}
    for line in stream:
        if line.startswith("[Typedef]"):
            break
        elif line.startswith("[Term]") and term:
            # Set the default value for is_obsolete
            term["is_obsolete"] = term.get("is_obsolete", False)
            yield term
            term = {}
        elif line.startswith("id:"):
            term["id"] = parse_line(line, sep="id:")
        elif line.startswith("name:"):
            term["name"] = parse_line(line, sep="name:")
        elif line.startswith("namespace:"):
            term["namespace"] = parse_line(line, sep="namespace:")
        elif line.startswith("is_a:"):
            elem = parse_line(line, sep="is_a:")
            elem = elem.split(" ! ")[0].strip()
            term.setdefault("is_a", []).append(elem)
        elif line.startswith("is_obsolete:"):
            term["is_obsolete"] = True

    yield term

def parse_gaf(fname):
    stream = gzip.open(fname, mode="rt", encoding="UTF-8")
    stream = filter(lambda x: not x.startswith("!"), stream)
    stream = map(lambda x: x.strip(), stream)
    #stream = map(lambda x: x.split("\t"), stream)
    stream = csv.reader(stream, delimiter="\t")
    return stream


def make_index(obo, gaf, index):

    if not os.path.isfile(obo):
        utils.stop(f"OBO file not found: {obo}")

    if not os.path.isfile(gaf):
        utils.stop(f"GAF file not found: {gaf}")

    utils.info(f"parsing: {gaf}")

    stream = parse_gaf(gaf)

    #stream = islice(stream, 10)
    # Set up mapping dictionaries
    gene2go, prot2go, go2gene, go2prot = {}, {}, {}, {}
    for row in stream:
        gene2go.setdefault(row[2], []).append(row[4])
        prot2go.setdefault(row[1], []).append(row[4])
        go2gene.setdefault(row[4], []).append(row[2])
        go2prot.setdefault(row[4], []).append(row[1])

    utils.info(f"parsing: {obo}")
    stream = open(obo)
    terms = parse_obo(stream)
    terms = filter(lambda x: not x.get("is_obsolete"), terms)
    terms = list(terms)
    obo = {}
    for term in terms:
        obo[term["id"]] = term

    # The complete data
    data = {
        utils.IDX_OBO: obo,
        utils.IDX_gene2go: gene2go,
        utils.IDX_prot2go: prot2go,
        utils.IDX_go2gene: go2gene,
        utils.IDX_go2prot: go2prot,
    }

    # Save the index
    stream = gzip.open(index,  mode="wt", encoding="UTF-8")
    utils.info(f"writing: {index}")
    json.dump(data, stream, indent=4)

    return data


if __name__ == "__main__":
    make_index(obo=utils.OBO_FILE, gaf=utils.GAF_FILE, index=utils.INDEX)
