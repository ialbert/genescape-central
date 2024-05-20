from shiny import reactive
from shiny import App, render, ui
import asyncio, os
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
        ui.output_code("data_csv"),

        # The dot file as text.
        ui.output_code("data_dot"),

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
                ),

                # Info message label.
                ui.tags.div(
                    ui.output_text("info_msg"),
                    align="center"),

                # The graph root object.
                ui.p(
                    ui.tags.b(GRAPH_TAB),
                    id="graph_root", align="center"),
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
            ui.img(src="node-colors.png", ),
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


def server(input, output, session):
    pass


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
