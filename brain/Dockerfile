# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

ARG AUTH_TOKEN

WORKDIR /brain

COPY brain/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy rest of the app
COPY . .

CMD python3 brain/awake.py --env production --auth-token $AUTH_TOKEN