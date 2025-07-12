from flask import Flask, request
import os
import load_env
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from llm_answer import get_llm_answer
from stt_helper import stt_func
from tts_helper import tts_func  
import time
from pinecone_client import search_chunks  


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

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
    filename = data.get("filename", "audio.wav")
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
        top_chunks = search_chunks(text, top_k=5)
        context = "\n\n".join(top_chunks)
        print(f"Semantic Search time :{time.time() - time_rec:.2f} s")

        time_rec = time.time()
        bot_reply = get_llm_answer(text,context)
        print("response len: ",len(bot_reply))
        print(f"LLM response time :{time.time() - time_rec:.2f} s")
        
        #emit("bot_response", {"message": bot_reply, "audio": None}, room=session_id)
        time_rec = time.time()
        bot_audio = tts_func(bot_reply)
        print(f"TTS time :{time.time() - time_rec:.2f} s")
        print("audio len: ",len(bot_audio))
        print("response len: ",len(bot_reply))
        emit("bot_response", {"message": bot_reply, "audio": bot_audio}, room=session_id)
        
    except Exception as e:
        print("error:", e)



@app.route("/")
def home():
    return "Backend running"

if __name__ == "__main__":
    socketio.run(app, port=5000, debug=False)