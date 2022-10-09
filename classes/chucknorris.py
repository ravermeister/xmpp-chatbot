# coding=utf-8
from html.parser import HTMLParser
from random import randint
from common.strings import StaticAnswers

import requests
import urllib3


class ChuckNorrisParser(HTMLParser):

    def __init__(self, parser_type):
        super().__init__()

        if parser_type not in ['de_1', 'de_2']:
            raise NotImplementedError("Parser %s is not implemented" % parser_type)

        # parser_type: de_1
        self.article = False
        self.paragraph = False
        # parser_type: de_2
        self.div_entry = False
        self.paragraph = False

        self.jokes = []
        self.type = parser_type
        self.reset_tag_search()

    def reset_tag_search(self):
        # parser_type: de_1
        self.article = False
        self.paragraph = False
        # parser_type: de_2
        self.div_entry = False
        self.paragraph = False

    def handle_starttag(self, tag, attrs):
        if self.type == 'de_1':
            if not self.article:
                self.article = (tag == "article")
            elif self.article and not self.paragraph:
                self.paragraph = (tag == "p")
        else:
            if not self.div_entry:
                self.div_entry = (tag == "div" and ('class', 'entry') in attrs)
            elif self.div_entry and not self.paragraph:
                self.paragraph = (tag == "p")

    def handle_data(self, data):
        if self.article and self.paragraph:
            self.jokes.append(data)
            self.reset_tag_search()
        elif self.div_entry and self.paragraph:
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
        # currently unavailable
        self.api_en_1 = "https://api.icndb.com/jokes/random"
        self.api_en_2 = "https://api.chucknorris.io/jokes/random"
        # currently unavailable
        self.api_de_1 = "https://chuck-norris-witze.de"
        self.api_de_2 = "https://www.roundhousekick.de/wp-admin/admin-ajax.php?id=&post_id=0&slug=home&canonical_url=/&posts_per_page=50&page=%s&offset=0&post_type=post&repeater=default&seo_start_page=1&preloaded=false&preloaded_amount=0&order=DESC&orderby=date&action=alm_get_posts&query_type=standard"

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
            response_json = requests.get(api_url, verify=False).json()
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
            parser = ChuckNorrisParser('de_1')
            parser.feed(html)

            joke_index = randint(0, (len(parser.get_jokes()) - 1))
            return parser.get_jokes()[joke_index]
        except Exception as error:
            return "Fehler beim Aufruf der Chuck Norris API: %s" % error

    def reply_de_2(self):
        try:
            urllib3.disable_warnings()
            max_pages = 50
            page = randint(1, max_pages)
            api_url = self.api_de_2 % page
            response_json = requests.get(api_url, verify=False).json()
            html = response_json["html"].replace('\\r', '').replace('\\n', '').replace('\\t', '').replace('\\', '')
            parser = ChuckNorrisParser('de_2')
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
            return self.reply_de_2()
        else:
            return self.reply_en_2()
