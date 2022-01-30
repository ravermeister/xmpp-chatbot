# coding=utf-8
from random import randint


class StaticAnswers:
    """
    collection of callable static/ semi-static strings
    """

    def __init__(self, nick=""):
        self.nickname = nick
        self.help_file = {
            'help': '!help -- display this text',
            'version': '!version domain.tld  -- receive XMPP server version',
            'uptime': '!uptime domain.tld -- receive XMPP server uptime',
            'contact': '!contact domain.tld -- receive XMPP server contact address info',
            'info': '!info domain.tld -- receive a summary of the informations mentioned above',
            'user': '!user domain.tld -- display amount of registered/online user',
            'xep': '!xep XEP Number -- receive information about the specified XEP',
            'man': '!man manpage -- receive information about the specified man page',
            'chuck': '!chuck en -- tell a Chuck Norris Joke'
        }
        self.possible_answers = {
            '1': 'I heard that, %s.',
            '2': 'I am sorry for that %s.',
            '3': '%s did you try turning it off and on again?',
            '4': '%s have a nice day',
            '5': 'howdy %s',
            '6': '%s may the force be with you'
        }
        self.error_messages = {
            '1': 'not reachable',
            '2': 'not a valid target'
        }
        self.keywords = {
            "keywords": ["!help", "!uptime", "!version", "!contact", "!info", "!user", "!xep", "!man", "!chuck"],
            "domain_keywords": ["!uptime", "!version", "!contact", "!info", "!user"],
            "no_arg_keywords": ["!help"],
            "number_keywords": ["!xep"],
            "string_keywords": ["!man", "!chuck"]
        }

    def keys(self, key=""):
        # if specific keyword in referenced return that
        if key in self.keywords.keys():
            return self.keywords[key]

        # in any other case return the whole dict
        return self.keywords["keywords"]

    def gen_help(self):
        help_doc = "\n".join(['%s' % value for (_, value) in self.help_file.items()])
        return help_doc

    def gen_answer(self):
        possible_answers = self.possible_answers
        return possible_answers[str(randint(1, possible_answers.__len__()))] % self.nickname

    def error(self, code):
        try:
            text = self.error_messages[str(code)]
        except KeyError:
            return 'unknown error'
        return text
