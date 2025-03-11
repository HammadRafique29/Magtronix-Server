import os
import torch
import docker
import random
import shutil
import ollama
import open_webui
import subprocess
from ollama import chat
from ollama import ChatResponse
from threading import Thread


RUNNING_PORT = 8093
file_dir = os.path.dirname(os.path.abspath(__file__))


class OllamaManager:

    def __init__(self, API_ENDPOINTS={}):
        self.RUNNING_TASKS = {}
        self.API_ENDPOINTS = API_ENDPOINTS
        self.RUNNING_PROCESS = None
        Thread(target=self.start_ollama, daemon=True).start()


    # Function to start open-webui.exe and save logs
    def start_ollama(self):
        log_file_path = os.path.join(file_dir, "ollama_serve.log")
        with open(log_file_path, "w", encoding="utf-8") as logfile:
            self.RUNNING_PROCESS = subprocess.Popen(
                ["ollama", "serve"],
                stdout=logfile,  # Redirect standard output to log file
                stderr=logfile,  # Redirect error output to log file
                cwd=os.getcwd(),  # Use the current directory
                env=os.environ,  # Pass environment variables
                creationflags=subprocess.CREATE_NO_WINDOW  # Hide console window (Windows only)
            ) 
            
    def clear_resources(self):
        print("#### Destructor: Text-To-Speech")
        try:
            if self.RUNNING_PROCESS:
                self.RUNNING_PROCESS.terminate()
                self.RUNNING_PROCESS.wait()
        except: pass
        self.RUNNING_TASKS = {}


    def delete_task(self, task_id):
        self.RUNNING_TASKS.pop(task_id)


    def running_tasks(self):
        running_tasks = []
        for key, task in self.RUNNING_TASKS.items():
            if isinstance(task, dict):  
                filtered_task = {k: v for k, v in task.items() if isinstance(v, (str, int, float, bool, list, dict))}
                running_tasks.append(filtered_task)
        return running_tasks
    

    def get_logs(self, task_id):
        logs = self.RUNNING_TASKS.get(task_id, {}).get('logs', '')
        logs += "\nSTATUS: " + ("RUNNING" if self.RUNNING_TASKS.get(task_id, {}).get('isRunning') else "STOPPED")
        return logs
    

    def get_files(self, task_id):
        files = self.RUNNING_TASKS.get(task_id, {}).get('files', [])
        return [{"name": file["name"], "loc": file["loc"]} for file in files]
    

    def get_installed_models(self):
        return [j['model'] for i in ollama.list() for j in i[1]]



    def download_model(self, model_name: str):
        try:
            if model_name in self.get_installed_models():
                raise Exception("Model is already Downloaded")
            
            for taskId, task in self.RUNNING_TASKS.items():
                if task.get("model_name") == model_name and task.get("status", "") != "Completed": 
                    raise Exception(f"Model is already downloading id {taskId}")
            
            task_id = 'ollama_'+str(random.randint(11111, 99999))

            self.RUNNING_TASKS[task_id] = { 
                "logs": "", 
                "progress": "0%", 
                "status": "Downloading...", 
                "isRunning": True,
                "task_id": task_id,
                "task_type": "Ollama - Download Model",
                "tags": f"Fetching ollama model--{model_name}" }
            
            def thread_worker(task_id, model_name):
                try:
                    for progress in ollama.pull(model_name, stream=True):
                        if not progress: 
                            self.RUNNING_TASKS[task_id]['logs'] = "Failed to download! Please make sure you following things: \n\t- Valid Model Name\n\t- Stable Internet Connection"
                            break

                        completed_ = progress.completed or 0 
                        total_ = progress.total or 1 

                        total_progress = f"{round((completed_ / total_) * 100)}%"
                        self.RUNNING_TASKS[task_id]['progress'] = total_progress
                        self.RUNNING_TASKS[task_id]['logs'] = f"Downloading [{total_progress}]"

                except Exception as e: self.RUNNING_TASKS[task_id]['logs'] = str(e)
                self.RUNNING_TASKS[task_id]['isRunning'] = False
                self.RUNNING_TASKS[task_id]['status'] = 'Completed'
            
            Thread(target=thread_worker, args=(task_id, model_name,), daemon=True).start()
            return { "rtn": "response/id", "value": task_id }
        
        except Exception as e: 
            raise Exception(str(e))



    def run_model(self, model_name: str, prompt="Tell me about you!", context=None):
        response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"]



    def ollama_chat(self, model_name, prompt, context=None):
        messages = []
        if context: messages.append({ 'role': 'system','content': context })
        messages.append( { 'role': 'user', 'content': prompt })
        response: ChatResponse = chat(model=model_name, messages=messages)
        return {"rtn": "response/md", "value": response['message']['content']}



    def summarize_text(self, model_name, prompt, words_count=None):
        try:
            try:
                words_count = int(words_count)
                words_count = words_count if len(words_count)>10 else None
                print(words_count)
            except: pass

            content_prompt_ = f"{'text_sumarize_wrd_pr' if words_count else 'text_sumarize_pr'}.txt"
            print(content_prompt_, words_count)
            with open(os.path.join(file_dir, "prompts", content_prompt_), "r") as f: context = f.read()
            return self.ollama_chat(model_name, prompt, context.replace('WORD_COUNT_LENGTH', str(words_count)) if words_count else context)
        except Exception as e: 
            raise Exception(str(e))






class OpenWebUIManager:

    def __init__(self, API_ENDPOINTS={}):

        self.port = 8090
        self.container_name = "open-webui"
        self.image = "ghcr.io/open-webui/open-webui:main"
        self.ollama_url = "http://localhost:11434/"
        self.local_url = f"http://localhost:{self.port}"
        self.RUNNING_CONTAINERS = {}
        self.API_ENDPOINTS = API_ENDPOINTS
        self.task_id = self.image + "_" + "default"
        self.running_process = None
        self.start_webui()



    def clear_resources(self):
        print("#### Destructor: OpenWeb-UI")
        if self.RUNNING_CONTAINERS:
            for key, cont in self.RUNNING_CONTAINERS.items():
                print(" --Stoping: open-WebUI")
                if cont['container'] or cont['isRunning']:
                    self.stop_container()
                self.RUNNING_CONTAINERS = {}
        else: self.stop_container()



    def get_logs(self, task_id):
        logs = self.RUNNING_CONTAINERS.get(task_id, {}).get('logs', '')
        logs += "\n\nPROGRESS: " + str(self.RUNNING_CONTAINERS.get(task_id, {}).get('progress'))
        logs += "\nSTATUS: " + ("RUNNING" if self.is_running() else "STOPPED")
        return logs
    


    def get_files(self, task_id):
        files = self.RUNNING_CONTAINERS.get(task_id, {}).get('files', [])
        return [{"name": file["name"], "loc": file["loc"]} for file in files]
    


    def is_running(self):
        check_command = ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"]
        result = subprocess.run(check_command, capture_output=True, text=True)
        return self.container_name in result.stdout.strip()
    


    def stop_container(self):

        if not self.is_running() and not self.RUNNING_CONTAINERS.get(self.task_id, None) and not self.running_process:
            print(f"Container '{self.container_name}' is not running.")
            return
        
        stop_command = ["docker", "stop", self.container_name]
        rm_command = ["docker", "rm", self.container_name]
        try:
            subprocess.run(stop_command, capture_output=True, text=True, check=True)
            subprocess.run(rm_command, capture_output=True, text=True, check=True)
            print("Container stopped and removed successfully.")
        except Exception as e: print(f"Error stopping container: {e.stderr}")

        try:
            result = subprocess.run(["tasklist"], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if "open-webui.exe" in line:
                    pid = int(line.split()[1])  # Extract PID
                    print(f"Stopping open-webui.exe with PID {pid}")
                    os.system(f"taskkill /F /PID {pid}")  # Force kill the process
        except: pass

        try:
            self.running_process.terminate()
            self.running_process.wait()
        except: pass



    def delete_container_data(self, task_id):
        cont_data = self.RUNNING_CONTAINERS.get(task_id)
        if cont_data:
            if cont_data['container'] or cont_data['isRunning']:
                self.stop_container()
                for dirs in self.RUNNING_CONTAINERS[task_id]['files']:
                    local_path = dirs['local_path']
                    if os.path.isdir(local_path): shutil.rmtree(local_path)
                    else: os.remove(local_path) 
                self.RUNNING_CONTAINERS.pop(task_id)
        else: self.stop_container()
        return ''


    def run_process(command, cwd, shell=True):
        print(command, cwd)
        process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
        stdout, stderr = process.communicate()  # Wait for process to finish and capture output
        print("STDOUT:", stdout.decode().strip())


    # Function to start open-webui.exe and save logs
    def thread_start(self):
        log_file_path = os.path.join(file_dir, "open-webui.log")
        with open(log_file_path, "w", encoding="utf-8") as logfile:
            self.running_process = subprocess.Popen(
                ["open-webui.exe", "serve", "--port", str(RUNNING_PORT)],
                stdout=logfile,  # Redirect standard output to log file
                stderr=logfile,  # Redirect error output to log file
                cwd=os.getcwd(),  # Use the current directory
                env=os.environ,  # Pass environment variables
                creationflags=subprocess.CREATE_NO_WINDOW  # Hide console window (Windows only)
            ) 
    
    def start_webui(self):

        task_id = self.image + "_" + "default"
        try:
            if self.is_running() or self.RUNNING_CONTAINERS.get(task_id, None): 
                return {'rtn': "response/str", "value": self.local_url}
            
            Thread(target=self.thread_start, daemon=True).start()
            
            self.RUNNING_CONTAINERS[task_id] = {
                'task_id': task_id, 
                'feature': "Ollama_WebUI", 
                "tags": self.image, 
                "progress": 99, 
                "logs": """""", 
                "isRunning": True, 
                "files": []
            }
        
            # client = docker.from_env()
            # container = client.containers.run(
            #     tty=True, 
            #     detach=True,
            #     stream=True, 
            #     network_mode="host",
            #     name=self.container_name,
            #     image="ghcr.io/open-webui/open-webui:main",
            #     volumes={"open-webui": {"bind": "/app/backend/data", "mode": "rw"}},
            #     extra_hosts={"host.docker.internal": "host-gateway"},
            #     restart_policy={"Name": "always"},
            #     environment={"OLLAMA_BASE_URL": "http://127.0.0.1:11434"},
            #     device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])] if torch.cuda.is_available() else []
            # )

            # if "running" in container.status:
            #     self.RUNNING_CONTAINERS[task_id] = {
            #         'task_id': task_id, 
            #         'feature': "Ollama_WebUI", 
            #         "tags": self.image, 
            #         'container': container, 
            #         "progress": container.status, 
            #         "logs": """""", 
            #         "isRunning": True, 
            #         "files": []
            #     }

            return {'rtn': "response/str", "value": self.local_url}
        
        except Exception as e:
            print(f"Error starting container: {e}")
            self.RUNNING_CONTAINERS[task_id] = {
                'task_id': self.image + "_" + "default", 
                'feature': "Ollama_WebUI", 
                "tags": self.image, 
                'container': None, 
                "progress": "Failed", 
                "logs": f"""{e}""", 
                "isRunning": False, 
                "files": []
            }
            return {'rtn': "response/str", "value": self.local_url}

    




if __name__ == "__main__":

    manager = OpenWebUIManager()
    OLLAMA_MANAGER = OllamaManager()
    OLLAMA_MANAGER.download_model("llama3.2:1b")

    OLLAMA_MANAGER.ollama_chat('deepseek-r1:1.5b', "Tell me about yourself?")
    print(manager.clear_resources())
    url = manager.start()
    if url:
        print(f"OpenWebUI is running at: {url}")

    manager.stop()