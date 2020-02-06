# -*- coding: utf-8 -*-

# Linux Manpages Request
class ManPageRequest:
	"""
	> query the Linux Manpages for the given argument
	"""
	def __init__(self):
		# init all necessary variables
		self.target, self.opt_arg = None, None

	def format(self, queries, target, opt_arg):
		self.target = target
		self.opt_arg = opt_arg

		manurl = "https://man.cx/"
		reply = manurl + self.target

		return reply
