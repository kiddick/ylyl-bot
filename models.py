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
    start_date = DateTimeField(default=datetime.now)


class Picture(BaseModel):

    url = CharField(default='')
    name = CharField(default='')
    path = CharField(default='')
    thread = IntegerField(default=0)

    @classmethod
    def check_existance(cls, name):
        return len(Picture.select().where(Picture.name == name)) > 0


def cleanup(thread_nums):
    candidates = [t.num for t in Thread.select() if t.num not in thread_nums]
    if not candidates:
        return

    logger.info('Performing cleanup')
    Thread.delete().where(Thread.num.in_(candidates)).execute()

    pics_num = 0
    for pic in Picture.select().where(Picture.thread.in_(candidates)):
        os.remove(pic.path)
        pics_num += 1

    logger.info('Removed %s pics' % pics_num)

    Picture.delete().where(Picture.thread.in_(candidates)).execute()


def create_tables():
    with db.transaction():
        for model in [Thread, Picture]:
            if not model.table_exists():
                db.create_table(model)

create_tables()
