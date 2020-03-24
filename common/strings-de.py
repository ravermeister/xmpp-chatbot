# -*- coding: utf-8 -*-
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
			'2': 'Ich weiß, sie mögen mich, ',
#			'3': 'Wenn das Universum ein helles Zentrum hat, bist du auf diesem Planeten am weitesten davon weg.',
#			'4': 'Vor lauter Aufregung hat mein Partner einen Schaltkreiskollaps erlitten.',
#			'5': 'Es würde gegen meine Programmierung verstoßen, eine Gottheit zu personifizieren.',
#			'6': 'Nach meiner Erfahrung gibt es so etwas wie Glück nicht.',
#			'7': 'Ich finde ihren Mangel an Glauben beklagenswert.',
#			'8': 'Hilfe, die Mühle ist ja nur Schrott!',
#			'9': 'Ich bin Luke Skywalker. Ich bin hier, um Sie zu retten.',
#			'10': '%s Vergiss nicht, die Macht wird mit dir sein, immer.',
#			'11': 'Das sind nicht die Droiden, die ihr sucht.',
#			'12': 'Die Macht ist stark in meiner Familie. Mein Vater hat sie, ich habe sie, sogar meine Schwester hat sie.',
#			'13': 'Ich liebe es, wenn ein Plan funktioniert.',
#			'14': 'Ich glaube nicht an Zufälle, ich glaube, dass es für alles was zufällig passiert einen Plan gibt.',
#			'15': 'Das ist die kleine Nachtmusik von Howling Mad Mondschein. Unser Programm kommt heute direkt aus den Indianerdünen.',
#			'16': 'Konfuzius sagt: Frauen und Würmer mit Warzen, sind schwer zu verarzten.',
#			'17': '%s Benutz deine Fantasie, oder ich borg dir meine!',
#			'18': '%s Glauben sie an Greenpeace? Also ich glaube an Greenpeace. Und Robert Hunter glaubt auch an Greenpeace. Und die armen Wale werden auch bald dran glauben müssen.',
#			'19': 'Uns fehlt nurnoch ein Kampflied und Uniformen und im Knopfloch tragen wir eine rote Nelke, aber keine aus Plastik den die ist was für Clowns. Und Clowns sind in einer ganz anderen Gewerkschaft.',
#			'20': 'Du hörst nur dein Erbsenhirn, wie es in deinem Kopf rumrollt!',
#			'21': '%s Es steht ihnen Frei, zu schreien und zu brüllen. Aber es wird sie niemand hören.',
#			'22': 'Ich steig nicht in ein Flugzeug.',
#			'23': 'Das ist meine Sprechede Faust, sie heißt KnockOut. Willst du mal mit KnockOut reden %s??'
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
		possible_answers = self.possible_answers
		return possible_answers[str(randint(1, possible_answers.__len__()))] % self.nickname

	def error(self,code):
		try:
			text = self.error_messages[str(code)]
		except KeyError:
			return 'unknown error'
		return text
