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
MINCOUNT = res.config.get("MINCOUNT", 1)

# Load the sidebar width.
SIDEBAR_WIDTH = res.config.get("SIDEBAR_WIDTH", 300)

# Default sidebar background color.
SIDEBAR_BG = res.config.get("SIDEBAR_WIDTH", "#f9f9f9")

# Home page link
HOME = "https://github.com/ialbert/genescape-central/"

HELP = """
The functional annotations will be shown in the table below. 
"""

DOCS = """

**Welcome to GeneScape**

Press Draw Tree to render the graph.


Tips for making graphs smaller:

1. Filter for minimum coverage in the functions. You can use regular expressions in the pattern.

### Legend

<img src="/static/node-help.png" class="img-fluid helpimg" alt="Alt text">

The coverage indicates how many genes in the input cover that function.

Green nodes indicate functions present in input genes.

Dark green nodes indicate leaf nodes in the ontology (highest possible granularity).


* Subtrees are colored by Ontology namespace: Cellular Component (pink), Molecular Function (blue), Biological Process (beige).
* The number `[234]` in a node indicates the number of annotation for that GO term in total.
* The number `(1/5)` in a node indicates how many input genes carry that function.
"""

print(os.getcwd())

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text_area("terms", label="Gene List", value=GENE_LIST),
        width=SIDEBAR_WIDTH, bg=SIDEBAR_BG,
    ),

    ui.navset_tab(
        ui.nav_panel("Graph", "Panel A content"),
        ui.nav_panel("Annotations", "Panel B content"),
        ui.nav_panel("Help",
                     ui.tags.p(
                         ui.markdown(DOCS)),
                     ui.img(src="node-colors.png", ),
                     ),

        id="tab", selected="Graph"
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
