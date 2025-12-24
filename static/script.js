document.addEventListener('DOMContentLoaded', () => {
    
    // --- GESTIONE NAVIGAZIONE ---
    const startButton = document.getElementById('startButton');
    const welcomePage = document.getElementById('welcomePage');
    const selectModelPage = document.getElementById('selectModelPage');
    const deploymentPage = document.getElementById('deploymentPage');
    const backButtons = document.querySelectorAll('.backButton');
    
    // Variabile per salvare il file selezionato
    let selectedFile = null;

    // Vai alla pagina di selezione
    startButton.addEventListener('click', () => {
        welcomePage.classList.add('hiddenPage');
        welcomePage.classList.remove('activePage');
        selectModelPage.classList.remove('hiddenPage');
        selectModelPage.classList.add('activePage');
    });

    // Gestione Upload File (Click e Drag & Drop)
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
        // Cambia pagina verso Deployment
        selectModelPage.classList.add('hiddenPage');
        selectModelPage.classList.remove('activePage');
        deploymentPage.classList.remove('hiddenPage');
        deploymentPage.classList.add('activePage');
        
        // Aggiorna titolo
        document.getElementById('modelNameTitle').innerText = file.name;
    }

    // Tasto Indietro
    backButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Logica semplice: torna sempre alla Home o ricarica per ora
            location.reload(); 
        });
    });


    // --- GESTIONE GENERAZIONE LIBRERIA ---
    const generateBtn = document.getElementById('generateLibBtn');
    const downloadBtn = document.getElementById('downloadLibBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');

    generateBtn.addEventListener('click', async () => {
        if (!selectedFile) {
            alert("Nessun file selezionato!");
            return;
        }

        const arch = document.getElementById('architectureInput').value || "x86_64"; // Default
        const cpu = document.getElementById('cpuInput').value || "generic"; // Default

        // Mostra caricamento
        loadingOverlay.classList.remove('hiddenPage');

        // Prepara i dati per Python
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

            // Se tutto va bene, riceviamo un file (Blob)
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            
            // Attiva il bottone di download
            downloadBtn.disabled = false;
            downloadBtn.style.opacity = "1";
            downloadBtn.onclick = () => {
                const a = document.createElement('a');
                a.href = url;
                // Nome del file scaricato
                a.download = selectedFile.name.replace('.onnx', '.a');
                document.body.appendChild(a);
                a.click();
                a.remove();
            };

            alert("Libreria generata con successo! Clicca su 'Download Static Library'.");

        } catch (error) {
            alert("Errore: " + error.message);
        } finally {
            loadingOverlay.classList.add('hiddenPage');
        }
    });
});