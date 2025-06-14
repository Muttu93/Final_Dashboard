function confirmDelete(event, file) {
    if (!confirm(`Are you sure you want to delete "${file}"?`)) {
        event.preventDefault();
    }
}

function confirmEditSave() {
    return confirm("Are you sure you want to save changes?");
}

window.onload = function() {
    const flashes = document.querySelectorAll('.flashes li');
    if (flashes.length > 0) {
        setTimeout(() => flashes.forEach(f => f.style.display = 'none'), 3000);
    }
}
