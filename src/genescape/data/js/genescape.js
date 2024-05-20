
var ZOOM_LEVEL = 1; // Initial zoom level
var ZOOM_STEP = 1.2; // Zoom step

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
        svg.setAttribute("width", "100%");
		svg.setAttribute("height", "100%");

		graph.innerHTML = '';
        graph.appendChild(svg);

		rect = graph.getBoundingClientRect();

		var bbox = svg.getBBox();

		zoom = rect.width/bbox.width;

		var svg_obj = document.querySelector('#svgtree');

		//svg_obj.style.transformOrigin = 'top left';
		//svg_obj.style.transform = `scale(${zoom})`;
		//debugger;

    }).catch(
        error => console.error("Error rendering Graphviz: ", error)
    );
}

// Saves the SVG as an image.
function save_image() {
    var svg = document.getElementById('svgtree');
    var svgData = new XMLSerializer().serializeToString(svg);
    var canvas = document.createElement("canvas");
    var ctx = canvas.getContext("2d");
    var img = document.createElement("img");

    img.setAttribute("src", "data:image/svg+xml;base64," + btoa(svgData));

    canvas.width = svg.width.baseVal.value;
    canvas.height = svg.height.baseVal.value;

    img.onload = function () {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        // Triggering download
        var link = document.createElement("a");
        link.download = "genescape.png";
        link.href = canvas.toDataURL("image/png").replace("image/png", "image/octet-stream");
        link.click();
    };
}

// Adjusts the zoom level of the graph
function adjust_zoom(action) {

    var svg = document.querySelector('#svgtree');

    if (!svg) return;

	// Adjust zoom level based on the action
    if (action === 'zoom_in') {
        ZOOM_LEVEL *= ZOOM_STEP
    } else if (action === 'zoom_out') {
        ZOOM_LEVEL /= ZOOM_STEP
    } else {
        ZOOM_LEVEL = 1;
    }

    // Apply new zoom level to the SVG
    svg.style.transform = `scale(${ZOOM_LEVEL})`;
    svg.style.transformOrigin = 'top left';

}

// Add event listeners to the DOM elements after page load.
document.addEventListener("DOMContentLoaded", function() {

        document.getElementById("save_image").addEventListener("click", save_image);

		document.querySelectorAll('button[data-action]').forEach(button => {
	        button.addEventListener('click', function() {
	            var action = this.getAttribute('data-action');
	            adjust_zoom(action);
	        });

		});
});
