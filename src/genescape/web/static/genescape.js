
document.body.addEventListener('htmx:onError', function(event) {
    var errorMessageDiv = document.getElementById('error');
    errorMessageDiv.style.display = 'block';
    errorMessageDiv.textContent = 'An error occurred: ' + (event.detail.errorMessage || 'Unknown error');
});
