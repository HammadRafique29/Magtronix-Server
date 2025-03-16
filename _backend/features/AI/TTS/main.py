

import torch
import requests
# from TTS.api import TTS
import random
import os
import json
import queue
import pandas as pd
import gdown
import random
import time
import shutil
import docker
from threading import Thread, Event
from datetime import datetime
from platformdirs import user_documents_path
from unittest.mock import patch


# "Adam, Alice, Aria, Bill, George, Lilly, Reacheal, Sarah", "Alex", "Arabella", "Bill L. Oxley", "BRIAN.wav", "Brittney", 
# "Dramatic British.wav", "Heather Rey", "John Fernandes", "Laura", "Mark", "Matilda", "Roger", "Sally Ford", "SARAH", "Tim Rooney", 
# "Todd Thomas", "Tyrone", "Realistic_Male", "realistic_male_2", "F5TTS_Male"

# ['en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 'cs', 'ar', 'zh-cn', 'hu', 'ko', 'ja', 'hi']


TTS_DATABASE_PATH = os.path.join(str(user_documents_path()), "Magtronix", "TTS")
if not os.path.exists(TTS_DATABASE_PATH): os.makedirs(TTS_DATABASE_PATH)


class TEXT_TO_SPEECH:

    def __init__(self, API_ENDPOINTS={}) -> None:

        self.TTS_MODELS_PATH = os.path.join(str(user_documents_path()), "tts_models") 
        self.API_ENDPOINTS = API_ENDPOINTS
        self.request_queue = queue.Queue()
        self.LANGUAGES = {
            'en': {'value': 'English', 'index': 0}, 'es': {'value': 'Spanish', 'index': 1},
            'fr': {'value': 'French', 'index': 2}, 'de': {'value': 'German', 'index': 3},
            'it': {'value': 'Italian', 'index': 4}, 'pt': {'value': 'Portuguese', 'index': 5},
            'pl': {'value': 'Polish', 'index': 6}, 'tr': {'value': 'Turkish', 'index': 7},
            'ru': {'value': 'Russian', 'index': 8}, 'nl': {'value': 'Dutch', 'index': 9},
            'cs': {'value': 'Czech', 'index': 10}, 'ar': {'value': 'Arabic', 'index': 11},
            'zh-cn': {'value': 'Chinese (Simplified)', 'index': 12}, 'hu': {'value': 'Hungarian', 'index': 13},
            'ko': {'value': 'Korean', 'index': 14}, 'ja': {'value': 'Japanese', 'index': 15},
            'hi': {'value': 'Hindi', 'index': 16}
        }
        self.VOICES = {}
        self.RUNNING_CONTAINERS = {}
        self.temp_queue = {}
        self.load_voices()
        self.API_ENDPOINTS = API_ENDPOINTS
        Thread(target=self.process_queue, daemon=True).start()
        # with patch('builtins.input', return_value='y'):
        #     self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)


    def load_voices(self):
        try:
            current_file_path = os.path.dirname(os.path.abspath(__file__))
            with open(os.path.join(current_file_path, 'voices.json')) as f: self.VOICES = json.load(f)
            return self.VOICES
        except Exception as e: print(e)


    def clear_resources(self):
        print("#### Destructor: Text-To-Speech")
        for key, cont in self.RUNNING_CONTAINERS.items():
            print(" --Stoping: ", cont['tags'])
            if cont['container'] or cont['isRunning']:
                self.stop_container(cont['container'])

            self.RUNNING_CONTAINERS = {}


    def stop_container(self, container):
        try:
            container.stop()
            container.remove()
            print(f"Container {container.id} stopped and removed.")
        except Exception as e:
            print(f"Error stopping container: {e}")


    def delete_container_data(self, task_id):
        cont_data = self.RUNNING_CONTAINERS.get(task_id)
        if cont_data:
            if cont_data['container'] or cont_data['isRunning']:
                self.stop_container(cont_data['container'])
                for dirs in self.RUNNING_CONTAINERS[task_id]['files']:
                    local_path = dirs['local_path']
                    if os.path.isdir(local_path): shutil.rmtree(local_path)
                    else: os.remove(local_path) 
                self.RUNNING_CONTAINERS.pop(task_id)
        return ''
    

    def get_logs(self, task_id):
        logs = self.RUNNING_CONTAINERS.get(task_id, {}).get('logs', '')
        logs += "\n\nPROGRESS: " + str(self.RUNNING_CONTAINERS.get(task_id, {}).get('progress'))
        logs += "\nSTATUS: " + ("RUNNING" if self.RUNNING_CONTAINERS.get(task_id, {}).get('isRunning') else "STOPPED")
        return logs
    

    def get_files(self, task_id):
        files = self.RUNNING_CONTAINERS.get(task_id, {}).get('files', [])
        return [{"name": file["name"], "loc": file["loc"]} for file in files]



    def add_voice(self, voice_name, voice_drive_id):
        try:
            if not voice_name or not voice_drive_id: return "Voice name & voice drive id is required", 404 
            current_file_path = os.path.dirname(os.path.abspath(__file__))
            with open(os.path.join(current_file_path, 'voices.json'), 'r') as f: voices = json.load(f)
            voices[voice_name] = voice_drive_id
            with open(os.path.join(current_file_path, 'voices.json'), 'w') as f: json.dump(voices, f)
            self.VOICES = voices
            return f"Voice {voice_name} Added Successfully"
        except Exception as e: 
            raise Exception(f"Unknow error occured {e}")
        


    def running_tasks(self):
        running_tasks = []
        for key, task in self.RUNNING_CONTAINERS.items():
            if isinstance(task, dict):  
                filtered_task = {k: v for k, v in task.items() if isinstance(v, (str, int, float, bool, list, dict))}
                running_tasks.append(filtered_task)
        return running_tasks
    


    def process_queue(self):
        while True:
            try:
                event = self.request_queue.get(timeout=10)
                event.set()
            except queue.Empty: pass 


    def get_voice(self):
        return list(self.VOICES.keys())
    

    def get_languages(self):
        temp = []
        for key, val in self.LANGUAGES.items(): temp.append(f"{key} ({val['value']})")
        return temp


    def create_file_download_link(self, filePath):
        response = requests.post(self.API_ENDPOINTS['generate_download_link'], json={"file_path": filePath})
        if response.status_code == 200: return response.json().get("download_link")
        else: return "https://drive.google.com/drive/file/fileNotFound"


    def get_current_datetime(self):
        now = datetime.now()
        return f"{now.date().day}_{now.hour}_{now.minute}_{now.second}"
    

    def download_speaker(self, id, name, output_path):
        download_url = f'https://drive.google.com/uc?id={id}'
        output_file = f"{os.path.join(output_path, f'{name}.wav')}"
        gdown.download(download_url, output_file, quiet=False)
        time.sleep(2)


    def get_installed_models(self):
        # models = os.listdir(os.path.join(str(user_documents_path()), "tts_models"))
        models = ["tts_models--multilingual--multi-dataset--xtts_v2"]
        return [x.replace('--', '/') for x in models]


    def wait_for_task_done(self, func, **kwargs):

        req_event = Event()
        self.request_queue.put(req_event)
        req_event.wait(timeout=1)

        task_id = kwargs.get('task_id')
        while self.RUNNING_CONTAINERS[task_id].get("isRunning", True):  time.sleep(1)
        self.RUNNING_CONTAINERS[task_id]['isRunning'] = True

        try: task_id, file_path = func(**kwargs)
        except Exception as e: print(e)

        self.RUNNING_CONTAINERS[task_id]['isRunning'] = False
        file_download_link = self.create_file_download_link(file_path)

        if kwargs.get('isTest') or kwargs.get('task_id', "Unknow") == "default":
            self.RUNNING_CONTAINERS[task_id]['files'].append({
                "name": os.path.basename(file_path),
                "local_path": file_path,
                "loc":  file_download_link
            })
        self.temp_queue[task_id].put(file_download_link)

        

    def run_docker_container(self, image, project_dir, task_id=None):

        client = docker.from_env()
        task_id = image + "_" + str(random.randint(11111,99999)) if not task_id else task_id

        volumes = {
            project_dir          : {"bind": "/tts_output", "mode": "rw"},
            self.TTS_MODELS_PATH : {"bind": "/root/.local/share/tts", "mode": "rw"},
        }

        if torch.cuda.is_available():
            container = client.containers.run(
                image,
                tty=True,               # Keep it running  
                detach=True,            # Run it Background
                stdin_open=True,        # Allow interaction
                auto_remove=True,       # Auto Delete After Stoping
                volumes=volumes,        # Attach Volumes
                entrypoint="/bin/bash", # Keeps container interactive
                runtime="nvidia",       # Use NVIDIA runtime for GPU support
                environment={"NVIDIA_VISIBLE_DEVICES": "all"}  # Use all available GPUs
            )

        else:  
            container = client.containers.run(
                image,
                tty=True,               # Keep it running  
                detach=True,            # Run it Background
                stdin_open=True,        # Allow interaction
                auto_remove=True,       # Auto Delete After Stoping
                volumes=volumes,        # Attach Volumes
                entrypoint="/bin/bash", # Keeps container interactive
            )
        self.RUNNING_CONTAINERS[task_id] = {
            'task_id': task_id, 
            'feature': "TTS", 
            "task_type": f"TTS - Transcribe",
            "tags": f"Converting Text To Speech, {image}, tts_models--multilingual--multi-dataset--xtts_v2", 
            'container': container, 
            "progress": 0, 
            "logs": """""", 
            "isRunning": False, 
            "files": []
        }
        print(f"Container {container.id} is running...")
        return task_id, container



    def transcribe(self, message="Hi", speaker_name="SARAH", language="en", output_dir=None, model_name="tts_models--multilingual--multi-dataset--xtts_v2", image="ghcr.io/coqui-ai/tts", WORKIND_DIR=None, task_id=None, isTest=True):

        language = language.split(' ')
        language = language[0] if len(language)>0 else language

        if language not in self.LANGUAGES.keys():
            raise Exception("LANGUAGE NOT FOUND... PLEASE SELECT A VALID ONE")
        
        if not task_id:
            task_id, container = self.run_docker_container( image, WORKIND_DIR )

        output_file = f"audio_{random.randint(11111, 99999)}.wav"
        output_path = f"/tts_output/Audios/{output_file}"
        speaker_path = f"/tts_output/Speakers/{speaker_name}.wav"

        command = [
            "bash", "-c",
            f""" echo 'y' | tts --model_name {model_name.replace('--', '/')} \
                --speaker_wav "{speaker_path}" \
                --language_idx "{language}" \
                --device {'cuda' if torch.cuda.is_available() else 'cpu'} \
                --out_path "{output_path}"\
                --text "{message}"
            """,
        ]
        if torch.cuda.is_available(): 
            command = command + ["--gpus", "all"]

        exec_result = self.RUNNING_CONTAINERS[task_id]['container'].exec_run(command, stream=True)
        for log in exec_result.output: 
            self.RUNNING_CONTAINERS[task_id]['logs'] += "\n"+ log.decode().strip()

        return task_id, os.path.join(output_dir, output_file)
    


    def bulk_tts_with_excel(self, sheet_id=None, message="Hi", model_name="tts_models--multilingual--multi-dataset--xtts_v2", image="ghcr.io/coqui-ai/tts:latest", speaker_name="SARAH", language="en", isSample=False):

        task_id = "default"

        try:
            WORKIND_DIR = os.path.join(
                str(user_documents_path()), 
                f"TTS_Output_Samples" if not sheet_id else f"TTS_Output_{random.randint(11111,99999)}"
            )
            SPEAKERS_DIR  = os.path.join(WORKIND_DIR, "Speakers")
            WAV_FILES_DIR = str(os.path.join(WORKIND_DIR, "Audios"))

            if not os.path.exists(WORKIND_DIR):   os.mkdir(WORKIND_DIR)
            if not os.path.exists(SPEAKERS_DIR):  os.mkdir(SPEAKERS_DIR)
            if not os.path.exists(WAV_FILES_DIR): os.mkdir(WAV_FILES_DIR)

            speaker_file = f"{SPEAKERS_DIR}/{speaker_name}.wav"
            if not os.path.exists(speaker_file):
                self.download_speaker(self.VOICES[speaker_name], speaker_name, SPEAKERS_DIR)

            if not sheet_id:
                if not self.RUNNING_CONTAINERS.get('default'):
                    task_id, container = self.run_docker_container( image, WORKIND_DIR, task_id="default")

                kwargs = {
                    "task_id":task_id, 
                    "message":message, 
                    "speaker_name":speaker_name, 
                    "language":language, 
                    "output_dir":WAV_FILES_DIR, 
                    "isTest":True
                }
                self.temp_queue[task_id] = queue.Queue()
                temp_thread = Thread(target=self.wait_for_task_done, args=(self.transcribe,), kwargs=kwargs, daemon=True)
                temp_thread.start()
                temp_thread.join()
                
                response = self.temp_queue[task_id].get() if self.temp_queue[task_id] else task_id
                return { 'rtn': "audio/file", "value": response }

            else:

                task_id, container = self.run_docker_container(image, WORKIND_DIR)

                SHEET_URL = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
                df = pd.read_csv(SHEET_URL, skiprows=0)
                nested_list = df.values.tolist()

                self.RUNNING_CONTAINERS[task_id]['isRunning'] = True

                def perform_bulk_task(task_id):

                    AUDIO_FILES = []
                    for index, content in enumerate(nested_list):
                        temp = []
                        for index2, message in enumerate(content):                            
                            task_id, file_path = self.transcribe(
                                task_id=task_id, message=message, speaker_name=speaker_name, language=language, output_dir=WAV_FILES_DIR, isTest=False)
                            
                            # file_path = self.create_file_download_link(file_path)
                            if file_path: temp.append(file_path)

                            if self.RUNNING_CONTAINERS.get(task_id): 
                                self.RUNNING_CONTAINERS[task_id]['progress'] = f"{ round((((index * 3) + (index2 + 1)) / (len(nested_list) * 3)) * 100 )}"

                        AUDIO_FILES.append(temp)
                        
                    RESULTS = [msg + audio for msg, audio in zip(nested_list, AUDIO_FILES)]  # Combine Data and Audio File Names
                    output_file = os.path.join(WORKIND_DIR, 'data.xlsx')                     # Save to Excel
                    pd.DataFrame(RESULTS).to_excel(output_file, index=False, header=False)

                    zip_name = os.path.join(TTS_DATABASE_PATH, f'text_to_speech_{self.get_current_datetime()}.zip')  # Create Zip Archive
                    shutil.make_archive(zip_name.replace('.zip', ''), 'zip', WORKIND_DIR)

                    shutil.rmtree(WORKIND_DIR)

                    self.RUNNING_CONTAINERS[task_id]['files'].append({
                        "name": os.path.basename(zip_name),
                        "local_path": WORKIND_DIR,
                        "loc":  self.create_file_download_link(zip_name)
                    })
                    try:
                        if self.RUNNING_CONTAINERS.get(task_id): 
                            self.RUNNING_CONTAINERS[task_id]['isRunning'] = False
                            self.RUNNING_CONTAINERS[task_id]['progress'] = "100"
                            self.stop_container(self.RUNNING_CONTAINERS[task_id].get('container'))
                            self.RUNNING_CONTAINERS[task_id]['container'] = None
                    except: pass
                
                thread = Thread( target=perform_bulk_task, args=(task_id,), daemon=True ).start()                
                return { 'task_id' : task_id }

        except Exception as e:
            print(e)
            shutil.rmtree(WORKIND_DIR)
            try:
                if self.RUNNING_CONTAINERS.get(task_id): 
                    self.RUNNING_CONTAINERS[task_id]['isRunning'] = False
                    self.RUNNING_CONTAINERS[task_id]['logs'] += "\n"+ f"{e}".strip()
                    self.RUNNING_CONTAINERS[task_id].get('container').stop()
            except Exception as e: pass
            raise Exception(str(e))




if __name__ == "__main__":

    TEXT_TO_SPEECH_ = TEXT_TO_SPEECH()
    print(TEXT_TO_SPEECH_.bulk_tts_with_excel("19MA75pOtEjoVxXC3cabQmev3oQCqdV2RvI6-4Zu_Pvg"))