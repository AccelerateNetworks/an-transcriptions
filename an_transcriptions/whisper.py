import os
import whisper

model = whisper.load_model("base")

def transcribe(filename):
    result = model.transcribe(filename)
    os.remove(filename)
    return result["text"]
