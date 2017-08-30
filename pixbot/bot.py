# TODO add webserver that has a get that takes secret key and then adds job to send

import os
import json
import threading

from telegram.ext import (
    CommandHandler,
    Updater,
    )


KEY = os.environ.get('PIXBOT_TELEGRAM_KEY')
USER_STORE = os.environ.get('PIXBOT_STORE', os.path.join(os.environ.get('PWD'), '.pixuserstore'))
ADMIN_USER = os.environ.get('PIXBOT_ADMIN')
DEBUG = True if os.environ.get('PIXBOT_DEBUG') == 'True' else False


updater = Updater(token=KEY)


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


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('shutdown', shutdown))
updater.start_polling()
