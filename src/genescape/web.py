from shiny import reactive
from shiny import App, render, ui
from pathlib import Path
from datetime import datetime
import time, asyncio
from genescape import icons

from genescape import __version__, annot, build, resources, tree, utils

# Default gene list.
GENE_LIST = '''
ABTB3
BCAS4
C3P1
GRTP1
'''

# Default pattern.
PATTERN = ""

# Default dot file.
DOT = '''
digraph SimpleGraph {
    A -> B;
    B -> C;
    C -> A;
}
'''

# Default sidebar width.
SIDEBAR_WIDTH = 300

# Default sidebar background color.
SIDEBAR_BG = "#f8f8f8"

# Home page link
HOME = "https://github.com/ialbert/genescape-central/"

# Load the default resources.
res = resources.init()

# This is the global index name
INDEX = res.INDEX

# Shiny UI
app_ui = ui.page_sidebar(

    ui.sidebar(
        ui.input_text_area("terms", label="Gene List", value=GENE_LIST),
        ui.input_text("mincount", label="Minimum count (integer)", value="1"),
        ui.input_text("pattern", label="Word pattern (regex)", value=PATTERN),
        ui.input_select(
            "root",
            "Ontology root:", {
                utils.NS_ALL: "All roots",
                utils.NS_BP: "Biological Process",
                utils.NS_MF: "Molecular Function",
                utils.NS_CC: "Cellular Component"
            },
        ),
        ui.input_action_button("submit", "Draw Tree", class_="btn-success", icon=icons.icon_play),

        ui.output_code("annot_elem"),
        ui.download_link("download_csv", "Download annotations", icon=icons.icon_down),
        ui.output_code("dot_elem"),
        ui.download_link("download_dot", "Download dot file", icon=icons.icon_down),

        width=SIDEBAR_WIDTH, bg=SIDEBAR_BG,
    ),

    ui.head_content(
        ui.tags.script(
            """
            $(function() {
                Shiny.addCustomMessageHandler("trigger", function(message) {
                    render_graph_delay();
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

    ui.tags.hr(),

    ui.tags.p(
        ui.div("""Press "Draw Tree" to generate the graph""", id="graph_elem", align="center"),
    ),

    ui.tags.div(
        ui.tags.hr(),
        ui.tags.p(
            ui.tags.a(HOME, href=HOME),
        ),
        ui.tags.p(f"GeneScape {__version__}"),
        align="center",
    ),
    ui.output_text("run_elem"),

    title=f"GeneScape" , id="main",

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
    ann_value = reactive.Value("# The annotations will appear here.")
    dot_value = reactive.Value("# The dot file will appear here.")

    res = resources.init()

    # External index or default
    index = INDEX or res.INDEX

    async def create_tree(text):
        mincount = int(input.mincount())
        pattern = input.pattern()

        inp = text2list(text)

        root = input.root()

        graph, ann = tree.parse_input(inp=inp, index=index, mincount=mincount, pattern=pattern, root=root)

        dot = tree.write_tree(graph, ann, out=None)

        text = annot.ann2csv(ann)

        ann_value.set(text)
        dot_value.set(dot)

        await session.send_custom_message("trigger", 1)

        return dot, text

    @render.download( filename=lambda: "genescape.csv")
    async def download_csv():
        await asyncio.sleep(0.5)
        yield ann_value.get()

    @render.download(filename=lambda: "genescape.dot.txt")
    async def download_dot():
        await asyncio.sleep(0.5)
        yield dot_value.get()

    @output
    @render.text
    def annot_elem():
        return ann_value.get()

    @output
    @render.text
    def dot_elem():
        return dot_value.get()

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

        # Remind the user that a computation is in progress.
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Generating the image", detail="Please wait...")
            for i in range(1, 10):
                p.set(i, message="Computing")
                await asyncio.sleep(0.1)

        dot, text = await create_tree(input.terms())


app = App(app_ui, server)

if __name__ == '__main__':
    import shiny
    shiny.run_app(app)
