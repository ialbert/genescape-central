import re

from genescape import utils
from genescape.plugins import default

COL_MAP = {
    "Term": "goid",
    "Overlap": "common_size",
    "Adjusted P-value": "pval",
}

EMPTY_COLS = {"category": "", "domain_size": 0, "query_size": 0}


def relabel(graph, node, g2d):
    return default.relabel(graph, node, g2d)


def parse_term(term):
    # Extract goid and term name from the 'Term' column
    name = goid = "?"

    patt = r"(.*) \((GO:\d+)\)"
    match = re.search(patt, term)
    if match:
        name = match.group(1)
        goid = match.group(2)
    return goid, name


def parse_overlap(overlap):
    # Extract common size and term size from the 'Overlap' column
    common_size, term_size = overlap.split("/")
    common_size = int(common_size)
    term_size = int(term_size)
    return common_size, term_size


def check_format(fname):
    return default.check_format(fname, col_map=COL_MAP)


def get_stream(fname):
    stream = default.rename_columns(fname, col_map=COL_MAP)

    def remapper(row):
        row["goid"], row["name"] = parse_term(row["goid"])
        row["common_size"], row["term_size"] = parse_overlap(row["common_size"])

        row.update(EMPTY_COLS)

        return row

    stream = map(remapper, stream)

    return stream


if __name__ == "__main__":
    # inp = utils.CSV
    inp = "../data/enrichr-output.txt"
    stream = get_stream(inp)
    for row in stream:
        # print(row)
        break
