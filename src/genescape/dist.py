"""
Builds a distribution package for the Genescape application.
"""

import subprocess
import sys
from pathlib import Path
import os
import click
import shutil
from zipfile import ZipFile
from genescape import __version__, utils

@click.command()
@click.option("--name", default="GeneScape", help="The name of the executable")
@click.option("--tag", is_flag=True, help="Run a git tag command")
@click.option("--build", is_flag=True, help="Run a git tag command")
@click.help_option("-h", "--help")
def run(name="GeneScape", tag=False, build=False):
    if tag:
        tag_cmd()

    if build:
        build_cmd(name=name)

def tag_cmd():
    # The git command
    cmd = ["git", "tag", f"v{__version__}"]
    subprocess.run(cmd, check=True)
    utils.info(f"{' '.join(cmd)}")

    # Push the tag to the remote
    push = ["git", "push", "--tags" ]
    subprocess.run(push, check=True)
    utils.info(f"Version: v{__version__}")


def build_cmd(name="GeneScape", version=__version__):
    # The PyInstaller command
    cmd = [
        "pyinstaller",
        "src/genescape/server.py",
        "--add-data=src/genescape/data:genescape/data",
        "-i", "docs/images/logo.ico",
        "-n", name,
        "-y", "--onefile"
    ]

    # Run PyInstaller
    subprocess.run(cmd, check=True)

    # The path to the distribution directory
    dist_path = Path(os.getcwd(), "dist")

    # The executable's name might differ by platform
    exe_name = f"{name}.exe" if sys.platform == "win32" else name

    # Find the dist directory where the executable is placed
    exe_path = dist_path / exe_name

    # Create a directory for the distribution
    os.makedirs(dist_path.parent, exist_ok=True)

    # Platform name for the zip file
    if sys.platform == "win32":
        plat_name = "Windows"
    elif sys.platform == "darwin":
        plat_name = "MacOS"
    else:
        plat_name = "Linux"

    # The path to the zip file.
    zip_name = f"{name}-{version}-{plat_name}.zip"
    zip_path = dist_path / zip_name

    with ZipFile(zip_path, 'w') as zipf:
        zipf.write(exe_path, arcname=exe_name)

    utils.info(f"File: {zip_path}")

    # Also create a latest version
    latest_path = dist_path /f"{name}-latest.zip"
    shutil.copy(zip_path, latest_path)
    utils.info(f"File: {latest_path}")

if __name__ == "__main__":
    run()

