import difflib, sys, subprocess
import os

import pytest, click
from pathlib import Path
from genescape import main
from click.testing import CliRunner

# Testing directory
TEST_DIR = Path(__file__).parent

def read_file(fname):
    """
    Check if the contents of two files are identical. Use on text files only.
    """
    with open(fname,  mode="r") as fp:
        data = fp.read()
    return data

def show_diff(exp, gen, cmd):
    diffs = difflib.unified_diff(exp.splitlines(), gen.splitlines())
    diffs = list(diffs)[:10]
    print("\n".join(diffs))
    print(f"# Command: genescape {cmd}")

    # Fix up the command to show the fix
    fix = cmd.replace("/out/", "/files/")
    print(f"# Replace: genescape {fix}")

PARAMS = [
    ("test_genes.txt", "test_genes.csv", "annotate"),
    ("hs_genes1.txt", "hs_genes1.csv", "annotate"),
    ("hs_genes2.txt", "hs_genes2.csv", "annotate"),
    ("hs_genes1.txt", "hs_genes1.dot", "tree"),
    ("hs_genes2.txt", "hs_genes2.dot", "tree"),
]

@pytest.mark.parametrize("inp_name, out_name, cmd", PARAMS)
def test_genescape(inp_name, out_name, cmd):

    inp_path = Path("test/files") / inp_name
    exp_path = Path("test/files") / out_name
    gen_path = Path("test/out") / out_name

    full = f"{cmd} -o {gen_path} {inp_path}"

    runner = CliRunner()

    res = runner.invoke(main.run, full.split())

    # Check that the command completed correctly
    if res.exit_code != 0:
        print (f"Command: genescape {full}")
        assert res.exit_code == 0

    exp_value = read_file(exp_path)
    gen_value = read_file(gen_path)

    if exp_value != gen_value:
        show_diff(exp_value, gen_value, full)
        raise AssertionError(f"content mismatch: {out_name}")


@pytest.mark.parametrize("cmd", ["build -s", "annotate -t", "tree -t -o test/out/genescape.pdf"])
def test_run(cmd):

    full = f"{cmd}"

    runner = CliRunner()

    res = runner.invoke(main.run, full.split())

    # Check that the command completed correctly
    assert res.exit_code == 0

if __name__ == "__main__":
    pytest.main([__file__, '--verbose'])
