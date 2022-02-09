#!/usr/bin/env python3
# coding=utf-8

"""
	James the MagicXMPP Bot
	build with Slick XMPP Library
	Copyright (C) 2018 Nico Wellpott, 2022 Jonny Rimkus

	See the file LICENSE for copying permission.
"""
import slixmpp
import ssl
import configparser
import logging

from argparse import ArgumentParser
from slixmpp.exceptions import XMPPError

import common.misc as misc
from common.strings import StaticAnswers
from classes.servercontact import ServerContact
from classes.version import Version
from classes.uptime import LastActivity
from classes.xep import XEPRequest
from classes.info import ServerInfo
from classes.users import UserInfo
from classes.manpage import ManPageRequest
from classes.chucknorris import ChuckNorrisRequest


class QueryBot(slixmpp.ClientXMPP):
	def __init__(self, jid, password, room, nick, reply_private=False, admin_command_users=""):
		slixmpp.ClientXMPP.__init__(self, jid, password)
		self.ssl_version = ssl.PROTOCOL_TLSv1_2
		self.room = room
		self.nick = nick
		self.use_message_ids = True
		self.reply_private = reply_private
		self.admin_users = admin_command_users.split(sep=",")

		self.functions = {
			"!uptime": LastActivity(),
			"!contact": ServerContact(),
			"!version": Version(),
			"!info": ServerInfo(),
			"!user": UserInfo(),
			"!xep": XEPRequest(),
			"!man": ManPageRequest(),
			"!chuck": ChuckNorrisRequest()
		}
		self.admin_functions = [
			"!user"
		]

		# session start event, starting point for the presence and roster requests
		self.add_event_handler('session_start', self.start)

		# register receive handler for both groupchat and normal message events
		self.add_event_handler('message', self.message)

	# noinspection PyUnusedLocal
	def start(self, event):
		"""
		:param event -- An empty dictionary. The session_start event does not provide any additional data.
		"""
		self.send_presence()
		self.get_roster()

		# If a room password is needed, use: password=the_room_password
		if self.room:
			for rooms in self.room.split(sep=","):
				logging.debug("joining: %s" % rooms)
				# join_muc will be deprecated in slixmpp 1.8.0
				# see https://slixmpp.readthedocs.io/en/latest/api/plugins/xep_0045.html?highlight=join_muc_wait#slixmpp.plugins.xep_0045.XEP_0045.join_muc_wait
				# self.plugin['xep_0045'].join_muc_wait(rooms, self.nick, maxstanzas=0)
				self.plugin['xep_0045'].join_muc(rooms, self.nick)

	def send_response(self, reply_data, original_msg):

		nick_added = False
		# add pre predefined text to reply list
		if not reply_data:
			if self.nick in original_msg['body'] and not original_msg['type'] == "chat":
				reply_data.append(StaticAnswers(original_msg['mucnick']).gen_answer())
				nick_added = True
			elif original_msg['type'] == "chat":
				reply_data.append(StaticAnswers(original_msg['mucnick']).gen_answer())

		# remove None type from list and send all elements
		reply_data = list(filter(None, reply_data))

		if reply_data:
			# use bare jid as default receiver
			msg_to = original_msg['from'].bare
			# use original message type as default answer type
			msg_type = original_msg['type']

			# if msg type is groupchat and reply private is False prepend mucnick
			if original_msg["type"] == "groupchat" and self.reply_private is False and nick_added is False:
				reply_data[0] = "%s: " % original_msg["mucnick"] + reply_data[0]
			# if msg type is groupchat and reply private is True answer as with private message
			# do NOT use bare jid for receiver
			elif original_msg["type"] == "groupchat" and self.reply_private is True:
				msg_to = original_msg['from']
				msg_type = 'chat'
			# if msg type is chat (private) do NOT use bare jid for receiver
			elif original_msg['type'] == "chat":
				msg_to = original_msg['from']

			# reply = misc.deduplicate(reply)
			self.send_message(msg_to, mbody="\n".join(reply_data), mtype=msg_type)

	async def message(self, msg):
		"""
		:param msg: received message stanza
		"""
		data = {
			'words': list(),
			'reply': list(),
			'queue': list()
		}

		# catch self messages to prevent self flooding
		if msg['mucnick'] == self.nick:
			return

		data = self.build_queue(data, msg)
		keyword_occurred = False
		# queue
		for job in data['queue']:
			keys = list(job.keys())
			keyword = keys[0]
			target = job[keyword][0]
			opt_arg = job[keyword][1]
			queries = dict()

			if keyword == '!help':
				keyword_occurred = True
				data['reply'].append(StaticAnswers().gen_help(msg['from'], self.admin_users, self.admin_functions))
				continue
			# user is not allowed to call admin Commands
			elif keyword in self.admin_functions \
				and msg['from'] not in self.admin_users \
				and msg['from'].bare not in self.admin_users:
				keyword_occurred = True
				data['reply'].append(StaticAnswers().error(3) % keyword)
				continue

			try:
				if keyword == "!uptime":
					keyword_occurred = True
					queries['xep_0012'] = await self['xep_0012'].get_last_activity(jid=target)

				elif keyword == "!version":
					keyword_occurred = True
					queries['xep_0072'] = await self['xep_0092'].get_version(jid=target)

				elif keyword == "!contact":
					keyword_occurred = True
					queries['xep_0157'] = await self['xep_0030'].get_info(jid=target, cached=False)

				elif keyword == "!info":
					keyword_occurred = True
					queries['xep_0012'] = await self['xep_0012'].get_last_activity(jid=target)
					queries['xep_0072'] = await self['xep_0092'].get_version(jid=target)
					queries['xep_0157'] = await self['xep_0030'].get_info(jid=target, cached=False)

				elif keyword == "!user":
					keyword_occurred = True
					queries['xep_0133'] = self['xep_0133']
					queries['xep_0030'] = self['xep_0030']
					queries['response_func'] = self.send_response
					queries['original_msg'] = msg
					self.functions[keyword].process(queries=queries, target=target, opt_arg=opt_arg)
					continue
			except XMPPError as error:
				logging.info(misc.HandleError(error, keyword, target).report())
				data['reply'].append(misc.HandleError(error, keyword, target).report())
				continue

			data["reply"].append(self.functions[keyword].format(queries=queries, target=target, opt_arg=opt_arg))

		# remove None type from list and send all elements
		reply_data = list(filter(None, data["reply"]))

		# do not send default answer if no response and keyword occurred
		if not reply_data and keyword_occurred:
			return

		self.send_response(data['reply'], msg)

	# noinspection PyMethodMayBeStatic
	def build_queue(self, data, msg):
		# building the queue
		# double splitting to exclude whitespaces
		data['words'] = " ".join(msg['body'].split()).split(sep=" ")
		wordcount = len(data["words"])

		# check all words in side the message for possible hits
		for x in enumerate(data['words']):
			# check for valid keywords
			index = x[0]
			keyword = x[1]

			# match all words starting with ! and member of no_arg_keywords
			if keyword.startswith("!") and keyword in StaticAnswers().keys("no_arg_keywords"):
				data['queue'].append({keyword: [None, None]})

			# matching all words starting with ! and member of keywords
			elif keyword.startswith("!") and keyword in StaticAnswers().keys("keywords"):
				# init variables to circumvent IndexErrors
				target, opt_arg = None, None

				# compare to wordcount if assignment is possible
				if index + 1 < wordcount:
					target = data["words"][index + 1]

				if index + 2 < wordcount:
					if not data["words"][index + 2].startswith("!"):
						opt_arg = data["words"][index + 2]

				# only add job to queue if domain is valid
				if misc.validate(keyword, target):
					logging.debug("Item added to queue %s" % {str(keyword): [target, opt_arg]})
					data['queue'].append({str(keyword): [target, opt_arg]})

		# deduplicate queue elements
		data["queue"] = misc.deduplicate(data["queue"])

		return data


if __name__ == '__main__':
	# command line arguments.
	parser = ArgumentParser()
	parser.add_argument('-q', '--quiet', help='set logging to ERROR', action='store_const', dest='loglevel',
						const=logging.ERROR, default=logging.INFO)
	parser.add_argument('-d', '--debug', help='set logging to DEBUG', action='store_const', dest='loglevel',
						const=logging.DEBUG, default=logging.INFO)
	parser.add_argument('-D', '--dev', help='set logging to console', action='store_const', dest='logfile',
						const="", default='bot.log')
	args = parser.parse_args()

	# logging
	logging.basicConfig(filename=args.logfile, level=args.loglevel, format='%(levelname)s: %(asctime)s: %(message)s')
	logger = logging.getLogger(__name__)

	# configfile
	config = configparser.RawConfigParser()
	config.read('./bot.cfg')

	args.reply_private = ("yes" == config.get('General', 'reply_private'))
	args.admin_command_users = config.get('General', 'admin_command_users')
	args.jid = config.get('Account', 'jid')
	args.password = config.get('Account', 'password')
	args.room = config.get('MUC', 'rooms')
	args.nick = config.get('MUC', 'nick')

	# init the bot and register used slixmpp plugins
	xmpp = QueryBot(args.jid, args.password, args.room, args.nick, args.reply_private, args.admin_command_users)
	xmpp.register_plugin('xep_0012')  # Last Activity
	xmpp.register_plugin('xep_0030')  # Service Discovery
	xmpp.register_plugin('xep_0045')  # Multi-User Chat
	xmpp.register_plugin('xep_0060')  # PubSub
	xmpp.register_plugin('xep_0085')  # Chat State Notifications
	xmpp.register_plugin('xep_0092')  # Software Version
	xmpp.register_plugin('xep_0128')  # Service Discovery Extensions
	xmpp.register_plugin('xep_0199')  # XMPP Ping
	xmpp.register_plugin('xep_0133')  # Service Administration
	# xmpp.register_plugin('xep_0050')  # Ad-Hoc Commands

	# connect and start receiving stanzas
	xmpp.connect()
	xmpp.process()
