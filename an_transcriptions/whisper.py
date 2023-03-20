import whisper

model = whisper.load_model("base")

def transcribe(filename):
    result = model.transcribe(filename)
    return result["text"]
