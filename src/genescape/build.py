#
# Parse an OBO and produces a GZIPed JSON file
#
import csv
import gzip
import json
import os
from pathlib import Path

from genescape import resources, utils
from genescape.__about__ import __version__


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

    stream = csv.reader(stream, delimiter="\t")
    return stream


def make_index(obo, gaf, index, with_synonyms=False):

    if not os.path.isfile(obo):
        utils.stop(f"OBO file not found: {obo}")

    if not os.path.isfile(gaf):
        utils.stop(f"GAF file not found: {gaf}")

    utils.info(f"reading: {gaf}")

    stream = parse_gaf(gaf)

    # stream = islice(stream, 10)
    # Set up mapping dictionaries

    sym2go, go2sym = {}, {}

    # Set up a forward and a reverse mapping.
    for row in stream:
        db_id, db_sym, go_id, db_other = row[1], row[2], row[4], row[10]

        # Decide which symbols to use.
        if with_synonyms:
            synons = list(filter(None, db_other.strip().split("|")))
            symbols = [db_id, db_sym, *synons]
        else:
            symbols = [db_sym]

        # Convert all symbols to uppercase
        symbols = map(lambda x: x.upper(), symbols)

        # Add all elements into the mapping
        for sym in symbols:
            sym2go.setdefault(sym, []).append(go_id)
            go2sym.setdefault(go_id, []).append(sym)

    # Remove duplicates
    for key in sym2go:
        sym2go[key] = list(set(sym2go[key]))

    for key in go2sym:
        go2sym[key] = list(set(go2sym[key]))

    utils.info(f"reading: {obo}")
    stream = gzip.open(obo, mode="rt", encoding="utf-8") if obo.name.endswith(".gz") else open(obo)
    terms = parse_obo(stream)
    terms = filter(lambda x: not x.get("is_obsolete"), terms)
    terms = list(terms)

    # The total number of symbols
    sym_count = len(sym2go) or 1

    # Number of genes annotated with this GO term.
    def gene_count(goid):
        return len(go2sym.get(goid, []))

    # Create a dictionary of GO terms
    obo_dict = {}
    for term in terms:
        goid = term["id"]
        gcnt = gene_count(goid)
        term[utils.GO2GENE_COUNT] = gcnt
        term[utils.GO2GENE_PERC] = (gcnt / sym_count) * 100
        obo_dict[term["id"]] = term

    # Database metadata
    meta = dict(
        version=__version__, date=utils.get_date(), gaf=gaf.name, obo=obo.name, index=index.name, synonyms=with_synonyms
    )

    # The complete data
    data = {
        utils.IDX_META_DATA: meta,
        utils.IDX_OBO: obo_dict,
        utils.IDX_GO2SYM: go2sym,
        utils.IDX_SYM2GO: sym2go,
    }

    # Save the index
    stream = gzip.open(index, mode="wt", encoding="UTF-8")

    # Get index statistics
    utils.index_stats(data, verbose=True)

    # Print progress information
    utils.info(f"writing: {index}")

    # Write the index to a file
    json.dump(data, stream, indent=4)

    return data


if __name__ == "__main__":
    cnf = resources.get_config()
    res = resources.init(cnf)
    obo = res.OBO_FILE
    gaf = res.GAF_FILE
    ind = Path("genescape.json.gz")

    @utils.timer
    def test_make_index():
        retval = make_index(obo=obo, gaf=gaf, index=ind, with_synonyms=False)
        return retval

    @utils.timer
    def test_load_json():
        retval = resources.get_json(ind)
        return retval

    vals = test_make_index()
    obj = test_load_json()

    # data = obj[utils.IDX_SYM2GO]
    # print (json.dumps(data, indent=4))
