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
        self.xep_0050 = None
        self.target, self.opt_arg = None, None

    # noinspection PyMethodMayBeStatic
    def process(self, queries, target, opt_arg):
        self.xep_0050 = queries['xep_0133'].xmpp['xep_0050']
        self.response_func = queries['response_func']
        self.original_msg = queries['original_msg']

        register_session = {
            'next': self.registered_users_start,
            'error': self.registered_users_error
        }
        queries['xep_0133'].get_registered_users_num(jid=target, session=register_session)
        # return "Userinfo: queries=%s, target=%s, opt_args=%s" % (queries, target, opt_arg)

    def registered_users_start(self, iq, session):
        """
        Process the initial command result.

        Arguments:
            iq      -- The iq stanza containing the command result.
            session -- A dictionary of data relevant to the command
                       session. Additional, custom data may be saved
                       here to persist across handler callbacks.
        """
        logging.debug("Registered Users Command completed")
        self.xep_0050.complete_command(session)

    # noinspection PyMethodMayBeStatic
    def registered_users_error(self, iq, session):
        """
        Process an error that occurs during command execution.

        Arguments:
            iq      -- The iq stanza containing the error.
            session -- A dictionary of data relevant to the command
                       session. Additional, custom data may be saved
                       here to persist across handler callbacks.
        """
        logging.error("%s - %s" % (iq['error']['condition'], iq['error']['text']))
        response = list()
        response.append("%s %s" % (iq['error']['condition'], iq['error']['text']))

        # Terminate the command's execution and clear its session.
        # The session will automatically be cleared if no error
        # handler is provided.
        self.xep_0050.terminate_command(session)
        self.response_func(response, self.original_msg)
