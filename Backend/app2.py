from flask import Flask, request
import os
import load_env
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from llm_answer import get_llm_answer,stream_llm_answer
from stt_helper import stt_func
from tts_helper import  tts_func_streaming 
import time
from pinecone_client import search_chunks  
import uuid


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

_ = search_chunks("warm up",1)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@socketio.on("connect")
def handle_connect():
    session_id = request.sid
    #print(f"Socket connected: {session_id}")
    
@socketio.on("audio_blob")
def handle_audio(data):
    time_rec = time.time()
    session_id = request.sid
    wavBuffer = data.get("wav")
    filename = f"{uuid.uuid4().hex}.wav"
    if not wavBuffer:
        emit("bot_response", {"message": "No audio blob received"}, room=session_id)
        return

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as f:
        f.write(wavBuffer)
    print(f"Audio save time :{time.time() - time_rec:.2f} s")
    #print(f"Audio saved: {filepath}")

    try:
        #result = stt_func(wavBuffer)
        time_rec = time.time()
        result = stt_func(filepath)
        print(f"STT time :{time.time() - time_rec:.2f} s")
        text = result.get("text", "").strip()
        print("user text len: ",len(text))
        emit("user_said", {"message": text}, room=session_id)
        
        time_rec = time.time()
        top_chunks = search_chunks(text, top_k=3)
        context = "\n\n".join(top_chunks)
        print(f"Semantic Search time :{time.time() - time_rec:.2f} s")
        
        buffer = ""
        sentence_acc = ""
        start_time = time.time()
        first_sen = True
        MAX_WORDS = 20
        for token in stream_llm_answer(text, context):
            if not token:
                continue

            buffer += token

            if any(token.endswith(p) for p in [".", "!", "?",":"]) or len(buffer.split()) >= MAX_WORDS:
                try:
                    if(first_sen): print(f"1st sentence emitted in {time.time() - start_time:.2f}s")
                    sentence = buffer.strip()
                    sentence_acc += sentence + " "
                    emit("bot_partial", {"message": sentence_acc.strip()}, room=session_id)

                    def send_audio_chunk(b64):
                        nonlocal first_sen
                        if(first_sen): print(f"1st audio emitted in {time.time() - start_time:.2f}s")
                        first_sen = False
                        emit("bot_audio_chunk", {"audio": b64}, room=session_id)

                    tts_func_streaming(sentence, send_audio_chunk)
                except Exception as tts_error:
                    print("TTS error:", tts_error)

                buffer = ""
        emit("bot_response", {"message": sentence_acc.strip()}, room=session_id)


    except Exception as e:
        print("error:", e)
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route("/")
def home():
    return "Backend running"

if __name__ == "__main__":
    socketio.run(app, port=5000, debug=False)