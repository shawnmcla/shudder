import sys
from lib.cfg import read_config_from_file

print("Reading configuration file..")
if not read_config_from_file():
    print("Error parsing configuration file.")
    sys.exit(0)
print("Config loaded!")

import re
import threading
import lib.irc as irc
from lib.cmd import process_message

def _consoleLoop():
    print("Starting console thread")
    while True:
        _input = ""
        while not _input:
            _input = input()
        #TODO: Interpret command heh

def handle_message(message):
    """Parse and split IRC message and send it to the command processor

    Sends the username of the author and their message to the command processor
    If the message was a valid command the command processor returns some output,
    queue it for sending.
    """
    chatMessageRegex = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    userName = re.search(r"\w+", message).group(0)
    msg = chatMessageRegex.sub("", message)
    result = process_message(userName, msg)
    if result:
        if type(result) is str:
            _irc.queue_out_messages(result)
        _irc.queue_out_messages(*result)

_irc = irc.Irc(handle_message)
_irc.start_bot()
consoleThread = threading.Thread(target=_consoleLoop)
consoleThread.start()
