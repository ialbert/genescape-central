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
    ("test_genes_hs_1.txt", "out_test_genes_hs_1.csv", "annotate"),
    ("test_genes_hs_1.txt", "out_test_genes_hs_1_signal.csv", "annotate --mincov 1 --match signal"),
    ("test_genes_hs_2.txt", "out_test_genes_hs_2.csv", "annotate"),
    ("test_goids.txt", "out_test_goids.csv", "annotate --mincov 1"),

    ("test_genes_hs_1.txt", "out_test_genes_hs_1.dot", "tree"),
    ("test_genes_hs_1.txt", "out_test_genes_hs_1_signal.dot", "tree --mincov 1 --match signal"),
    ("test_genes_hs_2.txt", "out_test_genes_hs_2.dot", "tree"),
    ("test_goids.txt", "out_test_goids.dot", "tree --mincov 1"),

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


@pytest.mark.parametrize("cmd", ["build -s --idx src/genescape/data/human.index.gz", "annotate -t -o test/out/genescape.csv", "tree -t -o test/out/genescape.pdf"])
def test_run(cmd):

    full = f"{cmd}"

    runner = CliRunner()

    res = runner.invoke(main.run, full.split())

    # Check that the command completed correctly
    assert res.exit_code == 0

if __name__ == "__main__":
    pytest.main([__file__, '--verbose'])
