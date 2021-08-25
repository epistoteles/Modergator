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


TOKEN = ""

with open("telegram-bot/telegram_bot_token.txt", "r") as file:
    TOKEN = file.readline().strip()

print("TOKEN", TOKEN)
# flag scores above threshold as hateful
IMAGE_THRESHOLD = 0.5
TEXT_THRESHOLD = 0.5
DATA_STUMP = 'data/'

# use ports of portdict or docker ports
if os.path.isfile("portdict.pickle"):
    HOSTDICT = {"meme-model-api": '127.0.0.1',
                "text-api": '127.0.0.1',
                "ocr-api": '127.0.0.1',
                "asr-api": '127.0.0.1',
                "target-api": '127.0.0.1'}
    PORTDICT = pickle.load(open("portdict.pickle", "rb"))
else:
    HOSTDICT = {"meme-model-api": '172.20.0.11',
                "text-api": '172.20.0.12',
                "ocr-api": '172.20.0.13',
                "asr-api": '172.20.0.14',
                "target-api": '172.20.0.15'}
    PORTDICT = {"meme-model-api": 5001,
                "text-api": 5002,
                "ocr-api": 5003,
                "asr-api": 5004,
                "target-api": 5005}


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

debug = False


# Define a few command handlers. These usually take the two arguments update and context.
def start_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user.name
    message = f"Hello {user}!\n\nI am Modergator and able to keep an eye out for hateful content in any group that you add me to. If hate speech or offensive messages are detected, I will automatically intervene. I am able to understand text, memes and voice messages, currently limited to English language. Analyzing a meme takes some time for me, so please be patient. If you want to know more about how to interact with me, please type /howto. I will process everything, but never store anything else than temporarily logged user input, but NOT an id. Users are able to opt-out of this on an individual basis.\n\nHow to use me: Simply add me as a group member in your group. I am always listening in the background.\n\nYou can try out my skills right here in the chat. Simply send a text, image or voice message. If you want to know more, please type /help."
    update.message.reply_text(message)
    update.message.reply_sticker('CAACAgQAAxkBAAECzc1hJk-ca5GJr_3DrbU2mr_4z1vUJwACFQoAAsnWMFGh76YrQgo2GyAE')

def howto_command(update: Update, _: CallbackContext) -> None:
    """Give more information about how to use the bot for command /howto."""
    message = f"Text messages:\nYou can write or forward text messages. If I think it is hateful or offensive, I will reply to it. However, if you edit your message I will not be able to analyze it again.\n\n" \
               "Voice messages:\nYou can record and send a voice message and also forward one. I will transcribe it as good as I can. If I then think the transcription is hateful or offensive, I will reply to it.\n\n" \
               "Memes:\nYou can upload memes directly from your phone or send links ending in an image format. I will try to recognise the text on the meme and based on this estimate as well as the visuals if it is hateful or not. Analyzing a meme takes some time, so please be patient. I will only reply if I consider your image hateful.\n\n" \
               "Images:\nIf you send an image and I think it is not a meme, I will not reply to it.\n\n" \
               "Everything you send (always anonymized) will be temporarily logged so I can process your messages."

    update.message.reply_text(message)


def about_command(update: Update, _: CallbackContext) -> None:
    """Give more information about hate speech and the bot for the command /about."""
    message = f"Hate speech is any kind of communication that attacks or uses pejorative or discriminatory language with reference to a person or a group on the basis of who they are, in other words, based on their religion, ethnicity, nationality, race, colour, descent, gender or other identity factors (https://www.un.org/en/genocideprevention/documents/UN%20Strategy%20and%20Plan%20of%20Action%20on%20Hate%20Speech%2018%20June%20SYNOPSIS.pdf).\n\nTo prevent and handle hate speech, I classify each message, image and voice message and intervene if it was considered hateful or offensive. If you don't agree with my classification, you can type /poll to discuss the result with other group members (this feature is still in development). All messages sent in this group are processed (but never stored permanently) by me. If you don't agree to this processing, please type /optout and your messages will not be processed any more.\n\nHave fun and be nice!"
    update.message.reply_text(message)


def welcome_message(update: Update, context: CallbackContext) -> None:
    group = update.effective_chat.title
    users = ", ".join([x.name for x in update.message.new_chat_members if not x.is_bot])
    message = f"Hello {users} and welcome to {group}! I am Modergator and keep an eye out for hateful content in this group. This means I am reading, seeing and listening to (but never storing) everything you and others write, send or speak. Analyzing a meme takes some time for me, so please be patient.\n\nIf you want to know more about how to interact with me, please type /howto.\n\nIf you don’t want me to process and moderate your data, please /optout.\n\nLearn more about hate speech here: /about."
    if users:
        context.bot.send_message(text=message, chat_id=update.message.chat_id)
        context.bot.send_sticker(sticker='CAACAgQAAxkBAAECzc1hJk-ca5GJr_3DrbU2mr_4z1vUJwACFQoAAsnWMFGh76YrQgo2GyAE',
                                 chat_id=update.message.chat_id)


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('I am Modergator and keep an eye out for hateful messages in this group.\n'
                              'You can use the following commands:\n'
                              '/howto to learn more about how to interact with me\n'
                              '/optout to optout of the processing of your messages\n'
                              '/optin to opt-in again to the processing of your messages\n'
                              '/poll to dispute the classification (this feature is in progress)\n'
                              '/debug to see Modergators internal workings\n'
                              '/joke to make Modergator tell a joke\n'
                              '/help to get an overview of the commands\n')


def debug_command(update: Update, context: CallbackContext) -> None:
    """Always print lots of info for debugging purposes."""
    global debug
    debug = not debug
    update.message.reply_text(f"Debug mode is now {'on' if debug else 'off'}.\n\n")
    if debug:
        context.bot.send_sticker(sticker='CAACAgQAAxkBAAECzilhJqt7WBEwVU_M_FCzmzhRv1dOsQACPQoAAtcCOVEnuAJJ5xegvSAE',
                             chat_id=update.message.chat_id)


def optout_command(update: Update, _: CallbackContext) -> None:
    """Save user to opt-out list"""
    user = update.effective_user
    optoutlist = pickle.load(open('optoutlist.pickle', 'rb'))
    if user.id not in optoutlist:
        pickle.dump(optoutlist + [user.id], open('optoutlist.pickle', 'wb'))
        update.message.reply_text(
            f'Your user ID {user.id} has been saved to my opt-out list. To opt in again, use the /optin command.')
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
        "How would you classify the previous message?",
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


def handle_text(update: Update, context: CallbackContext) -> None:
    """Check text messages"""
    optoutlist = pickle.load(open('optoutlist.pickle', 'rb'))
    if (update.effective_user.id not in optoutlist):
        print('Handling text')

        answer = ''
        debug_message = '*Debug information:*\n\n'
        image_scores = {}
        image_ocr_text = ''

        """handle URLs"""
        entities = update.message.parse_entities()
        for key, value in entities.items():
            if key.type == 'url' and value.endswith(('.jpg', '.png', '.gif', '.jpeg', '.JPG', '.JPEG')):
                #KATRIN: detection API
                if detect_meme(value):
                    answer, image_ocr_text, image_scores = return_score_url(value, answer, image_ocr_text, image_scores)

        """use hateXplain to evaluate text messages, return label and scores"""
        text = update.message.text
        answer, label, debug_message, label_score = return_score_text_and_target(text, answer,debug_message, "text")

        answer_bot(answer, label, label_score, debug_message, context, update)
    else:
        pass

def handle_voice(update: Update, context: CallbackContext) -> None:
    """Handle voice messages"""
    optoutlist = pickle.load(open('optoutlist.pickle', 'rb'))
    if (update.effective_user.id not in optoutlist):
        print('Handling voice')

        answer = ''
        debug_message = '*Debug information:*\n\n'

        if update.message.voice:
            file_id = update.message.voice.file_id
            file_path = context.bot.getFile(file_id).file_path

        text = voice_to_text(file_path)
        answer, lable, debug_message, label_score = return_score_text_and_target(text,answer,debug_message,"asr")

        answer_bot(answer, label, label_score, debug_message, context, update)
    else:
        pass


def handle_image(update: Update, context: CallbackContext) -> None:
    """Check images and their caption"""
    optoutlist = pickle.load(open('optoutlist.pickle', 'rb'))
    if (update.effective_user.id not in optoutlist):
        print('Handling image')

        answer = ''
        debug_message = '*Debug information:*\n\n'
        image_scores = {}
        image_ocr_text = ''

        entities = update.message.parse_caption_entities()
        for key, value in entities.items():
            if key.type == 'url' and value.endswith(('.jpg', '.png', '.gif', '.jpeg', '.JPG', '.JPEG')):
                print(f'    Scoring caption image URL {value}')
                if detect_meme(value):
                        image_scores[value] = score_image(value)['result']



        """use hateXplain to evaluate the image caption and then evaluate the targets"""
        if update.message.caption:
            text = update.message.caption
            answer, label, debug_message, label_score = return_score_text_and_target(text,answer,debug_message,"caption")

        # get file_path of image
        if update.message.document:
            file_path = update.message.document.get_file().file_path
        elif update.message.photo:
            file_id = update.message.photo[-1].file_id
            file_path = context.bot.getFile(file_id).file_path
        else:
            raise NotImplementedError('Image type not implemented')

        #TODO TRAIN detection
        # score image
        answer, image_ocr_text, image_scores, debug_message = return_score_url(file_path, answer,image_ocr_text,image_scores, debug_message)

        target_groups = score_target(image_ocr_text)
        if target_groups and image_scores['sent from your device']:
            answer += f"your hate was probably directed towards the following group(s): {target_groups}.\n"

        if answer:
            update.message.reply_text(answer)
            context.bot.send_sticker(sticker='CAACAgQAAxkBAAECzh9hJpr02fbzkfolQjjqj8FsOrsNfgACIwoAApmdQVPxErY3me_ggSAE',
                                     chat_id=update.message.chat_id)
        if debug:
            debug_message += f'\nTo turn debug information off, type /debug\.'
            context.bot.send_message(text=debug_message, chat_id=update.message.chat_id, parse_mode='MarkdownV2')

    else:
        pass

def return_score_text_and_target(text,answer,debug_message,type):


def return_score_text_and_target(text,answer,debug_message,type):
    label, label_score, scores = score_text(text)
    if label in ['offensive', 'hate']:
        answer += f"{'I am sure' if label_score > 0.8 else 'I am quite sure' if label_score > 0.65 else 'I think'} that this {type} message is {label}. Please be nice and stick to the community guidelines.\n\n"
        target_groups = score_target(text)
        if len(target_groups) > 0:
            answer += f"Your hate was probably directed towards the following group(s): {target_groups}.\n\n"
        answer += f"If you think I made a mistake, use the /poll command to start a dispute.\n\n"
    if(type=="voice"):
        debug_message += f"``` Transcribed text:\n" \
                         f"   {text}\n" \
                         f"```"
    debug_message += f"``` Text scores:\n" \
                     f"   hateful:   {scores[0]:.3f}\n" \
                     f"   normal:    {scores[1]:.3f}\n" \
                     f"   offensive: {scores[2]:.3f}\n" \
                     f"```"
    return answer, label, debug_message, label_score


def return_score_url(file_path, answer, image_ocr_text, image_scores, debug_message):
    print(f'    Scoring sent image URL {file_path}')
    score_image_dic = score_image(file_path)
    image_ocr_text = score_image_dic['ocr_text']
    image_scores['sent from your device'] = score_image_dic['result']

    for key, value in image_scores.items():
        print("value:", value)
        if value:
            answer += f"Your image {key} was deemed hateful.\n"
            answer += f"We have estimated this with the transcription \"{image_ocr_text}\"."
        image_ocr_text_escaped = image_ocr_text
        for x in ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
            image_ocr_text_escaped = image_ocr_text_escaped.replace(x, f'\\{x}')
        debug_message += f"``` Image:\n" \
                         f"   classification:{'' if value else ' not'} hateful\.\n" \
                         f"   transcription:  \"{image_ocr_text_escaped}\"\n```"

    return answer, image_ocr_text, image_scores, debug_message


def answer_bot(answer, label, label_score, debug_message, context, update):
    if answer:
        update.message.reply_text(answer)
        if label in ['offensive']:
            context.bot.send_sticker(sticker='CAACAgQAAxkBAAECynRhIpFGQOdm7y-TY1FrRx3viIVZzgAC7QgAAnjTQFOyIhXLSEwbjiAE',
                                     chat_id=update.message.chat_id)
        elif label in ['hate'] and label_score < 0.6:
            context.bot.send_sticker(sticker='CAACAgQAAxkBAAECynJhIpFAWoXulQIFegHdKvtbweVWEQACzQkAAiu4SVOn7vfLIW3CcSAE',
                                     chat_id=update.message.chat_id)
        elif label in ['hate'] and label_score >= 0.6:
            context.bot.send_sticker(sticker='CAACAgQAAxkBAAECziFhJpr7eX1xs3HCpaV_GIzoHWmyQAAC1w8AAriMSFOjwvkd64nNJCAE',
                                     chat_id=update.message.chat_id)
    if debug:
        debug_message += f'\nScores range from 0 \(not sure\) to 1 \(very sure\)\. To turn debug information off, type /debug\.'
        context.bot.send_message(text=debug_message, chat_id=update.message.chat_id, parse_mode='MarkdownV2')


def score_image(image_url):
    print("Scoring image")
    """Receives image URL and return hatefulness score"""
    filename = image_url.split("/")[-1]

    # include ocr-api, get extracted text which will be directed to text api
    params = {"path": image_url}
    r_ocr = requests.get(url=f"http://{HOSTDICT['ocr-api']}:{PORTDICT['ocr-api']}/ocr", params=params)
    ocr_text = r_ocr.json()['ocr_text']
    print(f'    OCR text recognized: {ocr_text}')  # TODO: remove debug print
    params = {"image": image_url, "image_description": ocr_text}
    r = requests.post(url=f"http://{HOSTDICT['meme-model-api']}:{PORTDICT['meme-model-api']}/classifier", data=params)
    if r.status_code == 200:
        r.raw.decode_content = True
        with open(f'{DATA_STUMP}image/{filename}', 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    else:
        raise ConnectionError(r.status_code)

    data = r.json()
    print(f'    Scored image with ', {data['result']} )
    return {"result": data['result'], "ocr_text": ocr_text} #TODO warum als dic und nicht die variablen?


def score_text(text):
    print("Scoring text: ", text)
    """Receives text string and returns label and label scores"""
    params = {"text": text}
    r = requests.get(url=f"http://{HOSTDICT['text-api']}:{PORTDICT['text-api']}/classifier", params=params)
    label = r.json()['label']
    label_score = r.json()['label_score']
    scores = [float(x) for x in json.loads(r.json()['scores'])]
    label_score = float(label_score)
    print("label: ", label, " label_score: ", label_score, " scores: ", scores)
    return label, label_score, scores


def score_target(text):
    print("Scoring target with text: ", text)
    params = {"text": text}
    r = requests.get(url=f"http://{HOSTDICT['target-api']}:{PORTDICT['target-api']}/classifier", params=params)
    target_groups = json.dumps(r.json()['target_groups'])
    target_groups = target_groups.replace('\"', '')
    target_groups = target_groups.replace('\'', '')
    target_groups = target_groups.replace('[', '')
    target_groups = target_groups.replace(']', '')
    print("scored targets: ", target_groups)
    return target_groups

def detect_meme(url):
    print("Start Meme Detection")
    params = {"url": url}
    r = requests.get(url=f"http://127.0.0.1:{PORTDICT['meme-detection-api']}/classifier", params=params)
    is_meme = r.json()["result"]
    print("is_meme: ", is_meme)
    return is_meme

def detect_meme(url):
    print("Start Meme Detection")
    params = {"url": url}
    r = requests.get(url=f"http://127.0.0.1:{PORTDICT['meme-detection-api']}/classifier", params=params)
    is_meme = r.json()["result"]
    print("is_meme: ", is_meme)
    return is_meme


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
    r_asr = requests.get(url=f"http://{HOSTDICT['asr-api']}:{PORTDICT['asr-api']}/asr", params=params)
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
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("about", about_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("optout", optout_command))
    dispatcher.add_handler(CommandHandler("joke", joke_command))
    dispatcher.add_handler(CommandHandler("howto", howto_command))
    dispatcher.add_handler(CommandHandler("poll", poll_command))
    dispatcher.add_handler(CommandHandler("optin", optin_command))
    dispatcher.add_handler(CommandHandler("debug", debug_command))
    dispatcher.add_handler(CommandHandler("goodvibes", goodvibes_command))
    dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
    dispatcher.add_handler(MessageHandler(Filters.poll, receive_poll))
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome_message))

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
