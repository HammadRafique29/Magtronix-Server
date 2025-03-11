import os, shutil, docker
import importlib



file_path = os.path.dirname(os.path.abspath(__file__))

LOADED_FEATURES = {}

modules = {
    { "OllamaManager": os.path.join(file_path, "AI", "ollama_model", "ollama_" ) },
    { "OpenWebUIManager": os.path.join(file_path, "AI", "ollama_model", "ollama_" ) },
    { "TEXT_TO_SPEECH": os.path.join(file_path, "AI", "TTS", "main" )}
}


for class_name, file_path in modules.items():
    module = importlib.import_module(file_path)
    LOADED_FEATURES[class_name] = {"class" : getattr(module, class_name), "instance": None}  # Store class reference
    LOADED_FEATURES[class_name]['instance'] = LOADED_FEATURES[class_name]['class']()
    print(f"Loaded: {class_name} -> Class: {class_name} from {file_path}")



class first_time_setup():
    
    def __init__(self):
        pass


    def installation_and_setup():
        pass



    def install_docker():
        pass


    def install_python_packages():
        pass


    def docker_images():
        pass


    def docker_images_models():
        pass


    def get_progress():
        pass