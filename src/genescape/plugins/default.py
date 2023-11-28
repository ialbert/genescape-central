import csv

COL_MAP = {}


def get_csv(fname, col_map):
    # Get the separator used in the file
    sep = "," if fname.endswith(".csv") else "\t"

    # Get the stream from the file
    stream = csv.DictReader(open(fname), delimiter=sep)

    # Produce the new remapped rows.
    for old_row in stream:
        new_row = {}
        for old_key, new_key in col_map.items():
            new_row[new_key] = old_row[old_key]
        yield new_row
