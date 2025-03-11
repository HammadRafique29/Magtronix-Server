import requests, os
import platform, time
from selenium import webdriver
from selenium.webdriver import Remote
import undetected_chromedriver as uc
from selenium.webdriver import ChromeOptions
from threading import Thread


BASE_URL = "http://localhost:8092"
cur_os = platform.system()
current_dir = os.path.dirname(os.path.abspath(__file__))


def fetch_request(method, endpoint, json_data):
    try:
        r = requests.request(method, f"{BASE_URL}/{endpoint}", json=json_data)
        response = r.json()
        print(response)
        data = response.get("data", {}).get("response")
        return data if r.status_code == 200 else (response.get("error"), False) # or {"status": "failed", "error": "No data or error in response"}
    except requests.exceptions.RequestException as e: return  (str(e), False) #{"status": "failed", "error": str(e)}
    except ValueError: return ("Unknow Error Occured", False)  #{"status": "failed", "error": "Invalid JSON response"}
    

def driver_get_task(task_id):
    return fetch_request("GET", "get-account", {"account_id": task_id})

def driver_get_tasks():
    return fetch_request("GET", "get-all-accounts", {})

def driver_update_task(task_id):
    return fetch_request("GET", "get-account", {"account_id": task_id})

def driver_temp_driver(proxy=None, device="desktop", headless=False):
    return fetch_request("POST", "get-temp-driver", {'proxy_url': proxy, "device": device, "headless": headless})

def driver_delete_task(task_id):
    return fetch_request("POST", "delete-account", {'account_id': task_id})

def driver_update_time(task_id):
    return fetch_request("POST", "update-last-login", {'account_id': task_id})

def driver_fingerprints():
    return fetch_request("GET", "get-browser-fingerprints", {})

def driver_add_fingerprint(f_type, fngerprnt):
    return fetch_request("POST", "add-browser-fingerprint", {"f_type": f_type, "fingerprint": fngerprnt})

def driver_run_driver(task_id, headless):
    return fetch_request("POST", "run-account", {"args": {'account_id': task_id, "headless": headless}})

def driver_add_task(task_id, accType, tags, proxy=None, device="desktop", data={}):
    res = fetch_request("POST", "add-account", {"args": {"acc_type": accType, "account_id": task_id, "profile_tags": tags, "proxy_url": proxy, "platform": device, "data": data}})
    print(res)

import subprocess
def start_chrome_driver():
    venv_dir = os.path.join(os.getcwd(), 'venv')
    
    if not os.path.exists(venv_dir):
        print("ChromeDriver: Virtual environment 'venv' not found. Please create and activate it.")
        return None 

    bin_dir = os.path.join(venv_dir, 'Scripts' if os.name == 'nt' else 'bin')
    try:
        python_executable = next(os.path.join(bin_dir, file) for file in os.listdir(bin_dir) if 'python' in file.lower())
    except StopIteration:
        print("ChromeDriver: No Python executable found in the virtual environment.")
        return None

    chrome_driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chrome_driver.py')

    with open("backend.log", "w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [python_executable, chrome_driver_path],
            stdout=log, 
            stderr=log,  # Save both stdout and stderr
            text=True 
        )
    print(f"Started chrome_driver.py (PID: {process.pid})")
    return process


def close_chrome_driver():
    return fetch_request("POST", "close-app", {})







if __name__ == "__main__":

    driver = driver_temp_driver()
    if driver:
        print(driver["address"], driver["port"])
        options = ChromeOptions()
        options.add_argument(f"--remote-debugging-port={driver['port']}")
        driver = uc.Chrome(options=options, headless=False)
        driver.get("https://www.google.com")
        print(driver.title)
    else:
        print("ERROR: Invalid driver response ->", driver)

    print(close_chrome_driver())
