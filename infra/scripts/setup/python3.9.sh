#! /bin/bish

# See: https://gist.github.com/plembo/6bc141a150cff0369574ce0b0a92f5e7

# This script is used to setup python3.9 on Ubuntu 18.04
sudo apt install build-essential
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update && sudo apt upgrade
sudo apt install python3.9 python3.9-dev python3.9-venv
python3.9 -m ensurepip --default-pip --user
python3.9 -m pip install --upgrade pip --user

# Open shell
python3.9