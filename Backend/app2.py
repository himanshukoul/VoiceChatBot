from flask import Flask, request
import os
import load_env
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from llm_answer import get_llm_answer, stream_llm_answer
from stt_helper import stt_func         # Remote STT (Colab)
from stt_helper_local import stt_func_local  # Local STT (GPU)
from tts_helper import tts_func_streaming
import time
from pinecone_client import search_chunks
import uuid
import torch  

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if torch.cuda.is_available():
    print("GPU available — using local STT")
    stt_engine = stt_func_local
else:
    print("No GPU — using remote STT")
    stt_engine = stt_func

# Warmup
warmup_file = os.path.join(BASE_DIR, "warmUpSTT.wav")
_ = stt_engine(warmup_file)
_ = search_chunks("warm up", 1)

@socketio.on("connect")
def handle_connect():
    pass 

@socketio.on("audio_blob")
def handle_audio(data):
    init_rec = time.time()
    session_id = request.sid
    wavBuffer = data.get("wav")
    filename = f"{uuid.uuid4().hex}.wav"

    if not wavBuffer:
        emit("bot_response", {"message": "No audio blob received"}, room=session_id)
        return

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as f:
        f.write(wavBuffer)
    print(f"Audio save time: {time.time() - init_rec:.2f}s")

    try:
        # STT
        time_rec = time.time()
        result = stt_engine(filepath)  
        print(f"STT time: {time.time() - time_rec:.2f}s")

        text = result.get("text", "").strip()
        print("User text len:", len(text))
        emit("user_said", {"message": text}, room=session_id)

        # Semantic search
        time_rec = time.time()
        top_chunks = search_chunks(text, top_k=3)
        context = "\n\n".join(top_chunks)
        print(f"Semantic Search time: {time.time() - time_rec:.2f}s")

        # Stream LLM + TTS
        buffer = ""
        sentence_acc = ""
        start_time = time.time()
        first_sen = True
        MAX_WORDS = 20

        for token in stream_llm_answer(text, context):
            if not token:
                continue

            buffer += token
            if any(token.endswith(p) for p in [".", "!", "?", ":"]) or len(buffer.split()) >= MAX_WORDS:
                try:
                    if first_sen:
                        print(f"1st sentence emitted after RAG search in {time.time() - start_time:.2f}s")

                    sentence = buffer.strip()
                    sentence_acc += sentence + " "
                    emit("bot_partial", {"message": sentence_acc.strip()}, room=session_id)

                    def send_audio_chunk(b64):
                        nonlocal first_sen
                        if first_sen:
                            print(f"1st audio emitted after RAG search in {time.time() - start_time:.2f}s")
                            print(f"1st audio emitted from start in {time.time() - init_rec:.2f}s")
                        first_sen = False
                        emit("bot_audio_chunk", {"audio": b64}, room=session_id)

                    tts_func_streaming(sentence, send_audio_chunk)

                except Exception as tts_error:
                    print("TTS error:", tts_error)
                buffer = ""

        emit("bot_response", {"message": sentence_acc.strip()}, room=session_id)

    except Exception as e:
        print("Error:", e)
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route("/")
def home():
    return "Backend running"

if __name__ == "__main__":
    socketio.run(app, port=5000, debug=False)
