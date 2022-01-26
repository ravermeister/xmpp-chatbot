#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
	James the MagicXMPP Bot
	build with Slick XMPP Library
	Copyright (C) 2018 Nico Wellpott

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
from classes.manpage import ManPageRequest
from classes.chucknorris import ChuckNorrisRequest


class QueryBot(slixmpp.ClientXMPP):
	def __init__(self, jid, password, room, nick, reply_private=False):
		slixmpp.ClientXMPP.__init__(self, jid, password)
		self.ssl_version = ssl.PROTOCOL_TLSv1_2
		self.room = room
		self.nick = nick
		self.use_message_ids = True
		self.reply_private = reply_private
		logging.debug("reply private is configured to: %s" % self.reply_private)
		self.functions = {
			"!uptime": LastActivity(),
			"!contact": ServerContact(),
			"!version": Version(),
			"!info": ServerInfo(),
			"!xep": XEPRequest(),
			"!man": ManPageRequest(),
			"!chuck": ChuckNorrisRequest()
		}

		# session start event, starting point for the presence and roster requests
		self.add_event_handler('session_start', self.start)

		# register receive handler for both groupchat and normal message events
		self.add_event_handler('message', self.message)

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

		# queue
		for job in data['queue']:
			keys = list(job.keys())
			keyword = keys[0]
			target = job[keyword][0]
			opt_arg = job[keyword][1]
			queries = dict()

			if keyword == '!help':
				data['reply'].append(StaticAnswers().gen_help())
				continue

			try:
				if keyword == "!uptime":
					queries['xep_0012'] = await self['xep_0012'].get_last_activity(jid=target)

				elif keyword == "!version":
					queries['xep_0072'] = await self['xep_0092'].get_version(jid=target)

				elif keyword == "!contact":
					queries['xep_0157'] = await self['xep_0030'].get_info(jid=target, cached=False)

				elif keyword == "!info":
					queries['xep_0012'] = await self['xep_0012'].get_last_activity(jid=target)
					queries['xep_0072'] = await self['xep_0092'].get_version(jid=target)
					queries['xep_0157'] = await self['xep_0030'].get_info(jid=target, cached=False)

			except XMPPError as error:
				logging.info(misc.HandleError(error, keyword, target).report())
				data['reply'].append(misc.HandleError(error, keyword, target).report())
				continue
				
			data["reply"].append(self.functions[keyword].format(queries=queries, target=target, opt_arg=opt_arg))

		# remove None type from list and send all elements
		reply = list(filter(None, data['reply']))		
		
		nickAdded = False
		# add pre predefined text to reply list
		if not reply:
			if self.nick in msg['body'] and not msg['type'] == "chat":
				data['reply'].append(StaticAnswers(msg['mucnick']).gen_answer())
				nickAdded = True
			elif msg['type'] == "chat":
				data['reply'].append(StaticAnswers(msg['mucnick']).gen_answer())

		# remove None type from list and send all elements
		reply = list(filter(None, data['reply']))	
				
		if reply:
			# use bare jid as default receiver
			msgto=msg['from'].bare
			# use original message type as default answer type
			msgtype=msg['type']
			
			# if msg type is groupchat and reply private is False prepend mucnick
			if msg["type"] == "groupchat" and self.reply_private == False and nickAdded == False:
				reply[0] = "%s: " % msg["mucnick"] + reply[0]
			# if msg type is groupchat and reply private is True answer as with private message
			# do NOT use bare jid for receiver
			elif msg["type"] == "groupchat" and self.reply_private == True:
				msgto=msg['from']
				msgtype='chat'
			# if msg type is chat (private) do NOT use bare jid for receiver
			elif msg['type'] == "chat":
				msgto=msg['from']
			
			# reply = misc.deduplicate(reply)
			self.send_message(msgto, mbody="\n".join(reply), mtype=msgtype)


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
	logging.debug("reply private switch is: %s" % ("yes" == config.get('General', 'reply_private'))
	args.reply_private = ("yes" == config.get('General', 'reply_private'))
	args.jid = config.get('Account', 'jid')
	args.password = config.get('Account', 'password')
	args.room = config.get('MUC', 'rooms')
	args.nick = config.get('MUC', 'nick')

	# init the bot and register used slixmpp plugins
	xmpp = QueryBot(args.jid, args.password, args.room, args.nick)
	xmpp.register_plugin('xep_0012')  # Last Activity
	xmpp.register_plugin('xep_0030')  # Service Discovery
	xmpp.register_plugin('xep_0045')  # Multi-User Chat
	xmpp.register_plugin('xep_0060')  # PubSub
	xmpp.register_plugin('xep_0085')  # Chat State Notifications
	xmpp.register_plugin('xep_0092')  # Software Version
	xmpp.register_plugin('xep_0128')  # Service Discovery Extensions
	xmpp.register_plugin('xep_0199')  # XMPP Ping

	# connect and start receiving stanzas
	xmpp.connect()
	xmpp.process()
