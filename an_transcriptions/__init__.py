import os
import time
import sys

from flask import Flask, flash, request, redirect, url_for, send_from_directory, make_response, jsonify
import ffmpeg
from werkzeug.utils import secure_filename
from redis import Redis
from rq import Queue, get_current_job
from rq.job import Job
from rq.exceptions import NoSuchJobError
import whisper

ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'flac'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "/tmp"

api_keys = []
api_keys_enabled = True
try:
    with open("api_keys.txt") as f:
        for line in f:
            credential = line.split(',')
            api_keys.append(credential[0])
except FileNotFoundError:
    app.logger.warning("api_keys.txt not found, continuing with no API keys")
    api_keys_enabled = False

redis = Redis()
q = Queue(connection=redis)

model = whisper.load_model("base")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def authenticate():
    if not api_keys_enabled:
        return

    if request.path == "/": # always allow unauthenticated access to /
        return
    
    if request.headers.get("Authorization", "") not in api_keys:
        return make_response(jsonify({'error': 'invalid api key'}), 401)


@app.route('/')
def index():
    return '''
    <!doctype html>
    <head>
    <title>Upload an Audio File</title>
    </head>
    <body>
    <center>
        <h1>Upload your audio file</h1>
        <form method="post" enctype="multipart/form-data" action="/enqueue">
            <input type=file name=file>
            <input type=submit value=Upload>
        </form>
    </center>
    </body>
    </html>
    '''

@app.route('/enqueue', methods=["POST"])
def upload():
    f = request.files.get("file")
    # check if the post request has the file part
    # if user does not select file, browser submit an empty part without filename
    if f is None or f.filename == "":
        return "no file in request", 400

    if not allowed_file(f.filename):
        return "filename not allowed", 400

    filename = secure_filename(f.filename)
    fileLocation = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    f.save(fileLocation)
    job = q.enqueue(transcribe, fileLocation)
    return jsonify({"id": job.id}), 201

@app.route('/j/<job_id>')
def get_job(job_id):
    try:
        job = Job.fetch(job_id, connection=redis)
    except NoSuchJobError:
        return jsonify({"error": "job not found"}), 404

    return jsonify({
        "status": job.get_status(), # Possible values are queued, started, deferred, finished, stopped, scheduled, canceled and failed
        "result": job.result
    })

# Return a JSON error rather than a HTTP 404
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

def transcribe(filename):
    job = get_current_job()
    
    # normalize file
    # normalized = os.path.join(app.config['UPLOAD_FOLDER'], job.id + ".wav")
    # ffmpeg_input = ffmpeg.input(filename)
    # stream = ffmpeg.output(ffmpeg_input, normalized, acodec='pcm_s16le', ac=1, ar='16k')
    # ffmpeg.run(stream)

    result = model.transcribe(filename)
    return result["text"]
