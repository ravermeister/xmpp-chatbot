# coding=utf-8
class UserInfo:
    """
    queries, user info on the Server
    such as online users and registered users
    """

    def __init__(self):
        # init all necessary variables
        self.target, self.opt_arg = None, None

    # noinspection PyMethodMayBeStatic
    def process(self, queries, target, opt_arg):
        return "Userinfo: queries=%s, target=%s, opt_args=%s" % (queries, target, opt_arg)

    def format(self, queries, target, opt_arg):
        text = self.process(queries, target, opt_arg)
        return text
