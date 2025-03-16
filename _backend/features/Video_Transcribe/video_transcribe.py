
import os
import requests
from moviepy.editor import VideoFileClip
import tempfile
import random
import logging

logging.getLogger("moviepy").setLevel(logging.ERROR)

class VIDEO_TRANSCRIBE_:

    def __init__(self, API_ENDPOINTS={}, whisper_model="base"):

        self.WHISPER_MODEL = whisper_model
        self.API_ENDPOINTS = API_ENDPOINTS
        self.VIDEO_FORMATS = [
            "mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "mpeg", "mpg", "m4v",
            "3gp", "3g2", "ogv", "vob", "ts", "m2ts", "mts", "divx", "f4v", "rm", "rmvb",
            "asf", "dv", "mxf", "nut"
        ]
        self.AUDIO_FORMATS = [
            "mp3", "wav", "aac", "flac", "ogg", "wma", "m4a", "alac", "opus", "amr",
            "aiff", "au", "ra", "ac3", "tta", "mp2", "dts", "mid", "mka"
        ]
        self.TEMP_AUDIO_DIR = tempfile.mkdtemp()

        self.RUNNING_TASKS = []


    def clear_resouces(self):
        self.RUNNING_TASKS = []



    def create_file_download_link(self, filePath):
        response = requests.post(self.API_ENDPOINTS['generate_download_link'], json={"file_path": filePath})
        if response.status_code == 200: return response.json().get("download_link")
        else: return "https://drive.google.com/drive/file/fileNotFound"



    def transcribe_video(self, video_path):
        try:

            output_audio_path = os.path.join(self.TEMP_AUDIO_DIR, f"audio_{random.randint(11111,99999)}.mp3")

            # Suppress MoviePy and ImageIO logs
            logging.getLogger("moviepy").setLevel(logging.ERROR)
            logging.getLogger("imageio_ffmpeg").setLevel(logging.ERROR)
            os.environ["FFMPEG_STDERR"] = "quiet"

            video = VideoFileClip(video_path)  # No verbose argument
            audio = video.audio
            audio.write_audiofile(output_audio_path, codec="mp3", ffmpeg_params=["-loglevel", "error"], logger=None)
            video.close()
            response = self.transcribe_audio(output_audio_path)
            os.remove(output_audio_path)

            return {"rtn": "response/str", "value": response.get('value', '')} 

        except Exception as e:
            raise Exception(f"ERROR! Failed to extract audio from video. {video_path} \n {e}")




    def transcribe_audio(self, audio_path):
        try:
            
            with open(audio_path, "rb") as audio_file:
                files = {"file": audio_file}
                data = {"model": self.WHISPER_MODEL}
                response = requests.post(self.API_ENDPOINTS['WHISPER_URL'], files=files, data=data)

            if response.status_code == 200:
                response = response.json()
                os.remove(audio_path)
                return {"rtn": "response/str", "value":  response.get('data', {}).get('response', {}).get('value', '')}  
            else: 
                print(f"ERROR! Failed to Transcribe Audio... \n {response.json().get('error')}")
                return {"rtn": "response/str", "value":  str(response.json().get('error', 'Unknow Error Occurs'))}
            
        except Exception as e:
            print(f"Error: {e}")
            raise Exception(str(e))



    def transcribe(self, media_path):
        try:
            file_type = os.path.basename(media_path).split('.')[1]
            if file_type in self.AUDIO_FORMATS: return self.transcribe_audio(media_path)
            elif file_type in self.VIDEO_FORMATS: return self.transcribe_video(media_path)
            else: raise Exception("Invalid file uploaded! Required audio/video file")
            
        except Exception as e:
            print(f"Error: {e}")
            raise Exception(str(e))
        



if __name__ == "__main__":
    
    # audios_path = os.path.join(os.getcwd(), "audios")
    # audio_loc = os.path.join(audios_path, f"audio_{random.randint(11111,99999)}.mp3") 
    # if not os.path.exists(audios_path): os.makedirs(audios_path)
    
    VIDEO_TRANSCRIBE = VIDEO_TRANSCRIBE_()
    audio_path = VIDEO_TRANSCRIBE.extract_audio_from_video("/home/magician/Desktop/Large Project/docs/heygen.mp4")
    transcribed_text = VIDEO_TRANSCRIBE.transcribe_audio(audio_path)
    print("Transcribed Text: ", transcribed_text)