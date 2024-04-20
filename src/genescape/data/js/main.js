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
        //svg.setAttribute("width", "100%");
        //svg.setAttribute("height", "1200px");
        graph.innerHTML = '';
        graph.appendChild(svg);
    }).catch(
        error => console.error("Error rendering Graphviz:", error)
    );
}

function saveSvgAsImage() {
    var svg = document.querySelector('svg');
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

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("saveImage").addEventListener("click", saveSvgAsImage);
});
