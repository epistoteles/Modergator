<div align="center">
  <img src="https://github.com/katrinc/hatefulmemes_2021/blob/main/.github/modergator.png" alt="Modergator" width="400">
</div>

<h4 align="center">Snapping back on hate speech</h4>

<div align="center">
  <img src="https://img.shields.io/badge/python-v3.8-blue.svg">
  <img src="https://img.shields.io/badge/contributions-welcome-orange.svg">
</div>
  
<p align="center">
  <a href="#-key-features">Key Features</a> •
  <a href="#-how-to-use">How To Use</a> •
  <a href="#%EF%B8%8F-installation">Installation</a> •
  <a href="#components">Components</a> •
  <a href="#-code-contributors">Contributors</a> •
  <a href="#%EF%B8%8F-license">License</a>
</p>

# Modergator - Hate Speech Detection
This bot is able to process several kinds of messages send in a Telegram group. The messages are checked for hate speech.

## 🎯 Key Features

This bot does A, B and C.

## 💡 How To Use

Usage for Telegram user (non-techies)

## ⚙️ Installation

As torch 1.4.0 does not work with python versions later than 3.8, you need python 3.8.

First, you need to install the following dependencies:
```
sudo apt-get -y install screen net-tools tesseract-ocr virtualenv
```
This is the only step for which you need sudo rights.

Next, run the provided install script:
```
source install.sh
```
This does the following:
- create several virtual environments
- create user-specific configs
- download models that are too big for GitHub
- install all Python dependencies


### Using the Telegram Bot

And then start the bot with
```
source run.sh
```
This will start a virtual environment, install all dependencies inside it and start each program inside a screen session.


### Meme API

### Voice API

### Target API
### How the target detection works

the target detection is based on HateXplain (for more information see https://github.com/hate-alert/HateXplain). The dataset contains annotated tweets which have been labeled as hate speech, offensive or normal language. The detection is trained on the dataset and returns a list of discriminated target groups.

The telegram bot executes the target detection for all kinds of messages.

###Folder description
model.py --> the trained model
main.py --> the target api that communicates with the bot and the model

### Usage instructions
The trained model can be used to predict new input.

-> the pth must be download [TODO: link] and placed into target-api/model

## ‎‍💻 Contributors

## ⚠️ License


## Dump: Below here old README concent to be deleted

Go into meme-model-api/vilio/py-bottom-up-attention/ and run in a virtual evironment (source meme-model-api/memeenv/bin/activate) ```python3 setup.py build develop```. This will create a configs directory with files in vilio/py-bottom-up-attention/detectron2/model_zoo that is not pushed to git
(because its user-specific) <---- now in install.py

* to use the target API, add the model "hate_target.pth" from here https://www.kaggle.com/katinka21/modergator-target-detection-model into the folder:  target-api/model/hate_target.pth.
* to use the meme API, add the model "LASTtrain.pth" from here https://www.kaggle.com/muennighoff/viliou36?select=LASTtrain.pth into the folder:  model-meme-api/vilio/input/viliou36/LASTtrain.pth"  <---- not necessary any more, now uploaded to git with git-lfs
