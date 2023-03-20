# Accelerate Networks Transcription Service
*a little REST API to perform audio transcriptions*

This is a small python tool to transcribe audio asynchronously.


## Install

1. Install [whisper](https://github.com/openai/whisper)
1. Install the application's requirements: `pip3 install -r requirements.txt`
1. for production deployments, install gunicorn: `pip3 install gunicorn`
1. Install redis: `sudo apt install -y redis-server` or use a container: `podman run -p 6379:6379 docker.io/library/redis`

Once all dependencies are installed, run the web server: `gunicorn -b 0.0.0.0:5000 an_transcriptions:app` and start the backround worker: `rq worker`. The worker must share a filesystem (at least `/tmp`) with the web server.

## Authentication

When started, the program will attempt to read a file `api_keys.txt` from the current working directory. Each line of this file will be treated as an API key, up to the first comma character. For example:

```
API_KEY_1, assigned to user a
API_KEY_2, assigned to user b
```
here `API_KEY_1` and `API_KEY_2` will be accepted as valid API keys.

## Endpoints

* `POST /enqueue` - request a transcoding
    * Upload the file with form field `file`: ```curl -X POST http://transcription-service:5000/enqueue -H "Authorization: Bearer API_KEY_1" -F file=@/tmp/transcode-me.wav```
    * You will get a response with a job ID back: `{"id":"f757e53e-bad8-402a-94e7-ccc11baf39c5"}`
* `GET /j/<job_id>` - check on the status of a transcode request
    * response will be JSON with a status and possible result: `{"status": "finished", "result": "the transcribed text"}`
    * `status` may be one of queued, started, deferred, finished, stopped, scheduled, canceled and failed
    * result will be `null` unless `status` is `finished`.
    * the job results will be purged after 500 seconds (a little over 8 minutes)
