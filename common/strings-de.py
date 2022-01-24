# -*- coding: utf-8 -*-
# 24.01.2022 Jonny Rimkus <jonny@rimkus.it>
# add method for Chuck Norris default answers

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
		self.possible_answers = {
			'1': '%s möge die Macht mit dir sein',
			'2': 'Ich weiß %s, sie mögen mich, weil ich ein Schurke bin. Es gab leider nicht genug Schurken in ihrem Leben.',
			'3': 'Wenn das Universum ein helles Zentrum hat, ist %s auf diesem Planeten am weitesten davon weg.',
			'4': '%s es würde gegen meine Programmierung verstoßen, eine Gottheit zu personifizieren.',
			'5': '%s nach meiner Erfahrung gibt es so etwas wie Glück nicht.',
			'6': '%s ich finde ihren Mangel an Glauben beklagenswert.',
			'7': 'Ich bin Luke Skywalker. %s Ich bin hier, um Sie zu retten.',
			'8': '%s vergiss nicht, die Macht wird mit dir sein, immer.',
			'9': '%s das sind nicht die Droiden, die ihr sucht.',
			'10': '%s die Macht ist stark in meiner Familie. Mein Vater hat sie, ich habe sie, sogar meine Schwester hat sie.',
			'11': '%s ich liebe es, wenn ein Plan funktioniert.',
			'12': '%s, Konfuzius sagt: Frauen und Würmer mit Warzen, sind schwer zu verarzten.',
			'13': '%s benutz deine Fantasie, oder ich borg dir meine!',
			'14': '%s glauben sie an Greenpeace? Also ich glaube an Greenpeace. Und Robert Hunter glaubt auch an Greenpeace. Und die armen Wale werden auch bald dran glauben müssen.',
			'15': '%s uns fehlt nur noch ein Kampflied und Uniformen und im Knopfloch tragen wir eine rote Nelke, aber keine aus Plastik denn die ist was für Clowns. Und Clowns sind in einer ganz anderen Gewerkschaft.',
			'16': '%s du hörst nur dein Erbsenhirn, wie es in deinem Kopf rumrollt!',
			'17': '%s Es steht ihnen Frei, zu schreien und zu brüllen. Aber es wird sie niemand hören.',
			'18': '%s ich steig nicht in ein Flugzeug.',
			'19': 'Das ist meine Sprechede Faust, sie heißt KnockOut. Willst du mal mit KnockOut reden %s??',
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

	def gen_chucknorris_answer(self):
		use_nick = randint(0, 1)
		apiUrl ="https://api.chucknorris.io/jokes/random"
		if use_nick == 1:
			apiUrl = "https://api.chucknorris.io/jokes/random?name=%s" % self.nickname

		apiRequest = request.Request(apiUrl)
		apiRequest.add_header("accept", "application/json")
		apiRespone = request.urlopen(apiRequest)
		if apiResponse.status != 200:
			self.error(self, 1)
		return None

		responseJson = json.loads(apiResponse.read())
		return responseJson["value"]

	def gen_answer(self):
		chucknorris_answer = self.gen_chucknorris_answer()
		if chucknorris_answer != None and chucknorris_answer != "":
			return chucknorris_answer

		possible_answers = self.possible_answers
		return possible_answers[str(randint(1, possible_answers.__len__()))] % self.nickname
			
	def error(self,code):
		try:
			text = self.error_messages[str(code)]
		except KeyError:
			return 'unknown error'
		return text
