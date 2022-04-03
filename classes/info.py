# coding=utf-8
from classes.servercontact import ServerContact
from classes.uptime import LastActivity
from classes.version import Version
from common.strings import StaticAnswers

# XEP-0012: Last Activity
# XEP-0072: Server Version
# XEP-0157: Contact Addresses for XMPP Services


class ServerInfo:
	"""
	> query the server uptime of the specified domain, defined by XEP-0012
	> process and format a version query
	> plugin to process the server contact addresses from a disco query
	"""

	def __init__(self, static_answers: StaticAnswers):
		# init all necessary variables
		self.static_answers = static_answers
		self.target, self.opt_arg = None, None

	def format(self, queries, target, opt_arg):
		self.target = target
		self.opt_arg = opt_arg

		srv_uptime = LastActivity(self.static_answers).format(queries=queries, target=self.target, opt_arg=self.opt_arg)
		srv_version = Version(self.static_answers).format(queries=queries, target=self.target, opt_arg=self.opt_arg)
		srv_contact = ServerContact(self.static_answers).format(queries=queries, target=self.target, opt_arg=self.opt_arg)

		return "%s\n%s\n%s" % (srv_uptime, srv_version, srv_contact)
