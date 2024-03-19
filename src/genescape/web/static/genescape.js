
// General error handler for HTMX events.
function handleHTMXError(event) {
    var err_msg = event.type + ': ' + (event.detail.errorMessage || 'server error')

	// Show the error message in the console.
	console.log(err_msg);

	// Select the error layout elements.
    var err_bar = document.getElementById('error-bar');
	var err_div = document.getElementById('error-div');

  	err_bar.style.display = 'block';

    err_div.textContent = err_msg;
    err_div.style.display = 'block';

    // Hide the error message after a few seconds.
    setTimeout(function() {
        err_bar.style.display = 'none';
        err_div.style.display = 'none';
    }, 3000);

}

// Add event listeners for HTMX events.
document.body.addEventListener('htmx:sendError', handleHTMXError);
document.body.addEventListener('htmx:responseError', handleHTMXError);

// Add event listener for the `data-toggle-width` attribute.
document.addEventListener('click', function(e) {
    if (e.target && e.target.dataset.toggleWidth === 'true') {
        var leftDiv = document.getElementById('sideBar');
        var rightDiv = document.getElementById('mainBar');
        if (leftDiv.classList.contains('col-sm-3')) {
            leftDiv.classList.remove('col-sm-3');
            leftDiv.classList.add('col-sm-0');
            rightDiv.classList.remove('col-sm-9');
            rightDiv.classList.add('col-sm-12');
        } else {
            leftDiv.classList.remove('col-sm-0');
            leftDiv.classList.add('col-sm-3');
            rightDiv.classList.remove('col-sm-12');
            rightDiv.classList.add('col-sm-9');
        }
    }
});

function resize_container(svg){
	var height = svg.getBoundingClientRect().height;
	var contr = document.getElementById('graphContainer');
	contr.style.height = height + 'px';

	console.log('height:', height);
}

function render_graph(content) {
	graph = document.getElementById('graph')
	contr = document.getElementById('graphContainer')
    Viz.instance().then(function(viz) {
        var svg = viz.renderSVGElement(content);
        //svg.setAttribute("width", "100%");
        //svg.setAttribute("height", "1200px");
        graph.innerHTML = '';
        graph.appendChild(svg);

        resize_container(svg);


    }).catch(
        error => console.error("Error rendering Graphviz:", error)
    );

}

var zoomLevel = 1; // Initial zoom level

// Function to adjust SVG zoom based on action
function adjustSVGZoom(zoomAction) {
    var svg = document.querySelector('#graph svg');
    if (!svg) return;

	console.log('Adjusting SVG zoom:', zoomAction);

    // Adjust zoom level based on the action
    if (zoomAction === 'zoom-in') {
        zoomLevel *= 1.1; // Zoom in by 10%
    } else if (zoomAction === 'zoom-out') {
        zoomLevel /= 1.1; // Zoom out by 10%
    } else {
        consol.log("invalid zoom level")
    }

    // Apply new zoom level to the SVG
    svg.style.transform = `scale(${zoomLevel})`;
    svg.style.transformOrigin = 'top left';

    var height = svg.getBoundingClientRect().height;

}

// Bind click events to buttons
document.querySelectorAll('button[data-action]').forEach(button => {
    button.addEventListener('click', function() {
        var action = this.getAttribute('data-action');
        adjustSVGZoom(action);
    });
});


console.log('Genescape javascript loaded OK');
