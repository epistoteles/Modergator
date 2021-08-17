#!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import glob
import logging
import os

import requests
from telegram import Update, ForceReply, Poll, ParseMode, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PollAnswerHandler, PollHandler
import json
import shutil
import pickle


TOKEN = "1878091664:AAFkmm0fylr3SmNMW_U7xa-JEtkFBIOTheQ"

# flag scores above threshold as hateful
IMAGE_THRESHOLD = 0.5
TEXT_THRESHOLD = 0.5
DATA_STUMP = 'data/'
PORTDICT = pickle.load(open("portdict.pickle", "rb"))


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr"Hello {user.mention_markdown_v2()}\! Welcome to this group\. We do not tolerate hatespeech here\. Hatespeech is any kind of communication that attacks or uses pejorative or discriminatory language with reference to a person or a group on the basis of who they are, in other words, based on their religion, ethnicity, nationality, race, colour, descent, gender or other identity factor: https\://www\.un\.org/en/genocideprevention/documents/UN%20Strategy%20and%20Plan%20of%20Action%20on%20Hate%20Speech%2018%20June%20SYNOPSIS\.pdf\. To prevent hatespeech, I classify each message and image and notify you if it was considered hateful or offensive\. If you don't agree with the classification, you can type /poll to discuss the result with the group members\. All messages send in this group are processed by me\. If you don't agree to this processing, please do not send any messages\. We are currently working on opt\-out options\. Thank you, your Modergator\!",
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('I am Modergator and keep an eye out for hateful messages in this group. TODO'
                              'You can use the following commands:'
                              '/help'
                              '/joke'
                              '/optout'
                              '/optin')


def optout_command(update: Update, _: CallbackContext) -> None:
    """Save user to opt-out list"""
    user = update.effective_user
    optoutlist = pickle.load(open('optoutlist.pickle', 'rb'))
    if user.id not in optoutlist:
        pickle.dump(optoutlist + [user.id], open('optoutlist.pickle', 'wb'))
        update.message.reply_text(
            f'Your user ID {user.id} has been saved to our opt-out list. To opt in again, use the /optin command.')
    else:
        update.message.reply_text(
            f'You have already opted out. To opt in again, use the /optin command.')


def optin_command(update: Update, _: CallbackContext) -> None:
    """Remove user from opt-out list"""
    user = update.effective_user
    optoutlist = pickle.load(open('optoutlist.pickle', 'rb'))
    if user.id in optoutlist:
        optoutlist.remove(user.id)
        pickle.dump(optoutlist, open('optoutlist.pickle', 'wb'))
        update.message.reply_text(
            f'Your user ID {user.id} has been opted in again. To opt out, use the /optout command.')
    else:
        update.message.reply_text(
            f'You have already opted in. To opt out, use the /optout command.')


def joke_command(update: Update, _: CallbackContext) -> None:
    """Return a Chuck Norris dev joke when the command /joke is issued."""
    params = {"category": "dev"}
    r = requests.get(url='https://api.chucknorris.io/jokes/random', params=params)
    text = r.json()['value']
    update.message.reply_text(text)


def goodvibes_command(update, context):
    """Return a good vibes meme when the command /goodvibes is issued."""
    url = "http://imgflip.com/s/meme/Grumpy-Cat.jpg"
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=url)
    update.message.reply_text("Don't be like the grumpy cat. Spread good vibes")


def poll_command(update: Update, context: CallbackContext) -> None:
    """Sends a poll to discuss if the classification was correct"""
    questions = ["Offensive", "Hateful", "Normal", "I don't know"]
    message = context.bot.send_poll(
        update.effective_chat.id,
        "How would you classify the previous text?",
        questions,
        is_anonymous=True,
        allows_multiple_answers=False,
    )
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)


def receive_poll_answer(update: Update, context: CallbackContext) -> None:
    """Summarize a users poll vote"""
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]
    context.bot.send_message(
        context.bot_data[poll_id]["chat_id"],
        f"{update.effective_user.mention_html()} feels {answer_string}!",
        parse_mode=ParseMode.HTML,
    )
    context.bot_data[poll_id]["answers"] += 1
    # Close poll after three participants voted
    if context.bot_data[poll_id]["answers"] == 3:
        context.bot.stop_poll(
            context.bot_data[poll_id]["chat_id"], context.bot_data[poll_id]["message_id"]
        )


def receive_poll(update: Update, context: CallbackContext) -> None:
    """On receiving polls, reply to it by a closed poll copying the received poll"""
    actual_poll = update.effective_message.poll
    # Only need to set the question and options, since all other parameters don't matter for
    # a closed poll
    update.effective_message.reply_poll(
        question=actual_poll.question,
        options=[o.text for o in actual_poll.options],
        # with is_closed true, the poll/quiz is immediately closed
        is_closed=True,
        reply_markup=ReplyKeyboardRemove(),
    )


def handle_text(update: Update, _: CallbackContext) -> None:
    """Check text messages"""
    print('Handling text')

    answer = ''
    image_scores = {}

    """handle URLs"""
    entities = update.message.parse_entities()
    for key, value in entities.items():
        if key.type == 'url' and value.endswith(('.jpg', '.png', '.gif')):
            print(f'    Scoring caption image URL {value}')
            score = score_image(value)
            image_scores[value] = score

    """use hateXplain to evaluate text messages, return label and scores"""
    text = update.message.text
    params = {"text": text}
    r = requests.get(url=f"http://127.0.0.1:{PORTDICT['text-api']}/classifier", params=params)
    print(r.json())
    label = r.json()['label']
    text_scores = json.loads(r.json()['scores'])
    if label in ['offensive', 'hate']:
        target_groups = score_target(text)
        print("target_groups: ", target_groups)
        answer += f"Your message was deemed {label}. The scores are (hate, normal, offensive): {str(text_scores)}.\n"
        if target_groups:
            answer += f"your hate was probably directed towards {target_groups}."

    for key, value in image_scores.items():
        answer += f"Your image {key} was deemed{'' if value else ' not'} hateful.\n"

    #Access sender
    #sender = update.message.from_user
    #answer += f'The message was send by {sender}.\n'

    if answer:
        update.message.reply_text(answer)
        


def handle_voice(update: Update, context: CallbackContext) -> None:
    """Handle voice messages"""
    print('Handling voice')

    answer = ''

    if update.message.voice:
        file_id = update.message.voice.file_id
        file_path = context.bot.getFile(file_id).file_path

    text = voice_to_text(file_path)
    label, text_scores = score_text(text)

    target_groups = score_target(text)

    if label in ['hate', 'normal', 'offensive']:
        answer += f"Your voice message was deemed {label}.\n" \
                  f"Scores (hate, normal, offensive): {str(text_scores)}.\n" \
                  f"Transcription: {text}"
        if target_groups:
            answer += f"your hate was probably directed towards {target_groups}."

    if answer:
        update.message.reply_text(answer)


def handle_image(update: Update, context: CallbackContext) -> None:
    """Check images and their caption"""
    print('Handling image')

    answer = ''
    image_scores = {}

    entities = update.message.parse_caption_entities()
    for key, value in entities.items():
        if key.type == 'url' and value.endswith(('.jpg', '.png', '.gif')):
            print(f'    Scoring caption image URL {value}')
            score = score_image(value)
            image_scores[value] = score

    if update.message.caption:
        text = update.message.caption
        label, text_scores = score_text(text)
        if label in ['offensive', 'hate']:
            answer += f"Your message was deemed {label}. Scores (hate, normal, offensive): {str(text_scores)}.\n"

    # get file_path of image
    if update.message.document:
        file_path = update.message.document.get_file().file_path
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_path = context.bot.getFile(file_id).file_path
    else:
        raise NotImplementedError('Image type not implemented')

    # score image
    print(f'    Scoring sent image URL {file_path}')
    score = score_image(file_path)
    image_scores['sent from your phone'] = score

    for key, value in image_scores.items():
        answer += f"Your image {key} was deemed{'' if value else ' not'} hateful.\n"

    target_groups = score_target(text)
    if target_groups:
        answer += f"your hate was probably directed towards {target_groups}.\n"

    if answer:
        update.message.reply_text(answer)


def score_image(image_url):
    """Receives image URL and return hatefulness score"""
    filename = image_url.split("/")[-1]

    # include ocr-api, get extracted text which will be directed to text api
    params = {"path": image_url}
    r_ocr = requests.get(url=f"http://127.0.0.1:{PORTDICT['ocr-api']}/ocr", params=params)
    print(r_ocr.json())
    ocr_text = r_ocr.json()['ocr_text']
    print(f'OCR text recognized: {ocr_text}')  # TODO: remove debug print
    params = {"image": image_url, "image_description": ocr_text}
    r = requests.post(url=f"http://localhost:{PORTDICT['meme-model-api']}/classifier", data=params)
    if r.status_code == 200:
        r.raw.decode_content = True
        with open(f'{DATA_STUMP}image/{filename}', 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    else:
       raise ConnectionError(r.status_code)

    data = r.json()
    return data['result']


def score_text(text):
    """Receives text string and returns label and label scores"""
    params = {"text": text}
    r = requests.get(url=f"http://127.0.0.1:{PORTDICT['text-api']}/classifier", params=params)
    print(r.json())
    label = r.json()['label']
    text_scores = json.loads(r.json()['scores'])
    return label, text_scores

def score_target(text):
    params = {"text": text}
    r = requests.get(url=f"http://127.0.0.1:{PORTDICT['target-api']}/classifier", params=params)
    target_groups = json.dumps(r.json()['target_groups'])
    return target_groups

def voice_to_text(voice_url):
    """Receives voice URL and returns text"""
    print('Transcribing voice to text')

    filename = voice_url.split("/")[-1]
    r = requests.get(url=voice_url, stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True
        with open(f'{DATA_STUMP}voice/{filename}', 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    else:
        raise ConnectionError(r.status_code)

    params = {"filename": filename}
    r_asr = requests.get(url=f"http://127.0.0.1:{PORTDICT['voice-api']}/asr", params=params)
    transcription = r_asr.json()['transcription']
    for f in glob.glob(f'{DATA_STUMP}voice/*'):
        os.remove(f)

    print(f'Transcription: {transcription}')
    return transcription


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("joke", joke_command))
    dispatcher.add_handler(CommandHandler("optout", optout_command))
    dispatcher.add_handler(CommandHandler("optin", optin_command))
    dispatcher.add_handler(CommandHandler("goodvibes", goodvibes_command))
    dispatcher.add_handler(CommandHandler("poll", poll_command))
    dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
    dispatcher.add_handler(MessageHandler(Filters.poll, receive_poll))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dispatcher.add_handler(MessageHandler((Filters.photo | Filters.document.category('image')) & ~Filters.command, handle_image))
    dispatcher.add_handler(MessageHandler(Filters.voice & ~Filters.command, handle_voice))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()