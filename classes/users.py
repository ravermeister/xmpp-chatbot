# coding=utf-8
import asyncio
import logging

from common.strings import StaticAnswers


class UserInfo:
    """
    queries, user info on the Server
    such as online users and registered users
    """

    def __init__(self, static_answers: StaticAnswers):
        # init all necessary variables
        self.static_answers = static_answers
        self.response_func = None
        self.response_file_func = None
        self.original_msg = None
        self.response_data = list()
        self.response_file_lists = list()
        self.xep_0030 = None
        self.xep_0050 = None
        self.xep_0096 = None
        self.max_list_entries = 10
        self.fallback_session = {}
        self.target, self.opt_arg = None, None

    # noinspection PyUnusedLocal
    def process(self, queries, target, opt_arg):
        self.xep_0050 = queries['xep_0133'].xmpp['xep_0050']
        self.xep_0030 = queries['xep_0030']
        self.xep_0096 = queries['xep_0096']
        self.response_func = queries['response_func']
        self.original_msg = queries['original_msg']
        self.response_data = list()
        self.max_list_entries = queries['max_list_entries']

        queries['xep_0133'].get_registered_users_num(jid=target, session={
            'next': self.command_start,
            'error': self.command_error,
            'command': 'get-registered-users-num',
            'send_response': False
        })

        queries['xep_0133'].get_online_users_num(jid=target, session={
            'next': self.command_start,
            'error': self.command_error,
            'command': 'get-online-users-num',
            'send_response': False
        })

        # doesn't work with my ejabberd 21.12
        # 'get-online-users-list', 'get-online-users', 'get-active-users', 'get-registered-users-list'
        queries['xep_0133'].get_online_users(jid=target, session={
            'next': self.command_start,
            'error': self.command_error,
            'target': target,
            'command': 'get-online-users',
            'send_response': True
        })

    def command_start(self, iq, session):
        """
        Process the initial command result.

        Arguments:
            iq      -- The iq stanza containing the command result.
            session -- A dictionary of data relevant to the command
                       session. Additional, custom data may be saved
                       here to persist across handler callbacks.
        """

        if not self.response_data:
            self.response_data.append(" ")

        logging.debug("Command handler for: '%s'" % session['command'])

        if session['command'] == 'get-registered-users-num':
            # noinspection SpellCheckingInspection
            registered_users_elems = iq.xml.findall(".//{jabber:x:data}field[@var='registeredusersnum']/{jabber:x:data}value")
            if registered_users_elems:
                registered_users_num = registered_users_elems[0].text
                self.response_data.append("Registered Users: %s" % registered_users_num)
            else:
                logging.warning("received invalid data in response for xep_0133 - get-registered-users-num")
                self.response_data.append("received invalid data in response")
        elif session['command'] == 'get-online-users-num':
            # noinspection SpellCheckingInspection
            online_users_elems = iq.xml.findall(".//{jabber:x:data}field[@var='onlineusersnum']/{jabber:x:data}value")
            if online_users_elems:
                online_users_num = online_users_elems[0].text
                self.response_data.append("Online Users: %s" % online_users_num)
            else:
                logging.warning("received invalid data in response for xep_0133 - get-online-users-num")
                self.response_data.append("received invalid data in response")
        elif session['command'] == 'get-online-users':
            logging.debug("online user list response: %s" % iq.xml)

        if session['send_response']:
            self.response_func(self.response_data, self.original_msg)

        # Other options include using:
        # continue_command() -- Continue to the next step in the workflow
        # cancel_command()   -- Stop command execution.
        self.xep_0050.complete_command(session)

    # noinspection PyMethodMayBeStatic
    def command_error(self, iq, session):
        """
        Process an error that occurs during command execution.

        Arguments:
            iq      -- The iq stanza containing the error.
            session -- A dictionary of data relevant to the command
                       session. Additional, custom data may be saved
                       here to persist across handler callbacks.
        """
        error_text = "%s: %s %s" % (session['command'], iq['error']['condition'], iq['error']['text'])
        logging.error("%s" % error_text)

        if not self.response_data:
            self.response_data.append(" ")

        if session['command'] == 'get-online-users':
            # fallback for get-online-users in ejabberd
            logging.debug("fallback method for ejabberd for get online user list")
            self.fallback_session = {
                'command': 'get-online-users',
                'send_response': session['send_response']
            }
            fallback_task = asyncio.create_task(
                self.xep_0030.get_items(
                    jid=session['target'],
                    node='online users',
                    callback=self.fallback_onlineusers_ejabberd_callback_handler
                )
            )

            def ignore_coroutine_error(task: asyncio.Task) -> None:
                # noinspection PyBroadException
                try:
                    task.result()
                except Exception:
                    pass
            fallback_task.add_done_callback(ignore_coroutine_error)

            session['send_response'] = False
        else:
            self.response_data.append("%s" % error_text)

        if session['send_response']:
            self.response_func(self.response_data, self.original_msg)

        # Terminate the command's execution and clear its session.
        # The session will automatically be cleared if no error
        # handler is provided.
        self.xep_0050.terminate_command(session)

    def fallback_onlineusers_ejabberd_callback_handler(self, iq):

        session = self.fallback_session
        self.fallback_session = {}
        # error check
        response_type = iq.xml.get('type')

        if response_type == 'result':
            # noinspection HttpUrlsUsage
            response = iq.xml.findall(".//{http://jabber.org/protocol/disco#items}item")
            user_list = list()
            for user in response:
                user_jid = user.get("jid")
                user_split = user_jid.split("/")
                user_name = user_split[0]
                user_app = user_split[1].split(".")[0]
                user_entry = "%s using %s" % (user_name, user_app)
                user_list.append(user_entry)
            send_list = list(user_list)
            if len(send_list) > self.max_list_entries:
                del send_list[self.max_list_entries:]
                file = "\n".join(user_list)
                logging.error("File Content:\n%s" % file)
            for user in send_list:
                self.response_data.append(user)
        else:
            response = iq.xml.findall(".//{jabber:client}error")
            for error in response:
                if len(error) > 0:
                    error_type = error[0].tag.partition('}')[2]
                    error_text = error.find(".//{urn:ietf:params:xml:ns:xmpp-stanzas}text").text
                    self.response_data.append("%s: %s %s" % (session['command'], error_type, error_text))

        if session['send_response']:
            self.response_func(self.response_data, self.original_msg)
            # self.response_file_func(self.response_file_lists, self.original_msg)
