import sys
import threading
from lib.cfg import read_config_from_file, config
from lib.currency import initialize_currency_system
from lib.timedevents import initialize_timed_event_manager
from lib.cli import interpret_command

print("Reading configuration file..")
if not read_config_from_file():
    print("Error parsing configuration file.")
    sys.exit(0)
print("Config loaded!")
if len(sys.argv)>1 and sys.argv[1].lower() == "-d":
    print("DEBUG MODE")
    config['DEBUG'] = True

import re
from lib.irc import irc
from lib.cmd import process_message
from lib.database import initialize_database
initialize_database()
initialize_timed_event_manager()
initialize_currency_system()

def _consoleLoop():
    print("Starting console thread")
    while True:
        _input = ""
        while not _input:
            _input = input(">")
        interpret_command(_input)

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
            irc.queue_out_messages(result)
        irc.queue_out_messages(*result)

irc.start_bot(handle_message)

consoleThread = threading.Thread(target=_consoleLoop)
consoleThread.start()
