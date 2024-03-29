rm -rf build dist
pyinstaller src/genescape/server.py --add-data=src/genescape/data:genescape/data -y --onefile -i docs\images\logo.ico -n GeneScape
