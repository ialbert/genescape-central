from shiny import reactive
from shiny import App, render, ui
from pathlib import Path
from datetime import datetime
import time, asyncio
from genescape import icons

from genescape import __version__, annot, bottle, resources, tree, utils

GENE_LIST = '''
ABTB3
BCAS4
C3P1
GRTP1
ABTB3
BCAS4
C3P1
GRTP1
Cyp1a1
Sphk2
Sptlc2
GO:0005488
GO:0005515
'''

DOT = '''
digraph SimpleGraph {
    A -> B;
    B -> C;
    C -> A;
}
'''

# Load the default resources.
res = resources.init()


HOME = "https://github.com/ialbert/genescape-central/"

# Shiny UI
app_ui = ui.page_sidebar(

    ui.sidebar(
        ui.input_text_area("terms", label="Gene List", value=GENE_LIST),
        ui.input_text("mincount", label="Minimum count (integer)", value="1"),
        ui.input_text("pattern", label="Word pattern (regex)", value="protein|cytoplasm"),
        ui.input_selectize(
            "selectize",
            "Ontology root:", {
                "AA": "All roots",
                "BP": "Biological Process",
                "MF": "Molecular Function",
                "CC": "Cellular Component"},
        ),
        ui.input_action_button("submit", "Draw Tree", class_="btn-success", icon=icons.icon_play),

        ui.output_code("annot_elem"),
        ui.download_link("download_csv", "Download annotations", icon=icons.icon_down),
        ui.output_code("dot_elem"),
        ui.download_link("download_dot", "Download dot file", icon=icons.icon_down),

        width=400, bg="#f8f8f8",
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

    title="GeneScape", id="main",

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

    async def create_tree(text):
        mincount = int(input.mincount())
        pattern = input.pattern()

        inp = text2list(text)

        cnf = resources.get_config()

        res = resources.init(cnf)
        index = res.INDEX

        graph, ann = tree.parse_input(inp=inp, index=index, mincount=mincount, pattern=pattern)

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

    @render.text
    @reactive.event(input.submit)
    async def run_elem():
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Generating the image", detail="Please wait...")
            for i in range(1, 10):
                p.set(i, message="Computing")
                await asyncio.sleep(0.1)

        dot, text = await create_tree(input.terms())

        return f""


app = App(app_ui, server)

if __name__ == '__main__':
    import shiny
    shiny.run_app(app)
