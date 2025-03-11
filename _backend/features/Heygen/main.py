import os
import importlib
from threading import Thread
from _backend.features.chrome_driver.main import *
from _backend.features.Heygen.heygen_local_api import *
from _backend.features.Heygen.heygen_web_api import *
from _backend.features.chrome_driver.main import *

script_dir = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_DIR = os.path.join(script_dir, "accounts")
ACCOUNTS_DB = os.path.join(ACCOUNTS_DIR, "accounts.json")
if not os.path.exists(ACCOUNTS_DIR): os.makedirs(ACCOUNTS_DIR)
if not os.path.exists(ACCOUNTS_DB): 
    with open(ACCOUNTS_DB, 'w') as f: f.write(json.dumps({}))


class HEYGEN_:

    def __init__(self, API_ENDPOINTS={}, isPaid=False):
        self.HEYGEN_API = None
        self.HEYGEN_ACCOUNTS = self.load_accounts()
        self.update_and_refresh_accounts = lambda accounts: (lambda f: (json.dump(accounts, f), f.close()))(open(ACCOUNTS_DB, "w"))
        self.API_ENDPOINTS=API_ENDPOINTS
        self.RUNNING_TASKS = {}

    def clear_resources(self):
        print("#### Destructor: Text-To-Speech")
        self.RUNNING_TASKS = {}

    def running_tasks(self):
        running_tasks = []
        for key, task in self.RUNNING_TASKS.items():
            if isinstance(task, dict):  
                filtered_task = {k: v for k, v in task.items() if isinstance(v, (str, int, float, bool, list, dict))}
                running_tasks.append(filtered_task)
        return running_tasks

    def get_logs(self, task_id):
        logs = self.RUNNING_TASKS.get(task_id, {}).get('logs', '')
        logs += "\n\nPROGRESS: " + str(self.RUNNING_TASKS.get(task_id, {}).get('progress'))
        logs += "\nSTATUS: " + ("RUNNING" if self.RUNNING_TASKS.get(task_id, {}).get('isRunning') else "STOPPED")
        return logs
    

    def get_files(self, task_id):
        files = self.RUNNING_TASKS.get(task_id, {}).get('files', [])
        return [{"name": file["name"], "loc": file["loc"]} for file in files]
    

    def delete_data(self, task_id):
        driver_delete_task(task_id)
        task_id = self.RUNNING_TASKS.get(task_id)
        if task_id: self.RUNNING_TASKS.pop(task_id['task_id'])

        
    
    def create_file_download_link(self, filePath):
        response = requests.post(self.API_ENDPOINTS['generate_download_link'], json={"file_path": filePath})
        if response.status_code == 200: return response.json().get("download_link")
        else: return "https://drive.google.com/drive/file/fileNotFound"


    # Loads Heygen Accounts
    def load_accounts(self):
        if not os.path.exists(ACCOUNTS_DB):
            with open(ACCOUNTS_DB, "w") as f: json.dump({}, f)
            return {}
        else:
            with open(ACCOUNTS_DB, "r") as f: 
                return json.loads(f.read())


    # Update Specific Account
    def update_account(self, account_id, account_details):
        if not account_id or not account_details:
            raise Exception("Account Id & account details are required")
        
        self.HEYGEN_ACCOUNTS = self.load_accounts()
        self.HEYGEN_ACCOUNTS[account_id] = account_details
        self.update_and_refresh_accounts(self.HEYGEN_ACCOUNTS)


    # Remove Specific Account
    def remove_account(self, account_id):
        if not account_id:
            raise Exception("Account Id is required")

        if not self.HEYGEN_ACCOUNTS.get(account_id):
            raise Exception(f"No account is found with acc_id {account_id}")
        
        self.HEYGEN_ACCOUNTS.pop(account_id)
        self.update_and_refresh_accounts(self.HEYGEN_ACCOUNTS)
        return "Deleted Successfully"

    
    # Get All Accounts
    def get_accounts(self):
        return [self.HEYGEN_ACCOUNTS[x]['account_id'] for x in list(self.HEYGEN_ACCOUNTS.keys())]


    # Get Account Details
    def get_account(self, account_id):

        if not account_id: raise Exception("Account Id is required")
        account_data = self.HEYGEN_ACCOUNTS.get(account_id)
        if not account_data: raise Exception(f"No account is found with acc_id {account_id}")
        else: return account_data


    # Add New Account
    def add_account(self, account_id, username, password, is_paid):

        if not account_id: raise Exception("Unique Account Id is required")
        if not username or not password: raise Exception("Authentication details 'username or password' not provided")
        if self.HEYGEN_ACCOUNTS.get(account_id):raise Exception(f"Account with id {account_id} already exists")
        
        self.HEYGEN_ACCOUNTS[account_id] = {"account_id": account_id, "username": username, "password": password, "is_paid": is_paid}
        print(f"Here it is: {self.HEYGEN_ACCOUNTS[account_id]}")
        self.update_and_refresh_accounts(self.HEYGEN_ACCOUNTS)



    def random_time_sleep(self, a, b):
        time.sleep(random.uniform(a, b))
        return
    


    def request_chrome_driver(self, profile_name, headless):
        try:
            profile = driver_get_task(profile_name)
            if not profile: 
                res = driver_add_task(profile_name, "HEYGEN", "Heygen - Create Video", None, 'desktop', {})
                print(res)
            response = driver_run_driver(profile_name, headless)
            print(response)
            if not response and type(response) == tuple:
                if not response[1]: raise Exception(f"Failed to get chrome driver [initialization]! {response[0]}")

            options = ChromeOptions()
            options.add_argument(f"--remote-debugging-port={response['port']}")
            driver = uc.Chrome(options=options, headless=False)
            return driver
        except Exception as e:
            raise Exception(str(e))
    


    def generate(self, account_id, avatar_file_path, audio_file_path, is_portrait=True, headless_browser=False ):

        if not account_id: raise Exception("Account Id is required")
        account_details = self.HEYGEN_ACCOUNTS.get(account_id)
        if not account_details:raise Exception(f"No account is linked with account id {account_id}")
        task_id = "heygen_"+str(random.randint(11111,99999))

        self.RUNNING_TASKS[task_id] = {
            'task_id': task_id, 
            'feature': "HEYGEN", 
            "task_type": f"HEYGEN - Generate Video",
            "tags": f"Generate Video, {account_details['username']}, {[os.path.basename(avatar_file_path)]}", 
            "progress": 0, 
            "logs": """""", 
            "isRunning": True, 
            "files": []
        }
        time.sleep(2)
        Thread(target=self.generate_heygen_video, args=[task_id, account_id, avatar_file_path, audio_file_path, None, None, None, is_portrait, headless_browser], daemon=True).start()
        return {"task_id": task_id}



    def generate_heygen_video(self, task_id, account_id, avatar_file_path, audio_file_path, video_name=None, avatar_name=None, audio_file_name=None, is_portrait=True, headless_browser=False ): 
        try:
            account_details = self.HEYGEN_ACCOUNTS.get(account_id)
            print("Here is new Data: ", account_details, type(account_details['is_paid']))
            is_paid_acc = account_details['is_paid']
            HEYGEN_API = heygen_local_api(isPaid=False if is_paid_acc == "false" or not is_paid_acc else True)

            if not video_name: video_name = "project_" + str(random.randint(10000, 99999))
            if not avatar_name: avatar_name = "avatar_" + str(random.randint(10000, 99999))
            if not audio_file_name: audio_file_name = "audio_" + str(random.randint(10000, 99999)) + "_" + os.path.basename(audio_file_path)
        
            if not HEYGEN_API.verify_user(email=account_details['username']):
                self.RUNNING_TASKS[task_id]['logs'] += f"\nTrying to login account..."

                HEYGEN_DRIVER = HEYGEN_DRIVER_(self.request_chrome_driver(account_id, headless_browser), account_details)
                HEYGEN_DRIVER.driver.get("https://app.heygen.com/avatars")

                status = HEYGEN_DRIVER.isLogedin()
                if not status:  HEYGEN_DRIVER.login()

                cookies = HEYGEN_DRIVER.driver.execute_cdp_cmd("Network.getAllCookies", {})['cookies']
                HEYGEN_API.add_heygen_cookies(cookies)

                self.RUNNING_TASKS[task_id]['logs'] += f"\nCookies Fetched Successfully with session key..."
                HEYGEN_DRIVER.driver.quit()

    
            audio_upload_id = HEYGEN_API.upload_assets(audio_file_name, audio_file_path, 'audio')
            self.RUNNING_TASKS[task_id]['progress'] = 10
            self.RUNNING_TASKS[task_id]['logs'] += f"\n{'{:<{}}'.format('Audio ID: ', 15)} {audio_upload_id}"
            # print(f"{'{:<{}}'.format('Audio ID: ', 15)}", audio_upload_id)

            if audio_upload_id: 
                avatar_upload_id = HEYGEN_API.upload_avatars(avatar_name, avatar_file_path)
                self.RUNNING_TASKS[task_id]['progress'] = 20
                self.RUNNING_TASKS[task_id]['logs'] += f"\n{'{:<{}}'.format('Avatar ID: ', 15)} {avatar_upload_id}"
                # print(f"{'{:<{}}'.format('Avatar ID: ', 15)}", avatar_upload_id)

                while True:
                    self.random_time_sleep(7, 14)
                    video_resol = [(540, 960), (720, 1280)]
                    video_generated_id = HEYGEN_API.generate_video(video_name, avatar_name, avatar_upload_id, audio_file_name, audio_file_path, isPortrait=is_portrait, video_resolution=None)  # video_resolution=video_resol[1]
                    self.RUNNING_TASKS[task_id]['logs'] += f"\n{'{:<{}}'.format('Video ID: ', 15)} {video_generated_id}"
                    # print(f"{'{:<{}}'.format('Video ID: ', 15)}", video_generated_id)
                    if not video_generated_id: continue
                    self.RUNNING_TASKS[task_id]['progress'] = 45
                    break

                while True:
                    progress, status = HEYGEN_API.check_video_progress(video_generated_id)
                    self.RUNNING_TASKS[task_id]['logs'] += f"\n{'{:<{}}'.format('Progress: ', 15)}{round(progress, 2)}  [{status}]"
                    # print(f"{'{:<{}}'.format('Progress: ', 15)}{round(progress, 2)}  [{status}]")
                    if int(progress) > 95 or status.lower() == "completed": 
                        self.RUNNING_TASKS[task_id]['progress'] = 80
                        break
                    self.random_time_sleep(12, 13)

                downloadLinks = HEYGEN_API.getVideoDownloadLink(video_generated_id)
                high_reso_download_link = downloadLinks[list(downloadLinks.keys())[-1]]
                self.RUNNING_TASKS[task_id]['progress'] =  90
                self.RUNNING_TASKS[task_id]['files'] = [{"name": video_name, "loc": high_reso_download_link}]

                HEYGEN_API.delete_avatar(avatar_upload_id)
                HEYGEN_API.delete_asset(audio_upload_id)
                self.RUNNING_TASKS[task_id]['progress'] = 100
                self.RUNNING_TASKS[task_id]['isRunning'] = False
                
                # response = self.HEYGEN_API.delete_video(video_generated_id)
                # self.HEYGEN_API.download_file(high_reso_download_link)

        except Exception as e:
            self.RUNNING_TASKS[task_id]['progress'] = 100
            self.RUNNING_TASKS[task_id]['isRunning'] = False
            self.RUNNING_TASKS[task_id]['logs'] += f"\nFailed Error: \n{e}"
            try:
                HEYGEN_API.delete_avatar(avatar_upload_id)
                HEYGEN_API.delete_asset(audio_upload_id)
            except: pass
            return str(e), False

    