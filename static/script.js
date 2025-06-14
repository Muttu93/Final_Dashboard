function uploadFile(section) {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('section', section);

    fetch('/upload', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(data => alert(data.message))
    .then(() => window.location.reload());
}

function deleteFile(section, filename) {
    if (!confirm('Are you sure to delete this file?')) return;

    fetch(`/delete/${section}/${filename}`, { method: 'POST' })
    .then(res => res.json())
    .then(data => alert(data.message))
    .then(() => window.location.reload());
}

function editFile(section, filename) {
    fetch(`/edit/${section}/${filename}`)
    .then(res => res.json())
    .then(data => {
        const content = prompt("Edit file content:", data.content);
        if (content !== null) {
            if (!confirm("Are you sure to save these changes?")) return;
            fetch(`/edit/${section}/${filename}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `content=${encodeURIComponent(content)}`
            }).then(res => res.json())
              .then(data => alert(data.message));
        }
    });
}

function searchFiles() {
    let input = document.getElementById('search').value.toLowerCase();
    let cards = document.getElementsByClassName('file-card');
    for (let card of cards) {
        let txt = card.innerText.toLowerCase();
        card.style.display = txt.includes(input) ? 'block' : 'none';
    }
}
