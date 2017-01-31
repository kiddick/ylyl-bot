# -*- coding: utf-8 -*-

import logging
from collections import namedtuple
from threading import Thread
import time
import re
from telegram import InlineKeyboardButton as Button
from telegram import InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, \
    MessageHandler, Filters
from telegram import Bot


from aggregator import Config, Agregator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('bot')
conf = Config()


def q(b, u):
    print(u.message.chat_id)

if __name__ == '__main__':
    # updater = Updater(conf.bot_token)
    # updater.dispatcher.add_handler(CommandHandler('q', q))
    # updater.start_polling()
    # updater.idle()

    bot = Bot(conf.bot_token)
    agregator = Agregator('b')
    while True:
        logger.info('Start aggregation')
        for pic in agregator:
            logger.info('Sending %s' % pic.name)
            bot.sendPhoto(
                chat_id=conf.chat_id,
                photo=open(pic.path, 'rb'),
                caption=pic.caption
            )
            time.sleep(3)

        logger.info('Finish aggregation')
        time.sleep(conf.sleep_interval)
