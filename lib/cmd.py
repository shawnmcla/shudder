from lib.cfg import config
from lib.twitch import is_mod
from lib.botcommands import commands

"""Module which processes messages and parses commands."""

def _hasCorrectArgs(command, argc):
    """Verify if the number of arguments is valid.

    command is an entry of the commands dictionary.
    """
    if argc == command['argc'] or command['argc'] == 0 or command['argc'] == -1 and argc > 0:
        return True
    return False

def _hasCorrectPrivilege(command, userName):
    """Verify if the user has the appropriate privilege to call the command.
    
    command is an entry of the commands dictionary.
    """
    level = command['level']
    if level == 0:
        return True
    elif level == 2:
        return userName == config['ircChannel']
    else:
        return is_mod(userName)

def process_message(userName, message):
    """Process a message, checking for command calls."""
    commandName = message.split()[0]
    if commandName in commands:
        args = message.split()[1:]
        argc = len(args)
        cmd = commands[commandName]
        if _hasCorrectPrivilege(cmd, userName):
            if _hasCorrectArgs(cmd, argc):
                return cmd['caller'](userName, *args, commandName = commandName)
            else:
                return ["Invalid arguments. Usage: {}".format(cmd['usage'])]
        return None
