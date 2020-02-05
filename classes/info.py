# -*- coding: utf-8 -*-

import servercontact
import version
import uptime

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
		
		srvUptime = uptime.LastActivity()
		srvVersion = version.Version()
		srvContact = servercontact.ServerContact()

		reply = srvUptime.format(queries=[queries['xep_0012']], target=self.target, opt_arg=self.opt_arg)
		reply += "\n" + srvVersion.format(queries=[queries['xep_0072']], target=self.target, opt_arg=self.opt_arg)
		reply += "\n" + srvContact.format(queries=[queries['xep_0157']], target=self.target, opt_arg=self.opt_arg)

		return reply
