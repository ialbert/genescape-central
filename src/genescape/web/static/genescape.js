
document.body.addEventListener('htmx:responseError', function(event) {
    const { xhr, target } = event.detail;

	if (target.id === 'target') {
	    // Display the error message
	    document.getElementById('error').innerText = `Error ${xhr.status}: ${xhr.statusText}`;
    }

});
