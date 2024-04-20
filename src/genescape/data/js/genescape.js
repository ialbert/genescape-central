function render_graph_delay() {
    setTimeout(() => {
        render_graph()
    }, 1000);
}

function render_graph() {

    dot = document.getElementById('dot_elem').textContent;
    graph = document.getElementById('graph_elem')

    Viz.instance().then(function (viz) {
        var svg = viz.renderSVGElement(dot);
        svg.setAttribute("id", "svgtree");
        graph.innerHTML = '';
        graph.appendChild(svg);
    }).catch(
        error => console.error("Error rendering Graphviz:", error)
    );
}

function saveSvgAsImage() {
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

function resize_container(svg){

	var svg = document.getElementById('svgtree')

	var h = svg.getBoundingClientRect().height;
	var w = svg.getBoundingClientRect().width;

	var cn = document.getElementById('main');

	//cn.style.height = h + 'px';
	//cn.style.width  = w + 'px';

	console.log('cn:', cn.style.height, cn.style.width);
}

var zoomLevel = 1; // Initial zoom level

// Function to adjust SVG zoom based on action
function adjustSVGZoom(zoomAction) {

    console.log(zoomAction)

    var svg = document.querySelector('#svgtree');

    if (!svg) return;

    // Adjust zoom level based on the action
    if (zoomAction === 'zoom-in') {
        zoomLevel *= 1.2;
    } else if (zoomAction === 'zoom-out') {
        zoomLevel /= 1.2;
    } else {
        zoomLevel = 1;
    }

    // Apply new zoom level to the SVG
    svg.style.transform = `scale(${zoomLevel})`;
    svg.style.transformOrigin = 'top left';

	resize_container();

}

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("saveImage").addEventListener("click", saveSvgAsImage);

    document.querySelectorAll('button[data-action]').forEach(button => {

        button.addEventListener('click', function() {
            var action = this.getAttribute('data-action');
            console.log("ACTION", action);

            adjustSVGZoom(action);
        }
    );
});

});
