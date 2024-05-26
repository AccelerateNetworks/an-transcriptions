#!/bin/sh
exec multirun "redis-server" "gunicorn --bind 0.0.0.0:8000 -w 4 an_transcriptions:app" "rq worker"