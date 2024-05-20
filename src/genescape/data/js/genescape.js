
var ZOOM_LEVEL = 1; // Initial zoom level


// Renders the graph using Graphviz
function render_graph() {

	// Reset the zoom level.
	ZOOM_LEVEL = 1;

	// Get the DOM elements to operate on.
    dot = document.getElementById('dot_data');
    graph = document.getElementById('graph_root')

    // Pop modal window if either is missing
    if (!dot || !graph) {
		alert('Error: Missing required elements (dot_data or graph_root)!' );
		return;
	}

	// Get the dot value from the DOM element.
	dot = dot.textContent;

	Viz.instance().then(function (viz) {
        var svg = viz.renderSVGElement(dot);
        svg.setAttribute("id", "svgtree");
        graph.innerHTML = '';
        graph.appendChild(svg);
    }).catch(
        error => console.error("Error rendering Graphviz: ", error)
    );
}
