#!/bin/bash

# install virtualenv
pip3 install virtualenv

# create memeenv if it doesn't exit already and activate it
[[ -d meme-model-api/memeenv ]] || python3 -m virtualenv meme-model-api/memeenv
source meme-model-api/memeenv/bin/activate

# install meme-model-api requirements
pip3 install --upgrade pip
pip3 install -r meme-model-api/requirements.txt
pip3 install numpy==1.18.1 # to be sure that it is installed for requirements_git
sleep 10
pip3 install -r meme-model-api/requirements_git.txt
pip3 install flask_apispec

# create configs directory

cd meme-model-api/vilio/py-bottom-up-attention
python3 setup.py build develop
cd ../../..

# deactive memeenv
deactivate

# create venv if it doesn't exist already and activate it
#pip3 install virtualenv
[[ -d venv ]] || python3 -m virtualenv venv
source venv/bin/activate

# install all python requirements
pip3 install --upgrade pip
pip3 install -r requirements.txt
pip3 install -r text-api/requirements.txt
pip3 install -r ocr-api/requirements.txt
pip3 install -r asr-api/requirements.txt
pip3 install -r target-api/requirements.txt
pip3 install -r telegram-bot/requirements.txt

# deactive venv
deactivate

# print done
echo 'Finished setting up venvs and installing requirements'
