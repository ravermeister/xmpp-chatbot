# coding=utf-8
from common.strings import StaticAnswers


# XEP-0072: Server Version
class Version:
	"""
	process and format a version query
	"""

	def __init__(self, static_answers: StaticAnswers):
		# init all necessary variables
		self.static_answers = static_answers
		self.software_version = None
		self.target, self.opt_arg = None, None

	def format_result(self):
		# list of all possible opt_arg
		possible_opt_args = ["version", "os", "name"]

		messages = self.static_answers.lang.command_messages

		name = self.software_version['name']
		version = self.software_version['version']
		os = self.software_version['os']
		if not os:
			os = messages['version.unknown-os']

		# if opt_arg is given member of possible_opt_args list return that element
		if self.opt_arg in possible_opt_args:
			text = "%s: %s" % (self.opt_arg, self.software_version[self.opt_arg])

		# otherwise, return full version string
		else:
			text = messages['version.running-on'] % (self.target, name, version, os)

		return text

	def format(self, queries, target, opt_arg):
		self.software_version = queries['xep_0072']['software_version']

		self.target = target
		self.opt_arg = opt_arg

		reply = self.format_result()
		return reply
