"""
Builds a distribution package for the Genescape application.
"""

import subprocess
import sys
from pathlib import Path
import os
import shutil
from zipfile import ZipFile
from genescape import __version__, utils

def build(name="GeneScape", version=__version__):
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

    # Find the dist directory where the executable is placed
    exe_path = dist_path / name

    # Create a directory for the distribution
    os.makedirs(dist_path.parent, exist_ok=True)

    # The executable's name might differ by platform
    exe_name = f"{name}.exe" if sys.platform == "win32" else name

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
    build()

