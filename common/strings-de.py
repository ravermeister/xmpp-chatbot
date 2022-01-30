# coding=utf-8
from random import randint


class StaticAnswers:
    """
    collection of callable static/ semi-static strings
    """

    def __init__(self, nick=""):
        self.nickname = nick
        self.help_file = {
            'help': '!help -- diese Hilfe Anzeigen',
            'version': '!version domain.tld  -- die XMPP Server Version anzeigen',
            'uptime': '!uptime domain.tld -- die XMPP Server Laufzeit anzeigen',
            'contact': '!contact domain.tld -- die XMPP Server Kontakt Informationen anzeigen',
            'info': '!info domain.tld -- eine zusammenfassung der oberen Funktionen',
            'user': '!user domain.tld -- die anzahl der registrierten/online Benutzer auflisten',
            'xep': '!xep XEP Number -- die Informationen über eine XMPP XEP Spezifikation anzeigen',
            'man': '!man manpage -- einen Link zu der Man Page des angegeben Programms anzeigen',
            'chuck': '!chuck de -- einen ChuckNorris Witz erzählen'
        }
        self.possible_answers = {
            '1': '%s möge die Macht mit dir sein',
            '2': '%s es würde gegen meine Programmierung verstoßen, eine Gottheit zu personifizieren.',
            '3': 'Ich bin Luke Skywalker. %s Ich bin hier, um Sie zu retten.',
            '4': '%s vergiss nicht, die Macht wird mit dir sein, immer.',
            '5': '%s die Macht ist stark in meiner Familie. Mein Vater hat sie, ich habe sie, sogar meine Schwester '
                 'hat sie.',
            '6': '%s ich liebe es, wenn ein Plan funktioniert.',
            '7': '%s Es steht ihnen Frei, zu schreien und zu brüllen. Aber es wird sie niemand hören.',
            '8': '%s ich steig nicht in ein Flugzeug.'
        }
        self.error_messages = {
            '1': 'nicht erreichbar',
            '2': 'kein gültiges Ziel'
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
