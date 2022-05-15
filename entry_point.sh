#!/bin/bash
echo "Running DrexSpamAPI"
RUN_PORT=${PORT:-8989}

/app/env/bin/gunicorn --worker-tmp-dir /dev/shm -k uvicorn.workers.UvicornWorker --bind "0.0.0.0:${RUN_PORT}" app.main:app