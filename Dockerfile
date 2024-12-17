FROM python:3.13.0-alpine3.20

# Install system dependencies
RUN apk update && \
    apk add --no-cache \
        imagemagick \
        openssl \
        coreutils \
        findutils \
        ffmpeg && \
    rm -rf /var/cache/apk/*

# Install python dependencies
WORKDIR /code
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt && rm -rf /root/.cache/pip

# Copy UI and server files
COPY ./dist ui
COPY ./scripts/server.py .
COPY ./scripts/import_media.py .

EXPOSE 80

VOLUME ["/data", "/cert"]
ENV DATA_DIR=/data

CMD ["fastapi", "run", "server.py", "--port", "80"]
