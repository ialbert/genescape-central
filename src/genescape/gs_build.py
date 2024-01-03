#
# Parse an OBO and produces a GZIPed JSON file
#
import gzip
import json

from genescape.utils import info


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


def make_json(obo_name, json_name):
    info(f"parsing: {obo_name}")
    stream = open(obo_name)
    terms = parse_obo(stream)
    terms = filter(lambda x: not x.get("is_obsolete"), terms)
    terms = list(terms)
    stream = gzip.open(json_name, "wt", encoding="UTF-8")
    info(f"writing: {json_name}")
    json.dump(terms, stream, indent=4)
    return terms


if __name__ == "__main__":
    make_json("go-basic.obo", "go-basic.json.gz")
