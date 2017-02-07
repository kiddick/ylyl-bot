# -*- coding: utf-8 -*-

import logging
from collections import namedtuple
from threading import Thread
import time
import re
from concurrent import futures

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


def worker(entry):
    agregator = Agregator(entry)
    bot = Bot(entry.bot_token)

    while True:
        logger.info('%s: Start aggregation' % entry.name)

        for pic in agregator:
            logger.info('%s: Sending %s' % (entry.name, pic.url))
            try:
                bot.sendPhoto(
                    chat_id=entry.chat_id,
                    photo=pic.url,
                    caption=pic.caption
                )
            except telegram.error.BadRequest:
                logger.exception('%s went down' % entry.name)
            else:
                time.sleep(entry.sending_interval)

        logger.info('%s: Finish aggregation' % entry.name)
        time.sleep(entry.sleep_interval)

if __name__ == '__main__':
    # updater = Updater(conf.bot_token)
    # updater.dispatcher.add_handler(CommandHandler('q', q))
    # updater.start_polling()
    # updater.idle()
    with futures.ThreadPoolExecutor(max_workers=len(conf.entries)) as ex:
        for entry in conf.entries:
            ex.submit(worker, entry)
