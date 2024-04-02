import subprocess
import  difflib, pytest

def read_file(fname):
    """Check if the contents of two files are identical."""
    with open(fname, 'r') as fp:
        return fp.read()

def run_command(text):

        # The command split
        commands = text.split()

        # The last element is the expected output file
        exec = commands[:-1]

        # Execute the command
        subprocess.run(exec, check=True)

        # Define the path to the expected and generated output files
        fname_exp = commands[-1]
        fname_gen = commands[-2]

        # Read the contents of the expected and generated output files
        exp = read_file(fname_exp)
        gen = read_file(fname_gen)

        if exp != gen:
            diffs = difflib.unified_diff(exp.splitlines(), gen.splitlines(), fromfile=fname_exp, tofile=fname_gen)
            print("\n".join(diffs))
            print(f"# Generated file: {fname_gen}")
            print(f"# Expected file: {fname_exp}")
            print(f"# Command: {' '.join(exec)}")
            raise AssertionError("# Content mismatch")

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
    cmd = "genescape annotate test/files/hs_genes1.txt --csv -o test/out/hs_genes1.annot.json test/files/hs_genes1.annot.csv"
    run_command(cmd)

def test_annotate_hs_genes2_csv():
    cmd = "genescape annotate test/files/hs_genes2.txt --csv -o test/out/hs_genes2.annot.json test/files/hs_genes2.annot.csv"
    run_command(cmd)

if __name__ == "__main__":
    pass
