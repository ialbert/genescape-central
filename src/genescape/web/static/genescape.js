
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

console.log('Genescape javascaript loaded OK');
