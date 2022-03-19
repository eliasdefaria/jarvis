#!/bin/bash

# This script is used to setup Docker on Ubuntu 18.04

sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu `lsb_release -cs` test"
sudo apt update
sudo apt install docker-ce

# TODO: Change this to auto fill directory based on computer
sudo chmod -R 777 /home/jarvis/.docker/

# Check if docker was properly installed
docker -v

# Allow docker socket to be run without sudo permissions
sudo chmod 666 /var/run/docker.sock