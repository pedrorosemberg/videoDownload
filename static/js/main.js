document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('downloadForm');
    const progressContainer = document.getElementById('progressContainer');
    const downloadComplete = document.getElementById('downloadComplete');
    const errorAlert = document.getElementById('errorAlert');
    const downloadBtn = document.getElementById('downloadBtn');
    const progressBar = document.querySelector('.progress-bar');
    const statusText = document.getElementById('statusText');
    const downloadFileBtn = document.getElementById('downloadFileBtn');
    const newDownloadBtn = document.getElementById('newDownloadBtn');
    let currentFilePath = null;

    function showError(message) {
        errorAlert.textContent = message;
        errorAlert.classList.remove('d-none');
        progressContainer.classList.add('d-none');
        downloadBtn.disabled = false;
    }

    function resetForm() {
        form.reset();
        progressContainer.classList.add('d-none');
        downloadComplete.classList.add('d-none');
        errorAlert.classList.add('d-none');
        downloadBtn.disabled = false;
        progressBar.style.width = '0%';
        progressBar.textContent = '0%';
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const url = document.getElementById('url').value;
        const format = document.querySelector('input[name="format"]:checked').value;
        
        errorAlert.classList.add('d-none');
        downloadBtn.disabled = true;
        progressContainer.classList.remove('d-none');
        downloadComplete.classList.add('d-none');
        
        // Simulate progress while waiting for download
        let progress = 0;
        const progressInterval = setInterval(() => {
            if (progress < 90) {
                progress += 5;
                progressBar.style.width = `${progress}%`;
                progressBar.textContent = `${progress}%`;
            }
        }, 500);

        try {
            const formData = new FormData();
            formData.append('url', url);
            formData.append('format', format);
            
            const response = await fetch('/download', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            clearInterval(progressInterval);
            
            if (response.ok) {
                progressBar.style.width = '100%';
                progressBar.textContent = '100%';
                currentFilePath = data.file_path;
                downloadComplete.classList.remove('d-none');
                progressContainer.classList.add('d-none');
            } else {
                throw new Error(data.error || 'Erro ao fazer download');
            }
            
        } catch (error) {
            clearInterval(progressInterval);
            showError(error.message);
        }
    });

    downloadFileBtn.addEventListener('click', function() {
        if (currentFilePath) {
            window.location.href = `/get-file/${currentFilePath}`;
        }
    });

    newDownloadBtn.addEventListener('click', resetForm);
});
