<div align="center">
  <img src="https://github.com/Epistoteles/Modergator/blob/62e7fb1a4b162667d31f67f2c909e9aeed952fb4/.github/modergator.png" alt="Modergator" width="400">
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
  <a href="#-components">Components</a> •
  <a href="#-contributors">Contributors</a> •
  <a href="#%EF%B8%8F-license">License</a>
</p>

# 🐊 Modergator - Hate Detection for Text, Speech and Memes

Modergator is a Telegram bot able to moderate Telegram groups for hateful content.

Text messages are checked for whether they contain offensive and hateful speech, as well as the target groups that the speech is directed against (if there are any). Voice messages are transcribed and then handled the same way as a text messages.

Memes are also checked for hate which arises due to the combination of text and an image.

Currently, the bot can only understand English language.

## 🎯 Key Features

The bot will:
- check texts, voice messages and memes for hate
- intervene if necessary

Group members can:
- dispute wrong classifications in a /poll
- optionally /optout of data processing (GDPR-compliant)

## 💡 How To Use

In order to interact with the bot, a Telegram account is needed. For instructions on how to create an account see: https://telegram.org/. To find the bot, search for @modergator_bot in the search bar. You can then either interact directly with the bot or add the bot to a group by writing a message. Every message you or members of the group send are analyzed anonymously for potential hate speech or offensive language. If this case occurs, you will get a message from the bot. A score is calculated for the messages indicating how certain the classification is. The score is between 0 (not sure at all) and 1 (very, very sure). In case you disagree with the classification, you can type /poll and you and the other group members can vote and discuss their classification.

You don't want the bot to process your messages? Just type /optout and your messages will be ignored. You changed your mind? With /optin you can give access to the processing again.

As of now, the bot provides the following commands:
- /help to get an overview of the commands
- /optout to optout of the processing of your messages
- /optin to opt-in again to the processing of your messages
- /poll to dispute the classification
- /debug to see Modergators internal workings
- /joke to make Modergator tell a joke


## ⚙️ Installation

To host an instance of the bot on your own, you will need run both the bot itself as well as multiple APIs handling the different kinds of messages. We have developed the bot to be hosted on an Ubuntu server, other systems might need an adaption.

As the dependency torch 1.4.0 (needed for the meme API) does **not work with python versions later than 3.8**, you have to use python 3.8. This guide assumes you already have python 3.8 set up.

First, you need to install the following dependencies:
```
sudo apt-get -y install screen net-tools tesseract-ocr virtualenv ffmpeg
```
This is the only step for which you need sudo rights.

Next, you need to download the bigger models, unzip them, and place them in the right folders as described below:
* for the target-api, add the model `hate_target.pth` from here https://www.kaggle.com/katinka21/modergator-target-detection-model to this location: `target-api/model/hate_target.pth`.
* for the meme-model-api, add the model `LASTtrain.pth` from here https://www.kaggle.com/muennighoff/viliou36?select=LASTtrain.pth to this location: `meme-model-api/vilio/input/viliou36/LASTtrain.pth`.
* for the meme-detection-api, download the variable file `variables.data-00000-of-00001` from https://www.kaggle.com/katinka21/modergator-meme-detection-model-variable and place it into `/meme-detection-api/meme_classification_EfficientNetB7/variables/variables.data-00000-of-00001`.

Next, run the provided install script:
```
source install.sh
```
This might take a few minutes. It does the following:
- create several virtual environments
- create user-specific configs
- install all Python dependencies

Finally, you have to create a bot in the Telegram interface using the [Botfather bot](https://core.telegram.org/bots#6-botfather). You will get a message containing your Telegram bot credentials. Please paste your access token into a file named `telegram_bot_token.txt` inside the `telegram-bot` directory. Make sure that you disable the [privacy mode](https://core.telegram.org/bots#privacy-mode) when creating the bot, otherwise your bot won't be able to read other people's messages. You also need to make sure that /setjoingroups is enabled for your bot such that it can also be used in groups as well.

You are ready to run the bot!

### ▶ Running the Telegram Bot

Important: executing `run.sh` will kill all other screen sessions you have currently active. If you don't want that, you have to comment it out. You have to then make sure to kill all the screens concerning the bot if you want to run `run.sh` again.

#### Start the bot:
```
source run.sh
```
This will start the virtual environments and start each API as well as the bot inside a screen session.
You should now see the following sessions running:
- telegram-bot
- meme-detection-api
- target-api
- asr-api
- ocr-api
- text-api
- meme-model-api

#### Error handling
in case not all screen sessions could start, you can activate the virtual environment again by typing
```
source /venv/bin/activate
```
and then starting the corresponding python script in the modergator folder. In case the text-api did not start correctly, you would enter
```
python3 text-api/main.py
```  
to start the API manually. For the meme-model-api you type
```
source /memeenv/bin/activate
python3 meme-model-api/main.py
```
In case you run into errors concerning the torch version, make sure that you are really using Python 3.8 in the memeenv as python 3.9 cannot access torch 1.4. You can even try to run the following line in memeenv:
```
pip install torch==1.4.0 -f https://download.pytorch.org/whl/torch_stable.html
```

## 🧱 Components

Modergator consists of 6 APIs that the Telegram bot communicates with:

### 📝 Text API

In this API, the text message is used as an input for the HateXplain model (https://github.com/hate-alert/HateXplain). This model calculates a classification score indicating how likely the text messages consists of normal, offensive or hate speech. The scores are returned such that the bot can process the message further.

### 📢 ASR API
The purpose of the voice API is to transcribe Telegrams voice messages to text. They are then forwarded to the Text API.

To achieve this, Telegrams .oga files are first converted to .wav files. They are then given to Facebooks [speech To Text Transformer (S2T)](https://huggingface.co/facebook/s2t-small-librispeech-asr).

### 🔡 OCR API

Something about the ocr api

### 🖼 Meme API

The detection of hatespeech for memes has been developed by Niklas Muennighoff (https://github.com/Muennighoff/vilio). This model has been trained on the facebook dataset for multimodal natural language processing ([data set]https://ai.facebook.com/tools/hatefulmemes/). We added the prediction for a single meme as an input.
TODO longer description

Hint: Images that don't contain text won't return a response.

### 🧍‍♂️ Target API

#### How the Target Detection works

The target detection is based on the [HateXplain](https://github.com/hate-alert/HateXplain) data set. The dataset contains annotated tweets which have been labeled by three annotators each as hate speech, offensive or normal language. The detection is trained on the dataset and returns a list of possibly discriminated target groups which are for example Women, Christian or homosexual people.
The telegram bot runs the target detection for all kinds of messages.

### Target Detection Model TODO
The target detection model uses the post id and token as well as the annotated target to train the dataset. The model is build upon the pretrained model *bert-base-uncased*; a dropout and a target classification layer are added. The model could achieve the following evaluation parameters for the classification of 24 target groups: F1: 0.058, Precision: 0.3,  Recall: 0.032.


The best model is then used to predict the target groups of incoming telegram messages if they achieve a classification higher than the threshold 0.4 on the sigmoid of the output of the model prediction.



### API Documentation

We have documented our code with Swagger. The Swagger links will displayed in the terminal after running source run.sh.

## ‎‍💻 Contributors
This project is maintained by Katrin ([@katrinc](https://github.com/katrinc)), Korbinian ([@Epistoteles](https://github.com/Epistoteles)) and Skadi ([@julchen98](https://github.com/julchen98)). It has been created as part of a seminar at University of Hamburg under the supervision of Prof. Dr. Chris Biemann, Dr. Özge Alaçam and Dr. Seid Muhie Yimam. The OCR and the meme detection components have been contributed by Niklas von Boguszewski. Fabian Rausch has helped us immensely building the target group detection model. For the Meme API, we have used VILIO by Niklas Muennighoff.
Thank you!

## ⚠️ License
This repository has been published under the MIT license (see the file LICENSE.txt).
