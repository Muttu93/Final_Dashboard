// Show confirmation on Delete
function confirmDelete(event, file) {
    if (!confirm(`Are you sure you want to delete ${file}?`)) {
        event.preventDefault();
    }
}

// Show confirmation on Edit Save
function confirmEditSave() {
    return confirm("Are you sure you want to save these changes?");
}

// Flash messages auto-hide
window.onload = function() {
    const flashes = document.querySelectorAll('.flashes li');
    if (flashes.length > 0) {
        setTimeout(() => {
            flashes.forEach(flash => flash.style.display = 'none');
        }, 3000); // hide after 3 seconds
    }
}
