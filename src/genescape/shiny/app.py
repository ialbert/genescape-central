from shiny import reactive
from shiny import App, render, ui
import asyncio, os
from genescape import icons
from genescape import __version__, nexus, utils, resources
import pandas as pd

# Get a resource configuration file.
cnf_fname = os.environ.get("GENESCAPE_CONFIG", None)

# Load the configuration file.
cnf = resources.get_config(fname=cnf_fname)

# Load the default resources.
res = resources.init(config=cnf)

# Update the resources from the environment.
res.update_from_env()

# This is the global database choices
DATABASE_CHOICES = dict()

# Update the choices with the defaults.
DATABASE_CHOICES.update(res.index_choices())

PAGE_TITLE = res.config.get("PAGE_TITLE", "GeneScape")

# Default gene list.
GENE_LIST = res.config.get("GENE_LIST", "ABTB3\nBCAS4\nC3P1\nGRTP1")

# Default pattern.
PATTERN = res.config.get("PATTERN", "")

# Default mincount.
MINCOUNT = res.config.get("MINCOUNT", 1)

# Load the sidebar width.
SIDEBAR_WIDTH = res.config.get("SIDEBAR_WIDTH", 300)

# Default sidebar background color.
SIDEBAR_BG = res.config.get("SIDEBAR_WIDTH", "#f9f9f9")

# Home page link
HOME = "https://github.com/ialbert/genescape-central/"

HELP = """
Press "Draw Tree" to generate the graph.  The annotations will appear in the table below. 
        
Reduce the graph size by filtering for coverage or words in the functions (regex ok).
"""

DOCS = """
* The coverage indicates how many genes in the input cover that function.
* Green nodes indicate functions present in input genes.
* Dark green nodes indicate leaf nodes in the ontology (highest possible granularity).
* Subtrees are colored by Ontology namespace: Cellular Component (pink), Molecular Function (blue), Biological Process (beige).
* The number `[234]` in a node indicates the number of annotation for that GO term in total.
* The number `(1/5)` in a node indicates how many input genes carry that function.
"""
app_ui = ui.page_sidebar(

    ui.sidebar(
        ui.input_text_area("terms", label="Gene List", value=GENE_LIST),

        ui.div({"class": "left-aligned"},

               ui.input_select(
                   "database",
                   "Organism", DATABASE_CHOICES,
               ),

               ui.input_text("mincount", label="Coverage", value=MINCOUNT),
               ui.input_text("pattern", label="Pattern", value=PATTERN),

               ui.input_select(
                   "root",
                   "Root", {
                       utils.NS_ALL: "All roots",
                       utils.NS_BP: "Biological Process",
                       utils.NS_MF: "Molecular Function",
                       utils.NS_CC: "Cellular Component"
                   },
               ),
               ),
        ui.input_action_button("submit", "Draw Tree", class_="btn-success", icon=icons.icon_play),

        ui.tags.p(
            ui.download_link("download_csv", "Download annotations as CSV", icon=icons.icon_down),
        ),
        ui.tags.p(
            ui.download_link("download_dot", "Download graph as a DOT file", icon=icons.icon_down),
        ),
        ui.output_code("annot_csv"),
        ui.output_code("dot_elem"),

        width=SIDEBAR_WIDTH, bg=SIDEBAR_BG,
    ),

    ui.head_content(
        ui.tags.script(
            """
            $(function() {
                Shiny.addCustomMessageHandler("trigger", function(message) {
                    render_graph();
                });
            });
            """),
        ui.include_css(res.GENESCAPE_CSS),
        ui.include_js(res.VIZ_JS, defer=""),
        ui.include_js(res.GENESCAPE_JS, method="inline"),
    ),

    ui.tags.p(
        ui.input_action_button("zoom_in", label="Zoom", icon=icons.icon_zoom_in, class_="btn btn-light btn-sm",
                               data_action="zoom-in"),
        ui.tags.span(" "),
        ui.input_action_button("reset", label="Reset", icon=icons.zoom_reset, class_="btn btn-light btn-sm",
                               data_action="zoom-reset"),
        ui.tags.span(" "),
        ui.input_action_button("zoom_out", label="Zoom", icon=icons.icon_zoom_out, class_="btn btn-light btn-sm",
                               data_action="zoom-out"),
        ui.tags.span(" "),
        ui.input_action_button("saveImage", "Save", class_="btn btn-light btn-sm", icon=icons.icon_down),

        align="center",
    ),

    ui.tags.p(
        # ui.tags.hr(),
        ui.output_text("err_label"),
        ui.p(
            id="graph_elem", align="center"),
    ),

    ui.tags.p(
        ui.tags.div(
            ui.output_text("msg_elem"),
            align="center"),
    ),

    ui.tags.p(
        ui.output_data_frame("annot_table"),
    ),

    ui.tags.hr(),
    ui.markdown(DOCS),

    ui.tags.div(
        ui.tags.hr(),
        ui.tags.p(
            ui.tags.a(HOME, href=HOME),
        ),
        ui.tags.p(f"GeneScape {__version__}"),
        align="center",
    ),

    ui.output_text("run_elem"),

    title=PAGE_TITLE, id="main",

)


def text2list(text):
    """
    Parses a text block into a list of terms
    """
    terms = map(lambda x: x.strip(), text.splitlines())
    terms = filter(None, terms)
    terms = list(terms)
    return terms


def server(input, output, session):
    """
    Shiny server.
    """
    global res

    # The annotation table.
    ann_table = reactive.Value(pd.DataFrame())

    # Runtime messages
    msg_value = reactive.Value(HELP)

    # Runtime error message
    err_value = reactive.Value("")

    # Annotation as a CSV string (invisible)
    ann_csv = reactive.Value("# The annotation table will appear here.")

    # The dot file as a text (invisible)
    dot_value = reactive.Value("# The dot file will appear here.")

    async def create_tree(text):
        mincount = int(input.mincount())
        pattern = input.pattern()
        code = input.database()

        genes = text2list(text)

        root = input.root()

        # idx_fname = res.INDEX_FILE

        idx_fname = res.find_index(code=code)

        # msg = utils.index_stats(index=index, verbose=False)[-1]

        idx, dot, tree, ann, status = nexus.run(genes=genes, idx_fname=idx_fname, mincount=mincount, pattern=pattern,
                                                root=root)

        ann_table.set(ann)
        ann_csv.set(ann.to_csv(index=False))
        dot_value.set(dot.to_string())

        nodes = len(tree.nodes())
        edges = len(tree.edges())
        stats = nexus.stats(idx)

        valid_count = len(status.get('sym_valid',[]))

        # Set main message.
        msg = f"Recognized {valid_count} symbols. Subgraph with {nodes} nodes and {edges} edges. Index: {stats[0]:,d} mappings of {stats[1]:,d} genes,over {stats[2]} terms."
        msg_value.set(msg)

        # Set the error message
        miss = status.get("sym_miss")
        if miss:
            msg = f"Unknown symbols: {', '.join(miss)}"
            err_value.set(msg)
        else:
            err_value.set("")

        async def trigger():
            await session.send_custom_message("trigger", 1)

        session.on_flushed(trigger, once=True)

        return dot, text

    @render.download(filename=lambda: "genescape.csv")
    async def download_csv():
        await asyncio.sleep(0.5)
        yield ann_csv.get()

    @render.download(filename=lambda: "genescape.dot.txt")
    async def download_dot():
        await asyncio.sleep(0.5)
        yield dot_value.get()

    @output
    @render.data_frame
    def annot_table():
        df = ann_table.get()
        return render.DataTable(df, width='fit-content')

    @output
    @render.text
    def annot_csv():
        return ann_csv.get()

    @output
    @render.text
    def err_label():
        return err_value.get()

    @output
    @render.text
    def dot_elem():
        return dot_value.get()

    @output
    @render.text
    def msg_elem():
        return msg_value.get()

    @output
    @render.text
    def demo_elem():
        return dot_value.get()

    @output
    @render.text
    @reactive.event(input.submit)
    async def run_elem():
        await run_main()
        return ""

    # The main tree runner.
    async def run_main():
        limit = 10
        # Emulate some sort of progress bar
        with ui.Progress(min=1, max=limit) as p:
            p.set(message="Generating the image", detail="Please wait...")
            for i in range(1, limit):
                p.set(i)
                await asyncio.sleep(0.1)

            # Generate the tree
            await create_tree(input.terms())


app = App(app_ui, server)

if __name__ == '__main__':
    import shiny

    shiny.run_app(app)
