FROM python:3.7-slim

COPY ./app /app/app
COPY ./.env /app/.env 
COPY ./models /app/models
COPY ./entry_point.sh /app/entry_point.sh
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    python3-dev \
    python3-setuptools \
    python3-virtualenv \
    git \
    git-crypt \
    unzip \
    chromium-driver \
    gcc \
    make

RUN apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN chmod +x ./entry_point.sh

RUN virtualenv -p python3 env

RUN source env/bin/activate

RUN env/bin/python3 -m pip install -r requirements.txt

CMD [ "entry_point.sh" ]