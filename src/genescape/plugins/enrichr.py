from genescape import utils
from genescape.plugins import default
import re

COL_MAP = {
    "Term": "goid",
    "Overlap": "common_size",
    "Adjusted P-value": "pval",
}

EXTRA = {
    "category": "",
    "domain_size": 0,
    "query_size": 0
}

def parse_term(term):
    # Extract goid and term name from the 'Term' column
    name, goid = None, None

    patt = r'(.*) \((GO:\d+)\)'
    match = re.search(patt, term)
    if match:
        name = match.group(1)
        goid = match.group(2)
    return goid, name


def parse_overlap(overlap):
    # Extract common size and term size from the 'Overlap' column
    common_size, term_size = overlap.split('/')
    common_size = int(common_size)
    term_size = int(term_size)
    return common_size, term_size


def get_csv(fname):

    parsed = default.get_csv(fname, col_map=COL_MAP)

    for old_row in parsed:
        new_row = {}
        for key, val in old_row.items():
            if key == "goid":
                new_row["goid"], new_row["name"] = parse_term(val)
            elif key == "common_size":
                common_size, term_size = parse_overlap(val)
                new_row["common_size"] = common_size
                new_row["term_size"] = term_size
            else:
                new_row[key] = val

        # Add extra columns
        for key, val in EXTRA.items():
            new_row[key] = val

        yield new_row


if __name__ == "__main__":
    # inp = utils.CSV
    inp = "src/genescape/data/enrichr.txt"
    data = get_csv(inp)
    for row in data:
        utils.info(row)
        break

