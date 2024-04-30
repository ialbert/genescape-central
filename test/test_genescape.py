import difflib, sys
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


@pytest.mark.parametrize("inp_name, out_name, cmd", [
    ("test_genes.txt", "test_genes.csv", "annotate"),
    ("hs_genes1.txt", "hs_genes1.csv", "annotate"),
])
def test_annotate(inp_name, out_name, cmd):

    inp_path = Path("test/files") / inp_name
    exp_path = Path("test/files") / out_name
    gen_path = Path("test/out") / out_name

    full = f"{cmd} -o {gen_path} {inp_path}"

    runner = CliRunner()

    res = runner.invoke(main.run, full.split())

    # Check that the command completed correctly
    assert res.exit_code == 0

    exp_value = read_file(exp_path)
    gen_value = read_file(gen_path)

    if exp_value != gen_value:
        show_diff(exp_value, gen_value, full)
        raise AssertionError(f"content mismatch: {out_name}")

if __name__ == "__main__":
    pytest.main([__file__, '--verbose'])
