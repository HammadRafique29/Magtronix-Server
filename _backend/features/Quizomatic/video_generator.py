import os
import sys
import json
import shutil
import ctypes
import requests
import tempfile
import platform
import openpyxl
import warnings
import argparse
import subprocess
from threading import Thread
from random import randint
from ctypes import wintypes
from datetime import datetime
from pydub import AudioSegment
from colorama import Fore, Style, init as ColorInit
from moviepy.editor import VideoFileClip, concatenate_videoclips
warnings.filterwarnings("ignore", category=UserWarning)

os.environ["PYTHONIOENCODING"] = "utf-8"

# def is_admin():
#     try: return ctypes.windll.shell32.IsUserAnAdmin()
#     except: return False

# if not is_admin():
#     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
#     sys.exit()



ColorInit()
systemName = platform.system()

if systemName == "Windows": ctypes.windll.kernel32.SetConsoleTitleW("Video Generator")

YLCLR = Fore.YELLOW
GRCLR = Fore.GREEN
RDCLR = Fore.RED
RSCLR = Fore.RESET
BLCLR = Fore.BLUE

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

RUNNING_DIR      = os.path.join(CUR_DIR, "python_resource")
PUBLIC_DIR       = os.path.join(CUR_DIR, "public")
silent_1_sec     = os.path.join(RUNNING_DIR, '1silent-audio.wav')
timerAudio       = os.path.join(RUNNING_DIR, 'ticktick.mp3') 
combined_audio   = os.path.join(RUNNING_DIR, 'combined_audio.mp3')
NODE_MODULE_DIR  = os.path.join(CUR_DIR, "node_modules")
FFMPEG_BIN_PATH  = os.path.join(CUR_DIR, "ffmpeg", "bin")

if not os.path.exists(RUNNING_DIR):      os.makedirs(RUNNING_DIR)

QUESTION_AUDIO  = os.path.join(PUBLIC_DIR, "assets", "audios", "q1.wav")
OPTIONS_AUDIO   = os.path.join(PUBLIC_DIR, "assets", "audios", "o1.wav")
ANSWERS_AUDIO   =  os.path.join(PUBLIC_DIR,"assets", "audios", "an1.wav")
COMINED_AUDIO   = os.path.join(PUBLIC_DIR, "assets", "audios", "combined_audio.mp3")
BKG_IMAGE       = os.path.join(PUBLIC_DIR, "assets", "background_image.jpg")
VIDEO_GENERATION_DATA = os.path.join(PUBLIC_DIR, "assets", "video_generation_data.json")
DEFAULT_RENDERING_INPUT_SHEET = "data.xlsx"

ADD_TRANSCRIBED_DIR   = f"""{RSCLR}-- Add Project Transcibed Folder (y/n): {YLCLR}"""
INPUT_TRANSCRIBED_DIR = f"""{RSCLR}-- Enter Transcibed Folder: {YLCLR}"""
INPUT_DEFAULT_SHEET   = f"""{RSCLR}-- Use Default Sheet {Fore.GREEN}'FILEPATH'{Fore.RESET} (y/n): {YLCLR}"""
INPUT_USER_SHEET      = f"""{RSCLR}-- Enter Input Sheet Path: {YLCLR}"""
INPUT_DO_RENDERING    = f"""{RSCLR}-- Do Multiple Rendering (y/n): {YLCLR}"""
INPUT_DO_PORTRAIT    = f"""{RSCLR}-- Use Portrait Mode (y/n): {YLCLR}"""
INPUT_RENDER_LIMIT    = f"""{RSCLR}-- Number Of Videos (1,2,3..): {YLCLR}"""

clearScreen = lambda: os.system("cls") if systemName == "Windows" else os.system("clear")

INFORMATION = f"""{BLCLR}
#########################################################################################################
--------------------------------------- Quiz VIDEO GENERATOR --------------------------------------------
#########################################################################################################

    Developed By:   Hammad Rafique                                  Email: hammadrafique029@gmail.com
    Github Profile: @HammadRafique29                                Date:  9 March 2025 - 10:12 PM (PTC)  

    {YLCLR}Running Through Terminal{BLCLR} ---------------------------------------------------------------------------

    -- project_folder       :   Enter project directory containing,` data.xlsx`, `Images`, `Audios`
    -- renderMultipleVideos :  Used To Show Counter On Videos Top (Multi-Video-Generator)  --multi
    -- isPortrait           :  set Portrait mode to True [Youtube Shorts]

    -- python QUIZ_VIDEO_GENERATOR.py --file [FILE PATH] --multi [LIMIT]  --isPortrait

    {YLCLR}Normal Execution{BLCLR} ------------------------------------------------------------------------------------

    -- Use Project Path     :  Will Look For File In Current Folder With Name "{os.path.basename(DEFAULT_RENDERING_INPUT_SHEET)}"
    -- Multiple Rendering   :  Want To Create Multiple Videos In Single Video "Yes/No"
    -- No Muliple Rendering :  If "Multiple Rendering", How Many Videos In Single Video.
    -- Portrait Mode        :  Video made for youtube shorts or in portrait mode
    
###########################################################################################################{RSCLR}
"""

PROGRAM_INSTRUCTIONS = f"""
    {Fore.RED}No Problem! Below instruction will help you Input Sheet to program.
    - Provide project directory containing, [data.xlsx, Images, Audios] Through Terminal {GRCLR}{'python3' if systemName != 'Windows' else 'python'} Video_Generator.py [project_folder]{RSCLR}
    - More Terminal Commands are below....

    -- Use Project Path     :  Will Look For File In Current Folder With Name "{os.path.basename(DEFAULT_RENDERING_INPUT_SHEET)}"
    -- Multiple Rendering   :  Want To Create Multiple Videos In Single Video "Yes/No"
    -- No Muliple Rendering :  If "Multiple Rendering", How Many Videos In Single Video.
    -- Portrait Mode        :  Video made for youtube shorts or in portrait mode
    """

OPENING_SHEET_ERROR = f"""
    {RDCLR}ERROR OPENING SHEET:
    - FILEPATH {RDCLR}
    - Please Verify That You Provided The Correct Path....{RSCLR}.
    """
ERROR_READING_DATA = f"""
    {RDCLR}EMPTY: Unable To Find Data Insde sheet. 
    - FILEPATH {RSCLR}
    """

ERROR_TRANSCRIBED_SHEET = f"""
    {RDCLR}ERROR! Unable To Find xlsx File Inside.
    - FILEPATH {RDCLR}
    - Please Verify That You Provided Transcribed Folder Contains xlsx file....{RSCLR}.
    """

ERROR_TRANSCRIBED_DIR = f"""
    {RDCLR}ERROR! Unable To Process Provided Path.
    - FILEPATH {RDCLR}
    - Please Verify That You Provided Correct Path....{RSCLR}.
    """

ERROR_UNZIP_FFMPEG = f"""
    {RDCLR}ERROR: Please Unzip {GRCLR}"ffmpeg.7z"{RDCLR} in Current Folder & than Rename 
    {GRCLR}"ffmpeg-2024-12-16-git-d2096679d5-essentials_build"{RDCLR} (Extracted Folder) With {GRCLR}'ffmpeg'.{RSCLR}
"""

temp_video_data  = {
    "template": "single",
    "videoCount": 1,
    "videoData": [
        {   "questionText": "",
            "optionstext": "",
            "answerText": "",
            "questionAudio": "",
            "optionsAudio": "",
            "answerAudio": "",
            "combinedAudio": "",
            "backgroundImage": ""  
        }
    ]
}



class QUIZOMATIC:

    def __init__(self, API_ENDPOINTS={}):

        self.API_ENDPOINTS = API_ENDPOINTS
        self.RUNNING_TASKS = {}
        self.VIDEO_RESOLUTIONS = [
            {"resolution": "3840x2160", "desc": "4K UHD (YouTube, high-end displays)"},
            {"resolution": "2560x1440", "desc": "1440p QHD (YouTube, high-end monitors)"},
            {"resolution": "1920x1080", "desc": "1080p Full HD (YouTube standard, most screens)"},
            {"resolution": "1280x720", "desc": "720p HD (YouTube minimum HD)"},
            {"resolution": "854x480", "desc": "SD 480p (Standard Definition)"},
            {"resolution": "640x360", "desc": "360p (Low quality, mobile data saving)"},
            {"resolution": "426x240", "desc": "240p (Very low quality, slow networks)"},

            # Mobile Resolutions (Landscape)
            {"resolution": "2960x1440", "desc": "Samsung Galaxy S8/S9/S10+ (QHD+)"},
            {"resolution": "2778x1284", "desc": "iPhone 12 Pro Max (Super Retina XDR)"},
            {"resolution": "2688x1242", "desc": "iPhone XS Max (Super Retina)"},
            {"resolution": "2532x1170", "desc": "iPhone 12/13 (Retina)"},
            {"resolution": "2340x1080", "desc": "iPhone XR, 11, 12 Mini, many Androids (FHD+)"},
            {"resolution": "2220x1080", "desc": "Samsung Galaxy S8/S9/S10 (FHD+)"},
            {"resolution": "2160x1080", "desc": "Mid-range Android devices (FHD+)"},
            {"resolution": "1792x828", "desc": "iPhone XR, 11 (Liquid Retina)"},
            {"resolution": "1520x720", "desc": "Android HD+ resolution (budget devices)"},
            {"resolution": "1334x750", "desc": "iPhone 6/7/8 (Non-Plus Retina)"},
            {"resolution": "1280x720", "desc": "Older Android devices, HD resolution"}
        ]
        self.running_process = None


    def installation(self):
        try:
            self.check_and_install_remotion_dependencies()
            self.add_ffmpeg_path()
        except Exception as e:
            raise Exception(str(e))
        

    def clear_resources(self):
        print("#### Destructor: Quizomatic")
        if self.running_process:
            self.running_process.terminate()
            self.running_process.wait()
        self.RUNNING_TASKS = {}

    def get_logs(self, task_id):
        logs = self.RUNNING_TASKS.get(task_id, {}).get('logs', '')
        logs += "\n\nPROGRESS: " + str(self.RUNNING_TASKS.get(task_id, {}).get('progress'))
        logs += "\nSTATUS: " + ("RUNNING" if self.RUNNING_TASKS.get(task_id, {}).get('isRunning') else "STOPPED")
        return logs
    
    def get_files(self, task_id):
        files = self.RUNNING_TASKS.get(task_id, {}).get('files', [])
        return [{"name": file["name"], "loc": file["loc"]} for file in files]
    
    def delete_task(self, task_id):
        if self.RUNNING_TASKS.get(task_id):
            if self.RUNNING_TASKS[task_id]['isRunning']:
                self.RUNNING_TASKS[task_id]["stop_task"] = True
                raise Exception(str("Request accepted! Deleting task takes some time, please wait for 3-5 mintutes, and try again"))
            self.RUNNING_TASKS.pop(task_id)
        


    def get_video_resolutions(self):
        # return [f'{res["resolution"]} ({res["desc"]})' for res in self.VIDEO_RESOLUTIONS]
        return ["1920x1080 (Youtube - Landscape)", "1080x1920 (Youtube - Shorts)"]


    def running_tasks(self):
        running_tasks = []
        for key, task in self.RUNNING_TASKS.items():
            if isinstance(task, dict):  
                filtered_task = {k: v for k, v in task.items() if isinstance(v, (str, int, float, bool, list, dict))}
                running_tasks.append(filtered_task)
        return running_tasks


    def add_ffmpeg_path(self):
        if systemName == "Windows": 
            try:
                try: self.add_to_system_path(FFMPEG_BIN_PATH)
                except Exception as e: raise Exception(str(e)) 
            except Exception as e: raise Exception(str(e))
    

    def refresh_environment_variables(self):
        """Broadcasts a WM_SETTINGCHANGE message to refresh environment variables with a timeout."""
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
        TIMEOUT = 5000  # 5 seconds
        result = ctypes.windll.user32.SendMessageTimeoutW( HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, TIMEOUT, ctypes.byref(wintypes.DWORD()))
        if result == 0: print(f"\n  {YLCLR}Warning: Timeout occurred while broadcasting WM_SETTINGCHANGE.{RSCLR}")


    def add_to_system_path(self, new_path):
        try:
            import winreg
            new_path = os.path.abspath(new_path)
            current_path = os.environ.get("PATH", "")
 
            for p in current_path.split(";"):
                if ("ffmpeg/bin" in p or "ffmpeg\\bin" in p): return
            
            raise Exception(f"   {RDCLR}Ffmpeg not found. Download and ADD_TO_PATH{RSCLR}")

        except PermissionError:
            print(f"{RDCLR}Permission denied. Please run this script as an administrator.{RSCLR}")
            raise Exception(f"\n{RDCLR}Failed To Add FFmpeg To ENV PATH. Read {GRCLR}README.INSTALLATION.STEP2{RSCLR}\n")
        except Exception as e:raise Exception(str(e))

      
    # Validate Required Files & Tools To Run This Project
    def check_and_install_remotion_dependencies(self):

        try: subprocess.run(["node", "--version"], cwd=CUR_DIR, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True if systemName == "Windows" else False)
        except FileNotFoundError: raise Exception("Error: Node.js is not installed. Please install Node.js first.")
        try: subprocess.run(["npm", "--version"],  cwd=CUR_DIR, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True if systemName == "Windows" else False)
        except FileNotFoundError: raise Exception("Error: npm is not installed. Please install npm first")
        if not os.path.exists(os.path.join(CUR_DIR, "package.json")): raise Exception("Error: package.json file not found in the current directory.")
        try:
            if not os.path.exists(NODE_MODULE_DIR): 
                print(f"{GRCLR}-- Quizomatic: Installing dependencies from package.json...{RSCLR}")
                subprocess.run(["npm", "install", "--loglevel=error"],  cwd=CUR_DIR, check=True, shell=True if systemName == "Windows" else False)
        except subprocess.CalledProcessError as e: raise Exception("Error: Failed to install dependencies.")


    def create_file_download_link(self, filePath):
        if self.API_ENDPOINTS.get('generate_download_link'):
            response = requests.post(self.API_ENDPOINTS['generate_download_link'], json={"file_path": filePath})
            if response.status_code == 200: return response.json().get("download_link")
            else: return "https://drive.google.com/drive/file/fileNotFound"
        return False


    def get_current_datetime(self):
        now = datetime.now()
        return f"{now.date().day}_{now.hour}_{now.minute}_{now.second}"


    # "Get Current Date & Time"
    def get_datetime_str(self):
        now = datetime.now()
        return now.strftime("%Y_%m_%d_%H_%M_%S")


    # "Create Empty Sound Track."
    def create_silent_audio(self, duration_in_seconds, output_path):
        silence = AudioSegment.silent(duration=duration_in_seconds * 1000)
        silence.export(output_path, format="wav")
        print(f"Silent audio created at: {output_path}")


    # "Concatenate multiple audios and save them on specific folder."
    def concatenate_audios(self, audio_files, output_file):
        combined = AudioSegment.empty()
        for audio_file in audio_files:
            audio = AudioSegment.from_file(audio_file)
            combined += audio   
        combined.export(output_file, format="mp3")
        return output_file
    

    def concatenate_videos(self, video_paths, outputFile="testing.mp4", crop_seconds=0, crop_from_start=True):
        try:
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
            clips = []    
            for path in video_paths:
                if not os.path.isfile(path): continue
                clip = VideoFileClip(path)
                if crop_seconds > 0:
                    if crop_from_start: clip = clip.subclip(crop_seconds, clip.duration)
                    else:  clip = clip.subclip(0, clip.duration - crop_seconds)
                clips.append(clip)
            
            if not clips:
                sys.stdout = sys.__stdout__ 
                sys.stderr = sys.__stderr__ 
                return False

            final_clip = concatenate_videoclips(clips)
            final_clip.write_videofile(outputFile, codec="libx264", threads=4, logger=None)
            sys.stdout = sys.__stdout__ 
            sys.stderr = sys.__stderr__ 
            return outputFile
        except Exception as e: 
            sys.stdout = sys.__stdout__ 
            sys.stderr = sys.__stderr__ 
            print(e)
            return False        
        
        

    # "Run Remotion Project Using Subprocess and Get The Response"
    def render_remotion_video(self, task_id, values, outputFile):
        # if systemName == "Windows": outputFile = os.path.join("output", os.path.basename(outputFile))
        temp = None
        command = ["npm", "run", "py_render_win" if systemName == "Windows" else "py_render_linux", "--composition=videoGenerator", f"--output={outputFile}"]
        process = subprocess.Popen(
            command, 
            cwd=CUR_DIR, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            encoding="utf-8", 
            text=True, 
            shell=True if systemName == "Windows" else False
        )
        for line in process.stdout:
            if "Rendered" in line:
                parts = line.strip().split(",")
                rendered_part = parts[0]  # Example: "Rendered 10/797"
                time_part = parts[1] if len(parts) > 1 else ""
                output = f"########## {rendered_part} {time_part}"  # Progress string
                if temp and temp in self.RUNNING_TASKS[task_id]['logs']:
                    self.RUNNING_TASKS[task_id]['logs'] = self.RUNNING_TASKS[task_id]['logs'].replace(temp, output)
                else: self.RUNNING_TASKS[task_id]['logs'] += f"\n{output}"
                temp = output  # Store the latest progress string
                # sys.stdout.write(f"\r{Fore.RED}########## {output} {Fore.RESET}")
                # sys.stdout.flush()
        self.running_process = process
        process.wait()
        process.terminate()
        stderr_output = process.stderr.read()
        if stderr_output:
            if "No file extension specified" in stderr_output: return  True
            self.RUNNING_TASKS[task_id]['logs'] += f"\nError: {stderr_output}"
            print(f"Error: {stderr_output}", file=sys.stderr)
            return False
        return True


    # "Prepare Json File For Remotion (Video Details)"
    def prepare_video_data(self, task_id, videoDetails, outputFile,  index=0, resolution={ "width": 1080, "height": 1920}, direc={}):
        temp_combined_audio = combined_audio.replace('.mp3', self.get_datetime_str()+str(randint(1000, 9999))) + ".mp3"
        questionAudio = os.path.join(direc["AUDIO_FILES_DIR"], videoDetails[3])
        optionsAudio  = os.path.join(direc["AUDIO_FILES_DIR"], videoDetails[4])
        answerAudio   = os.path.join(direc["AUDIO_FILES_DIR"], videoDetails[5])
        combinedAudio = self.concatenate_audios([questionAudio, silent_1_sec, optionsAudio, silent_1_sec, timerAudio,silent_1_sec, answerAudio], temp_combined_audio) 
        
        VIDEO_DATA = {
            "template": "single",
            "videoCount": index+1,
            "width": resolution['width'],
            "height": resolution['height'],
            "videoData": [
                {
                    "questionText":  videoDetails[0], 
                    "optionstext":   ','.join([x.replace("\"",'').replace("“",'').replace('”','') for x in videoDetails[1].split(',')]),
                    "answerText":    videoDetails[2],
                    "questionAudio": shutil.copy(questionAudio, QUESTION_AUDIO).replace(PUBLIC_DIR, ''),
                    "optionsAudio":  shutil.copy(optionsAudio, OPTIONS_AUDIO).replace(PUBLIC_DIR, ''),
                    "answerAudio":   shutil.copy(answerAudio, ANSWERS_AUDIO).replace(PUBLIC_DIR, ''),
                    "combinedAudio": shutil.copy(combinedAudio, COMINED_AUDIO).replace(PUBLIC_DIR, ''),
                    "backgroundImage": shutil.copy(os.path.join(direc['IMAGES_FILES_DIR'], videoDetails[6]), BKG_IMAGE).replace(PUBLIC_DIR, ''),
                }
            ]
        }
        os.remove(temp_combined_audio)
        with open(VIDEO_GENERATION_DATA, "w") as f: f.write(json.dumps(VIDEO_DATA))
        return self.render_remotion_video(task_id, VIDEO_DATA, outputFile)



    # "Create Single Video & Save them in Specific Folder"
    def single_video_generator(self, task_id, datasets, direc={}, resolution={ "width": 1080, "height": 1920}):

        VIDEO_OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "Quizomatic_Output_" + str(randint(11111, 99999)))
        if not os.path.exists(VIDEO_OUTPUT_DIR):  
            os.makedirs(VIDEO_OUTPUT_DIR)
            
        videosPairs = datasets
        self.RUNNING_TASKS[task_id]['logs'] += f"\n{'#'*32} Single Video Generator {'#'*32}"
        # print(f"\n{Fore.YELLOW}{'#'*32} Single Video Generator {'#'*32}{Fore.RESET}", end=" ")

        for index, video in enumerate(videosPairs):

            if self.RUNNING_TASKS[task_id].get("stop_task"):
                if self.RUNNING_TASKS[task_id]["stop_task"]:
                    self.RUNNING_TASKS[task_id]['isRunning'] = False 
                    break

            outputFileName = f"{self.get_datetime_str()}.mp4"
            outputFilePath = os.path.join(VIDEO_OUTPUT_DIR, outputFileName)
            self.RUNNING_TASKS[task_id]['progress'] = index+1/len(videosPairs)
            self.RUNNING_TASKS[task_id]['logs'] += f"\n{index+1}/{len(videosPairs)} [{video[0][:50]}]"
            # print(f"\n{Fore.GREEN}{index+1}/{len(videosPairs)} [{video[0][:50]}]{Fore.RESET}")
            status     = self.prepare_video_data(task_id, video, outputFilePath, -1, resolution, direc=direc)
            
            if status: 
                self.RUNNING_TASKS[task_id]['logs'] += f"\nCompleted. {outputFileName}\n"
                # print(f"\n{Fore.YELLOW}Completed. {outputFileName}{Fore.YELLOW}{Fore.RESET}") 
            else:  
                self.RUNNING_TASKS[task_id]['logs'] += f"\nError Occur While Rendering & Concatenating Video Pack {index}\n\n"
                print(f"\n{Fore.RED}Error Occur While Rendering & Concatenating Video Pack {index}{Fore.RED}",  end="\n\n")
        
        self.RUNNING_TASKS[task_id]['logs'] += f"{'#'*86}"
        # print(f"{Fore.YELLOW}{'#'*86}{Fore.RESET}", end="\n\n")
        return VIDEO_OUTPUT_DIR



    # "Create Multiple Videos - Create Single Video & Than Merging Them"
    def multiple_video_generator(self, task_id, numberOfVideos, datasets, direc={}, resolution={ "width": 1080, "height": 1920}):

        videosPairs = [datasets[index if index==0 else index*numberOfVideos:(index+1)*numberOfVideos] for index, x in enumerate(datasets[::numberOfVideos])]
        # print(f"{GRCLR} Multi Rendering{RSCLR}")

        for index, videosPack in enumerate(videosPairs):

            if self.RUNNING_TASKS[task_id].get("stop_task"):
                if self.RUNNING_TASKS[task_id]["stop_task"]: 
                    self.RUNNING_TASKS[task_id]['isRunning'] = False
                    break

            self.RUNNING_TASKS[task_id]['progress'] = index+1/len(videosPairs)
            self.RUNNING_TASKS[task_id]['logs'] += f"\n{'#'*38} Job {index+1}/{len(videosPairs)} {'#'*38}"
            # print(f"\n{Fore.YELLOW}{'#'*38} Job {index+1}/{len(videosPairs)} {'#'*38}{Fore.RESET}", end=" ")

            concate_videos = []
            for index, video in enumerate(videosPack):
                outputFile = os.path.join(direc["VIDEO_OUTPUT_DIR"], f"{self.get_datetime_str()}.mp4")
                self.RUNNING_TASKS[task_id]['logs'] += f"\n{index+1}/{len(videosPack)} [{video[0][:50]}]"
                # print(f"\n{Fore.GREEN}{index+1}/{len(videosPack)} [{video[0][:50]}]{Fore.RESET}")
                status     = self.prepare_video_data(task_id, video, outputFile, index, resolution, direc=direc)
                if status: concate_videos.append(outputFile)

            self.RUNNING_TASKS[task_id]['logs'] += f"\nPost Processing Files! Waiting..."
            # print(f"\n{Fore.RED}Post Processing Files! Waiting...{Fore.RESET}")
            concatenated_video_name = f"{self.get_datetime_str()}.mp4"
            concatenated_video_path = os.path.join(direc["VIDEO_OUTPUT_DIR"], concatenated_video_name)

            try:
                concat_response =  self.concatenate_videos(concate_videos, crop_seconds=1, outputFile=concatenated_video_path)
                if concat_response: 
                    self.RUNNING_TASKS[task_id]['logs'] += f"Completed. {concatenated_video_name}\n"
                    # print(f"{Fore.YELLOW}Completed. {concatenated_video_name}{Fore.YELLOW}{Fore.RESET}")
                    for file in concate_videos: os.remove(file)
                else: 
                    self.RUNNING_TASKS[task_id]['logs'] += f"Error Occur While Rendering & Concatenating Video Pack {concate_videos}\n\n"
                    # print(f"{Fore.RED}Error Occur While Rendering & Concatenating Video Pack {concate_videos}{Fore.RED}",  end="\n\n")
            except Exception as e: 
                raise Exception(e)
            
        return direc["VIDEO_OUTPUT_DIR"]



    def generate_video(self, working_dir=None, render_videos=1, resolution="1080x1920", isTest=False):

        task_id = "quizomatic_" + str(randint(11111,99999))

        try:

            try: 
                render_videos = int(render_videos)
                if render_videos <= 0: raise Exception("")
            except: raise Exception("Video Length Should be any number between 1-9999...")

            try:
                resolution = resolution.split(" ")[0]
                resolution = resolution.split("x")
                resolution={ "width": int(resolution[0]), "height": int(resolution[1])}
            except Exception as e: raise Exception(f"{RDCLR} Failed while fetching resolution. {str(e)}{RSCLR}")

            IMAGES_FILES_DIR = AUDIO_FILES_DIR = VIDEO_OUTPUT_DIR = None

            if not working_dir: raise Exception("Working Dir Path is required...")
            if not os.path.exists(os.path.join(working_dir, "Audios")): raise Exception("Working Dir doesn't have Audios directory...")
            if not os.path.exists(os.path.join(working_dir, "Images")): raise Exception("Working Dir doesn't have Images directory...")
            if not os.path.exists(os.path.join(working_dir, DEFAULT_RENDERING_INPUT_SHEET)): raise Exception(f"No input (xlsx) file found with name {DEFAULT_RENDERING_INPUT_SHEET}")
            
            IMAGES_FILES_DIR = os.path.join(working_dir, "Images")
            if not os.path.exists(IMAGES_FILES_DIR): os.makedirs(IMAGES_FILES_DIR)

            AUDIO_FILES_DIR = os.path.join(working_dir, "Audios")
            if not os.path.exists(AUDIO_FILES_DIR): os.makedirs(AUDIO_FILES_DIR)

            VIDEO_OUTPUT_DIR = os.path.join(working_dir, "Quizomatic_Output_" + str(randint(11111, 99999)))
            if not os.path.exists(VIDEO_OUTPUT_DIR): os.makedirs(VIDEO_OUTPUT_DIR)

            direc = { "IMAGES_FILES_DIR": IMAGES_FILES_DIR, "AUDIO_FILES_DIR":AUDIO_FILES_DIR, "VIDEO_OUTPUT_DIR":VIDEO_OUTPUT_DIR }

            file_path = os.path.join(working_dir, DEFAULT_RENDERING_INPUT_SHEET)
            
            self.RUNNING_TASKS[task_id] = {
                'task_id': task_id, 
                'feature': "Quizomatic", 
                "task_type": f"Quizomatic - Create Quiz Videos",
                "tags": f"Generating Bulk Quiz Videos [Quizomatic]", 
                "progress": 0, 
                "logs": """""", 
                "isRunning": False, 
                "stop_task": False,
                "files": []
            }

            try:
                wb = openpyxl.load_workbook(file_path)
                sheet = wb.active
            except Exception as e: raise Exception(str(e))

            try:
                DATASET = [x for x in sheet.iter_rows(values_only=True)]
                if len(DATASET)<=0:  raise Exception(ERROR_READING_DATA.replace("FILEPATH", file_path))
            except Exception as e: raise Exception(str(e))


            def render_video(isTest=False):

                output_dir = None
                self.RUNNING_TASKS[task_id]['isRunning'] = True 
                self.RUNNING_TASKS[task_id]['progress'] = 2

                if render_videos and render_videos > 1:
                    try: output_dir = self.multiple_video_generator(task_id, render_videos, DATASET, direc=direc, resolution=resolution)
                    except Exception as e: raise Exception(str(e))
                else:
                    try: output_dir = self.single_video_generator(task_id, DATASET, direc=direc, resolution=resolution)
                    except Exception as e: raise Exception(str(e))

                if isTest: return output_dir

                zip_name = f'quizomatic_{self.get_current_datetime()}.zip'  # Create Zip Archive
                zip_path = os.path.join(tempfile.mkdtemp(), zip_name)
                shutil.make_archive(zip_path.replace('.zip', ''), 'zip', output_dir)

                download_link = self.create_file_download_link(zip_path)

                self.RUNNING_TASKS[task_id]['files'].append({
                    "name": os.path.basename(output_dir),
                    "local_path": output_dir,
                    "loc":  download_link if download_link else output_dir
                })

                self.RUNNING_TASKS[task_id]['progress'] = 100
                self.RUNNING_TASKS[task_id]['isRunning'] = False

            if self.RUNNING_TASKS[task_id].get("stop_task"):
                if self.RUNNING_TASKS[task_id]["stop_task"]: 
                    self.RUNNING_TASKS[task_id]['isRunning'] = False
                    return "Deleted Successfully"

            if isTest: return render_video(isTest=True)

            Thread(target=render_video, daemon=True).start() 
            return { "task_id" : task_id }
        
        except Exception as e:
            self.RUNNING_TASKS[task_id]['logs'] += "\nERROR! " + str(e)
            self.RUNNING_TASKS[task_id]['isRunning'] = False
            raise Exception(str(e))


        
def addProjectFolder(path):
    try:
        AUDIO_FILES_DIR  = os.path.join(path, "Audios") 
        xlsx_files = []
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.xlsx'): xlsx_files.append(os.path.join(root, file))
        if xlsx_files: return xlsx_files[0]
        else: raise Exception(ERROR_TRANSCRIBED_SHEET.replace('FILEPATH', path))
    except Exception as e: 
        if ERROR_TRANSCRIBED_SHEET.split('\n')[0] in str(e): print(e)
        else: raise Exception(ERROR_TRANSCRIBED_DIR.replace('FILEPATH', path))
        input()
        sys.exit()
        


if __name__ == "__main__":

    ################################
    # Checking Tools and Libraries
    clearScreen()

    try:
        QUIZOMATIC_ = QUIZOMATIC()
        QUIZOMATIC_.installation()

        ################################
        clearScreen()
        print(INFORMATION, end="\n\n")

        parser = argparse.ArgumentParser(description="Quizomatic - Generate bulk Quiz Videos")
        parser.add_argument("--project_folder",    default="",  help="Path to the Folder containing 'data.xlsx' Images, Audios", type=str)
        parser.add_argument("--multi", default="0", help="Rendering Multiple Videos INT i.e 6", type=str)
        parser.add_argument("--isPortrait", help="Video portrait mode", action="store_true")
        args = parser.parse_args()
        working_dir = args.project_folder
        renderMultipleVideos = args.multi
        isPortrait = args.isPortrait
        renderMultipleVideos = int(renderMultipleVideos)

        #########################################
        # Inputing Video Rendering Excel Sheet
        if not working_dir: 
            try:
                if input(ADD_TRANSCRIBED_DIR).lower() == "y": working_dir = input(INPUT_TRANSCRIBED_DIR)
                else: raise Exception(f"{RDCLR}Exiting! Project folder is Required{RSCLR}")

                if os.path.exists(DEFAULT_RENDERING_INPUT_SHEET):
                    useDefaultSheet = input(INPUT_DEFAULT_SHEET.replace('FILEPATH', os.path.basename(DEFAULT_RENDERING_INPUT_SHEET)))
                    if useDefaultSheet.lower() == "y": file_path = DEFAULT_RENDERING_INPUT_SHEET  # ASSOGN DEFAULT SHEET
                
                # if not file_path:
                #     userInputSheet = input(INPUT_USER_SHEET)
                #     if userInputSheet: file_path = userInputSheet
                #     else: raise Exception(f"{RDCLR}ERROR! Cannot go furthur without input sheet.{RSCLR}")
                
                if input(INPUT_DO_RENDERING).lower() == "y": 
                    try: renderMultipleVideos = int(input(INPUT_RENDER_LIMIT))                    # ASSOGN RENDERING VEIDEO LIMIT
                    except: raise Exception(f"{RDCLR}ERROR: RENDERING LIMIT SHOULD OF INTEGER 1,2,3,...{RSCLR}")

                if input(INPUT_DO_PORTRAIT).lower() == "y": isPortrait = True

            except Exception as e:
                print(f"{RDCLR}   ERROR OCCURED! {e}{RSCLR}")
                input()
                sys.exit()


        output_dir = None
        if renderMultipleVideos:
            print("   Rendering Videos Pack Of Length: ", renderMultipleVideos)
            output_dir = QUIZOMATIC_.generate_video(working_dir, render_videos=renderMultipleVideos, resolution="1080x1920" if isPortrait else "1920x1080", isTest=True)

        print(f"\n{GRCLR}VIDEO RENDERING COMPLETED. {output_dir}{RSCLR}\n")
        input()

    except Exception as e: 
        print(f"   {RDCLR}GOT UNEXPECTED ERROR: {e}. {RSCLR}")
        input()
        sys.exit()
    
    

    