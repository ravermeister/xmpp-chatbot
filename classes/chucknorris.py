# coding=utf-8
from html.parser import HTMLParser
from random import randint
from common.strings import StaticAnswers

import requests
import urllib3


class ChuckNorrisParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.jokes = []
        self.article = False
        self.paragraph = False
        self.reset_tag_search()

    def reset_tag_search(self):
        self.article = False
        self.paragraph = False

    def handle_starttag(self, tag, attrs):
        if not self.article:
            self.article = (tag == "article")
        elif self.article and not self.paragraph:
            self.paragraph = (tag == "p")

    def handle_data(self, data):
        if self.article and self.paragraph:
            self.jokes.append(data)
            self.reset_tag_search()

    def get_jokes(self):
        return self.jokes


class ChuckNorrisRequest:
    """
    > retrieve a ChuckNorris Joke
    """

    def __init__(self, static_answers: StaticAnswers):
        # init all necessary variables
        self.static_answers = static_answers
        self.target, self.opt_arg = None, None
        self.api_en_1 = "https://api.icndb.com/jokes/random"
        self.api_en_2 = "https://api.chucknorris.io/jokes/random"
        self.api_de_1 = "https://chuck-norris-witze.de"

    def reply_en_2(self):
        try:
            api_url = self.api_en_2
            response_json = requests.get(api_url).json()
            return response_json["value"]
        except Exception as error:
            return "Error Calling Chuck Norris API: %s" % error

    def reply_en_1(self):
        try:
            api_url = self.api_en_1
            response_json = requests.get(api_url).json()
            return response_json["value"]["joke"]
        except Exception as error:
            return "Error Calling Chuck Norris API: %s" % error

    def reply_de_1(self):
        try:
            urllib3.disable_warnings()
            max_pages = 50
            page = randint(1, max_pages)
            api_url = self.api_de_1 + "/page/%s" % page

            html = requests.get(api_url, verify=False).text
            parser = ChuckNorrisParser()
            parser.feed(html)

            joke_index = randint(0, (len(parser.get_jokes()) - 1))
            return parser.get_jokes()[joke_index]
        except Exception as error:
            return "Fehler beim Aufruf der Chuck Norris API: %s" % error

    # noinspection PyUnusedLocal
    def format(self, queries, target, opt_arg):
        self.target = target
        self.opt_arg = opt_arg
        if self.target == "de":
            return self.reply_de_1()
        else:
            return self.reply_en_1()
