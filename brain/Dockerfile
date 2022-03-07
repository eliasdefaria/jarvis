# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

ARG AUTH_TOKEN
ENV AUTH_TOKEN=${AUTH_TOKEN}

# Install server OS dependencies
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
        libatlas-base-dev gfortran nginx supervisor

# Configure project for execution in Docker
COPY brain/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Configure NGINX
RUN useradd --no-create-home nginx
RUN rm /etc/nginx/sites-enabled/default
RUN rm -r /root/.cache


# Copy server config
COPY infra/server/nginx.conf /etc/nginx/
COPY infra/server/jarvis-nginx.conf /etc/nginx/conf.d/
COPY infra/server/supervisord.conf /etc/

# Copy rest of the app
COPY . .


CMD ["/usr/bin/supervisord"]