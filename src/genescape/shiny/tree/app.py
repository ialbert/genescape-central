from shiny import reactive
from shiny import App, render, ui
import asyncio, os, time
from genescape import icons
from genescape import __version__, gs_graph, utils, resources
import pandas as pd
from pathlib import Path
from random import shuffle

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

# Load the default resources.
res = resources.init()


def random_gene_list(res, N=50):
    """
    Returns a random gene list.
    """
    idg = gs_graph.load_index_graph(res.INDEX_FILE)
    sym = gs_graph.random_symbols(idg, N=N)
    return "\n".join(sym)


# This is the global database choices
DATABASE_CHOICES = dict()

# Update the choices with the defaults.
DATABASE_CHOICES.update(res.index_choices())

PAGE_TITLE = res.config.get("PAGE_TITLE", "GeneScape")

# In testmode we generate a random gene list.
if os.environ.get("GENESCAPE_TEST"):
    GENE_LIST = random_gene_list(res, N=50)
    utils.info("test mode: Random gene list")
else:
    GENE_LIST = res.config.get("GENE_LIST", "ABTB3\nBCAS4\nC3P1\nGRTP1")

# Default pattern.
PATTERN = res.config.get("PATTERN", "")

# Default mincount.
MINCOUNT = res.config.get("MINCOUNT", "")

# Load the sidebar width.
SIDEBAR_WIDTH = res.config.get("SIDEBAR_WIDTH", 300)

# Default sidebar background color.
SIDEBAR_BG = res.config.get("SIDEBAR_WIDTH", "#f9f9f9")

# Home page link
HOME = "https://github.com/ialbert/genescape-central/"

GRAPH_TAB = """
Press "Draw Tree" to generate the graph.
"""

ANNOT_TAB = """

This panel shows the cumulative functional annotations across genes in the list.

The **Coverage** column indicates how many genes in the input cover that function.

> When the **Coverage** is not specified the program will guess a reasonable value for it.

How to reduce the graph size:

1. The **Coverage** filter will select for the minimum coverage.
1. The **Filtering pattern** will keep only functions that match.

Examples:

* **Coverage=5** at least 5 genes carrying the function
* **Filter=GTP|kinase** keep only functions that match both `GTP` and `kinase`.

"""

HELP_TAB = """
Type a list of genes of GO terms then press "Draw Tree".

Tips for making graphs smaller:

1. Filter for minimum coverage in the functions. You can use regular expressions in the pattern.

**Legend**

<img src="/static/node-help.png" class="img-fluid helpimg" alt="Alt text">

The coverage indicates how many genes in the input cover that function.

**Colors**

Green nodes indicate functions present in input genes.

Dark green nodes indicate leaf nodes in the ontology (highest possible granularity).

* Subtrees are colored by Ontology namespace: Cellular Component (pink), Molecular Function (blue), Biological Process (beige).
* The number `[234]` in a node indicates the number of annotation for that GO term in total.
* The number `(1/5)` in a node indicates how many input genes carry that function.
"""

app_ui = ui.page_sidebar(
    ui.sidebar(

        # The gene list.
        ui.input_text_area("input_list", label="Gene List", value=GENE_LIST),

        # Select the database.
        ui.input_select(
            "database",
            label="Organism:", choices=DATABASE_CHOICES,
        ),

        # Select the root
        ui.input_select(
            "root",
            "Domain:", {
                utils.NS_ALL: "All domains",
                utils.NS_BP: "Biological Process",
                utils.NS_MF: "Molecular Function",
                utils.NS_CC: "Cellular Component"
            },
            selected=utils.NS_BP,
        ),

        # Minimum count.
        ui.input_text("coverage", label="Coverage:", value=MINCOUNT),

        # Filtering pattern.
        ui.input_text("pattern", label="Word filter (regex ok):", value=PATTERN),

        # The main submit button.
        ui.input_action_button(
            "submit", "Draw Tree", class_="btn-success", icon=icons.icon_play
        ),

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

                ui.tags.div(
                    ui.input_action_button("zoom_in", label="Zoom", icon=icons.icon_zoom_in,
                                           class_="btn btn-light btn-sm", ),
                    ui.tags.span(" "),
                    ui.input_action_button("zoom_reset", label=" Reset", icon=icons.zoom_reset,
                                           class_="btn btn-light btn-sm"),
                    ui.tags.span(" "),
                    ui.input_action_button("zoom_out", label="Zoom", icon=icons.icon_zoom_out,
                                           class_="btn btn-light btn-sm"),
                    ui.tags.span(" "),
                    ui.input_action_button("save_image", "Save", class_="btn btn-light btn-sm", icon=icons.icon_down),

                    align="center", id="zoom_buttons",
                ),

                # Error message label.
                ui.tags.div(
                    ui.output_text(id="error_msg"),
                    class_="error_msg",
                ),

                # The graph root object.
                ui.div(
                    ui.tags.b(GRAPH_TAB),
                    id="graph_root", align="center"),

            ),
        ),

        ui.nav_panel(
            "Annotations", ui.tags.p(
                # Info message label.
                ui.tags.p(
                    ui.output_text(id="info_msg"),
                    class_="info_msg",
                ),

                ui.div(

                    ui.output_data_frame("df_data"),

                ),
                ui.tags.p(
                    ui.markdown(ANNOT_TAB),
                ),
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
    # Runtime messages
    info_value = reactive.Value("")

    # Runtime error message
    err_value = reactive.Value("")

    # Annotation as a CSV string (invisible)
    csv_value = reactive.Value("# The annotation CSV will appear here.")

    # Default dataframe.
    df_value = reactive.Value(pd.DataFrame())

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

        if coverage:
            try:
                coverage = int(coverage)
            except ValueError:
                coverage = 1

        pattern = input.pattern()
        root = input.root()

        res = resources.init()

        idx_fname = res.INDEX_FILE

        # The input gene list.
        targets = text2list(input.input_list())

        # Load the index.
        idg = gs_graph.load_index_graph(idx_fname)

        # Guess the coverage
        if not coverage:
            coverage = gs_graph.estimate(idg, targets=targets, pattern=pattern, root=root)

        # Create the subgraph.
        run = gs_graph.subgraph(idg, targets=targets, pattern=pattern, root=root, coverage=coverage)

        # Get the dataframe
        df = run.as_df()

        # Set the dataframe value.
        df_value.set(df)

        # Set the CSV data.
        csv_value.set(df.to_csv(index=False))

        # Create the pydot object.
        pg = run.as_pydot()

        # Set the dot data.
        dot_value.set(str(pg))

        # Set the info messages.
        info_str1 = f"Coverage={coverage}; Graph: {run.tree.number_of_nodes()} nodes and {run.tree.number_of_edges()} edges."
        # info_value1.set(info_str1)

        info_str2 = str(run.idx)
        info_value.set(f"{info_str1} {info_str2}")

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
    async def info_msg():
        return info_value.get()

    @render.text
    async def csv_data():
        return csv_value.get()

    @render.text
    async def dot_data():
        return dot_value.get()

    @render.data_frame
    async def df_data():
        df = df_value.get()
        dg = render.DataGrid(df, filters=True, width="100%")
        return dg

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
