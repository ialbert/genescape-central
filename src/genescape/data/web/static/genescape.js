
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
        var side = document.getElementById('sideBar');
        var main = document.getElementById('mainBar');

        if (side.classList.contains('col-sm-3')) {
            side.classList.remove('col-sm-3');
            side.classList.add('col-sm-1');
            main.classList.remove('col-sm-9');
            main.classList.add('col-sm-11');
        } else {
            side.classList.remove('col-sm-1');
            side.classList.add('col-sm-3');
            main.classList.remove('col-sm-11');
            main.classList.add('col-sm-9');
        }
    }
});

function submit(elemId, buttonId, eventName) {
    const element = document.getElementById(elemId);
    if (!element) return; // Exit if element does not exist

    element.addEventListener(eventName, function(e) {
        if (eventName === 'keydown' && e.key !== 'Enter') return;
        e.preventDefault();
        document.getElementById(buttonId).click();
    });
}

document.addEventListener('DOMContentLoaded', (event) => {
    submit('pattern', 'drawTree', 'keydown')
    submit('count', 'drawTree', 'keydown')
    submit('root', 'drawTree', 'change')
});

function resize_container(svg){

	var svg = document.getElementById('svgtree')

	var h = svg.getBoundingClientRect().height;
	var w = svg.getBoundingClientRect().width;

	var cn = document.getElementById('graphContainer');

	cn.style.height = h + 'px';
	cn.style.width  = w + 'px';

	//console.log('cn:', cn.style.height, cn.style.width);
}

function render_graph(content) {
	graph = document.getElementById('graph')
	contr = document.getElementById('graphContainer')
    Viz.instance().then(function(viz) {
        var svg = viz.renderSVGElement(content);
        svg.setAttribute("id", "svgtree");
        //svg.setAttribute("width", "100%");
        //svg.setAttribute("height", "1200px");
        graph.innerHTML = '';
        graph.appendChild(svg);

        resize_container();

    }).catch(
        error => console.error("Error rendering Graphviz:", error)
    );

}

var zoomLevel = 1; // Initial zoom level

// Function to adjust SVG zoom based on action
function adjustSVGZoom(zoomAction) {
    var svg = document.querySelector('#graph svg');
    if (!svg) return;

	//console.log('Adjusting SVG zoom:', zoomAction);

    // Adjust zoom level based on the action
    if (zoomAction === 'zoom-in') {
        zoomLevel *= 1.2; // Zoom in by 10%
    } else if (zoomAction === 'zoom-out') {
        zoomLevel /= 1.2; // Zoom out by 10%
    } else {
        consol.log("invalid zoom level")
    }

    // Apply new zoom level to the SVG
    svg.style.transform = `scale(${zoomLevel})`;
    svg.style.transformOrigin = 'top left';

	resize_container();

    //var height = svg.getBoundingClientRect().height;
    //var width = svg.getBoundingClientRect().width;

	//var contr = document.getElementById('graphContainer');

	//contr.style.height = 1.01 * height + 'px';
	//contr.style.width = 1.01 * width + 'px';

	//console.log('height:', height);
	//console.log('width:', width);

}

// Bind click events to buttons
document.querySelectorAll('button[data-action]').forEach(button => {
    button.addEventListener('click', function() {
        var action = this.getAttribute('data-action');
        adjustSVGZoom(action);
    });
});

function uploadFile() {
  var input = document.getElementById('file-input');
  if (input.files.length > 0) {
    var file = input.files[0];
    var formData = new FormData();
    formData.append('file', file);
	fetch('/upload/', {
	      method: 'POST',
	      body: formData,
	    })
	    .then(response => {
	      if (response.ok) {
	        return response.text();
	      }
	      throw new Error('Network response was not ok.');
	    })
	    .then(data => {
	      var input = document.getElementById('input');
	      input.value = data;
	    })
	    .catch(error => {
	      console.error('There has been a problem with your fetch operation:', error);
	    });
	  }
}

console.log('Genescape javascript loaded OK');
