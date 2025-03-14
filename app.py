import os
import json
import atexit
import signal
import random
import importlib
import platform
import tempfile
from flask_cors import CORS
from threading import Thread
from cryptography.fernet import Fernet
from platformdirs import user_documents_path
from _backend.features.AI.Whisper.main import WhisperSTT
from _backend.features.chrome_driver.chrome_driver import *
from _backend.features.chrome_driver.main import *
from _backend.features.AI.ollama_model.ollama_ import OllamaManager
from werkzeug.exceptions import RequestEntityTooLarge
from flask import Flask, jsonify, request, render_template, send_file, url_for, Response


SECRET_KEY = None
if os.path.exists(os.path.join(os.getcwd(), "secret.key")):
    with open("secret.key", "rb") as key_file: SECRET_KEY = key_file.read().strip()
else:
    SECRET_KEY = Fernet.generate_key()
    with open("secret.key", "wb") as key_file: key_file.write(SECRET_KEY)



app = Flask(__name__)
MAX_CONTENT_LENGTH = 100  # 100MB
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH * 1024 * 1024
os.environ["PYTHONIOENCODING"]   = "utf-8"
cipher = Fernet(SECRET_KEY)
CORS(app)

OPERATING_SYSTEM = platform.system()
clear_screen = lambda: os.system("cls" if platform.system()=="Windows" else "clear")
clear_screen()


chrome_process = start_chrome_driver()

LOADED_FEATURES = {}
OLLAMA_MANAGER = OllamaManager()

BACKEND =  os.path.join(os.getcwd(), "_backend")
ASSESTS_DIR = os.path.join(BACKEND, "assets")
DATABASE = os.path.join(BACKEND, "DB")
IMAGES_DIR = os.path.join(ASSESTS_DIR, "images")
DATABASE_FILES = os.path.join(DATABASE, "files")
DATABASE_FILE_JSON = os.path.join(DATABASE, 'file.json')
FEATURES_CONFIG = os.path.join(BACKEND, 'features_config.json')
CONNECTED_SERVERS = os.path.join(BACKEND, "connected_servers.json")
FILES_DIR = os.path.join(str(user_documents_path()), "AUTO_SOCAIL_FILES")

if not os.path.exists(DATABASE): os.makedirs(DATABASE)
if not os.path.exists(DATABASE_FILES): os.makedirs(DATABASE_FILES)
if not os.path.exists(IMAGES_DIR): os.makedirs(IMAGES_DIR)
if not os.path.exists(FILES_DIR): os.makedirs(FILES_DIR)

if not os.path.exists(CONNECTED_SERVERS):
    with open(CONNECTED_SERVERS, 'w') as f: f.write(json.dumps([]))

if not os.path.exists(DATABASE_FILE_JSON): 
    with open(DATABASE_FILE_JSON, 'w') as f: f.write(json.dumps({}))



DYNAMIC_OBJ_PARAMETERS = {
    "API_ENDPOINTS": {
        'generate_download_link': "http://127.0.0.1:8081/generate_download_link",
        'WHISPER_URL': "http://127.0.0.1:8081/whisper-transcribe",
        "CHROME_DRIVER": {
            "chrome_driver_remove_task" : driver_delete_task
        }
    }
}

# FILES MANAGEMENT
FILES_DATABASE = {}

def initiate_file_db():
    data = read_files()
    if data:
        for id, loc in data.items(): os.remove(loc)
    with open(DATABASE_FILE_JSON, 'w') as f: f.write(json.dumps({}))

def add_file(id, filePath):
    files = read_files()
    files[id] = filePath
    with open(DATABASE_FILE_JSON, 'w') as f: json.dump(files, f)

def read_files():
    try:
        with open(DATABASE_FILE_JSON, 'r') as f: return json.load(f)
    except FileNotFoundError: return {}
     
def get_file(id):
    files = read_files()
    path = files.get(id)
    if path and os.path.exists(path): return path
    return None

# Dynamically import feature classes
with open(f"{FEATURES_CONFIG}", "r") as f: config = json.load(f)
for feature_name, feature_data in config["features"].items():
    module_path = feature_data["module"]
    class_name = feature_data["class"]
    # try:
    module = importlib.import_module(module_path)
    LOADED_FEATURES[feature_name] = {"class" : getattr(module, class_name), "instance": None}  # Store class reference
    LOADED_FEATURES[feature_name]['instance'] = LOADED_FEATURES[feature_name]['class'](**DYNAMIC_OBJ_PARAMETERS)
    if hasattr(LOADED_FEATURES[feature_name]['instance'], "installation"):
        getattr(LOADED_FEATURES[feature_name]['instance'], "installation")()

    print(f"Loaded: {feature_name} -> Class: {class_name}")
    # except (ModuleNotFoundError, AttributeError) as e:
    #     print(f"Error loading {feature_name}: {e}")




@app.route('/whisper-transcribe', methods=['POST'])
def transcribe_audio():

    if 'file' not in request.files: return jsonify({"error": "No file uploaded"}), 400
    
    audio_file = request.files['file']
    model_size = request.form.get("model", "base")
    
    temp_audio_path = f"temp_{audio_file.filename}"
    audio_file.save(temp_audio_path)
    try:
        stt = WhisperSTT(model_size=model_size)
        text = stt.transcribe(temp_audio_path)
        os.remove(temp_audio_path)
        return jsonify({ "status": "success", "error": "", "data": {'response': text}})
    except Exception as e:
        os.remove(temp_audio_path)
        return jsonify({"status": "success", "error": str(e), "data": {'response': ''}}), 500



@app.errorhandler(RequestEntityTooLarge)
def handle_file_size_error(e):
    return jsonify({ "status": "error", "error": f"File size exceeds the limit of {MAX_CONTENT_LENGTH}MB", "data": {'response': ''}}), 413


@app.route("/upload-file", methods=["POST"]) 
def upload_file():
    if "file" not in request.files:
        return jsonify({ "status": "error", "error": "No File Found", "data": {'response': ''}}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({ "status": "error", "error": "No Selected File", "data": {'response': ''}}), 400

    file_path = os.path.join(DATABASE_FILES, file.filename)
    file.save(file_path)

    file_id = str(random.randint(111111, 9999999))
    add_file(file_id, file_path)

    return jsonify({ "status": "success", "error": "", "data": {'response': str(file_id)}}), 200






@app.route("/get-features", methods=["GET"])
def get_features():

    with open(f"{FEATURES_CONFIG}", "r") as f: 
        features = json.load(f)
        
    for key, feature in features["features"].items():
        module_name = feature["module"]
        class_name = feature["class"]
        feature['icon'] = os.path.join(IMAGES_DIR, feature['icon'])
        module = importlib.import_module(module_name)

        if LOADED_FEATURES.get(key):
            cls = LOADED_FEATURES[key]['class']
            instance = LOADED_FEATURES[key]['instance']
            if not instance: instance = LOADED_FEATURES[key]['instance'] = cls()

            for meth_key, meth_data in feature['methods'].items():
                meth_args = meth_data.get('args')
                meth_kargs = meth_data.get('kwargs')
                
                for arg_key, arg_func in meth_args.items():
                    if isinstance(arg_func, str) and hasattr(instance, arg_func): meth_args[arg_key] = getattr(instance, arg_func)()
                    feature['methods'].get(meth_key)['args'] = meth_args

                for karg_key, karg_func in meth_kargs.items():
                    if isinstance(karg_func, str) and hasattr(instance, karg_func): meth_kargs[karg_key] = getattr(instance, karg_func)()
                    feature['methods'].get(meth_key)['kwargs'] = meth_kargs

    return Response(json.dumps(features, indent=4), mimetype="application/json", status=200)




@app.route("/get-running-tasks", methods=["GET"])
def get_running_tasks():

    running_tasks = []
    feature = LOADED_FEATURES.get(feature_name)

    for featureName, FeatureData in LOADED_FEATURES.items():
        clas = FeatureData['class']
        inst = FeatureData['instance']
        if inst:
            if hasattr(inst, 'running_tasks'):
                running_tasks.append({featureName: getattr(inst, "running_tasks")()})
    
    return jsonify({ "status": "success", "error": "", "data": {'tasks': running_tasks}}), 200




@app.route("/run-feature", methods=["POST"])
def run_feature():

    data = json.loads(request.data.decode("utf-8"))
    feature_name = data.get("feature_name")
    func_name = data.get("func_name")
    args = data.get("args")
    files = data.get("uploads", {})

    try:
        kwargs = { **args.get("args", {}), **args.get("kwargs") }

        if files:
            for key, file_id in files.items():
                if key in kwargs: kwargs[key] = get_file(file_id)

        feature = LOADED_FEATURES.get(feature_name)

        if not feature: 
            print("Feature Not Found!", feature)
            return jsonify({ "status": "failed", "error": "Feature Not Found!", "data": { }}), 400

        if not feature['instance']:
            if feature['class']:
                feature = LOADED_FEATURES[feature_name] = { "class": feature['class'], "instance": feature['class']() }

        if not hasattr(feature['instance'], func_name):
            print("Requested Func Not Found!", func_name)
            return jsonify({ "status": "failed", "error": "Requested Feature Not Found!", "data": { }}), 400
        
        response = getattr(feature['instance'], func_name)(**kwargs)
        if type(response) == tuple: 
            if response[1] == 404 or not response[1]:
                return jsonify({ "status": "success", "error": response[0], "data": {'response': None}}), 400
            
        return jsonify({ "status": "success", "error": "", "data": {'response': response}}), 200
    
    except Exception as e:
        return jsonify({ "status": "failed", "error": str(e), "data": {'response': ""}}), 400





@app.route("/run-feature-operation", methods=["POST"])
def get_feature_operations():

    data = request.get_json()
    feature_name = data.get("feature")
    func_name = data.get("func_name")
    kwargs = data.get("kwargs")
    feature = LOADED_FEATURES.get(feature_name)

    if not feature: 
        print("Feature Not Found!", feature)
        return jsonify({ "status": "failed", "error": "Feature Not Found!", "data": { }}), 400

    if not feature['instance']:
        if feature['class']:
            feature = LOADED_FEATURES[feature_name] = { "class": feature['class'], "instance": feature['class']() }

    if not hasattr(feature['instance'], func_name):
        print("Requested Func Not Found!", func_name)
        return jsonify({ "status": "failed", "error": "Requested Feature Not Found!", "data": { }}), 400
    
    response = getattr(feature['instance'], func_name)(**kwargs)
    return jsonify({ "status": "success", "error": "", "data": {'response': response, "task_id": response}}), 200








@app.route("/get-servers", methods=["POST"])
def get_connected_servers():

    try:
        with open(CONNECTED_SERVERS, "r") as f: 
            servers = json.load(f)

        return jsonify({ "status": "success", "error": "", "data": {'response': servers}}), 200
    
    except Exception as e:
        return jsonify({ "status": "failed", "error": str(e), "data": {'response': ""}}), 400








def encrypt_file_path(file_path):
    """Encrypt the file path."""
    return cipher.encrypt(file_path.encode()).decode()


def decrypt_file_path(token):
    """Decrypt the token back to file path."""
    try: return cipher.decrypt(token.encode()).decode()
    except: return None


@app.route('/generate_download_link', methods=['POST'])
def generate_download_link():

    data = request.get_json()
    if not data or "file_path" not in data:
        return jsonify({"error": "Missing 'file_path' in request"}), 400

    file_path = data["file_path"]
    if request.remote_addr != "127.0.0.1":
        return jsonify({"error": "Unauthorized access"}), 403

    if not os.path.exists(file_path):
        print("File not found:", file_path)
        return jsonify({"download_file": "https://drive.google.com/drive/file/fileNotFound"}), 404

    encrypted_token = encrypt_file_path(file_path)
    download_url = url_for('download_file', token=encrypted_token, _external=True)
    return jsonify({"download_link": download_url})


@app.route('/download', methods=['GET'])
def download_file():

    token = request.args.get('token')
    if not token: return jsonify({"status": "failed", "error": "Missing 'token' in request"}), 400

    file_path = decrypt_file_path(token)
    if not file_path or not os.path.exists(file_path) or not os.path.isfile(file_path):
        return jsonify({"status": "failed", "error": "File not found"}), 404

    return send_file(file_path, as_attachment=True)




# Register cleanup function to run on exit
# Handle signals like SIGINT (CTRL+C) and SIGTERM (termination)
import gc 

def cleanup():
    print("Cleaning up resources before exit...")
    initiate_file_db()
    shutil.rmtree(DATABASE_FILES, ignore_errors=True)  # Deletes folder & contents
    for key, feature in LOADED_FEATURES.items():
        instance = LOADED_FEATURES[key].get('instance')
        if not instance: continue
        try:
            if hasattr(instance, "clear_resources"): getattr(instance, "clear_resources")()
            gc.get_referrers(instance)
            del instance
        except Exception as e:
            print(f"Error loading {feature_name}: {e}")


atexit.register(cleanup)
interrupt_limit = 0
def handle_signal(signal_received, frame):
    print(f"Received signal {signal_received}, shutting down gracefully...")
    cleanup()
    global interrupt_limit
    if interrupt_limit >= 2:
        try:
            close_chrome_driver()
            chrome_process.terminate()
        except: pass
        exit(0)
    else: interrupt_limit += 1

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


@app.route('/close-main-app', methods=['POST'])
def close_main_app():
    try:
        cleanup()
        try:
            close_chrome_driver()
            chrome_process.terminate()
        except: pass
    except Exception as e: print(e)
    os._exit(0)

    



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, debug=True, use_reloader=True)