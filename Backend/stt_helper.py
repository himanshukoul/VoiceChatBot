# import whisper
# model = whisper.load_model("small.en")

# def stt_func(fpath):
#     result = model.transcribe(fpath)
#     return result

import requests

COLAB_BASE_URL = "https://b0c527125540.ngrok-free.app/"  

def stt_func(filepath):
    with open(filepath, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{COLAB_BASE_URL}/stt", files=files)
    if response.status_code == 200:
        return response.json()
    else:
        return {"text": "STT error"}
