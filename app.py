import os
import subprocess
from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Cartelle temporanee
UPLOAD_FOLDER = '/tmp/zant_uploads'
OUTPUT_FOLDER = '/tmp/zant_outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Percorso della repo di Zant sul server
ZANT_REPO_PATH = "/var/www/Z-Ant"

@app.route('/')
def home():
    # Flask cercherà "index.html" dentro la cartella "templates"
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    # 1. Validazione File
    if 'model_file' not in request.files:
        return "Nessun file caricato", 400
    
    file = request.files['model_file']
    if file.filename == '':
        return "Nome file non valido", 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    # 2. Leggi i parametri dal Javascript
    target_arch = request.form.get('architecture', 'x86_64')
    target_cpu = request.form.get('cpu', 'generic')
    
    # Nome file output
    output_lib_name = "lib" + filename.replace('.onnx', '.a')
    output_path = os.path.join(OUTPUT_FOLDER, output_lib_name)

    # 3. Costruzione Comando Zant
    # Esempio comando: zig build-lib modello.onnx -target ... -mcpu ...
    
    command = [
        "zig", 
        "build-lib", 
        input_path, 
        f"-femit-bin={output_path}",
        "-target", f"{target_arch}-linux", # Assumiamo linux per ora, puoi renderlo dinamico
        f"-mcpu={target_cpu}"
    ]

    print(f"Eseguendo comando: {' '.join(command)}") # Log per debug

    try:
        # Eseguiamo il comando dentro la cartella di Zant
        result = subprocess.run(
            command, 
            cwd=ZANT_REPO_PATH, 
            capture_output=True, 
            text=True
        )

        if result.returncode != 0:
            return f"Errore Zig:\n{result.stderr}", 500
        
        # 4. Invia il file
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Errore Server: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)