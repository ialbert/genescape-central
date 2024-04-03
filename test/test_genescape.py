import difflib
import subprocess

import pytest


def read_file(fname):
    """
    Check if the contents of two files are identical. Use on text files only.
    """
    with open(fname,  mode="r") as fp:
        data = fp.read()
    return data


def run_command(text):

    # The command split
    elems = text.split()

    # The last element is the expected output file
    cmd = elems[:-1]

    # Execute the command
    subprocess.run(cmd, check=True)

    # Define the path to the expected and generated output files
    fname_exp = elems[-1]
    fname_gen = elems[-2]

    # Read the contents of the expected and generated output files
    exp = read_file(fname_exp)
    gen = read_file(fname_gen)

    if exp != gen:
        diffs = difflib.unified_diff(exp.splitlines(), gen.splitlines(), fromfile=fname_exp, tofile=fname_gen)
        diffs = list(diffs)[:10]
        print("\n".join(diffs))
        print(f"# Generated file: {fname_gen}")
        print(f"# Expected file: {fname_exp}")
        print(f"# Command: {' '.join(cmd)}")
        msg = "# Content mismatch"
        raise AssertionError(msg)


def test_tree_hs_genes1():
    cmd = "genescape tree test/files/hs_genes1.txt -o test/out/hs_genes1.tree.dot test/files/hs_genes1.tree.dot"
    run_command(cmd)


def test_tree_hs_genes2():
    cmd = "genescape tree test/files/hs_genes2.txt -o test/out/hs_genes2.tree.dot test/files/hs_genes2.tree.dot"
    run_command(cmd)


def test_annotate_hs_genes1_json():
    cmd = "genescape annotate test/files/hs_genes1.txt -o test/out/hs_genes1.annot.json test/files/hs_genes1.annot.json"
    run_command(cmd)


def test_annotate_hs_genes2_json():
    cmd = "genescape annotate test/files/hs_genes2.txt -o test/out/hs_genes2.annot.json test/files/hs_genes2.annot.json"
    run_command(cmd)


def test_annotate_hs_genes1_csv():
    cmd = "genescape annotate test/files/hs_genes1.txt --csv -o test/out/hs_genes1.annot.csv test/files/hs_genes1.annot.csv"
    run_command(cmd)


def test_annotate_hs_genes2_csv():
    cmd = "genescape annotate test/files/hs_genes2.txt --csv -o test/out/hs_genes2.annot.csv test/files/hs_genes2.annot.csv"
    run_command(cmd)


if __name__ == "__main__":
    pass
