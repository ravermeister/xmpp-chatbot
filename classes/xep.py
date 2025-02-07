# coding=utf-8
import os
import defusedxml.ElementTree as Et
import requests

from common.strings import StaticAnswers


class XEPRequest:
	"""
	class which requests the header of the referenced xep
	"""
	def __init__(self, static_answers: StaticAnswers):
		# init all necessary variables
		self.static_answers = static_answers
		self.reqxep, self.opt_arg = None, None

		self.xeplist = None
		self.acceptedxeps = list()

	def req_xeplist(self):
		"""
		query and save the current xep list to reduce network bandwidth
		"""
		# check if etag header is present if not set local_etag to ""
		if os.path.isfile("./common/.etag"):
			with open("./common/.etag") as file:
				local_etag = file.read()
		else:
			local_etag = ""

		with requests.Session() as s:
			# head request the xeplist.xml
			s.headers.update({'Accept': 'application/xml'})
			head = s.head("https://xmpp.org/extensions/xeplist.xml")
			etag = head.headers['etag']

			# compare etag with local_etag if they match up no request is made
			if local_etag == etag:
				with open("./common/xeplist.xml", "r") as file:
					self.xeplist = Et.fromstring(file.read())

			# if the connection is not possible use cached xml if present
			elif os.path.isfile("./common/xeplist.xml") and head.status_code != 200:
				with open("./common/xeplist.xml", "r") as file:
					self.xeplist = Et.fromstring(file.read())

			# in any other case request the latest xml
			else:
				r = s.get("https://xmpp.org/extensions/xeplist.xml")
				r.encoding = 'utf-8'
				local_etag = head.headers['etag']

				with open("./common/xeplist.xml", "w") as file:
					file.write(r.content.decode())
					self.xeplist = Et.fromstring(r.content.decode())

				with open('./common/.etag', 'w') as string:
					string.write(local_etag)

		# populate xep comparison list
		for xep in self.xeplist.findall(".//*[@accepted='true']/number"):
			self.acceptedxeps.append(xep.text)

	def get(self):
		"""
		function to query the xep entry if xepnumber is present in xeplist
		:return: formatted xep header information
		"""
		# all possible subtags grouped by location
		last_revision_tags = ["date", "version", "initials", "remark"]
		xep_tags = [
			"number", "title", "abstract", "type", "status", "approver",
			"shortname", "sig", "lastcall", "date", "version", "initials", "remark"
		]

		# check if xeplist is accurate
		self.req_xeplist()
		messages = self.static_answers.lang.command_messages

		result = list()
		# if requested number is member of acceptedxeps continue
		if str(self.reqxep) in self.acceptedxeps:
			searchstring = ".//*[@accepted='true']/[number='%s']" % self.reqxep

			for item in self.xeplist.findall(searchstring):
				# if the opt_arg references is member of xeptag return only that tag
				if self.opt_arg in xep_tags:

					# if the opt_arg references is member of last_revision_tags return only that subtag
					if self.opt_arg in last_revision_tags:
						query = item.find("last-revision").find(self.opt_arg)
					else:
						query = item.find(self.opt_arg)

					# append opt_arg results to the result list
					if query is not None:
						result.append("%s : %s" % (query.tag, query.text))
					else:
						result.append(messages['xep.no-tag'] % (self.reqxep, self.opt_arg))

				# in any other case return the general answer
				else:
					result_opts = ["title", "type", "abstract", "status"]
					for tag in result_opts:
						result.append(item.find(tag).text)

		# if the requested number is no member of acceptedxeps and/or not accepted return error.
		else:
			result.append(messages['xep.unavailable'] % self.reqxep)

		return result

	# noinspection PyUnusedLocal
	def format(self, queries, target, opt_arg):
		"""
		:param queries:
		:param target: number int or str to request the xep for
		:param opt_arg:
		:return:
		"""
		self.reqxep = int(target)
		self.opt_arg = opt_arg

		reply = self.get()

		text = '\n'.join(reply)
		return text
