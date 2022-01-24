# 24.01.2022 Jonny Rimkus <jonny@rimkus.it>
# add method for Chuck Norris default answers

import logging
import requests

class Answers:

	def __init__():
		self.api_en_1 = "https://api.icndb.com/jokes/random"
		self.api_en_2 = "https://api.chucknorris.io/jokes/random"
		self.api_de_1 = "https://chuck-norris-witze.de"
		
	def answer_en2(nickname=None):
		apiUrl = self.api2_en
		if nickname != None and len(nickname) > 0:
			apiUrl = self.api2_en + "?name=%s" % nickname
		logging.debug("using Chuck Norris API URL '%s'" % apiUrl)

		try:
			responseJson = requests.get(apiUrl).json()
			return responseJson["value"]
		except Exception as error:
			logging.error("Error Calling Chuck Norris API: %s" % error)
		return None
				
