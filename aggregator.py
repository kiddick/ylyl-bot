import os
import re
import logging
import yaml
from chan import api as chan
import requests
from models import Thread as ThreadModel
from models import Picture as PictureModel
import models

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('agregator')


class ConfigEntry(object):

    def __init__(self, name, entry_dict):
        for k, v in entry_dict.items():
            setattr(self, k, v)
        self.name = name


class Config(object):

    def __init__(self):
        self.entries = []

        cwd = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(cwd, 'config.yaml')) as stream:
            config = yaml.load(stream)

        for k, v in config.items():
            if k != 'entries':
                setattr(self, k, v)
            else:
                for name, content in v.items():
                    self.entries.append(ConfigEntry(name, content))


conf = Config()


class Agregator(object):

    def __init__(self, conf_entry):
        self.name = conf_entry.name
        self.board = conf_entry.board
        self.search_tags = conf_entry.search_tags

    def get_matched_threads(self):
        result = set()

        for num, op_text in chan.get_preview(self.board).items():
            for tag in self.search_tags:
                if tag in op_text.lower():
                    result.add(int(num))
                    logger.info('Thread is matched: %s - %s' % (num, op_text))

        return list(result)

    def search(self):
        matched_threads = self.get_matched_threads()

        models.cleanup(matched_threads)

        for thread_num in matched_threads:
            ThreadModel.get_or_create(num=thread_num)

        return matched_threads

    def __iter__(self):
        session = requests.Session()
        for thread in self.search():
            for post in chan.Thread(self.board, num=thread).posts:

                for pic in post.pictures:

                    if PictureModel.check_existance(pic.url):
                        continue

                    picture = PictureModel.create(
                        url=pic.url,
                        thread=thread,
                        caption=purify_message(post.message))

                    yield picture


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
