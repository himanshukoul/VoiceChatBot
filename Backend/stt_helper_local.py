import whisper
model = whisper.load_model("small.en")

def stt_func_local(fpath):
    result = model.transcribe(fpath)
    return result
