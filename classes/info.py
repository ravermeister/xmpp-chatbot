from classes.servercontact import ServerContact
from classes.version import Version
from classes.uptime import LastActivity


# XEP-0012: Last Activity
# XEP-0072: Server Version
# XEP-0157: Contact Addresses for XMPP Services
class ServerInfo:
	"""
	> query the server uptime of the specified domain, defined by XEP-0012
	> process and format a version query
	> plugin to process the server contact addresses from a disco query
	"""

	def __init__(self):
		# init all necessary variables
		self.target, self.opt_arg = None, None

	def format(self, queries, target, opt_arg):
		self.target = target
		self.opt_arg = opt_arg

		srv_uptime = LastActivity()
		srv_version = Version()
		srv_contact = ServerContact()

		reply = srv_uptime.format(queries=queries, target=self.target, opt_arg=self.opt_arg)
		reply += "\n" + srv_version.format(queries=queries, target=self.target, opt_arg=self.opt_arg)
		reply += "\n" + srv_contact.format(queries=queries, target=self.target, opt_arg=self.opt_arg)

		return reply
