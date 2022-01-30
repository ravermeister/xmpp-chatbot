# coding=utf-8
import logging


class UserInfo:
    """
    queries, user info on the Server
    such as online users and registered users
    """

    def __init__(self):
        # init all necessary variables
        self.response_func = None
        self.original_msg = None
        self.response_data = list()
        self.xep_0050 = None
        self.target, self.opt_arg = None, None

    # noinspection PyMethodMayBeStatic
    def process(self, queries, target, opt_arg):
        self.xep_0050 = queries['xep_0133'].xmpp['xep_0050']
        self.response_func = queries['response_func']
        self.original_msg = queries['original_msg']
        self.response_data = list()

        register_session = {
            'next': self.registered_users,
            'error': self.users_error
        }
        queries['xep_0133'].get_registered_users_num(jid=target, session=register_session)

        online_session = {
            'next': self.online_users,
            'error': self.users_error
        }
        queries['xep_0133'].get_online_users_num(jid=target, session=online_session)

    def online_users(self, iq, session):
        """
        Process the initial command result.

        Arguments:
            iq      -- The iq stanza containing the command result.
            session -- A dictionary of data relevant to the command
                       session. Additional, custom data may be saved
                       here to persist across handler callbacks.
        """

        send_response = True
        if not self.response_data:
            send_response = False
            self.response_data.append(" ")

        # noinspection SpellCheckingInspection
        online_users_elems = iq.xml.findall(".//{jabber:x:data}field[@var='onlineusersnum']/{jabber:x:data}value")
        if online_users_elems:
            online_users_num = online_users_elems[0].text
            self.response_data.append("Online Users: %s" % online_users_num)
        else:
            logging.warning("received invalid data in response for xep_0133 - get-online-users-num")
            self.response_data.append("received invalid data in response")

        self.xep_0050.complete_command(session)
        if send_response:
            self.response_func(self.response_data, self.original_msg)

    def registered_users(self, iq, session):
        """
        Process the initial command result.

        Arguments:
            iq      -- The iq stanza containing the command result.
            session -- A dictionary of data relevant to the command
                       session. Additional, custom data may be saved
                       here to persist across handler callbacks.
        """

        send_response = True
        if not self.response_data:
            send_response = False
            self.response_data.append(" ")

        # noinspection SpellCheckingInspection
        registered_users_elems = iq.xml.findall(".//{jabber:x:data}field[@var='registeredusersnum']/{jabber:x:data}value")
        if registered_users_elems:
            registered_users_num = registered_users_elems[0].text
            self.response_data.append("Total Registered Users: %s" % registered_users_num)
        else:
            logging.warning("received invalid data in response for xep_0133 - get-registered-users-num")
            self.response_data.append("received invalid data in response")

        self.xep_0050.complete_command(session)
        if send_response:
            self.response_func(self.response_data, self.original_msg)

    # noinspection PyMethodMayBeStatic
    def users_error(self, iq, session):
        """
        Process an error that occurs during command execution.

        Arguments:
            iq      -- The iq stanza containing the error.
            session -- A dictionary of data relevant to the command
                       session. Additional, custom data may be saved
                       here to persist across handler callbacks.
        """
        error_text = "%s: %s" % (iq['error']['condition'], iq['error']['text'])
        logging.error("%s - %s" % (iq['error']['condition'], iq['error']['text']))

        # Terminate the command's execution and clear its session.
        # The session will automatically be cleared if no error
        # handler is provided.
        self.xep_0050.terminate_command(session)
        if error_text not in self.response_data:
            self.response_data.append(error_text)
            self.response_func(self.response_data, self.original_msg)
