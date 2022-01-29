# coding=utf-8
class UserInfo:
    """
    queries, user info on the Server
    such as onine users and registered users
    """

    def __init__(self):
        # init all necessary variables
        self.possible_vars = [
            'get-registered-users-num',
            'get-disabled-users-num', 'get-online-users-num',
            'get-active-users-num',
            'get-registered-users-list',
            'get-disabled-users-list',
            'get-online-users-list',
            'get-online-users',
            'get-active-users',
        ]

        self.target, self.opt_arg = None, None

    def process(self):
        return ""

    def format(self, queries, target, opt_arg):
        return "userinfo"
