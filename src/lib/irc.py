# encoding=utf8
import logging
import re
import socket
import ssl
import sys
import time

logger = logging.getLogger("rant")
THRESHOLD = 5 * 60  # five minutes, make this whatever you want


class IRC:

    def __init__(self, config):
        self.config = config
        self.buffer = ""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1)
        self.sock.settimeout(10)
        self.connect()

    def next_message(self):
        while "\r\n" not in self.buffer:
            read = self.sock.recv(2040)
            if not read:
                print("Connection was lost")
                self.connect()  # Reconnect.
            else:
                self.buffer += read.decode()
        line, self.buffer = self.buffer.split("\r\n", 1)
        logger.info(line)
        if line.startswith("PING"):
            self.sock.send((line.replace("PING", "PONG") + "\r\n").encode())
        return line

    def check_for_message(self, data):
        if re.match(r"^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+\.irc\.hashbang\.sh PRIVMSG #[a-zA-Z0-9_]+ :.+$", data):  # noqa
            return True

    def check_for_connected(self, data):
        if re.match(r"^:.+ 001 .+ :connected to hashbang$", data):
            return True

    def check_for_ping(self, data):
        last_ping = time.time()
        if data.find("PING") != -1:
            self.sock.send("PONG " + data.split()[1] + "\r\n")
            last_ping = time.time()
        if (time.time() - last_ping) > THRESHOLD:
            sys.exit()

    def get_message(self, data):
        return re.match(
            r"^:(?P<username>.*?)!.*?PRIVMSG (?P<channel>.*?) :(?P<message>.*)", data  # noqa
        ).groupdict()

    def check_login_status(self, data):
        if re.match(r"^:irc\.hashbang\.sh NOTICE \* :Login unsuccessful\r\n$", data):  # noqa
            return False
        else:
            return True

    def send_message(self, channel, username, message):
        self.sock.send("PRIVMSG {0} :{1}{2}\r\n".format(
            channel, username, message).encode())

    def connect(self):
        try:
            logger.info(
                "Connecting to {0}:{1}".format(
                    self.config["server"], self.config["port"]
                )
            )
            self.sock.connect((self.config["server"], self.config["port"]))
        except Exception as error:
            sys.exit(
                "Cannot connect to server ({0}:{1}). \"{2}\"".format(
                    self.config["server"], self.config["port"], error
                )
            )

        self.sock.settimeout(None)

        self.sock.send("NICK {0}\r\n".format(self.config["username"]).encode())
        self.sock.send("USER {0} {0} {0} :{0}\r\n".format(
            self.config["username"]).encode())
        # sock.send("PASS {0}\r\n".format(self.config["password"]).encode())

        login_message = self.next_message()

        if "unsuccessful" in login_message:
            sys.exit(
                "Failed to login. Check your password "
                "and username in src/config/config.py"
            )

        # Wait until we're ready before starting stuff.
        while "376" not in self.next_message():
            pass

        self.join_channels(self.channels_to_string(self.config["channels"]))

    def channels_to_string(self, channel_list):
        return ",".join(channel_list)

    def join_channels(self, channels):
        logger.info("Joining channels {0}.".format(channels))
        self.sock.send("JOIN {0}\r\n".format(channels).encode())
        logger.info("Joined channels.")

    def leave_channels(self, channels):
        logger.info("Leaving channels {0},".format(channels))
        self.sock.send("PART {0}\r\n".format(channels).encode())
        logger.info("Left channels.")
