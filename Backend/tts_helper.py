# import io
# import base64
# import torch
# import torchaudio
# from chatterbox.tts import ChatterboxTTS

# device = "cuda" if torch.cuda.is_available() else "cpu"
# model = ChatterboxTTS.from_pretrained(device=device)
# def tts_func(text):
#     wav = model.generate(text)
#     buffer = io.BytesIO()
#     torchaudio.save(buffer, wav, model.sr, format="wav")
#     buffer.seek(0)
#     encoded = base64.b64encode(buffer.read()).decode("utf-8")
#     return encoded
# import requests

# COLAB_BASE_URL = "https://3adefab2314e.ngrok-free.app/"  

# def tts_func(text):
#     response = requests.post(
#         f"{COLAB_BASE_URL}/tts",
#         json={"text": text}
#     )
#     if response.status_code == 200:
#         return response.json().get("audio", "")
#     else:
#         return ""

from elevenlabs.client import ElevenLabs
import base64
import os
import time

eleven = ElevenLabs(api_key=os.getenv("ELEVEN_LABS_API_KEY"))

def tts_func_streaming(text, emit_callback):
    audio_stream = eleven.text_to_speech.stream(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2"
    )

    buffer = bytearray()
    min_chunk_duration = 2.0  
    sample_rate = 24000  
    bytes_per_second = 24000  

    last_emit = time.time()

    for chunk in audio_stream:
        if isinstance(chunk, bytes):
            buffer.extend(chunk)

            if len(buffer) >= bytes_per_second * min_chunk_duration:
                b64 = base64.b64encode(buffer).decode("utf-8")
                emit_callback(b64)
                buffer = bytearray() 

    if buffer:
        b64 = base64.b64encode(buffer).decode("utf-8")
        emit_callback(b64)
