GENOMES = [
    ("human", "https://current.geneontology.org/annotations/goa_human.gaf.gz"),
    ("mouse", "https://current.geneontology.org/annotations/mgi.gaf.gz"),
    ("rat", "https://current.geneontology.org/annotations/rgd.gaf.gz"),
    ("zebrafish", "https://current.geneontology.org/annotations/zfin.gaf.gz"),
    ("drosophila", "https://current.geneontology.org/annotations/fb.gaf.gz"),
    ("celegans", "https://current.geneontology.org/annotations/wb.gaf.gz"),
    ("yeast", "https://current.geneontology.org/annotations/sgd.gaf.gz"),
    ("arabidopsis", "https://current.geneontology.org/annotations/tair.gaf.gz"),
    ("ecoli", "https://current.geneontology.org/annotations/ecocyc.gaf.gz"),
]

def main():
    for name, url in GENOMES:
        gaf = url.split("/")[-1]
        gaf = f"obo/{gaf}"
        idx = f"obo/{name}.index.gz"
        cmd = f"make index GAF_URL={url} GAF={gaf} IDX={idx}"
        print(cmd)


if __name__ == '__main__':
    main()
