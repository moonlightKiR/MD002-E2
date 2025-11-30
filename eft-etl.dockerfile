FROM python:3.11-alpine

WORKDIR /eft-etl

RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev

COPY eft-etl/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY eft-etl/ .
