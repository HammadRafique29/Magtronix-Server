import whisper
import torch
import os

class WhisperSTT:
    
    def __init__(self, API_ENDPOINTS={}, model_size="base", device="cpu"):
        
        self.SUPPORTED_MODELS = {
            "tiny": "tiny",
            "base": "base",
            "small": "small",
            "medium": "medium",
            "large": "large",
            "large-v2": "large-v2"
        }
        if model_size not in self.SUPPORTED_MODELS: 
            raise ValueError(f"Unsupported model size: {model_size}. Choose from {list(self.SUPPORTED_MODELS.keys())}")
        
        self.model_size = model_size
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.API_ENDPOINTS = API_ENDPOINTS
        self.model = self._load_model()

        self.AUDIO_FORMATS = [
            "mp3", "wav", "aac", "flac", "ogg", "wma", "m4a", "alac", "opus", "amr",
            "aiff", "au", "ra", "ac3", "tta", "mp2", "dts", "mid", "mka"
        ]
        

    def _load_model(self):
        print(f"Loading Whisper model: {self.model_size} on {self.device}")
        return whisper.load_model(self.model_size, device=self.device)
    

    def transcribe(self, audio_path):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        file_type = os.path.basename(audio_path).split('.')[1]
        if not file_type or file_type not in self.AUDIO_FORMATS:
            raise Exception("Invalid file uploaded! Required audio/video file")
        
        result = self.model.transcribe(audio_path)
        return {'rtn': "response/str", "value": result["text"]}
    

    @classmethod
    def available_models(cls):
        """Returns the list of available Whisper models."""
        return list(cls.SUPPORTED_MODELS.keys())



# Example Usage
if __name__ == "__main__":
    stt = WhisperSTT(model_size="base")
    text = stt.transcribe("/home/magician/Desktop/Large Project/docs/intro.mp3")
    print("Transcribed Text:", text)
