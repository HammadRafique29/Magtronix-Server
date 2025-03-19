
import configparser
import http.client
import httplib2
import json
import os
import random
import sys
import time
import random
import argparse
from datetime import datetime, timedelta, timezone  # Use timezone.utc instead of UTC

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


httplib2.RETRIES = 1
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
                        http.client.IncompleteRead, http.client.ImproperConnectionState,
                        http.client.CannotSendRequest, http.client.CannotSendHeader,
                        http.client.ResponseNotReady, http.client.BadStatusLine)



DATABASE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'database')
if not os.path.exists(DATABASE_DIR): os.makedirs(DATABASE_DIR)

ACCOUNTS_FILE = os.path.join(DATABASE_DIR, 'accounts.json')
if not os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, 'w') as f: f.write(json.dumps({}))



DATABASE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'database')
ACCOUNTS_DATABASE_FILE = os.path.join(DATABASE_PATH, 'accounts.json')
if not os.path.exists(DATABASE_PATH): os.makedirs(DATABASE_PATH)



class YOUTUBE_UPLOAD:

    def __init__(self, API_ENDPOINTS={}):

        self.API_ENDPOINTS = API_ENDPOINTS
        self.VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
        self.MAX_RETRIES = 3
        self.FORCE_TOKEN_REFRESH_DAYS = 5
        self.YOUTUBE_API_SERVICE_NAME = "youtube"
        self.YOUTUBE_API_VERSION = "v3"
        self.get_iso_timestamp = lambda: datetime.now(timezone.utc).isoformat()
        self.SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
        self.YOUTUBE_ACCOUNTS = {}
        self.get_privacy_statues = lambda: ["public", "private", "unlisted"]
        self.initialize_accounts()



    def initialize_accounts(self):
        
        if os.path.exists(ACCOUNTS_DATABASE_FILE): 
            with open(ACCOUNTS_FILE, "r") as f: self.YOUTUBE_ACCOUNTS = json.load(f)
            return

        self.YOUTUBE_ACCOUNTS = {}
        with open(ACCOUNTS_FILE, 'w') as f:
            f.write(json.dumps({}))
    

    def read_accounts(self):
        with open(ACCOUNTS_FILE, 'r') as f:
            return json.load(f)
    

    def write_account_data(self, accounts):
        
        if not accounts: raise Exception("Not valid request for adding accounts data...")
        
        try:
            with open(ACCOUNTS_FILE, 'w') as f: f.write(json.dumps(accounts))
            self.YOUTUBE_ACCOUNTS = accounts
        except Exception as e:
            self.YOUTUBE_ACCOUNTS = accounts
            raise Exception(f"Error! Writing Account Data: {e}")



    def add_account(self, account_id, client_secrets):

        account_id = str(account_id)

        if account_id in self.YOUTUBE_ACCOUNTS:
            raise Exception(f"Account Already Found with Account ID: {account_id}. Try to create a unique id for account....")

        if not isinstance(client_secrets, (dict, str)) or (isinstance(client_secrets, str) and not os.path.exists(client_secrets)):
            raise Exception("Client Secret File Not Provided or Not Valid....")
        
        if os.path.exists(client_secrets) or os.path.isabs(client_secrets):
            with open(client_secrets, "r") as f: client_secrets_data = json.load(f)
        
        if isinstance(client_secrets, dict): client_secrets_data = client_secrets
            
        if not client_secrets_data.get('installed', {}).get('client_id') or not client_secrets_data.get('installed', {}).get('client_secret'):
            raise Exception("Client Secret File Not Valid....")

        accounts = self.read_accounts()
        accounts[account_id] = { "id": account_id, "client_secrets": client_secrets_data }
        self.write_account_data(accounts)

    
    def get_account(self, account_id):
        accounts = self.read_accounts()
        if account_id in accounts : return accounts[account_id]
        return None


    def get_all_accounts(self):
        accounts = self.read_accounts()
        return list(accounts.keys())


    def delete_account(self, account_id):
        accounts = self.read_accounts()
        if account_id in accounts:  accounts.pop(account_id)
        self.write_account_data(accounts)


    def update_account(self, account_id, ky, vl, remove=False):
        accounts = self.read_accounts()

        if account_id in accounts: 
            if remove:
                if accounts[account_id].get(ky, None): accounts[account_id].pop(ky)
            else: accounts[account_id][ky] = vl
        
        self.write_account_data(accounts)


    def get_client_secrets(self, account_id):
        account = self.read_accounts()
        if account_id in account: return account[account_id].get('client_secrets', None)
        return None
    
    def get_youtube_oauth2(self, account_id):
        account = self.read_accounts()
        if account_id in account: 
            code = account[account_id].get('youtube_oauth2_store', None)
            if code: return json.loads(code)
        return None



    def check_files(self, account_id):
        """Check if required files exist."""
        # required_files = [CLIENT_SECRETS_FILE]

        client_secrets = self.get_client_secrets(account_id)
        if not client_secrets: return None

        # for file in required_files:
        #     if not os.path.exists(file):
        #         print(f"Error: Required file {file} does not exist.")
        #         sys.exit(1)



    def get_youtube_categories(self, category=None):
        youtube_categories = {
            "1": "Film & Animation", "2": "Autos & Vehicles", "10": "Music", "15": "Pets & Animals", "17": "Sports", "19": "Travel & Events", 
            "20": "Gaming", "22": "People & Blogs", "23": "Comedy", "24": "Entertainment", "25": "News & Politics", "26": "Howto & Style",
            "27": "Education", "28": "Science & Technology", "29": "Nonprofits & Activism"
        }
        if not category: return [x[1] for x in youtube_categories.items()]
        else: 
            cate_id = [x[0] for x in youtube_categories.items() if x[1] == category ]
            if len(cate_id)>0: return cate_id[0]
            else: return 27



    def refresh_token_with_retry(self, creds):
        """Attempt to refresh the token with retries."""
        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            try:
                creds.refresh(Request())
                # print(f"Refresh successful: new expiry={creds.expiry}")
                return True
            except HttpError as e: pass
                # print(f"HttpError refreshing token (attempt {retry_count+1}): status={e.resp.status}, content={e.content}")
            except RefreshError as e: pass
                # print(f"RefreshError refreshing token (attempt {retry_count+1}): {e}")
            except Exception as e: pass
                # print(f"Unexpected error refreshing token (attempt {retry_count+1}): {e}")
            retry_count += 1
            time.sleep(2 ** retry_count)
        return False



    def get_authenticated_service(self, account_id, args, authorization_code=None):
        """
        Get an authenticated YouTube service object for headless systems.

        Ensures correct handling of token expiry for automatic refresh.
        Keeps creds.expiry offset-naive for library compatibility, uses custom expiry check with timezone-aware current_time.
        Compatible with Python 3.9+ using timezone.utc.
        """
        creds = None
    
        if self.get_youtube_oauth2(account_id):
        # if os.path.exists(OAUTH2_STORAGE_FILE):
            try:
                # with open(OAUTH2_STORAGE_FILE, 'r') as token:
                #     creds_data = json.load(token)

                creds_data = self.get_youtube_oauth2(account_id)
                # print(f"Loaded credentials data: {creds_data}")
                creds = Credentials.from_authorized_user_info(creds_data,self.SCOPES)
                # print(f"Existing credentials: token={creds.token[:10]}..., expiry={creds.expiry}, refresh_token={creds.refresh_token[:10]}...")
                
                current_time = datetime.now(timezone.utc)  # Timezone-aware UTC
                should_refresh = False
                
                if not creds.refresh_token:
                    # print("No refresh token available, forcing new authentication.")
                    should_refresh = True

                elif creds.expiry:
                    # Do not modify creds.expiry to keep it offset-naive for library compatibility
                    # Convert to timezone-aware for our comparison
                    expiry_aware = creds.expiry.replace(tzinfo=timezone.utc)
                    time_to_expiry = expiry_aware - current_time
                    # print(f"Token expiry: {creds.expiry}, time to expiry: {time_to_expiry}")
                    # Custom expiry check
                    is_expired = current_time >= expiry_aware
                    should_refresh = (is_expired or 
                                    time_to_expiry.total_seconds() < 300 or  # Refresh if less than 5 minutes remaining
                                    time_to_expiry.days <= -self.FORCE_TOKEN_REFRESH_DAYS or
                                    args.get("force_refresh") if isinstance(args, dict) else args.force_refresh)
                else:
                    # print("No expiry set in credentials, forcing refresh.")
                    should_refresh = True

                if should_refresh and creds and creds.refresh_token:
                    # print("Attempting to refresh token.")
                    success = self.refresh_token_with_retry(creds)
                    if success:
                        # print(f"Token refreshed: token={creds.token[:10]}..., expiry={creds.expiry}")

                        self.update_account(account_id, "youtube_oauth2_store", creds.to_json())
                        # print(f"Updated credentials saved to {account_id}")

                        # with open(OAUTH2_STORAGE_FILE, 'w') as token:
                        #     json.dump(json.loads(creds.to_json()), token)
                        #     print(f"Updated credentials saved to {OAUTH2_STORAGE_FILE}")
                    else:
                        # print("Token refresh failed after retries, forcing new authentication.")
                        self.update_account(account_id, "youtube_oauth2_store", None, remove=True)
                        # os.remove(OAUTH2_STORAGE_FILE)
                        creds = None
                        
            except (ValueError, json.JSONDecodeError) as e:
                # print(f"Invalid or corrupted credentials file ({e}), initiating new authentication.")
                # os.remove(OAUTH2_STORAGE_FILE)
                self.update_account(account_id, "youtube_oauth2_store", None, remove=True)
                creds = None

        if not creds or not creds.valid:

            client_secrets = self.get_client_secrets(account_id)
            if not client_secrets:
                raise Exception(f"Client Secret Not found for account id {account_id} during authentication.")
            
            flow = InstalledAppFlow.from_client_config(
                client_secrets, self.SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob")
            
            # flow = InstalledAppFlow.from_client_secrets_file(
            #     CLIENT_SECRETS_FILE,self.SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob")
            
            if not authorization_code:

                # print("No valid credentials found, initiating manual authentication for headless system.")

                authorization_url, _ = flow.authorization_url(
                    access_type='offline',
                    include_granted_scopes='true'
                )
                
                # print(f"Please visit this URL on a device with a browser to authorize the application:")
                print(authorization_url)
                return "NEED_AUTHENTICATION", authorization_url
            

            # code = input("Enter the authorization code: ").strip()
            # print(f"Code entered: {code}")
            code = authorization_code
            
            try:
                flow.fetch_token(code=code)
                creds = flow.credentials
                # print(f"Credentials obtained: token={creds.token[:10]}..., expiry={creds.expiry}, refresh_token={creds.refresh_token[:10]}...")
                if not creds.expiry:
                    # print("Warning: No expiry set after initial authentication, setting manually.")
                    creds.expiry = datetime.utcnow() + timedelta(seconds=3600)  # Keep offset-naive for library
            except Exception as e:
                print(f"Failed to fetch token with code: {e}")
                raise Exception("Failed to fetch token with code.")
                # sys.exit(1)

            # with open(OAUTH2_STORAGE_FILE, 'w') as token:
            #     json.dump(json.loads(creds.to_json()), token)
            #     print(f"Credentials saved to {OAUTH2_STORAGE_FILE}, expiry={creds.expiry}")

            self.update_account(account_id, "youtube_oauth2_store", creds.to_json())
            # print(f"  Credentials saved for {account_id}, expiry={creds.expiry}")

        if creds and not creds.valid and creds.refresh_token:
            # print("Credentials invalid but refresh token available, attempting final refresh.")
            success = self.refresh_token_with_retry(creds)
            if success:
                # with open(OAUTH2_STORAGE_FILE, 'w') as token:
                #     json.dump(json.loads(creds.to_json()), token)
                self.update_account(account_id, "youtube_oauth2_store", creds.to_json())
                # print(f"Credentials refreshed: token={creds.token[:10]}..., expiry={creds.expiry}")
            else:
                # print(f"Final refresh attempt failed. Please re-authenticate manually for account_id {account_id}")
                # os.remove(OAUTH2_STORAGE_FILE)
                # sys.exit(1)
                self.update_account(account_id, "youtube_oauth2_store", None, remove=True)
                raise Exception(f"Final refresh attempt failed. Please re-authenticate manually or try to add account again for account_id {account_id}")

        return build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION, credentials=creds)




    def initialize_upload(self, youtube, options):
        """Initialize and execute the upload process for a video to YouTube."""
        tags = None
        if options.get("keywords"):
            tags = options.get("keywords").split(",")

        body = dict(
            snippet=dict(
                title=options.get("title"),
                description=options.get("description"),
                tags=tags,
                categoryId=self.get_youtube_categories(options.get("category", "Entertainment")),
                defaultLanguage=options.get("language"),
                defaultAudioLanguage=options.get("defaultAudioLanguage") if options.get("defaultAudioLanguage") else None,
                recordingDetails=dict(
                    location=dict(
                        latitude=float(options.get("latitude")) if options.get("latitude") else None,
                        longitude=float(options.get("longitude")) if options.get("longitude") else None
                    )
                ) if options.get("latitude") and options.get("longitude") else None
            ),
            status=dict(
                privacyStatus=options.get("privacyStatus"),
                selfDeclaredMadeForKids=options.get("madeForKids"),
                license=options.get("license"),
                publicStatsViewable=options.get("publicStatsViewable"),
                publishAt=options.get("publishAt") if options.get("publishAt") else None
            )
        )

        if options.get("ageGroup") or options.get("gender") or options.get("geo"):
            body['status']['targeting'] = {}
            if options.get("ageGroup"):
                body['status']['targeting']['ageGroup'] = options.get("ageGroup")
            if options.get("gender"):
                body['status']['targeting']['genders'] = [options.get("gender")]
            if options.get("geo"):
                body['status']['targeting']['countries'] = options.get("geo").split(',')

        insert_request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(options.get("videofile"), chunksize=-1, resumable=True)
        )

        response = self.resumable_upload(insert_request)
        
        if options.get("thumbnail"):
            self.upload_thumbnail(youtube, response['id'], options.get("thumbnail"))
        
        if options.get("playlistId"):
            self.add_video_to_playlist(youtube, response['id'], options.get("playlistId"))

        return { "rtn": "response/success", "value": f"Video with id {response['id']} was successfully uploaded."}




    def add_video_to_playlist(self, youtube, video_id, playlist_id):
        """Add the uploaded video to a specified playlist."""
        add_video_request = youtube.playlistItems().insert(
            part="snippet",
            body={
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }
        )
        response = add_video_request.execute()
        print(f"Video {video_id} added to playlist {playlist_id}")




    def upload_thumbnail(self, youtube, video_id, thumbnail_path):
        """Upload a thumbnail for the video if specified."""
        try:
            request = youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            )
            response = request.execute()
            print(f"Thumbnail uploaded for video {video_id}: {response}")
        except HttpError as e:
            print(f"An error occurred while uploading the thumbnail: {e}")




    def resumable_upload(self, insert_request):
        """Implement resumable upload with exponential backoff strategy."""
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                print("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print(f"Video id '{response['id']}' was successfully uploaded.")
                        return response 
                    else:
                        raise Exception(f"The upload failed with an unexpected response: {response}")
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = f"A retriable error occurred: {e}"

            if error is not None:
                print(error)
                retry += 1
                if retry > self.MAX_RETRIES:
                    raise Exception("Failed with maximum retry limit. Try again later....")
                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print(f"Sleeping {sleep_seconds} seconds and then retrying...")
                time.sleep(sleep_seconds)

        return None
    


    def add_youtube_account(self, account_id, client_secrets, authorization_code=None):

        self.add_account(account_id, client_secrets)

        if account_id not in self.YOUTUBE_ACCOUNTS:
            raise Exception(f"Account Id not found in database. Please add account first. {account_id}")
        
        client_secrets = self.get_client_secrets(account_id)
        if not client_secrets: 
            raise Exception(f"Failed to get client secrets associated with account {account_id}. Add account again")


        response = self.get_authenticated_service(account_id, args={"no_upload":True, "force_refresh":True}, authorization_code=authorization_code)

        if isinstance(response, tuple):
            if str(response[0]) == "NEED_AUTHENTICATION":
                return {"rtn": "response/md", "value": f"Authorization URL: \n\n{response[1]}\n\nCopy and Paste In Your Browser.\nAfter Verification, go to `Re-Authenticate-Account` & enter you autorization code"}
            
        elif isinstance(response, build):
            return "Authorization Completed! You can upload video now."

        else: return "Authorization Completed! You can upload video now."


    
    def re_authenticate_youtube_account(self, account_id, authorization_code=None):

        if account_id not in self.YOUTUBE_ACCOUNTS:
            raise Exception(f"Account Id not found in database. Please add account first. {account_id}")
        
        client_secrets = self.get_client_secrets(account_id)
        if not client_secrets: 
            raise Exception(f"Failed to get client secrets associated with account {account_id}. Add account again")

 
        response = self.get_authenticated_service(account_id, args={"no_upload":True, "force_refresh":True}, authorization_code=authorization_code)

        if isinstance(response, tuple):
            if str(response[0]) == "NEED_AUTHENTICATION":
                return {"rtn": "response/md", "value": f"Authorization URL: \n\n{response[1]}\n\nCopy and Paste In Your Browser.\nAfter Verification, go to `Re-Authenticate-Account` & enter you autorization code"}

        else: return "Authorization Completed! You can upload video now."



    def upload_video(
            self,
            account_id,                               # Account ID
            videofile,                                # Video File Path
            video_title,                                    # Video Ttile
            thumbnail=None,                           # Thumbnail File Path
            description="Testing Description",        # Video Description
            category="Comedy",                        # Category Name or ID
            keywords="Magtronix, Magtronix Server",   # "Video keywords, comma separated"
            privacyStatus="public",                   # get_privacy_statues
            latitude=0.0,                             # latitude in float
            longitude=0.0,                            # longitude in float
            language="en",                            # language 'en'
            playlistId=None,                          # Youtube platlistID
            license="youtube",                        # Youtube license
            publishAt=None,                           # Publish time in UTC
            publicStatsViewable=False,                # Stats (bool)
            madeForKids=False,                        # Made for Kids (bool)
            ageGroup=None,                            # Age Group (age18_24)
            gender=None,                              # male, female              
            geo=None,                                 # Geographic targeting (comma-separated ISO 3166-1 alpha-2 country codes)
            defaultAudioLanguage=None,                # Default audio language for the video
            no_upload=False,                          # No upload during authentication
            force_refresh=True                        # Force to refresh token automatically
        ):

        kwargs = {  
            "videofile": videofile,
            "title": video_title,
            "description": description,
            "category": category,
            "keywords": keywords,                 
            "privacyStatus": privacyStatus,       
            "latitude": latitude,
            "longitude": longitude,
            "language": language,
            "playlistId": playlistId,
            "thumbnail": thumbnail,
            "license": license,
            "publishAt": publishAt,
            "publicStatsViewable": publicStatsViewable,
            "madeForKids": madeForKids,
            "ageGroup": ageGroup,
            "gender": gender,
            "geo": geo,
            "defaultAudioLanguage": defaultAudioLanguage,
            "no_upload": no_upload,
            "force_refresh": force_refresh
        }

        if account_id not in self.YOUTUBE_ACCOUNTS:
            raise Exception(f"Account Id not found in database. Please add account first. {account_id}")
        
        client_secrets = self.get_client_secrets(account_id)
        if not client_secrets: raise Exception(f"Failed to get client secrets associated with account {account_id}. Add account again")

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        youtube = self.get_authenticated_service(account_id, kwargs)
        if isinstance(youtube, tuple):
            if str(youtube[0]) == "NEED_AUTHENTICATION":
                return {"rtn": "response/str", "value": f"Authentication Expired. Validate again using 'Re_Authenticate_Youtube_Account' module...\n Authentication URL: {youtube[1]}\nCopy and Paste In Your Browser.\nAfter Verification, enter you autorization code"}
        
        try: return self.initialize_upload(youtube, kwargs)
        except HttpError as e:

            error_response = e.content
            error_str = error_response.decode("utf-8")
            error_json = json.loads(error_str)

            for error in error_json["error"]["errors"]:
                error["message"] = error["message"].replace("\\u003c", "<").replace("\\u003e", ">").replace("\\u0022", '"')

            error_json["error"]["message"] = error_json["error"]["message"].replace("\\u003c", "<").replace("\\u003e", ">").replace("\\u0022", '"')
            # print(f"An HTTP error {e.resp.status} occurred: {json.dumps(error_json, indent=2)}")
            raise Exception(f"An HTTP error {e.resp.status} occurred:\n{json.dumps(error_json, indent=2)}")
            


