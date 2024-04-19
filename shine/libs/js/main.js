function render_graph() {

	dot = document.getElementById('dot_elem').textContent;
	graph = document.getElementById('graph_elem')

    Viz.instance().then(function(viz) {
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
