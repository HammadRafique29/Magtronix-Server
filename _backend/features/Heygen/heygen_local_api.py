import os
import json
import time
import random
import string
import requests
import platform
import urllib.request
from pathlib import Path
from pydub import AudioSegment
from urllib.parse import urlparse, parse_qs, unquote

import warnings
warnings.filterwarnings("ignore")


# Add Heygen Cookie   (add_heygen_cookies)   - Add Cookies i.e heygen_session before starting using requests     -> None
# Generate RandomID   (generate_id)          - Generate Random 8 Char Long Ids for temp use on tags              -> str
# Storage Request     (storage_request)      - Request for pre-signed url to upload audio file on AMZ Bucket     -> JSON
# Delete Asset        (delete_asset)         - Delete specific asset file based on asset ID.                     -> 200
# Get Audio Duration  (get_audio_duration)   - Returns the exact duration of an audio file in seconds.           -> Float
# Get Single Avartar  (getAvatar_by_id)      - Get Specific Avatar Details (more results - listAvatarAssets)     -> JSON
# Get Video Link      (getVideoDownloadLink) - Get Videos Download Links, multiple resolutions 720, 1080, etc    -> JSON
# Get Photar Details  (getPhotarDetails)     - Get Photr detials like width, height, preview, etc                -> JSON
# Upload File Server  (upload_file_to_s3)    - Upload file to Amzon Buckets using presigned URL                  -> 200
# Update File Server  (update_uploaded_file)  - Update Uploaded File with name (after upload_file_to_s3).        -> JSON
# Upload Assets       (upload_assets)        - Upload Asset directly to Heygen Assets Page, both Img, Audio      -> Asset Id
# Upload Avatars      (upload_avatars)       - Upload Avatars directly to Heygen Avatars Page, [PHOTO]           -> Group Id
# List Audios Assets  (listAudioAssets)      - List All Audios assets stored in Heygen Assets Page               -> Assets [List]
# List Avatar Assets  (listAvatarAssets)     - List All Avatars upload to Heygen Avatars Page                    -> Assets [List]
# Create draft video  (create_draft_video)   - Draft Video is created for video generation (step1)               -> video ID.
# Save draft video    (save_draft_video)     - Save the video after created with video name & other details      -> Video ID.
# Prepare Video       (prepare_video)        - Preapre Video data for final video generation [JSON]              -> Request [JSON].
# Prepare Video       (prepare_video)        - Preapre Video data for final video generation [JSON]              -> Request [JSON].
# Submint Video       (enerate_video)        - Submit Video for generation after saving draft video [Final]      -> Download ID



class heygen_local_api:

    def __init__(self, isPaid): 

        self.isPaid = isPaid
        self.STORAGE_URL = "https://api2.heygen.com/v1/file/url.get"
        self.UPDATE_AUDIO_URL = "https://api2.heygen.com/v1/file.upload"
        self.DELETE_ASSET_URL = "https://api2.heygen.com/v1/asset.delete"
        self.LIST_ALL_AVATARS_URL = "https://api2.heygen.com/v1/avatar_group/photo.private.list"
        self.LIST_AUDIO_ASSET_URL = "https://api2.heygen.com/v1/heygen_project_item/list"
        self.LIST_AVATAR_ASSET_URL = "https://api2.heygen.com/v1/avatar_group/photo.private.list"
        self.GET_SINGLE_AVATAR_URL = "https://api2.heygen.com/v1/avatar.get?avatar_id={}&avatar_type=photar"
        self.CREATE_DRAFT_VIDEO_URL = "https://api2.heygen.com/v1/pacific/draft/create" 
        self.SAVE_DRAFT_VIDEO_URL  = "https://api2.heygen.com/v1/pacific/draft/save"
        self.VIDEO_GENERATE_URL  = "https://api2.heygen.com/v3/video.generate"
        self.VIDEO_DOWNLOAD_DETAILS_URL = "https://api2.heygen.com/v1/pacific/collaboration/video.details"

        self.cookies = { }
        self.COOKIES_PATH = os.path.join(os.getcwd(), "cookies.json")
        self.load_cookies()

        self.headers = {
            "authority": "api2.heygen.com",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "x-path": "/assets",
            "x-zid": "T4xtODxkbkN5FS80wWbvAiiY722wLHK6",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }




    def verify_user(self, email):
        try:
            url = "https://api2.heygen.com/v1/space/user.list"

            headers = self.headers
            headers['path'] = "/v1/space/user.list"
            headers['x-path'] = "/home"

            response = requests.get(url, headers=headers, cookies=self.cookies)
            response = response.json()
            if response['data'][0]['email'] == email: return True
            else: return False
            
        except Exception as e:return False



    def add_heygen_cookies(self, cookies):
        formatted_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
        self.cookies = formatted_cookies
        with open(self.COOKIES_PATH, 'w') as f: f.write(json.dumps(self.cookies))



    def load_cookies(self):
        if os.path.exists(self.COOKIES_PATH):
            with open(self.COOKIES_PATH, 'r') as f: self.cookies = json.loads(f.read())



    def get_audio_duration(self, file_path):
        audio = AudioSegment.from_file(file_path)
        return round(audio.duration_seconds, 3)
    


    def generate_id(self):
        return str(''.join(random.choices(string.ascii_letters + string.digits, k=8)))
    



    def storage_request(self, storage_type="audio"):
        try:
            params = {"file_type": storage_type, "pipeline": "asset" }
            response = requests.get(self.STORAGE_URL, params=params, cookies=self.cookies, headers=self.headers)
            return response.json()
        
        except Exception as e:
            raise Exception(f"ERROR! Failed To Send Upload File Storage Request. \n{e} ")




    def upload_file_to_s3(self, file_path, tmp_storage):
        try:
            pre_signed_url = tmp_storage['data']['url']
            file_key = tmp_storage['data']['key']

            with open(file_path, 'rb') as file:
                headers = {
                    "Content-Type": "audio/mpeg",
                    "x-amz-server-side-encryption": "AES256"
                }
                response = requests.put(pre_signed_url, data=file, headers=headers)
                if response.status_code == 200: return True
                return False
            
        except Exception as e:
            raise Exception(f"ERROR! Failed To Upload File To S3. \n{e} ")
                



    def update_uploaded_file(self, name, id, storage_type='audio'):
        try:
            payload = { "name": name, "id": id, "file_type": storage_type, "pipeline": "asset" }
            response = requests.post(self.UPDATE_AUDIO_URL, headers=self.headers, cookies=self.cookies, json=payload)
            return response.json()
        
        except Exception as e:
            raise Exception(f"ERROR! Failed To Update Uploaded {name}. \n{e} ")
        
    



    def delete_video(self, id):
        try:
            url = f"https://api2.heygen.com/v1/pacific/videos.trash"
            headers = self.headers
            headers['path']   =  f"/v1/pacific/videos.trash"
            headers['scheme'] = "https"
            headers['method'] =  "POST"
            headers['accept'] = "application/json, text/plain, */*"
            headers['x-path'] = "/home"
            payload = {"video_ids":[id]}

            response = requests.post(url, headers=headers, data=json.dumps(payload), cookies=self.cookies)
            if response.status_code == 200:
                response = response.json()
                return True
            else: raise Exception(response.text)
        
        except Exception as e:
            raise Exception(f"ERROR! Failed To Delete Avatar File {id}. \n{e} ")





    def delete_avatar(self, id):
        try:
            url = f"https://api2.heygen.com/v1/avatar_group.delete?id={id}"
            headers = self.headers
            headers['path']   =  f"/v1/avatar_group.delete?id={id}"
            headers['scheme'] = "https"
            headers['method'] =  "DELETE"
            headers['accept'] = "application/json, text/plain, */*"
            headers['x-path'] = "/avatars"

            response = requests.delete(url, headers=headers, cookies=self.cookies)
            if response.status_code == 200:
                response = response.json()
                return True
            else: raise Exception(response.text)
        
        except Exception as e:
            raise Exception(f"ERROR! Failed To Delete Avatar File {id}. \n{e} ")





    def delete_asset(self, ids):
        try:
            # Headers Sections
            headers = self.headers
            headers['path']   =  "/v1/asset.delete"
            headers['scheme'] = "https"
            headers['method'] =  "POST"
            headers['authority'] =  "api2.heygen.com"
            headers['accept'] = "application/json, text/plain, */*"
            headers['x-path'] = "/assets"
            data = {"ids": [ids]}
            # Request Sections
            response = requests.post(self.DELETE_ASSET_URL, headers=headers, json=data, cookies=self.cookies)
            if response.status_code == 200:
                response = response.json()
                if response['message'] == 'Success': return True
                else: return False, response['message']
            else: raise Exception(response.text)

        except Exception as e:
            raise Exception(f"ERROR! Failed To Delete Asset File {ids}. \n{e} ")




    def listAvatarDetails(self):
        try:
            response = requests.get(self.LIST_ALL_AVATARS_URL, cookies=self.cookies, headers=self.headers)
            return response.json()
        
        except Exception as e:
            raise Exception(f"ERROR! Failed To Get Avatar Asset Details. \n{e} ")




    def getAvatar_by_id(self, id):
        try:
            # Headers Sections
            headers = self.headers
            headers['path'] = f"/v1/avatar.get?avatar_id={id}&avatar_type=photar"
            headers['scheme'] = 'https'
            headers['accept'] = 'application/json, text/plain, */*'
            headers['method'] = 'GET'
            headers['x-path'] = '/avatars/looks'
            # Request Sections
            response = requests.get(self.GET_SINGLE_AVATAR_URL.format(id), cookies=self.cookies)
            if response.status_code == 200: print(response.json())
            else:raise Exception('')

        except Exception as e:
            raise Exception(f"ERROR! Failed To Get Avatar Details by ID: {id} \n{e} ")
        



    def get_voice_ids(self):
        try:
            url = "https://api2.heygen.com/v1/public_voices?page=1&limit=29&language=Hindi"
            response = requests.get(url, headers=self.headers, cookies=self.cookies)
            voice = response.json()['data']
            print(len(voice))
            return voice
    
        except Exception as e:
            raise Exception(f"ERROR! Failed To Get Voice IDs \n{e} ")
        



    def generate_audio(self, voice_id="bc22af81440d4212acf315103d7faf82", message="Hi, How are you?"):
        try:
            url = "https://api2.heygen.com/v2/online/text_to_speech.generate"
            data = {
                "text_type": "ssml",
                "text": f"<speak><voice name='{voice_id}'><prosody rate='1' pitch='0%'>{message}</prosody></voice></speak>",
                "voice_id": f"{voice_id}",
                "settings": {"speed": 1, "pitch": 0}
            }
            response = requests.post(url, headers=self.headers, cookies=self.cookies, json=data)
            response = response.json()['data']
            return response
    
        except Exception as e:
            raise Exception(f"ERROR! Failed To Generate Voices IDs \n{e} ")
        




    def create_draft_video(self):
        try:
            # Headers Sections
            headers = self.headers
            headers['path'] = "/v1/pacific/draft/create"
            headers['scheme'] = 'https'
            headers['accept'] = 'application/json, text/plain, */*'
            headers['method'] = 'POST'
            headers['x-path'] = '/create-v3/draft'
            # Request Section
            response = requests.post(self.CREATE_DRAFT_VIDEO_URL, cookies=self.cookies, headers=headers, json={})
            if response.status_code == 200:
                response = response.json()
                video_id = response['data']['video_id']
                return video_id
            else: raise Exception('')

        except Exception as e:
            raise Exception(f"ERROR! Failed To Create Draft Video. \n{e}")
        



    def save_draft_video(self, name, video_id, draft):
        try:
            # Headers Sections
            headers = self.headers
            headers['path'] = "v1/pacific/draft/save"
            headers['scheme'] = 'https'
            headers['accept'] = 'application/json, text/plain, */*'
            headers['method'] = 'POST'
            headers['x-path'] = f'/create-v3/{video_id}'
            # Request Section
            response = requests.post(self.SAVE_DRAFT_VIDEO_URL, cookies=self.cookies, headers=headers, json=draft)
            if response.status_code == 200: return response.json()
            else: raise Exception('')
            
        except Exception as e:
            raise Exception(f"ERROR! Failed To Save Draft Video {name}. \n{e}")




    def upload_assets(self, name, file_path, storage_type):
        try:
            tmp_storage   = self.storage_request(storage_type)
            if not tmp_storage: return False
            upload_status = self.upload_file_to_s3(file_path, tmp_storage)
            if not upload_status: return False
            update_response = self.update_uploaded_file(name, tmp_storage['data']['id'], storage_type)
            return update_response.get('data', {}).get('id')
            
        except Exception as e:
            raise Exception(f"ERROR! Failed To Upload Asset {name}. \n{e}")
    
    


    def upload_avatars(self, avatar_name, avatar_file_path):
        try:
            url_base = "https://api2.heygen.com/v1/avatar_group/photo"
            
            # Create temp storage
            headers = {**self.headers, "path": "/v1/avatar_group/photo/temp.create?num_photos=1", "method": "GET", "x-path": "/avatars"}
            response = requests.get(f"{url_base}/temp.create?num_photos=1", headers=headers, cookies=self.cookies).json()
            print(response)
            pre_signed_url, file_key, temp_id = response['data']['upload_urls'][0], response['data']['keys'][0], response['data']['temporary_user_photar_ids'][0]

            # Upload avatar
            headers = {"Content-Type": "audio/mpeg", "x-amz-server-side-encryption": "AES256"}
            with open(avatar_file_path, 'rb') as file: requests.put(pre_signed_url, data=file, headers=headers)

            # Validate avatar
            headers = {**self.headers, "path": f"/v1/avatar_group/photo/temp.validate?temporary_user_photar_id={temp_id}"}
            data    = {"temporary_user_photar_id": temp_id}
            requests.get(f"{url_base}/temp.validate", headers=headers, params=data, cookies=self.cookies)

            # Generate final avatar
            data = {"parent_temporary_user_photar_id": temp_id, "name": avatar_name}
            while True:
                response = requests.get(f"{url_base}/temp.convert", headers=headers, params=data, cookies=self.cookies)
                response = response.json()
                if "Photo hasn't completed validation" in str(response.get("message", "")):
                    time.sleep(3)
                    continue
                print(response)
                break

            if not response.get('data'): raise Exception(response.get("message"))
            return response['data']['group_id']
        
        except Exception as e:
            print(e)
            raise Exception(f"ERROR! Failed To Upload Avatar. \n{e}")




    def listAudioAssets(self):
        try:
            headers = self.headers
            headers['path'] = "/v1/heygen_project_item/list?item_types=asset&limit=999"
            headers['x-path'] = "/assets"
            data = {'item_types': 'asset', 'limit': '999'}

            response = requests.get(self.LIST_AUDIO_ASSET_URL, headers=headers, cookies=self.cookies, params=data)
            if response.status_code == 200:
                response = response.json()
                return response.get('data', {}).get('list', [])
            return []
        
        except Exception as e:
            raise Exception(f"ERROR! Failed To Get Audios Assets List. \n{e}")




    def listAvatarAssets(self):
        try:
            headers = self.headers
            headers['path'] = "/v1/avatar_group/photo.private.list"
            headers['x-path'] = "/avatars"

            response = requests.get(self.LIST_AVATAR_ASSET_URL, headers=headers, cookies=self.cookies)
            if response.status_code == 200:
                response = response.json()
                return response.get('data', {}).get('avatar_groups', [])
            return []
        
        except Exception as e:
            raise Exception(f"ERROR! Failed To Get Avatar Assets List. \n{e}")
    




    def getPhotarDetails(self, id):
        try:
            url = "https://api2.heygen.com/v1/avatar.get"
            headers = self.headers
            headers['path'] = f"/v1/avatar.get?avatar_id={id}&avatar_type=photar"
            headers['x-path'] = "/avatars/looks"
            data = { 'avatar_id': id, 'avatar_type': 'photar' }

            response = requests.get(url, headers=headers, cookies=self.cookies, params=data)
            if response.status_code == 200:
                response = response.json()
                return response.get('data', {}).get('photar', {})
            return {}
        
        except Exception as e:
            raise Exception(f"ERROR! Failed To Get Avatar Assets List. \n{e}")





    def prepare_video(self, video_name, avatar_upload_id, audio_name, audio_pth, avatar_name, isPortrait=True, resolution=None):
        try:

            audio_preview_src = None
            audios_assets = self.listAudioAssets()
            for i in audios_assets:
                if i['asset_value'] == audio_name:
                    audio_preview_src = i['file_meta']['meta']['audios']['mp3']

            if not audio_preview_src: raise Exception(f"ERROR! Failed To Get Audio Asset Details (Empty).")
            if not avatar_upload_id: raise Exception(f"ERROR! Failed To Get Avatar Details (Empty).")

            while True :
                photr_details = self.getPhotarDetails(avatar_upload_id)
                if photr_details['status'] != "pending": break
                time.sleep(4)

            avatar_preview_src = photr_details['image_url']
            avatar_width = photr_details['image_width']
            avatar_height = photr_details['image_height']

            video_id = self.create_draft_video()
            audio_duration = self.get_audio_duration(audio_pth)
            print("IsPaid: ", self.isPaid, isPortrait)

            if self.isPaid:
                video_resolution_width  = 1080 if isPortrait else 1920
                video_resolution_height = 1920 if isPortrait else 1080
            else:
                video_resolution_width  = 720 if isPortrait else 1280
                video_resolution_height = 1280 if isPortrait else 720

            print("Video Resolution1: ", video_resolution_width, video_resolution_height)

            if resolution:
                video_resolution_width = resolution[0]
                video_resolution_height = resolution[1]

            print("Video Resolution2: ", video_resolution_width, video_resolution_height)

            avatar_crop_circle = {
                "x": 261.9554901123047, 
                "y": 50.27671813964844, 
                "width": 435.4571228027344, 
                "height": 435.4571228027344}
            
            avatar_close_up = {"x": 44.142578125, "y": 0, "width": 870.9142456054688, "height": 866.7588806152344}

            request_ = {
                "id": video_id,
                "title": video_name,
                "draft_info": {
                    "track": {
                        "audio": [],
                        "elements": {
                            "g4TzgzQP": {
                                "animation":None,
                                "background":None,
                                "cropX": 0,
                                "cropY": 0,
                                "dataset":None,
                                "groupId":None,
                                "height": avatar_height,
                                "id": "g4TzgzQP",
                                "left": round((avatar_width / 2.85) * (video_resolution_width / 720)) , # int(video_resolution_height / 2) + int(avatar_width / 3  # int(video_resolution_height / 2) - int(video_resolution_width / 2) * 0.200  #round((avatar_width / 2.85) * (video_resolution_width / 720))
                                "meta":None,
                                "name":None,
                                "opacity": 1,
                                "rotate": 0,
                                "scaleX": 1.947261663286004, # if isPortrait else 2.16,
                                "scaleY": 1.947261663286004, # if isPortrait else 2.16,
                                "scenes": [
                                    "7PLlXts1"
                                ],
                                "timeline": {
                                    "duration": audio_duration,
                                    "start": 0
                                },
                                "top": avatar_height-26 if isPortrait else 540 ,
                                "transition":None,
                                "width": avatar_width,
                                "fit": "none",
                                "fit_box":None,
                                "avatarAssetId": avatar_upload_id,
                                "circleBackground": "#f6f6fc",
                                "faceSwap":None,
                                "matting":False,
                                "naturalHeight": avatar_height,
                                "naturalWidth": avatar_width,
                                "processedImage": "",
                                "renderType": "normal",
                                "smileWeight":None,
                                "speechId": "",
                                "speechItemId": "",
                                "talkingPhoto":None,
                                "type": "avatar",
                                "volume": 1,
                                "eyeContact":False
                            }
                        },
                        "extendTracks": [],
                        "scenes": [
                            {
                                "background": "#ffffff",
                                "backgroundElementId":None,
                                "duration": audio_duration,
                                "elements": [
                                    "g4TzgzQP"
                                ],
                                "id": "7PLlXts1",
                                "transition":None,
                                "fit_to_speech": [],
                                "scale_with_speech":None
                            }
                        ],
                        "speech": {
                            "children": [
                                {
                                    "id": "trZGYB9Q",
                                    "type": "audio",
                                    "fileType": "upload",
                                    "audioAssetId": "5QkS4sdu"
                                }
                            ],
                            "id": "LK5yT2QE"
                        }
                    },
                    "resolution": {
                        "width": video_resolution_width,
                        "height": video_resolution_height,
                    },
                    "assets": {
                        "avatar": {
                            avatar_upload_id: {
                                "id": avatar_upload_id,
                                "version": 1,
                                "type": "avatar",
                                "gender": "unknown",
                                "avatarStateId": avatar_upload_id,
                                "isPhotar":True,
                                "isMotion":False,
                                "isCustom":False,
                                "isPrivate":True,
                                "avatarType": "photar",
                                "preview": {
                                    "normal": {
                                        "size": {
                                            "width": avatar_width, # 1080 if isPortrait else 1920 ,
                                            "height": avatar_height, # 1920 if isPortrait else 1080,
                                        },
                                        "src": avatar_preview_src
                                    }
                                },
                                "enableMatting":True,
                                "enableEnhance":True,
                                "enable4k":False,
                                "hasAlpha":False,
                                "name": avatar_name,
                                "avatarName": avatar_name,
                                "availableStyle": {
                                    "normal":True,
                                    "circle":True,
                                    "closeUp":True
                                },
                                "cropRect": {
                                    "circle":  avatar_crop_circle,
                                    # "circle": {
                                    #     "x": 0.9554901123047,
                                    #     "y": 0.27671813964844,
                                    #     "width": 435.4571228027344, # 1080 if isPortrait else 1920 ,  # 459.2821655273437,
                                    #     "height": 435.4571228027344 , # 459.28216552734375
                                    # },
                                    "closeUp": avatar_close_up
                                    # "closeUp":{
                                    #     "x": 0.142578125,
                                    #     "y": 0,
                                    #     "width": 870.9142456054688,
                                    #     "height": 866.7588806152344,
                                    # }
                                },
                                "endOffset": 0,
                                "startOffset": 0,
                                "presetVoice": {
                                    "free": {
                                        "pitch": 0,
                                        "speed": 1,
                                        "text": "Welcome to the new era of video creation with HeyGen! Simply type your script to get started!",
                                        "tts_audio_url": "https://resource.heygen.ai/text_to_speech/locale=model=id=2zquSWgvHVYqBXQb26TcdM.mp3",
                                        "tts_duration": 5.6939910000000005,
                                        "voice_gender": "male",
                                        "voice_id": "71c663964e82485eabca1f4aedd7bfc1",
                                        "voice_language": "English",
                                        "voice_name": "Troy-Natural",
                                        "provider":None,
                                        "elevenlabs_voice_settings":None
                                    },
                                    "premium": {
                                        "pitch": 0,
                                        "speed": 1,
                                        "text": "Welcome to the new era of video creation with HeyGen! Simply type your script to get started!",
                                        "tts_audio_url": "https://resource.heygen.ai/text_to_speech/locale=model=id=2zquSWgvHVYqBXQb26TcdM.mp3",
                                        "tts_duration": 5.6939910000000005,
                                        "voice_gender": "male",
                                        "voice_id": "71c663964e82485eabca1f4aedd7bfc1",
                                        "voice_language": "English",
                                        "voice_name": "Troy-Natural",
                                        "provider":None,
                                        "elevenlabs_voice_settings":None
                                    }
                                },
                                "supportDynamicFps":False,
                                "avatarGroupId": avatar_upload_id,
                                "enableEyeContact":False,
                                "avatarVersion": "V3"
                            }
                        },
                        "audio": {
                            "5QkS4sdu": {
                                "id": "5QkS4sdu",
                                "type": "audio",
                                "name": audio_name,
                                "duration": audio_duration,
                                "url": audio_preview_src
                            }
                        }
                    },
                    "beta": "0.1",
                    "meta": {
                        "fps": 25,
                        "name": video_name,
                        "videoId":None,
                        "asr": {},
                        "ttsLink": "link"
                    },
                    "scale": 1,
                    "version": "3"
                },
                "tab": "2025-02-04 21:56:07.551"
            }
            return request_

        except Exception as e:
            raise Exception(f"ERROR! Failed To Prepare Video Generation Details. \n{e}")




    def generate_video(self, vid_name, avatar_name, avatar_upload_id, audio_name, audio_pth, isPortrait, video_resolution=None ):
        try:
            request_ = self.prepare_video(vid_name, avatar_upload_id, audio_name, audio_pth, avatar_name, isPortrait, resolution=video_resolution)
            request_['video_id'] = request_['id']
            response = requests.post(self.VIDEO_GENERATE_URL, headers=self.headers, cookies=self.cookies, json=request_)
            if response.status_code == 200:
                response = response.json()
                video_generated_id = response.get('data', {}).get('id')
                return video_generated_id 

            else: raise Exception(response.text)
            
        except Exception as e:
            raise Exception(f"ERROR! Failed To Generate Video. \n{e}")
        
        
    
    def getVideoDownloadLink(self, video_generated_id):
        try:
            headers = self.headers
            headers['path'] = f"/v1/pacific/collaboration/video.details?item_id={video_generated_id}"
            headers['x-path'] = f"/videos/{video_generated_id}"
            data = { 'item_id': video_generated_id }

            response = requests.get(self.VIDEO_DOWNLOAD_DETAILS_URL, headers=headers, cookies=self.cookies, params=data)
            response = response.json()

            download_urls = {}
            for i in response['data'].get('variants', []).values(): download_urls[i['height']] = i['key']
            return download_urls

        except Exception as e:
            raise Exception(f"ERROR! Failed To Generate Video. \n{e}")
        
    


    def check_video_progress(self, videoID):
        try:
            url = "https://api2.heygen.com/v2/pacific/video/check_status"

            headers = self.headers
            headers['accept'] = "application/json, text/plain, */*"
            headers['content-type']  = "application/json"
            headers['path'] = "/v2/pacific/video/check_status"
            headers['method'] = "POST"
            headers['x-path'] = '/home'
            data = {"videos":[videoID]}

            respone = requests.post(url, cookies=self.cookies, headers=headers, json=data, verify=False)
            respone = respone.json()
            res_data = respone['data']['list'][0]
            progress, status = res_data['progress'], res_data['status']
            return progress, status
        
        except Exception as e:
            raise Exception(f"ERROR! Failed To Get Video Progress Information. \n{e}")






    def download_file(self, url, save_path=None):
        try:
            save_path = Path(save_path or (os.environ["USERPROFILE"] + "\\Downloads" if platform.system() == "Windows" else os.environ["HOME"] + "/Downloads"))
            save_path.mkdir(parents=True, exist_ok=True)
            parsed_url, query_params = urlparse(url), parse_qs(urlparse(url).query)
            filename = unquote(query_params.get("response-content-disposition", [""])[0].split("filename*=UTF-8''")[-1]) or os.path.basename(parsed_url.path)
            file_path = save_path / filename.replace(';', '')
            urllib.request.urlretrieve(url, file_path)
            return str(file_path)
        
        except Exception as e:
            raise Exception(f"ERROR! Failed To Download Video. Might be Processing right now. Try Again after 2 min \n{e}")





