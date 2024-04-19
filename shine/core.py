from shiny import reactive
from shiny import App, render, ui
from pathlib import Path
from datetime import datetime
import time

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

app_ui = ui.page_sidebar(

    ui.sidebar(
        ui.input_text_area("terms", label="Gene List", value=GENE_LIST),
        ui.input_action_button("submit", "Draw Tree", onclick=""),
        ui.output_code("annot_elem"),
        width=300,
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
        ui.include_css(site_css),
        ui.include_js(site_js_viz, defer=""),
        ui.include_js(site_js_main, method="inline"),
    ),

    ui.div("""Press "Draw Tree" to generate the graph""", id="graph_elem"),

    ui.output_code("dot_elem"),

    ui.output_text("run_elem"),

    #ui.output_("AAA", id="demo_elem"),

    title="GeneScape",

)





def text2list(text):
    terms = map(lambda x: x.strip(), text.splitlines())
    terms = filter(None, terms)
    terms = list(terms)
    return terms

value = "A"

def server(input, output, session):

    ann_value = reactive.Value("X")
    dot_value = reactive.Value(DOT)

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

        inp = text2list(input.terms())
        cnf = resources.get_config()
        res = resources.init(cnf)
        index = res.INDEX
        graph, ann = tree.parse_input(inp=inp, index=index)

        dot = tree.write_tree(graph, ann, out=None)

        text = annot.ann2csv(ann)

        ann_value.set(text)
        dot_value.set(dot)

        await session.send_custom_message("trigger", 1)

        return f"OK: {inp}"






app = App(app_ui, server)
