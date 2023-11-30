import csv
import gzip

# Should be a list of pairs
COL_MAP = []


# Opens a file and returns a stream.
def open_file(fname, sep=None):
    if fname.endswith(".gz"):
        stream = gzip.open(fname, mode="rt", encoding="UTF-8")
    else:
        stream = open(fname, encoding="utf-8-sig")

    if sep is None:
        sep = "," if fname.endswith(".csv") else "\t"
    stream = csv.DictReader(stream, delimiter=sep)
    return stream


# Checks format based on a column map.
def check_format(fname, col_map):
    stream = open_file(fname)
    header = set(stream.fieldnames)
    target = set(col_map.keys())
    miss = target - header
    valid = len(miss) == 0
    return valid


def relabel(graph, node, g2d):
    label = graph.nodes[node]["label"]
    return label


def rename_columns(fname, col_map):
    # Open the file.
    stream = open_file(fname)

    # Produce the new remapped rows.
    for old_row in stream:
        new_row = {}
        for old_key, new_key in col_map.items():
            new_row[new_key] = old_row[old_key]
        yield new_row
