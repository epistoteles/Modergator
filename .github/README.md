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

# 🐊 Modergator - Hate Speech Detection

Modergator is a Telegram bot able to process multiple kinds of messages sent in a Telegram group. The messages are checked for hate speech and an evaluation of the offensiveness and hatefulness are given. 

WARNING: The repository contains content that is offensive and/or hateful in nature.

## 🎯 Key Features

This bot checks incoming messages for hate speech and offensive language based on the HateXplain dataset and model (https://github.com/hate-alert/HateXplain). Memes are analyzed with vilio (https://github.com/Muennighoff/vilio) which has been trained on the Facebook dataset for multimodal natural language processing (https://ai.facebook.com/tools/hatefulmemes/). Furthermore, the content is checked for possible offended target groups by a model based on the hateXplain dataset.
There exists an option to opt out of the processing of messages for the group members.

## 💡 How To Use

In order to interact with the bot, a Telegram account is needed. For instructions on how to create an account see: https://telegram.org/. To find the bot, you search for @modergator_bot in the search bar in the telegram application. You can then either interact directly with the bot or add the bot to a group. Every message you or members of the group send are analyzed anonymously for potential hate speech or offensive language. If this case occurs, you will get a message from the bot. In case you disagree with the classification, you can type /poll and you and the other group members can vote and discuss their classification.

You don't want the bot to process your messages? Just type /optout and your messages will be ignored. You changed your mind? With /optin you can give access to the processing again.

## ⚙️ Installation

For running the bot by your own, you will need to install several python packages and run different APIs handling different kinds of messages.

As torch 1.4.0 does not work with python versions later than 3.8, you need to use python 3.8.

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

You are done installing!

### ▶ Running the Telegram Bot

You start the bot with:
```
source run.sh
```
This will start a virtual environment, install all dependencies inside it and start each program inside a screen session.
You should now see the following sessions running:
-telegram-bot
-text-api
-ocr-api
-voice-api
-target-api
-meme-model-api

Error handling: in case not all screen sessions could start, you can activate the virtual environment again by typing
```
source /veenv/bin/activate
```
and then starting the corresponding python script. In case the text-api did not start correctly, you would enter
```
python3 text-api/main.py
```  
to start the API manually. For the meme-model-api you type
```
source /memeenv/bin/activate
python3 meme-model-api/main.py
```
### 🖼 Meme API

The detection of hatespeech for memes has been developed by Niklas Muennighoff (https://github.com/Muennighoff/vilio). We have added the prediction for a single meme as an input.

### 📢 Voice API

### 🧍‍♂️ Target API
#### How the Target Detection works

The target detection is based on the HateXplain data set (see https://github.com/hate-alert/HateXplain). The dataset contains annotated tweets which have been labeled by three annotators each as hate speech, offensive or normal language. The detection is trained on the dataset and returns a list of possibly discriminated target groups.
The telegram bot runs the target detection for all kinds of messages.

#### Folder description TODO
model.py --> the trained model
main.py --> the target api that communicates with the bot and the model

### Target Detection Model TODO
The target detection model uses the post id and token as well as the annotated target to train the dataset. The model is build upon the pretrained model *bert-base-uncased*; a dropout and a target classification layer are added. The model could achieve the following evaluation parameters for the classification of 24 target groups: TODO

The best model is then used to predict the target groups of incoming telegram messages if they achieve a classification higher than the threshold 0.4 on the sigmoid of the output of the model prediction.

-> the pth must be download [TODO: link] and placed into target-api/model

## ‎‍💻 Contributors
The bot has been created in the Master's project at Universität Hamburg under the supervision of Prof. Dr. Chris Biemann, Dr. Özge Alaçam and Dr. Seid Muhie Yimam. The OCR and the meme detection have been contributed by Niklas von Boguszewski and Fabian Rausch has helped us immensely building the target group detection model. Thank you!

## ⚠️ License
This repository has been licensed with MIT (see the file LICENSE).

## Dump: Below here old README concent to be deleted

Go into meme-model-api/vilio/py-bottom-up-attention/ and run in a virtual evironment (source meme-model-api/memeenv/bin/activate) ```python3 setup.py build develop```. This will create a configs directory with files in vilio/py-bottom-up-attention/detectron2/model_zoo that is not pushed to git
(because its user-specific) <---- now in install.py

* to use the target API, add the model "hate_target.pth" from here https://www.kaggle.com/katinka21/modergator-target-detection-model into the folder:  target-api/model/hate_target.pth.
* to use the meme API, add the model "LASTtrain.pth" from here https://www.kaggle.com/muennighoff/viliou36?select=LASTtrain.pth into the folder:  model-meme-api/vilio/input/viliou36/LASTtrain.pth"  <---- not necessary any more, now uploaded to git with git-lfs
