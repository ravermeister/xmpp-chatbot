#!/usr/bin/env python3
# coding=utf-8

"""
	James the MagicXMPP Bot
	build with Slick XMPP Library
	Copyright (C) 2018 Nico Wellpott, 2022 Jonny Rimkus

	See the file LICENSE for copying permission.
"""
import configparser
import logging
import os
import ssl
import sys
from argparse import ArgumentParser
from typing import Optional, Dict, List

import slixmpp
import slixmpp_omemo
from omemo.exceptions import MissingBundleException
from slixmpp import JID
from slixmpp.exceptions import XMPPError, IqError, IqTimeout
from slixmpp_omemo import PluginCouldNotLoad, MissingOwnKey, UndecidedException, EncryptionPrepareException
from slixmpp_omemo import NoAvailableSession, UntrustedException

import common.misc as misc
from classes.chucknorris import ChuckNorrisRequest
from classes.info import ServerInfo
from classes.manpage import ManPageRequest
from classes.servercontact import ServerContact
from classes.uptime import LastActivity
from classes.users import UserInfo
from classes.version import Version
from classes.xep import XEPRequest
from common.strings import StaticAnswers


class QueryBot(slixmpp.ClientXMPP):

	def __init__(self, jid, password, room, nick,
			reply_private=False, admin_command_users="", max_list_entries=10, language="en"):
		slixmpp.ClientXMPP.__init__(self, jid, password)
		self.eme_ns_legacy = "eu.siacs.conversations.axolotl"
		self.eme_ns = "urn:xmpp:omemo:0"

		self.ssl_version = ssl.PROTOCOL_TLSv1_2
		self.room = room
		self.nick = nick
		self.use_message_ids = True
		self.reply_private = reply_private
		self.admin_users = admin_command_users.split(sep=",")
		self.max_list_entries = max_list_entries
		self.staticAnswers = StaticAnswers(language)

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

	async def send_response(self, reply_data, original_msg):

		nick_added = False
		# add pre predefined text to reply list
		if not reply_data:
			if self.nick in original_msg['body'] and not original_msg['type'] == "chat":
				reply_data.append(self.staticAnswers.gen_answer(original_msg['mucnick']))
				nick_added = True
			elif original_msg['type'] == "chat":
				reply_data.append(self.staticAnswers.gen_answer(original_msg['mucnick']))

		# remove None type from list and send all elements
		reply_data = list(filter(None, reply_data))

		if reply_data:
			# use bare jid as default receiver
			msg_to = original_msg['from'].bare
			# use original message type as default answer type
			msg_type = original_msg['type']

			# if msg type is groupchat and reply private is False prepend mucnick
			if original_msg["type"] == "groupchat" and self.reply_private is False and nick_added is False:
				reply_data[0] = "%s: %s" % (original_msg["mucnick"], reply_data[0])
			# if msg type is groupchat and reply private is True answer as with private message
			# do NOT use bare jid for receiver
			elif original_msg["type"] == "groupchat" and self.reply_private is True:
				msg_to = original_msg['from']
				msg_type = 'chat'
			# if msg type is chat (private) do NOT use bare jid for receiver
			elif original_msg['type'] == "chat":
				msg_to = original_msg['from']

			# send omemo encrypted message, if we received an encrypted message
			if self['xep_0384'].is_encrypted(original_msg):
				msg_to = original_msg['from']
				await self.send_encrypted_message(reply_data, msg_to, original_msg['type'], msg_type)
			else:
				self.send_message(msg_to, mbody="\n".join(reply_data), mtype=msg_type)

	async def send_encrypted_message(self, reply_data, msg_to, msg_src_type, msg_type):
		if msg_src_type == 'groupchat':
			room = msg_to.bare
			if msg_type == 'chat':
				user = msg_to.resource
				user_jid = JID(self['xep_0045'].get_jid_property(room, user, 'jid'))
				msg = self.make_message(mto=user_jid, mtype=msg_type)
				recipients = [user_jid]
			else:
				msg = self.make_message(mto=room, mtype=msg_type)
				recipients = [JID(self['xep_0045'].get_jid_property(room, user, 'jid'))
						for user in self['xep_0045'].get_roster(room)]  # if user not in self.jid
		else:
			msg = self.make_message(mto=msg_to, mtype=msg_type)
			recipients = [msg_to]

		# noinspection PyTypeChecker
		expect_problems = {}  # type: Optional[Dict[JID, List[int]]]
		retry = True
		while retry:
			try:
				encrypted_msg = await self['xep_0384'].encrypt_message(
					"\n".join(reply_data), recipients, expect_problems
				)
				msg.append(encrypted_msg)
				msg.send()
				retry = False
			except (UndecidedException, UntrustedException) as exn:
				# The library prevents us from sending a message to an
				# untrusted/undecided barejid, so we need to make a decision here.
				# This is where you prompt your user to ask what to do. In
				# this bot we will automatically trust undecided recipients.
				await self['xep_0384'].trust(exn.bare_jid, exn.device, exn.ik)
			# TODO: catch NoEligibleDevicesException
			except EncryptionPrepareException as exn:
				# This exception is being raised when the library has tried
				# all it could and doesn't know what to do anymore. It
				# contains a list of exceptions that the user must resolve, or
				# explicitely ignore via `expect_problems`.
				# TODO: We might need to bail out here if errors are the same?
				for error in exn.errors:
					if isinstance(error, MissingBundleException):
						# We choose to ignore MissingBundleException. It seems
						# to be somewhat accepted that it's better not to
						# encrypt for a device if it has problems and encrypt
						# for the rest, rather than error out. The "faulty"
						# device won't be able to decrypt and should display a
						# generic message. The receiving end-user at this
						# point can bring up the issue if it happens.
						logging.warning(
							"Could not find keys for device >%s< of recipient >%s<. Skipping"
							% (error.device, error.bare_jid)
						)
						jid = JID(error.bare_jid)
						device_list = expect_problems.setdefault(jid, [])
						device_list.append(error.device)
			except (IqError, IqTimeout) as exn:
				logging.error('An error occurred while fetching information on a recipient.\n%r' % exn)
				retry = False
			except Exception as exn:
				logging.error('An error occurred while attempting to encrypt.\n%r' % exn)
				retry = False

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

		# decrypt message if it was omemo encrypted
		if self['xep_0384'].is_encrypted(msg):
			msg_decrypted = await self.decrypt_message(msg)
			if msg_decrypted is None:
				return
			msg['body'] = msg_decrypted

		data = self.build_queue(data, msg['body'])
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
					queries['xep_0096'] = self['xep_0096']
					queries['response_func'] = self.send_response
					queries['original_msg'] = msg
					queries['max_list_entries'] = self.max_list_entries
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

		await self.send_response(data['reply'], msg)

	async def decrypt_message(self, msg):
		try:
			encrypted = msg['omemo_encrypted']
			if msg['type'] == 'groupchat':
				room = msg['from'].bare
				user = msg['from'].resource
				msg_from = JID(self['xep_0045'].get_jid_property(room, user, 'jid'))
				decrypted = await self['xep_0384'].decrypt_message(encrypted, msg_from, True)
			else:
				decrypted = await self['xep_0384'].decrypt_message(encrypted, msg['from'], True)
			# decrypt_message returns Optional[str]. It is possible to get
			# body-less OMEMO message (see KeyTransportMessages), currently
			# used for example to send heartbeats to other devices.
			if decrypted is not None:
				return decrypted.decode('utf8')
		except MissingOwnKey:
			# The message is missing our own key, it was not encrypted for
			# us, and we can't decrypt it.
			logging.warning("Message not encrypted for me.")
		except NoAvailableSession:
			# We received a message from that contained a session that we
			# don't know about (deleted session storage, etc.). We can't
			# decrypt the message, and it's going to be lost.
			# Here, as we need to initiate a new encrypted session, it is
			# best if we send an encrypted message directly. XXX: Is it
			# where we talk about self-healing messages?
			logging.warning('Error: Message uses an encrypted session I don\'t know about.')
			await self.send_encrypted_message(
				['Error: Message uses an encrypted session I don\'t know about.'],
				msg['from'],
				msg['from'],
				msg['type']
			)
		except EncryptionPrepareException:
			# Slixmpp tried its best, but there were errors it couldn't
			# resolve. At this point you should have seen other exceptions
			# and given a chance to resolve them already.
			logging.warning('Error: I was not able to decrypt the message.')

		except (Exception,) as exn:
			logging.warning('Error: Exception occurred while attempting decryption.\n%r' % exn)

		logging.warning("Error: Exception occurred while attempting decryption")

# noinspection PyMethodMayBeStatic
	def build_queue(self, data, msg_body):
		# building the queue
		# double splitting to exclude whitespaces
		data['words'] = " ".join(msg_body.split()).split(sep=" ")
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
	args.max_list_entries = int(config.get('General', 'max_list_entries'))
	args.data_dir = config.get('General', 'data_dir')
	args.locale = config.get('General', 'language')

	args.jid = config.get('Account', 'jid')

	args.password = config.get('Account', 'password')
	args.room = config.get('MUC', 'rooms')
	args.nick = config.get('MUC', 'nick')

	# init the bot and register used slixmpp plugins
	xmpp = QueryBot(args.jid, args.password, args.room, args.nick,
					args.reply_private, args.admin_command_users, args.max_list_entries, args.language)
	xmpp.register_plugin('xep_0012')  # Last Activity
	xmpp.register_plugin('xep_0030')  # Service Discovery
	xmpp.register_plugin('xep_0045')  # Multi-User Chat
	xmpp.register_plugin('xep_0060')  # PubSub
	xmpp.register_plugin('xep_0085')  # Chat State Notifications
	xmpp.register_plugin('xep_0092')  # Software Version
	xmpp.register_plugin('xep_0096')  # XEP-0096: SI File Transfer
	xmpp.register_plugin('xep_0128')  # Service Discovery Extensions
	xmpp.register_plugin('xep_0199')  # XMPP Ping
	xmpp.register_plugin('xep_0133')  # Service Administration
	xmpp.register_plugin('xep_0380')  # Explicit Message Encryption

	# Ensure OMEMO data dir is created
	os.makedirs(args.data_dir, exist_ok=True)
	try:
		xmpp.register_plugin(
			'xep_0384', {
				'data_dir': args.data_dir,
			}, module=slixmpp_omemo,
		)  # OMEMO Encryption
	except (PluginCouldNotLoad,):
		logger.exception('An error occurred when loading the omemo plugin.')
		sys.exit(1)

	# connect and start receiving stanzas
	xmpp.connect()
	xmpp.process()
