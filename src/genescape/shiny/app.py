from shiny import reactive
from shiny import App, render, ui
import asyncio, os
from genescape import icons
from genescape import __version__, nexus, utils, resources

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

app_ui = ui.page_sidebar(

    ui.sidebar(
        ui.input_text_area("terms", label="Gene List", value=GENE_LIST),

        ui.div({"class": "left-aligned"},

               ui.input_select(
                   "database",
                   "Organism", DATABASE_CHOICES,
               ),

               ui.input_text("mincount", label="Mincount", value=MINCOUNT),
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

    ui.tags.hr(),

    ui.tags.p(

        ui.p("""Press "Draw Tree" to generate the graph""", id="graph_elem", align="center"),
        # TODO ui.div(
        #    ui.output_text("msg_elem"),
        #    align="center",
        # ),
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

    ann_value = reactive.Value("# The annotations will appear here.")
    dot_value = reactive.Value("# The dot file will appear here.")
    msg_value = reactive.Value("Runtime messages will appear here.")

    async def create_tree(text):
        mincount = int(input.mincount())
        pattern = input.pattern()
        code = input.database()

        genes = text2list(text)

        root = input.root()

        idx_fname = res.INDEX_FILE

        #index = res.find_index(code=code)

        #msg = utils.index_stats(index=index, verbose=False)[-1]

        msg = "OK"

        dot, tree, ann = nexus.run(genes=genes, idx_fname=idx_fname, mincount=mincount, pattern=pattern, root=root)

        ann_value.set(ann)
        dot_value.set(dot.to_string())
        msg_value.set(msg)

        async def trigger():
            await session.send_custom_message("trigger", 1)

        session.on_flushed(trigger, once=True)

        return dot, text

    @render.download(filename=lambda: "genescape.csv")
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
