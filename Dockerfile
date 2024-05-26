FROM python:3.9

WORKDIR /app

ENV PATH="/home/python/.local/bin:$PATH"

ARG UID=1000
ARG GID=1000

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential curl wget git libpq-dev gnupg \
  && wget -c https://github.com/nicolas-van/multirun/releases/download/1.1.3/multirun-x86_64-linux-gnu-1.1.3.tar.gz -O - | tar -xz \
  && mv multirun /bin \
  && apt-get install -y redis-server ffmpeg \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean \
  && groupadd -g "${GID}" python \
  && useradd --create-home --no-log-init -u "${UID}" -g "${GID}" python \
  && mkdir -p /app/data /app/data/passports /app/static /app/media \
  && chown python:python -R /app

USER python

RUN pip install openai-whisper
RUN mkdir -p /home/python/.cache/whisper && wget -O /home/python/.cache/whisper/base.pt https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt

COPY --chown=python:python ./an_transcriptions/ ./an_transcriptions/
COPY --chown=python:python requirements.txt docker-entrypoint.sh ./

RUN pip install gunicorn
RUN pip install -r requirements.txt

WORKDIR /app

RUN chmod +x docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]