import os
import subprocess
from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)

ROOT_PATH = os.getenv('ZANT_REPO_PATH') # <-- check .env file, remember to modify server side also
ZANT_REPO_PATH = ROOT_PATH + "/Z-Ant"

@app.route('/')
def home():
    # Flask will search for index.html in folder "templates"
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():

    # 1. File presence
    if 'model_file' not in request.files:
        return "No file uploaded", 400

    file = request.files['model_file']

    # 2. Raw filename sanity
    if not file.filename:
        return "Invalid filename", 400

    # 3. Sanitize filename
    filename = secure_filename(file.filename)

    # secure_filename can return empty string
    if not filename:
        return "Unsafe filename", 400

    # 4. Enforce extension
    if not filename.lower().endswith('.onnx'):
        return "Only .onnx files are allowed", 400

    # OPTIONAL: enforce max length
    if len(filename) > 255:
        return "Filename too long", 400
    
    # temp folders 
    UPLOAD_FOLDER = ZANT_REPO_PATH + "/datasets/models/" + filename
    OUTPUT_FOLDER = ZANT_REPO_PATH + "/datasets/models/" + filename

    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    # 2. Leggi i parametri dal Javascript
    target_arch = request.form.get('architecture', 'x86_64')
    target_cpu = request.form.get('cpu', 'generic')
    
    # Nome file output
    output_lib_name = "lib_zant.a"
    output_path = os.path.join(OUTPUT_FOLDER, output_lib_name)

    # 3. Costruzione Comando Zant

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

def create_zant_CLI_string(request) :
    """
    Zant Flags nowdays available:
    
    """


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


