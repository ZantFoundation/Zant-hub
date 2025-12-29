import os
import subprocess
from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Cartelle temporanee
UPLOAD_FOLDER = '/tmp/zant_uploads'
OUTPUT_FOLDER = '/tmp/zant_outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Rileva automaticamente dove siamo
if os.path.exists("/var/www/Z-Ant"):
    # Siamo sul Server Vultr
    ZANT_REPO_PATH = "/var/www/Z-Ant"
else:
    # Siamo sul tuo PC Locale (Modifica questo percorso con la tua cartella locale di Z-Ant!)
    # Esempio: "/home/mirko/Documents/zig/Tiny/Z-Ant"
    ZANT_REPO_PATH = os.getenv('ZANT_REPO_PATH') 

@app.route('/')
def home():
    # Flask will search for index.html in folder "templates"
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    # 1. File Validation
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
    output_lib_name = "lib_zant.a"
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