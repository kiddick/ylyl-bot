import os
import re
import logging
import yaml
from chan import api as chan
import requests
from models import Thread as ThreadModel
from models import Picture as PictureModel
import models

pics_base_dir = 'pics'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('agregator')


class Config(object):

    def __init__(self):
        cwd = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(cwd, 'config.yaml')) as stream:
            config = yaml.load(stream)

        for k, v in config.items():
            setattr(self, k, v)

conf = Config()


class Picture(object):

    def __init__(self, chan_pic):
        self.chan_pic = chan_pic
        self.thread_num = chan_pic.url.split('/')[-2]
        self.name = ''.join(chan_pic.url.split('/')[-2:])
        self.path = os.path.join(pics_base_dir, self.name)
        self.caption = ''

    def save_to_db(self):
        PictureModel.get_or_create(
            name=self.name,
            path=self.path,
            thread=self.thread_num
        )

    def download(self, session=None):

        logger.info('Downloading %s', self.chan_pic.url)
        if session:
            resp = session.get(self.chan_pic.url)
        else:
            resp = requests.get(self.chan_pic.url)

        with open(self.path, 'wb') as output:
            output.write(resp.content)

        target_size = self.chan_pic.size
        real_size = os.path.getsize(self.path) >> 10
        logger.info('Size (target/real): %s / %s' % (target_size, real_size))

        self.save_to_db()

    def remove(self):
        pass


class Agregator(object):

    def __init__(self, board):
        self.board = board
        self.thread_nums = []
        if not os.path.isdir(conf.pics_base_dir):
            os.makedirs(conf.pics_base_dir)

    def search(self):
        matched_threads = get_matched_threads(self.board)

        models.cleanup(matched_threads)

        for thread_num in matched_threads:
            ThreadModel.get_or_create(num=thread_num)

        self.thread_nums = matched_threads

    def __iter__(self):
        self.search()
        session = requests.Session()
        for thread in self.thread_nums:
            for post in chan.Thread(self.board, num=thread).posts:

                for pic in post.pictures:
                    picture = Picture(pic)

                    if PictureModel.check_existance(picture.name):
                        continue

                    picture.download(session)
                    picture.caption = purify_message(post.message)
                    yield picture


def get_matched_threads(board):
    result = set()

    for num, op_text in chan.get_preview(board).items():
        for tag in conf.search_tags:
            if tag in op_text.lower():
                result.add(int(num))
                logger.info('Thread is matched: %s - %s' % (num, op_text))

    return list(result)


def purify_message(text):
    rules = [
        (r'<a.*?</a>', ''),
        (r'<br>', ' '),
        (r'<span.*?>', ''),
        (r'</span>', '')
    ]

    for rule in rules:
        pattern, repl = rule
        text = re.sub(pattern, repl, text)

    return text
