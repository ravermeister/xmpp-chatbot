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
            '2': 'not a valid target',
            '3': 'you are not allowed to execute the command %s'
        }
        self.keywords = {
            "keywords": ["!help", "!uptime", "!version", "!contact", "!info", "!user", "!xep", "!man", "!chuck"],
            "domain_keywords": ["!uptime", "!version", "!contact", "!info", "!user"],
            "no_arg_keywords": ["!help"],
            "number_keywords": ["!xep"],
            "string_keywords": ["!man", "!chuck"]
        }
        self.admin_commands = ["user"]

    def keys(self, key=""):
        # if specific keyword in referenced return that
        if key in self.keywords.keys():
            return self.keywords[key]

        # in any other case return the whole dict
        return self.keywords["keywords"]

    def gen_help(self, from_user, admin_users, admin_functions):
        admin_functions = [key[1:] for key in admin_functions]
        # noinspection DuplicatedCode
        help_items = self.help_file.items()
        if from_user not in admin_users and from_user.bare not in admin_users:
            # remove admin commands from help
            filtered_keys = [key for key in self.help_file.keys() if key not in admin_functions]
            help_items = {key: self.help_file[key] for key in filtered_keys}.items()

        help_doc = "\n".join(['%s' % value for (_, value) in help_items])
        return help_doc

    def gen_answer(self):
        possible_answers = self.possible_answers
        nick_with_suffix = "%s:" % self.nickname
        return possible_answers[str(randint(1, possible_answers.__len__()))] % nick_with_suffix

    def error(self, code):
        try:
            text = self.error_messages[str(code)]
        except KeyError:
            return 'unknown error'
        return text
