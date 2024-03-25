import csv
import re
from itertools import chain

from genescape import utils


def run(fname=None, mcol="term_id", pcol=None, pval=None, match=None, delim=","):
    stream = utils.get_lines(fname)
    header = next(stream)

    # Regex matches on the entire line.
    if match:
        patt = re.compile(match, re.IGNORECASE)
        stream = filter(lambda x: patt.search(x), stream)

    # Concatenate header to stream
    stream = chain([header], stream)

    stream = csv.DictReader(stream, delimiter=delim)

    # Check that mcol in header
    if mcol not in stream.fieldnames:
        utils.stop(f"Column --col={mcol} not found in headers: {stream.fieldnames}")

    # Filter by p-value
    if pcol:
        if pcol not in stream.fieldnames:
            utils.stop(f"Column --pcol={pcol} not found in headers {stream.fieldnames}!")
        stream = filter(lambda x: float(x[pcol]) < pval, stream)

    stream = map(lambda x: x[mcol], stream)

    for row in stream:
        print(row)

    return stream


if __name__ == "__main__":
    run(fname=utils.TEST_GPROFILER)
