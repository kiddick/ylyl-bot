import time
import random
import os
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger('agregator')

from peewee import *

# config = load_config()
DATABASE_NAME = 'sesh.db'


db = SqliteDatabase(DATABASE_NAME)


class BaseModel(Model):

    class Meta:
        database = db


class Thread(BaseModel):

    num = IntegerField(default=0)
    board = CharField(default='b')
    start_date = DateTimeField(default=datetime.now)


class Picture(BaseModel):

    url = CharField(default='')
    caption = CharField(default='')
    thread = IntegerField(default=0)

    @classmethod
    def check_existance(cls, url):
        return len(Picture.select().where(Picture.url == url)) > 0


def cleanup(board, thread_nums):
    query = Thread.select().where(Thread.board == board)
    candidates = [t.num for t in query if t.num not in thread_nums]
    if not candidates:
        return

    logger.info('Performing cleanup')
    Thread.delete().where(Thread.num.in_(candidates)).execute()
    Picture.delete().where(Picture.thread.in_(candidates)).execute()


def create_tables():
    with db.transaction():
        for model in [Thread, Picture]:
            if not model.table_exists():
                db.create_table(model)

create_tables()
