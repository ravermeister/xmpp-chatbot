# -*- coding: utf-8 -*-
# 24.01.2022 Jonny Rimkus <jonny@rimkus.it>
# Chuck Norris default answers

import logging
import json
import urllib.request

from random import randint

class StaticAnswers:
	"""
	collection of callable static/ semi-static strings
	"""
	def __init__(self, nick=""):
		self.nickname = nick
		self.helpfile = {
			'help':		'!help -- diese Hilfe Anzeigen',
			'version':	'!version domain.tld  -- die XMPP Server Version anzeigen',
			'uptime':	'!uptime domain.tld -- die XMPP Server Laufzeit anzeigen',
			'contact':	'!contact domain.tld -- die XMPP Server Kontakt Informationen anzeigen',
			'info':		'!info domain.tld -- eine zusammenfassung der oberen funktionen',
			'xep': 		'!xep XEP Number -- die Informationen über eine XMPP XEP Spezifkation anzeigen',
			'man':		'!man manpage -- einen Link zu der Man Page des angegeben Programms anzeigen'
		}
		self.error_messages = {
			'1': 'nicht erreichbar',
			'2': 'kein gültiges Ziel'
		}
		self.keywords = {
			"keywords": ["!help", "!uptime", "!version", "!contact", "!info", "!xep", "!man"],
			"domain_keywords": ["!uptime", "!version", "!contact", "!info"],
			"no_arg_keywords": ["!help"],
			"number_keywords": ["!xep"],
			"string_keywords": ["!man"]
		}

	def keys(self, key=""):
		# if specific keyword in referenced return that
		if key in self.keywords.keys():
			return self.keywords[key]

		# in any other case return the whole dict
		return self.keywords["keywords"]

	def gen_help(self):
		helpdoc = "\n".join(['%s' % value for (_, value) in self.helpfile.items()])
		return helpdoc

	def gen_answer(self):
        use_nick = randint(0, 1)
        apiUrl ="https://api.chucknorris.io/jokes/random"
        if use_nick == 1:
            apiUrl = "https://api.chucknorris.io/jokes/random?name=%s" % self.nick
        logging.debug("using Chuck Norris API URL: %s" % apiUrl)

        apiRequest = request.Request(apiUrl)
        apiRequest.add_header("accept", "application/json")        
        apiRespone = request.urlopen(apiRequest)
        if apiResponse.status != 200:
            logging.error("Error calling Chuck Norris API, return Code %s" % apiResponse.status)
            return "Error Calling %s, Status %s" % apiUrl apiResponse.status
        
        responseJson = json.loads(apiResponse.read())
        
		return responseJson["value"]

	def error(self,code):
		try:
			text = self.error_messages[str(code)]
		except KeyError:
			return 'unknown error'
		return text
