"""
Custom IRC bot for #!

Shane Engelman <contact@shane.gg>
pgp: 346001CA
"""

import logging
from collections import deque

import markovify
from lib.irc import IRC
from lib.logging_config import set_up_logging

logger = logging.getLogger("rant")
logger.setLevel(logging.DEBUG)

ANNOYING_USERS = ["singlerider"]
CONFIG = {
    "server": "irc.hashbang.sh",
    "port": 6697,
    "username": "testbot",
    "channels": ["#!test"],
}


class Bot(object):

    def __init__(self, config):
        self.irc = IRC(config)
        self.annoying_user_messages = {
            user: deque([], maxlen=10) for user in ANNOYING_USERS
        }
        set_up_logging()

    def get_logs_for_user(self, username):
        with open("{0}.log".format(username), "r") as f:
            logs = f.read()
        return logs

    def format_response(self, response):
        return "{0}?".format(response.rstrip("."))

    def send_message(self, channel, username, message):
        self.irc.send_message(channel, username, message)

    def is_annoying_user(self, username):
        if username in ANNOYING_USERS:
            return True
        return False

    def handle_annoying_user(self, channel, username, message):
        self.annoying_user_messages[username].add(message)
        text_model = markovify.NewlineText(
            "\n".join(self.annoying_user_messages[username])
        )
        formatted_response = text_model.make_sentence()
        if formatted_response:
            self.send_message(channel, username, formatted_response)

    def run(self):
        while True:
            try:
                data = self.irc.next_message()
                if not self.irc.check_for_message(data):
                    continue
                message_dict = self.irc.get_message(data)
                channel = message_dict["channel"]
                message = message_dict["message"]
                username = message_dict["username"]
                if self.is_annoying_user(username):
                    self.handle_annoying_user(channel, username, message)
            except Exception as error:
                error_message = "{0}\n=>{1}".format(
                    message_dict, error)
                with open("errors.txt", "a") as f:
                    f.write(error_message)


if __name__ == "__main__":
    Bot(CONFIG).run()
