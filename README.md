# Accelerate Networks Transcription Service
*a little REST API to perform audio transcriptions*

This is a small python tool to transcribe audio asynchronously.

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
