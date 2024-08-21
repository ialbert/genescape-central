

var ZOOM_IN = 1.3;
var ZOOM_OUT = 1 / ZOOM_IN;

var initialBox = null; // Initial viewBox of the SVG element

function resize_container(){
	var div = document.getElementById('graph_root');
	var svg = document.getElementById('svgtree');


	const bbox = svg.getBBox();
    //div.style.width = `${bbox.width}px`;
    //div.style.height = `${bbox.height}px`;

	div.style.display = 'none';
    div.offsetHeight;  // Trigger a reflow
    div.style.display = 'block';


}

// Renders the graph using Graphviz
function render_graph() {

	currentZoom = 1;

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
        svg.setAttribute("preserveAspectRatio", "xMinYMin meet");
        //svg.setAttribute("width", "100%");
		//svg.setAttribute("height", "100%");
		svg.setAttribute("height", "800px");

		graph.innerHTML = '';
        graph.appendChild(svg);


    }).catch(
        error => console.error("Error rendering Graphviz: ", error)
    );

	addEventListeners();

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

var currentZoom = 1;

// JavaScript function to zoom SVG
function zoom_SVG(zoomFactor) {
    const svg = document.getElementById("svgtree");
    const div = document.getElementById("graph_root");

	currentZoom *= zoomFactor;

	svg.style.transformOrigin = 'top left';
    svg.style.transform = `scale(${currentZoom})`;

    resize_container();
}

function reset_SVG() {
	currentZoom = 1;
    const svg = document.getElementById("svgtree");
	svg.style.transform = `scale(${currentZoom})`;

	resize_container();
}

// Add event listeners to the DOM elements after page load.
function addEventListeners() {
        //document.getElementById("save_image").addEventListener("click", save_image);
		document.getElementById('zoom_in').addEventListener('click', () => zoom_SVG(ZOOM_IN));
		document.getElementById('zoom_out').addEventListener('click', () => zoom_SVG(ZOOM_OUT));
		document.getElementById('zoom_reset').addEventListener('click', reset_SVG);
}
