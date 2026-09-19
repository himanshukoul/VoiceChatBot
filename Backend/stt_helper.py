import requests

COLAB_BASE_URL = "https://a7a74b4ad52c.ngrok-free.app"  #change according to url in colab

def stt_func(filepath):
    with open(filepath, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{COLAB_BASE_URL}/stt", files=files)
    if response.status_code == 200:
        return response.json()
    else:
        return {"text": "STT error"}
