# coding=utf-8

import socket


class PasteBin:
    """
    > uses the configured https://termbin.com service
    > to post long Text and returned the URL to share the Text
    """

    def __init__(self, raw_msg):
        # init all necessary variables
        self.raw_msg = raw_msg
        self.paste_url = "termbin.com"
        self.paste_port = 9999
        self.max_response_len = 256

    def format(self, raw_msg):
        self.raw_msg = raw_msg

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.paste_url, self.paste_port))
        sock.send(bytearray(self.raw_msg, 'UTF-8'))
        response = sock.recv(self.max_response_len)
        sock.close()
        url = str(response, 'UTF-8').replace('\00', '')

        return url
