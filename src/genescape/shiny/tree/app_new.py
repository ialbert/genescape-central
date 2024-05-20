from shiny import reactive
from shiny import App, render, ui
import asyncio, os, time
from genescape import icons
from genescape import __version__, gs_graph, utils, resources
import pandas as pd
from pathlib import Path

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

# Load the default resources.
res = resources.init()

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
MINCOUNT = res.config.get("MINCOUNT", "autodetect")

# Load the sidebar width.
SIDEBAR_WIDTH = res.config.get("SIDEBAR_WIDTH", 300)

# Default sidebar background color.
SIDEBAR_BG = res.config.get("SIDEBAR_WIDTH", "#f9f9f9")

# Home page link
HOME = "https://github.com/ialbert/genescape-central/"

HELP = """
The functional annotations will be shown in the table below. 
"""

GRAPH_TAB = """
Press "Draw Tree" to generate the graph.
"""

ANNOT_TAB = """

## Functional annotations

This panel shows the functional annotations for the input genes.

Each gene is annotated with GO terms. The coverage indicates how many genes in the input cover that function.

You can filter the table by entering a regular expression in the pattern field.
"""

HELP_TAB = """

## How to use GeneScape

Tips for making graphs smaller:

1. Filter for minimum coverage in the functions. You can use regular expressions in the pattern.

## Legend

<img src="/static/node-help.png" class="img-fluid helpimg" alt="Alt text">

The coverage indicates how many genes in the input cover that function.

## Colors

Green nodes indicate functions present in input genes.

Dark green nodes indicate leaf nodes in the ontology (highest possible granularity).

* Subtrees are colored by Ontology namespace: Cellular Component (pink), Molecular Function (blue), Biological Process (beige).
* The number `[234]` in a node indicates the number of annotation for that GO term in total.
* The number `(1/5)` in a node indicates how many input genes carry that function.
"""

print(os.getcwd())

app_ui = ui.page_sidebar(
    ui.sidebar(

        # The gene list.
        ui.input_text_area("input_list", label="Gene List", value=GENE_LIST),

        # The main submit button.
        ui.input_action_button(
            "submit", "Draw Tree", class_="btn-success", icon=icons.icon_play
        ),

        # Select the database.
        ui.input_select(
            "database",
            "Organism", DATABASE_CHOICES,
        ),

        # Minimum count.
        ui.input_text("coverage", label="Coverage", value=MINCOUNT),

        # Filtering pattern.
        ui.input_text("pattern", label="Pattern (regex ok)", value=PATTERN),

        # Download button for annotation CSV.
        ui.tags.p(
            ui.download_link("download_csv", "Download CSV file", icon=icons.icon_down),
        ),

        # Download button for the dot data
        ui.tags.p(
            ui.download_link("download_dot", "Download DOT file", icon=icons.icon_down),
        ),

        # The annotation data as csv.
        ui.output_code("csv_data"),

        # The dot file as text.
        ui.output_code("dot_data"),

        width=SIDEBAR_WIDTH, bg=SIDEBAR_BG,
    ),

    ui.navset_tab(

        # Graph panel.
        ui.nav_panel(
            "Graph", ui.tags.p(

                ui.tags.p(
                    ui.input_action_button("zoom_in", label="Zoom", icon=icons.icon_zoom_in,
                                           class_="btn btn-light",
                                           data_action="zoom_in"),
                    ui.tags.span(" "),
                    ui.input_action_button("zoom_reset", label="Reset", icon=icons.zoom_reset,
                                           class_="btn btn-light",
                                           data_action="zoom_reset"),
                    ui.tags.span(" "),
                    ui.input_action_button("zoom_out", label="Zoom", icon=icons.icon_zoom_out,
                                           class_="btn btn-light ",
                                           data_action="zoom_out"),
                    ui.tags.span(" "),
                    ui.input_action_button("save_image", "Save", class_="btn btn-light", icon=icons.icon_down),

                    align="center",
                ),

                # Error message label.
                ui.tags.div(
                    ui.output_text(id="error_msg"),
                    class_="error_msg",
                ),

                # Info message label.
                ui.tags.div(
                    ui.output_text(id="info_msg1"),
                    class_="info_msg", align="center",
                ),

                # The graph root object.
                ui.div(
                    ui.tags.b(GRAPH_TAB),
                    id="graph_root", align="center"),

                # Info message label.
                ui.tags.div(
                    ui.output_text(id="info_msg2"),
                    class_="info_msg", align="center",
                ),
                class_="graph_root",
            ),
        ),

        ui.nav_panel(
            "Annotations", ui.tags.p(
                ui.tags.p(
                    ui.output_data_frame("annot_root"),
                ),
                ui.markdown(ANNOT_TAB),
            ),
        ),

        ui.nav_panel(
            "Help", ui.tags.p(
                ui.markdown(HELP_TAB)),

        ),
        id="tabs", selected="Graph"
    ),

    ui.tags.div(
        ui.tags.p(
            ui.tags.a(HOME, href=HOME),
        ),
        ui.tags.p(f"GeneScape {__version__}"),
        align="center",
    ),

    ui.head_content(
        ui.tags.script(
            """
            // Page complete trigger.
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
    title=PAGE_TITLE, id="main",
)

def text2list(text):
    """
    Parses a text inptu into a list of terms
    """
    terms = map(lambda x: x.strip(), text.splitlines())
    terms = filter(None, terms)
    terms = list(terms)
    return terms

def server(input, output, session):
    # The annotation table.
    ann_df = reactive.Value(pd.DataFrame())

    # Runtime messages
    info_value1 = reactive.Value("")

    # Runtime messages
    info_value2 = reactive.Value("")

    # Runtime error message
    err_value = reactive.Value("")

    # Annotation as a CSV string (invisible)
    csv_value = reactive.Value("# The annotation CSV will appear here.")

    # The dot file as a text (invisible)
    dot_value = reactive.Value("# The dot file will appear here.")

    @reactive.effect
    @reactive.event(input.submit)
    async def submit():
        await create_tree()

    async def create_tree():
        limit = 10
        # Emulate some sort of progress bar
        with ui.Progress(min=1, max=limit) as p:
            p.set(message="Generating the image", detail="Please wait...")
            for i in range(1, limit):
                p.set(i)
                await asyncio.sleep(0.1)

        coverage = input.coverage()

        res = resources.init()

        idx_fname = res.INDEX_FILE

        # The input gene list.
        targets = text2list(input.input_list())

        print (targets)

        # Create the subgraph.
        run = gs_graph.subgraph(idx_fname, targets=targets)

        # get the dataframe
        df = run.as_df()

        # Create the pydot object.
        pg = run.as_pydot()

        # Set the dot data.
        dot_value.set(str(pg))

        # Set the CSV data.
        csv_value.set(df.to_csv(index=False))

        # Set the info messages.
        info_str1 = f"Graph: {run.tree.number_of_nodes()} nodes and {run.tree.number_of_edges()} edges."
        info_value1.set(info_str1)

        info_str2 = str(run.idx)
        info_value2.set(info_str2)

        # Set the error message.
        if run.errors:
            err_str = ",".join(run.errors)
            err_value.set(err_str)



        # The trigger function.
        async def trigger():
            await session.send_custom_message("trigger", 1)

        # Send a custom message to trigger the graph rendering.
        session.on_flushed(trigger, once=True)

    @render.text
    async def error_msg():
        return err_value.get()

    @render.text
    async def info_msg1():
        return info_value1.get()

    @render.text
    async def info_msg2():
        return info_value2.get()

    @render.text
    async def csv_data():
        return csv_value.get()

    @output
    @render.text
    async def dot_data():
        return dot_value.get()

    @render.download(filename=lambda: "genescape.csv")
    async def download_csv():
        await asyncio.sleep(0.5)
        yield csv_value.get()

    @render.download(filename=lambda: "genescape.dot.txt")
    async def download_dot():
        await asyncio.sleep(0.5)
        yield dot_value.get()

# The Static app
app_static = StaticFiles(directory=Path(__file__).parent / "static")

# Define UI
app_ui2 = ui.page_fluid(
    ui.input_action_button(
        "submit", "Draw Tree", class_="btn-success"
    ),
    ui.output_text("output")
)
# Define Server
def server2(input, output, session):

    info_value = reactive.Value("")

    #@reactive.effect
    @reactive.event(input.submit)
    def submit():
        print("HERE")

        # The trigger function.
        def trigger():
            session.send_custom_message("trigger", 1)

        # Send a custom message to trigger the graph rendering.
        session.on_flushed(trigger, once=True)

        info_value.set("SUBMIT")

    @render.text
    def output():
        # Access the reactive value
        return info_value.get()

# The shiny app
app_shiny = App(app_ui, server)


def app():
    routes = [
        Mount('/static', app=app_static),
        Mount('/', app=app_shiny)
    ]

    webapp = Starlette(routes=routes)

    return webapp


if __name__ == '__main__':
    import shiny

    shiny.run_app(app, host='localhost', port=8000, reload=True)
