from genescape import utils
from genescape.plugins import default

COL_MAP = {
    "source": "category",
    "term_id": "goid",
    "term_name": "name",
    "adjusted_p_value": "pval",
    "intersection_size": "common_size",
    "term_size": "term_size",
    "query_size": "query_size",
    "effective_domain_size": "domain_size",
}


def get_csv(fname):
    return default.get_csv(fname, col_map=COL_MAP)


def check_format(stream):
    header = set(stream.fieldnames)
    target = set(COL_MAP.keys())
    diff = target - header
    if diff:
        utils.stop(f"Missing columns: {diff}")


def relabel(graph, node, g2d):
    try:
        label = graph.nodes[node]["label"]

        row = g2d[node]

        val1 = float(row["term_size"]) / float(row["domain_size"])
        val2 = float(row["common_size"]) / float(row["query_size"])

        fold = val2 / val1

        label = f"{label}\n{row['common_size']} / {fold:.1f}x"

    except Exception as exc:
        utils.error(f"labeling error: {exc}")
        label = "?"

    return label


if __name__ == "__main__":
    inp = utils.CSV
    data = get_csv(inp)
    for row in data:
        utils.info(row)
        break
