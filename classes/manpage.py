# coding=utf-8
from common.strings import StaticAnswers


# Linux Manpages Request
class ManPageRequest:
	"""
	> query the Linux Manpages for the given argument
	"""
	def __init__(self, static_answers: StaticAnswers):
		# init all necessary variables
		self.static_answers = static_answers
		self.target, self.opt_arg = None, None

	# noinspection PyUnusedLocal
	def format(self, queries, target, opt_arg):
		self.target = target
		self.opt_arg = opt_arg

		man_url = "https://man.cx/"
		reply = man_url + self.target

		return reply
