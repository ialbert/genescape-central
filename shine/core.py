from shiny import reactive
from shiny import App, render, ui
from pathlib import Path
from datetime import datetime
import time, asyncio

from genescape import __version__, annot, bottle, resources, tree, utils

GENE_LIST = '''
ABTB3
BCAS4
'''

DOT = '''
digraph SimpleGraph {
    A -> B;
    B -> C;
    C -> A;
}
'''

base_dir = Path(__file__).parent / "libs"
site_css = base_dir / "style.css"
site_js_viz = base_dir / "js" / "viz-standalone.js"
site_js_main = base_dir / "js" / "main.js"

# Shiny UI
app_ui = ui.page_sidebar(

    ui.sidebar(
        ui.input_text_area("terms", label="Gene List", value=GENE_LIST),
        ui.input_text("mincount", label="Minimum count (integer)", value="1"),
        ui.input_text("pattern", label="Word pattern (regex)", value="protein|cytoplasm"),
        ui.input_selectize(
            "selectize",
            "Ontology root:",{
                "AA": "All roots",
                "BP": "Biological Process",
                "MF": "Molecular Function",
                "CC": "Cellular Component"},

        ),
        ui.input_action_button("submit", "Draw Tree", class_="btn-success"),
        ui.output_code("annot_elem"),
        ui.output_code("dot_elem"),

        width=400,
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
        ui.include_css(site_css),
        ui.include_js(site_js_viz, defer=""),
        ui.include_js(site_js_main, method="inline"),
    ),

    ui.div("""Press "Draw Tree" to generate the graph""", id="graph_elem"),
    ui.output_text("run_elem"),

    title="GeneScape",

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

    @reactive.event(input.mincount)
    async def _():
        dot, text = await create_tree(input.terms())

    @render.text
    @reactive.event(input.submit)
    async def run_elem():

        with ui.Progress(min=1, max=15) as p:
            p.set(message="Generating the image", detail="This may take a while...")
            for i in range(1, 10):
                p.set(i, message="Computing")
                await asyncio.sleep(0.1)

        dot, text = await create_tree(input.terms())


        return f""


app = App(app_ui, server)
