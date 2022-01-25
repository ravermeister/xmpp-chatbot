# 24.01.2022 Jonny Rimkus <jonny@rimkus.it>
# add method for Chuck Norris default answers

import urllib3
import requests

from random import randint
from html.parser import HTMLParser

class ChuckNorrisParser(HTMLParser):

    def initData(self):
        self.jokes = []
        self.resetTagSearch()
        
    def resetTagSearch(self):
        self.article = False
        self.paragraph = False
        
    def handle_starttag(self, tag, attrs):
        if(not self.article):
            self.article = (tag == "article")
        elif(self.article and not self.paragraph):
            self.paragraph = (tag == "p")

    def handle_data(self, data):
        if(self.article and self.paragraph):
            self.jokes.append(data)
            self.resetTagSearch()

    def get_jokes(self):
        return self.jokes

class ChuckNorrisRequest:
	"""
	> retrieve a ChuckNorris Joke
	"""
	def __init__(self):
		# init all necessary variables
		self.target, self.opt_arg = None, None
		self.api_en_1 = "https://api.icndb.com/jokes/random"
		self.api_en_2 = "https://api.chucknorris.io/jokes/random"
		self.api_de_1 = "https://chuck-norris-witze.de"
	
	def reply_en_2():
		try:
			apiUrl = self.api_en_2
			responseJson = requests.get(apiUrl).json()
			return responseJson["value"]
		except Exception as error:
			return "Error Calling Chuck Norris API: %s" % error	
	
	def reply_en_1():
		try:
			apiUrl = self.api_en_1
			responseJson = requests.get(apiUrl).json()
			return responseJson["value"]["joke"]
		except Exception as error:
			return "Error Calling Chuck Norris API: %s" % error	
	
	def reply_de_1():
		try:
			urllib3.disable_warnings()
			max_pages = 50
			page = randint(1, max_pages)
			apiUrl = self.api_de_1 + "/page/%s" % page

			html = requests.get(apiUrl, verify=False).text
			parser = ChuckNorrisParser()
			parser.initData()
			parser.feed(html)
		
			jokeIndex = randint(0, (len(parser.get_jokes()) - 1))
			return parser.get_jokes()[jokeIndex]
		except Exception as error:
			return "Fehler beim Aufruf der Chuck Norris API: %s" % error
	
	def format(self, queries, target, opt_arg):
		self.target = target
		self.opt_arg = opt_arg
		if(self.target == "de"):
			return self.reply_de_1()
		else
			return reply_en_1()
