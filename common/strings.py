# coding=utf-8

import logging
from importlib import import_module
from random import randint


class StaticAnswers:
    """
    collection of callable static/ semi-static strings
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, locale="en"):
        self.lang = import_module("lang.%s" % locale)
        logging.debug("loaded language: %s" % self.lang.language)

        self.keywords = {
            "keywords": ["!help", "!uptime", "!version", "!contact", "!info", "!user", "!xep", "!man", "!chuck",
                         "!paste"],
            "domain_keywords": ["!uptime", "!version", "!contact", "!info", "!user"],
            "no_arg_keywords": ["!help"],
            "number_keywords": ["!xep"],
            "string_keywords": ["!man", "!chuck"],
            "raw_msg_keywords": ["!paste"]

        }
        self.admin_commands = ["user"]

    def keys(self, key=""):
        # if specific keyword in referenced return that
        if key in self.keywords.keys():
            return self.keywords[key]

        # in any other case return the whole dict
        return self.keywords["keywords"]

    # noinspection PyUnresolvedReferences
    def gen_help(self, from_user, admin_users, admin_functions):
        admin_functions = [key[1:] for key in admin_functions]
        # noinspection DuplicatedCode
        help_items = self.lang.help_file.items()
        if from_user not in admin_users and from_user.bare not in admin_users:
            # remove admin commands from help
            filtered_keys = [key for key in self.lang.help_file.keys() if key not in admin_functions]
            help_items = {key: self.lang.help_file[key] for key in filtered_keys}.items()

        help_doc = "\n".join(['%s' % value for (_, value) in help_items])
        return help_doc

    # noinspection PyUnresolvedReferences
    def gen_answer(self, nickname=""):
        possible_answers = self.lang.possible_answers
        if len(nickname) > 0:
            nick_with_suffix = "%s:" % nickname
        else:
            nick_with_suffix = ""
        return possible_answers[str(randint(1, possible_answers.__len__()))] % nick_with_suffix

    # noinspection PyUnresolvedReferences
    def error(self, code):
        try:
            text = self.lang.error_messages[str(code)]
        except KeyError:
            return 'unknown error'
        return text
