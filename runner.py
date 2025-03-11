import os
import sys
import time
import glob
import shutil
import platform
import requests
import subprocess
from threading import Thread
from multiprocessing import Process
from colorama import Fore, Style, init as color_init
import atexit


# Initialize colorama
color_init()

# Constants
OS_NAME = platform.system()
CURRENT_DIR = os.getcwd()
VENV_PATH = os.path.join(CURRENT_DIR, "venv")
BACKEND_PATH = os.path.join(CURRENT_DIR, "app.py")
NODE_MODULE_DIR = os.path.join(CURRENT_DIR, "node_modules")
PY_MODULE_FILE = os.path.join(CURRENT_DIR, "requirements.txt")

# Colors
YLCLR = Fore.YELLOW
GRCLR = Fore.GREEN
RDCLR = Fore.RED
RSCLR = Fore.RESET
BLCLR = Fore.BLUE

# Set environment variable
os.environ["PYTHONIOENCODING"] = "utf-8"

CLEAR_SCREEN = lambda: os.system("cls" if OS_NAME == "Windows" else "clear")
CHECK_VENV_EXISTS = lambda: os.path.exists(VENV_PATH)
CREATE_SUBPROCESS = lambda command, cwd : subprocess.Popen(command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace" )
RUN_SUBPROCESS_CMD = lambda command: subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True if OS_NAME == "Windows" else False),



def RUN_SUBPROCESS(command, cwd, logs=True):
    process = CREATE_SUBPROCESS(command, cwd)
    if not logs:
        return process  # Return process immediately if logs are not needed

    log_file_path = os.path.join(cwd, "backend.log")
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        while process.poll() is None:  # Check if process is still running
            line = process.stdout.readline()
            if not line: break  # Exit loop if no more output
            log_file.write(line)
            log_file.flush()
    
    return process



def GET_VENE_EXECUTABLE(executable_name):
    script_dir = "Scripts" if OS_NAME == "Windows" else "bin"
    pattern = os.path.join(VENV_PATH, script_dir, f"{executable_name}*")
    candidates = glob.glob(pattern)
    return candidates[0] if candidates else None



def GET_NPM_EXECUTABLE():
    try:
        if OS_NAME == "Windows":
            command = r'(Get-ItemProperty "HKLM:\SOFTWARE\Node.js").InstallPath'
            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
            npm_dir = result.stdout.strip()
            npm_path = os.path.join(npm_dir, "npm.cmd") if npm_dir else None
            return npm_path if npm_path and os.path.exists(npm_path) else None
        else:
            return shutil.which("npm")
    except Exception as e:
        raise Exception(f"Error getting npm location: {str(e)}")
    


def INSTALL_PYTHON_PACKAGES():

    if CHECK_VENV_EXISTS(): return
    print(f"\n{GRCLR}-- INSTALLATION STARTED: {YLCLR}backend.log{RSCLR}")
    print(f"{GRCLR}-- Creating Python Environment...{RSCLR}")

    process = RUN_SUBPROCESS([sys.executable, "-m", "venv", "venv"], CURRENT_DIR)
    process.wait()
    if process.returncode != 0: raise Exception(f"{RDCLR}-- Error creating virtual environment. Return code: {process.returncode}{RSCLR}")

    print(f"{GRCLR}-- Installing Python Libraries...{RSCLR}")
    process = RUN_SUBPROCESS([GET_VENE_EXECUTABLE("pip"), "install", "-r", "requirements.txt"], CURRENT_DIR)
    process.wait()
    if process.returncode != 0: raise Exception(f"{RDCLR}-- Error installing packages. Return code: {process.returncode}{RSCLR}")




def INSTALL_NPM_PACKAGES():

    if os.path.exists(NODE_MODULE_DIR): return
    print(f"{GRCLR}-- Installing dependencies from package.json...{RSCLR}")

    try: RUN_SUBPROCESS_CMD(["node", "--version"])
    except FileNotFoundError: raise Exception("Error: Node.js is not installed. Please install Node.js first.")
    
    try: RUN_SUBPROCESS_CMD(["npm", "--version"])
    except FileNotFoundError: raise Exception("Error: npm is not installed. Please install npm first.")
    
    if not os.path.exists("package.json"): raise Exception("Error: package.json file not found in the current directory.")
    
    try: RUN_SUBPROCESS_CMD(["npm", "install", "--loglevel=error"])
    except subprocess.CalledProcessError: raise Exception("Error: Failed to install dependencies.")



def fix_electron_sandbox_permissions():
    if OS_NAME == "Linux":
        sandbox_path = os.path.join(CURRENT_DIR, "node_modules", "electron", "dist", "chrome-sandbox")
        if os.path.exists(sandbox_path):
            try:
                subprocess.run(["sudo", "chown", "root", sandbox_path], check=True)
                subprocess.run(["sudo", "chmod", "4755", sandbox_path], check=True)
                print("[INFO] Electron sandbox permissions fixed.")
            except subprocess.CalledProcessError as e: print(f"[ERROR] Failed to fix Electron sandbox: {e}")
        else: print("[WARNING] Electron sandbox file not found, skipping fix.")




def RUN_BACKEND_APPLICATION(command, cwd):
    os.chdir(cwd)
    command_str = ' '.join(command)
    os.system(f"{command_str} > backend.log 2>&1")





def start_ollama():
    try:
        subprocess.Popen(
            ["ollama", "serve"], 
            shell=True, 
            stdout=subprocess.DEVNULL,  # Suppress standard output
            stderr=subprocess.DEVNULL
        ).wait()
    except: pass


def start_docker_windows():
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen(
            ["net", "start", "Docker Desktop Service"],
            shell=True,
            stdout=subprocess.DEVNULL,  # Suppress standard output
            stderr=subprocess.DEVNULL   # Suppress standard error
        )
    except subprocess.CalledProcessError as e: pass



def logo():
    banner = """\n
Introducing:

███    ███  █████   ██████  ████████ ██████   ██████  ███    ██ ██ ██   ██ 
████  ████ ██   ██ ██          ██    ██   ██ ██    ██ ████   ██ ██  ██ ██  
██ ████ ██ ███████ ██   ███    ██    ██████  ██    ██ ██ ██  ██ ██   ███   
██  ██  ██ ██   ██ ██    ██    ██    ██   ██ ██    ██ ██  ██ ██ ██  ██ ██  
██      ██ ██   ██  ██████     ██    ██   ██  ██████  ██   ████ ██ ██   ██ 

🚀 Personal Local AI Automation - HammadRafique029
 """
    print(banner)


def check_server_status(url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200, response
    except: return False, None


if __name__ == "__main__":
    try:
        CLEAR_SCREEN()
        logo()

        server_status, response = check_server_status("http://localhost:8081/get-running-tasks")
        if server_status:
            print(f"{RDCLR}### Server Already Running. {RSCLR}")
            choice = input(f"{BLCLR}### Stop Server (y/n): {RSCLR}")
            if choice.lower() in ["y", "yes"]:
                requests.post("http://localhost:8081/close-main-app")
                time.sleep(8)
                server_status, _ = check_server_status("http://localhost:8081/get-running-tasks")
                if not server_status: print(f"{GRCLR}-- Server Stopped!{RSCLR}")
                sys.exit()
            else: sys.exit()
        else: pass

        # Thread(target=start_docker_windows, daemon=True).start()
        # Thread(target=start_ollama, daemon=True).start()

        CLEAR_SCREEN()
        logo()

        print(f"{RDCLR}### Server Not Running. {RSCLR}")
        choice = input(f"{BLCLR}### Start Server (y/n): {RSCLR}")
        if choice.lower() not in ["y", "yes"]:
            sys.exit()

        INSTALL_PYTHON_PACKAGES()
        INSTALL_NPM_PACKAGES()

        VENV_PYTHON_PATH = GET_VENE_EXECUTABLE("python")

        if OS_NAME == "Linux":
            fix_electron_sandbox_permissions()

        print(f"{BLCLR}### Starting Backend Server! Please Wait{RSCLR}")

        backend_command = [VENV_PYTHON_PATH, BACKEND_PATH]
        backend_process = Thread(target=RUN_BACKEND_APPLICATION, args=(backend_command, CURRENT_DIR,))
        backend_process.daemon = True
        backend_process.start()

        while True:
            server_status, _ = check_server_status("http://localhost:8081/get-running-tasks")
            if server_status:
                break
            time.sleep(3)

        print(f"\n{GRCLR}-- SERVER STARTED SUCCESSFULLY {RSCLR}")
        sys.exit()

    except Exception as e:
        print(f"{e}")
        input("\n\nPress any key to exit...")
