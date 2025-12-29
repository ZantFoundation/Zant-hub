document.addEventListener('DOMContentLoaded', () => {
    
    // --- NAVIGATION HANDLING ---
    const startButton = document.getElementById('startButton');
    const welcomePage = document.getElementById('welcomePage');
    const selectModelPage = document.getElementById('selectModelPage');
    const deploymentPage = document.getElementById('deploymentPage');
    const backButtons = document.querySelectorAll('.backButton');
    
    // Variable to store the selected file
    let selectedFile = null;

    // Go to the selection page
    startButton.addEventListener('click', () => {
        welcomePage.classList.add('hiddenPage');
        welcomePage.classList.remove('activePage');
        selectModelPage.classList.remove('hiddenPage');
        selectModelPage.classList.add('activePage');
    });

    // File Upload Handling (Click and Drag & Drop)
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');

    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    function handleFileSelection(file) {
        selectedFile = file;
        // Switch page to Deployment
        selectModelPage.classList.add('hiddenPage');
        selectModelPage.classList.remove('activePage');
        deploymentPage.classList.remove('hiddenPage');
        deploymentPage.classList.add('activePage');
        
        // Update title
        document.getElementById('modelNameTitle').innerText = file.name;
    }

    // Back Button
    backButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Simple logic: always return to Home or reload for now
            location.reload(); 
        });
    });

    // --- LIBRARY GENERATION HANDLING ---
    const generateBtn = document.getElementById('generateLibBtn');
    const downloadBtn = document.getElementById('downloadLibBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');

    generateBtn.addEventListener('click', async () => {
        if (!selectedFile) {
            alert("No file selected!");
            return;
        }

        const arch = document.getElementById('architectureInput').value || "x86_64"; // Default
        const cpu = document.getElementById('cpuInput').value || "generic"; // Default

        // Show loading indicator
        loadingOverlay.classList.remove('hiddenPage');

        // Prepare data for Python
        const formData = new FormData();
        formData.append('model_file', selectedFile);
        formData.append('architecture', arch);
        formData.append('cpu', cpu);

        try {
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorMsg = await response.text();
                throw new Error(errorMsg);
            }

            // If everything is OK, we receive a file (Blob)
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            
            // Enable the download button
            downloadBtn.disabled = false;
            downloadBtn.style.opacity = "1";
            downloadBtn.onclick = () => {
                const a = document.createElement('a');
                a.href = url;
                // Downloaded file name
                a.download = selectedFile.name.replace('.onnx', '.a');
                document.body.appendChild(a);
                a.click();
                a.remove();
            };

            alert("Successfully code-generated static library! Click on 'Download Static Library'.");

        } catch (error) {
            alert("Error: " + error.message);
        } finally {
            loadingOverlay.classList.add('hiddenPage');
        }
    });
});
