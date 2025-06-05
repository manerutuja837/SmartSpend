document.getElementById('open-popup').addEventListener('click', function(event) {
    event.preventDefault();  // Prevent the default behavior
    document.getElementById('popup').style.display = 'flex';  // Show the popup
});

// Close the popup when the close button is clicked
document.getElementById('close-popup').addEventListener('click', function() {
    document.getElementById('popup').style.display = 'none';  // Hide the popup
});