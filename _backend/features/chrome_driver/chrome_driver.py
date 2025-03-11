import os
import sys
import json
import time
import shutil
import random
import screeninfo
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumwire import webdriver as wire_webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from flask_cors import CORS
from flask import Flask, jsonify, request, render_template, send_file, url_for


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app)

DRVER_PATH      =  os.path.dirname(os.path.abspath(__file__))
DRVIER_DB_PATH  =  os.path.join(DRVER_PATH, 'db')
ACCOUNTS_FILE = os.path.join(DRVIER_DB_PATH, 'accounts.json')
PROFILE_PATH  = os.path.join(DRVIER_DB_PATH, 'profiles')
FINGERPRINTS_FILE = os.path.join(DRVIER_DB_PATH, 'fingerprints.json')
FINGERPRINTS = {"desktop":[{"user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36","screen_resolution":[1920,1080],"device_memory":8},{"user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36","screen_resolution":[1920,1080],"device_memory":8},{"user_agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36","screen_resolution":[1920,1080],"device_memory":8}],"android":[{"user_agent":"Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36","screen_resolution":[393,851],"device_memory":8,"scale_factor":2.5},{"user_agent":"Mozilla/5.0 (Linux; Android 11; Samsung Galaxy S21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36","screen_resolution":[360,800],"device_memory":12,"scale_factor":3.0},{"user_agent":"Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36","screen_resolution":[412,915],"device_memory":16,"scale_factor":3.5},{"user_agent":"Mozilla/5.0 (Linux; Android 10; Xiaomi Mi 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36","screen_resolution":[392,870],"device_memory":8,"scale_factor":2.8},{"user_agent":"Mozilla/5.0 (Linux; Android 12; Samsung Galaxy Note 20 Ultra) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36","screen_resolution":[412,915],"device_memory":12,"scale_factor":3.0},{"user_agent":"Mozilla/5.0 (Linux; Android 11; Google Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36","screen_resolution":[360,780],"device_memory":8,"scale_factor":2.5},{"user_agent":"Mozilla/5.0 (Linux; Android 12; Oppo Find X5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36","screen_resolution":[412,915],"device_memory":12,"scale_factor":3.5},{"user_agent":"Mozilla/5.0 (Linux; Android 10; Huawei P40 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36","screen_resolution":[360,780],"device_memory":8,"scale_factor":3.1}],"other":[{"user_agent":"Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1","screen_resolution":[2360,1640],"device_memory":8}]}

if not os.path.exists(DRVIER_DB_PATH): os.makedirs(DRVIER_DB_PATH)
if not os.path.exists(PROFILE_PATH): os.makedirs(PROFILE_PATH)

if not os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, 'w') as f: json.dump({}, f)

if not os.path.exists(FINGERPRINTS_FILE):
    with open(FINGERPRINTS_FILE, 'w') as f: json.dump(FINGERPRINTS, f)


# Initialize Accounts File
def initialize_accounts_file():
    if not os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'w') as f: json.dump({}, f)



# Load fingerprints from a JSON file
def load_fingerprint(filepath):
    try:
        with open(filepath, "r") as file: return json.load(file)
    except FileNotFoundError:
        print(f"Fingerprint file not found: {filepath}")
        return {}



# Add Devices Resolution - Mobile, Desktop, Tablet
def add_device_metrics(driver, fingerprint, isMobile):
    device_metrics = {
        "width": fingerprint['screen_resolution'][0], 
        "height": 1080,
        "deviceScaleFactor": fingerprint['scale_factor'] if isMobile else 0,
        "mobile": True if isMobile else False
    }
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", device_metrics)
    return device_metrics



# Retrieve an Account
def get_account(account_id):
    accounts = get_all_accounts()
    return accounts.get(account_id, None)



# Retrieve All Account
def get_all_accounts():
    with open(ACCOUNTS_FILE, 'r') as f: accounts = json.load(f)
    return accounts



# Update All Accounts
def update_refresh_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w') as f: json.dump(accounts, f)



# Update an Account
def update_accounts(account_id, ky, vl):

    if not account_id: return Exception("Invalid account id or missing")
    if not get_account(str(account_id)): return Exception(f"No account found with id: {account_id}")

    accounts = get_all_accounts()
    accounts[str(account_id)][ky] = vl
    update_refresh_accounts(accounts)
    return True



# Delete task profile & Account
def delete_account(account_id):

    if not account_id: raise Exception("Invalid account id or missing")
    if not get_account(str(account_id)): raise Exception(f"No account found with id: {account_id}")

    accounts = get_all_accounts()
    accounts.pop(str(account_id), True)
    # if "temp" in account_id:
    shutil.rmtree(os.path.join(PROFILE_PATH, account_id))
    
    print("Updated: ", accounts)
    update_refresh_accounts(accounts)
    return True


# Update Last Login
def update_last_login(account_id):

    if not account_id: return Exception("Invalid account id or missing")
    if not get_account(str(account_id)): return Exception(f"No account found with id: {account_id}")

    accounts = get_all_accounts()
    accounts[str(account_id)]["last_login"] = "2024-12-30"  # Use actual date
    update_refresh_accounts(accounts)



# Get Active Monitor Resolution
def get_active_monitor_resolution():
    try:
        monitors = screeninfo.get_monitors()
        for monitor in monitors:
            if monitor.is_primary:  return monitor.width, monitor.height
        if monitors: return monitors[0].width, monitors[0].height
        else: raise Exception("No active monitor detected.")
    except Exception as e:
        print(f"Error detecting monitor resolution: {e}")
        return None
    

# Save Cookies
def save_cookies(driver, filepath):
    with open(filepath, 'w') as file:
        json.dump(driver.get_cookies(), file)



# Load Cookies
def load_cookies(driver, filepath):
    with open(filepath, 'r') as file:
        cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)



# Get Fingerprints
def get_fingerprints():
    with open(FINGERPRINTS_FILE, 'r') as f: 
        return json.loads(f.read())
    


# Add Fingerprint
def add_fingerprint(f_type, fingerprint):
    fingerprints = get_fingerprints()
    if f_type not in fingerprints.keys(): fingerprints[f_type] = []
    fingerprints[f_type].append(fingerprint)
    with open(FINGERPRINTS_FILE, 'w') as f: 
        json.dump(fingerprints, f)
    return True
    


# Human Like Interaction
def human_like_interaction(driver, element):
    actions = ActionChains(driver)
    actions.move_to_element_with_offset(element, random.randint(-5, 5), random.randint(-5, 5))
    actions.pause(random.uniform(0.5, 1.5))
    actions.click()
    actions.perform()



# Get Random Fingerprints
def random_fingerprint(platform='desktop'):
    fingerprints = load_fingerprint(FINGERPRINTS_FILE)
    if platform not in fingerprints.keys(): return None
    platform_fingerprints = fingerprints[platform]
    if not platform_fingerprints: return None
    rnd = random.randint(0, len(platform_fingerprints)-1)
    return fingerprints[platform][rnd]



# Lounch Browser with fingerprint
def launch_browser_with_fingerprint(
        profile_name, 
        platform='desktop', 
        proxy_url=None,
        headless=False
    ):
    options = webdriver.ChromeOptions()
    fingerprint = random_fingerprint(platform)
    if not fingerprint:
        return "ERROR! Fingerprint Not Found..."

    seleniumwire_options = None
    if proxy_url: 
        seleniumwire_options =  { 
            'proxy': { 'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1' } 
        } if proxy_url else {}

    port = random.randint(9000, 9999)
    profile_dir = os.path.join(PROFILE_PATH, profile_name, 'driver_')
    print(profile_dir)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-cache')
    options.add_argument(f"--remote-debugging-port={port}")
    if headless: options.add_argument('--headless')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-component-update')
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument('--blink-settings=imagesEnabled=false')
    if proxy_url: options.add_argument(f'--proxy-server={proxy_url}')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument(f"--user-agent={fingerprint['user_agent']}")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("prefs", {"media.peerconnection.enabled": False})
    options.add_argument("--host-resolver-rules='MAP * 0.0.0.0 , EXCLUDE google.com'")
    try:
        driver = wire_webdriver.Chrome(options=options, seleniumwire_options=seleniumwire_options)
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": fingerprint['user_agent']})
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", { # Inject custom JavaScript for fingerprint spoofing
            "source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'languages', { value: ['en-US', 'en'] });
                Object.defineProperty(navigator, 'plugins', { value: [] });
                Object.defineProperty(navigator, 'platform', { value: 'Win32' });
                Object.defineProperty(navigator, 'getBattery', {
                    value: async () => ({
                        charging: true,
                        level: 0.76,
                        chargingTime: 120,
                        dischargingTime: Infinity
                    })
                });
                Object.defineProperty(window, 'RTCPeerConnection', {
                    value: () => null
                });
                Object.defineProperty(navigator, 'webdriver', {get: () => false});
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(param) {
                    if (param === 37445) return 'Intel Inc.'; // Vendor
                    if (param === 37446) return 'Intel Iris OpenGL Engine'; // Renderer
                    return getParameter.call(this, param);
                };
                // Canvas Spoofing: Manipulate getImageData
                const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
                CanvasRenderingContext2D.prototype.getImageData = function() {
                    const data = originalGetImageData.apply(this, arguments);
                    for (let i = 0; i < data.data.length; i++) {
                        data.data[i] ^= 0x10; // Simple manipulation
                    }
                    return data;
                };
                // Plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => {"0":{"0":{},"1":{}},"1":{"0":{},"1":{}},"2":{"0":{},"1":{}},"3":{"0":{},"1":{}},"4":{"0":{},"1":{}}}
                });
                // Geolocation
                navigator.geolocation.getCurrentPosition = function(success) {
                    success({ coords: { latitude: 37.7749, longitude: -122.4194, accuracy: 100 } });
                };
            """
        })
        width, height = fingerprint["screen_resolution"]  # Seting Chrome Window Resolution
        current_os_resol = get_active_monitor_resolution()
        device_metrics = { # Set device metrics
            "width": fingerprint['screen_resolution'][0],
            "height": fingerprint['screen_resolution'][1] if (platform != "android") else 1080,
            "deviceScaleFactor": fingerprint['scale_factor'] if (platform == "android") else 0, 
            "mobile": True if (platform == "android") else False
        }
        driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", device_metrics)
        resetResolution  = (
            width if (platform == "android") else current_os_resol[0] if current_os_resol else width, 
            current_os_resol[0] if current_os_resol else width
        )
        driver.set_window_size(resetResolution[0], resetResolution[1])
        print(f"RESIZING WINDOW: {resetResolution[0]}x{resetResolution[1]} {'Android' if device_metrics['mobile'] else 'Desktop'}")

        # Set custom user-agent and inject JS for spoofing
        if "device_memory" in fingerprint:
            script = f"Object.defineProperty(navigator, 'deviceMemory', {{get: () => {fingerprint['device_memory']}}});"
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})

        return f"http://127.0.0.1:{port}", port
    except Exception as e:
        print(f"Error launching browser: {e}")
        return None



# Add Automation Task & Account
def add_automation_task(acc_type, account_id, profile_tags, proxy_url=None, platform="desktop", data={}):

    initialize_accounts_file()

    if not account_id:
        raise Exception("Invalid account id or missing")
    
    account_id = str(account_id)

    if get_account(account_id):
        raise Exception("Account already found with provided username")
    
    with open(ACCOUNTS_FILE, 'r') as f: accounts = json.load(f)
    accounts[account_id] = {
        'acc_type': acc_type,
        'profile': account_id,
        "profile_tags": profile_tags,
        "proxy_url": proxy_url,
        "last_login": None,
        "platform": platform,
        "isRunning": False,
        "status": False,
        "data": data
    }
    print(accounts)
    with open(ACCOUNTS_FILE, 'w') as f:  json.dump(accounts, f)
    account = get_account(account_id)
    return account



# Run Automation Task & Account
def run_automation_task(account_id, headless=False):

    account_id = str(account_id)
    account_data = get_account(account_id)
    if not account_data: raise Exception("Account Not Found!")

    address, port = launch_browser_with_fingerprint(
        profile_name=account_data['profile'], 
        platform=account_data['platform'], 
        headless=headless,
        proxy_url=account_data['proxy_url'],
    )
    print("here is: ",account_id)
    update_last_login(account_id)
    update_accounts(account_id, "status", "Running")
    update_accounts(account_id, "isRunning", True)
    return {'address': address, "port": port}



def random_time_sleep(a, b):
    time.sleep(random.uniform(a, b))
    return



#################################################################################################
# -----------------------------------------------------------------------------------------------

@app.route('/get-account', methods=['GET'])
def driver_get_account():
    data = json.loads(request.data.decode("utf-8"))
    account_id = str(data.get('account_id', None))
    if not account_id: return jsonify({ "status": "failed", "error": "Account Id is required!", "data": { 'response': None }}), 400
    return jsonify({ "status": "success", "error": "", "data": { 'response': get_account(account_id) }}), 200



@app.route('/get-all-accounts', methods=['GET'])
def driver_get_all_accounts():
    return jsonify({ "status": "success", "error": "", "data": { 'response': get_all_accounts() }}), 200



@app.route('/update-account', methods=['POST'])
def driver_update_account():
    data = json.loads(request.data.decode("utf-8"))
    account_id = str(data.get('account_id', None))
    attr_name = data.get('key')
    attr_value = data.get('value')

    if not account_id or not attr_name or not attr_value:
        return jsonify({ 
            "status": "failed", "error": "AccountID, attribute name and its value is required!", "data": { 'response': None }
        }), 400
    
    try: return jsonify({ "status": "success", "error": "", "data": { 'response': update_accounts(account_id, attr_name, attr_value) }}), 200
    except Exception as e: return jsonify({ "status": "failed", "error": str(e), "data": { 'response': None }}), 400
    


@app.route('/delete-account', methods=['POST'])
def driver_delete_account():
    data = json.loads(request.data.decode("utf-8"))
    account_id = str(data.get('account_id', None))
    
    try: return jsonify({ "status": "success", "error": "", "data": { 'response': delete_account(account_id) }}), 200
    except Exception as e: return jsonify({ "status": "failed", "error": str(e), "data": { 'response': None }}), 400



@app.route('/update-last-login', methods=['POST'])
def driver_update_last_login():
    data = json.loads(request.data.decode("utf-8"))
    account_id = str(data.get('account_id', None))
    
    try: return jsonify({ "status": "success", "error": "", "data": { 'response': update_last_login(account_id) }}), 200
    except Exception as e: return jsonify({ "status": "failed", "error": str(e), "data": { 'response': None }}), 400



@app.route('/save-cookies', methods=['POST'])
def driver_save_cookies():
    data = json.loads(request.data.decode("utf-8"))
    account_id = str(data.get('account_id', None))
    
    try: return jsonify({ "status": "success", "error": "", "data": { 'response': save_cookies(account_id, "") }}), 200
    except Exception as e: return jsonify({ "status": "failed", "error": str(e), "data": { 'response': None }}), 400



@app.route('/load-cookies', methods=['POST'])
def driver_load_cookies():
    data = json.loads(request.data.decode("utf-8"))
    account_id = str(data.get('account_id', None))
    
    try: return jsonify({ "status": "success", "error": "", "data": { 'response': load_cookies(account_id, "") }}), 200
    except Exception as e: return jsonify({ "status": "failed", "error": str(e), "data": { 'response': None }}), 400



@app.route('/add-account', methods=['POST'])
def driver_add_account():
    data = json.loads(request.data.decode("utf-8"))
    kwargs = data.get('args')

    print(kwargs)
    if not kwargs:
        return jsonify({ 
            "status": "failed", 
            "error": "Fields are required [acc_type, account_id, profile_tags, proxy_url, platform, data]", 
            "data": { 'response': None }
        }), 400
    
    try: return jsonify({ "status": "success", "error": "", "data": { 'response': add_automation_task(**kwargs) }}), 200
    except Exception as e: return jsonify({ "status": "failed", "error": str(e), "data": { 'response': None }}), 400



@app.route('/run-account', methods=['POST'])
def driver_run_account():
    data = json.loads(request.data.decode("utf-8"))
    kwargs = data.get('args')
    
    if not kwargs:
        return jsonify({ 
            "status": "failed", 
            "error": "Fields is required! [account_id, headless]", 
            "data": { 'response': None }
        }), 400
    
    try: return jsonify({ "status": "success", "error": "", "data": { 'response': run_automation_task(**kwargs) }}), 200
    except Exception as e: 
        print(e)
        return jsonify({ "status": "failed", "error": str(e), "data": { 'response': None }}), 400
    



@app.route('/get-temp-driver', methods=['POST'])
def driver_temp_account():
    data = json.loads(request.data.decode("utf-8"))
    proxy_url = data.get('proxy_url', None)
    platform = data.get('device', None)
    headless = data.get('headless', False)

    temp_args = {
        "acc_type": "temporary",
        "account_id": f"temp_{random.randint(11111, 99999)}",
        "profile_tags": "running temporary driver",
        "proxy_url": proxy_url if proxy_url else None, 
        "platform": platform if platform else "desktop"
    }

    print(temp_args)
    try: 
        account = add_automation_task(**temp_args)
        if account:
            return jsonify({ "status": "success", "error": "", "data": { 'response': run_automation_task(temp_args['account_id'], headless) }}), 200
    except Exception as e: return jsonify({ "status": "failed", "error": str(e), "data": { 'response': None }}), 400




@app.route('/get-browser-fingerprints', methods=['GET'])
def driver_get_fingerprints():
    return jsonify({ "status": "success", "error": "", "data": { 'response': get_fingerprints() }}), 200



@app.route('/add-browser-fingerprint', methods=['POST'])
def driver_add_fingerprints():
    data = json.loads(request.data.decode("utf-8"))
    f_type = data.get('f_type')
    fingerprint = data.get('fingerprint')
    
    try: return jsonify({ "status": "success", "error": "", "data": { 'response': add_fingerprint(f_type, fingerprint) }}), 200
    except Exception as e: return jsonify({ "status": "failed", "error": str(e), "data": { 'response': None }}), 400



@app.route('/close-app', methods=['POST'])
def close_app():
    accounts = get_all_accounts()
    try:
        for acc in accounts.keys():
            if "temp" in acc or "temp" == acc: delete_account(acc)
    except Exception as e: print(e)

    os._exit(0)
    return "Shutting down the server...", 200





if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8092, debug=True)