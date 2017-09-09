import os
import json
import threading
import random

from bottle import (
    request,
    route,
    run,
    )
from telegram.ext import (
    CommandHandler,
    Job,
    Updater,
    )

#TODO trim '@' off of user names in store
#TODO better store management
#TODO better debugging
#TODO cleanup?

KEY = os.environ.get('PIXBOT_TELEGRAM_KEY')
USER_STORE = os.environ.get('PIXBOT_STORE', os.path.join(os.environ.get('PWD'), '.pixuserstore'))
ADMIN_USER = os.environ.get('PIXBOT_ADMIN')
DEBUG = True if os.environ.get('PIXBOT_DEBUG') == 'True' else False
PICTURE_PATH = os.environ.get('PIXBOT_PICTURE_PATH', 'pictures')


updater = Updater(token=KEY)
job_queue = updater.job_queue


def _shutdown():
    updater.stop()
    updater.is_idle = False


def start(bot, update):
    chat_id = update.message.chat_id
    username = update.message.from_user.name
    try:
        store = json.load(file(USER_STORE))
        if DEBUG:
            print 'Found store at %s' % USER_STORE
    except IOError, ValueError:
        if DEBUG:
            print 'Generating new store'
        store = {}
    store[username] = chat_id
    json.dump(store, file(USER_STORE, 'w'))
    bot.send_message(
        chat_id=chat_id,
        text='Hi there! People can now use me to send you pics!')


def shutdown(bot, update):
    username = update.message.from_user.name
    if DEBUG:
        print username
    if username == ADMIN_USER:
        if DEBUG:
            print "shutting down..."
        threading.Thread(target=_shutdown).start()


def _send_pic(bot, job=None, chat_id=None):
    if DEBUG:
        print PICTURE_PATH
    pic_list = os.listdir(PICTURE_PATH)
    random.shuffle(pic_list)
    pic = os.path.join(PICTURE_PATH, pic_list[0])
    if DEBUG:
        print pic
    if chat_id is None:
        if DEBUG:
            print "Getting chat_id from job"
        chat_id = job.context
        if DEBUG:
            print chat_id
    bot.send_photo(chat_id=chat_id, photo=open(pic, 'rb'))


def send_pic(bot, update):
    chat_id = update.message.chat_id
    if DEBUG:
        print chat_id
    _send_pic(bot, chat_id=chat_id)


def start_updater():
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('pic', send_pic))
    updater.dispatcher.add_handler(CommandHandler('shutdown', shutdown))
    updater.start_polling()


@route('/sendpic', method='post')
def send_pic_method():
    store = json.load(file(USER_STORE))
    username = request.forms.get('username')
    if username is not None:
        chat_id = store[username]
        job_queue.put(Job(_send_pic, 0.0, context=chat_id, repeat=False))


def _server():
    run(host='0.0.0.0', port=5000)


def server():
    threading.Thread(target=_server).start()


if __name__== "__main__":
    server()
    start_updater()
