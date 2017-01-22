"""Module which stores and defines bot chat commands."""

import lib.database as db
from lib.commands.flipcoin import flip_coin
from lib.commands.raffle import raffle
from lib.commands.bot import bot_info
from lib.currency import get_balance, pay, give_tokens

_FLAGALIAS = "-a="

"""List of commands.

Notes:
argc: argument count. -1 means no limit.
level: privilege level required to use command.
    0 -> Any User
    1 -> Mods+
    2 -> Channel owner

Commands with no arguments have no usage info.

Dynamic commands are commands created dynamically by users and do not call any custom functions.
"""

commands = {}


def has_correct_args(command, argc):
    """Verify if the number of arguments is valid.

    command is an entry of the commands dictionary.
    """
    if argc == command['argc'] or command['argc'] == 0 or command['argc'] == -1 and argc > 0:
        return True
    return False

def _subcommand(userName, subs, *args, **kwargs):
    """Handle a subcommand call."""
    subName = args[0]
    if not subName in subs.keys():
        return False
    sub = subs[subName]
    if not has_correct_args(sub, len(args[1:])):
        return [subs[subName]['usage']]
    return subs[subName]['caller'](userName, *(args[1:]), **kwargs)

def _command_subcommands(userName, *args, **kwargs):
    """Pass subcommands for the "!command" command."""
    subs = commands['!command']['subcommands']
    return _subcommand(userName, subs, *args, **kwargs)
def _raffle_subcommands(userName, *args, **kwargs):
    """Pass subcommands for the "!raffle" command."""
    subs = commands['!raffle']['subcommands']
    return _subcommand(userName, subs, *args, **kwargs)

def _is_dynamic(command):
    return 'dynamic' in command.keys() and command['dynamic']
def _is_alias(command):
    return 'isAlias' in command.keys() and command['isAlias']

def dynamic_caller(userName, *args, **kwargs):
    """Handle a dynamic command.
    
    Called whenever a dynamic command is used
    """
    if kwargs['commandName']:
        command = commands[kwargs['commandName']]
        if command['isAlias']:
            while _is_alias(command):
                if command['alias'] in commands.keys():
                    alias = commands[command['alias']]
                    if _is_alias(alias):
                        command = alias
                        continue
                    if _is_dynamic(alias):
                        return [alias['output']]
                return ["Error: Alias commands may only refer to a dynamic command."]
        return [command['output']]
    return None

def _add_dynamic_command(commandName, output):
    """Parse and add a dynamic command to the command dictionary."""
    splits = output.split()
    isAlias = False
    alias = None
    lookingForFlags = True

    if commandName in commands:
        return False

    for split in splits:
        if split[0] != "-":
            break
        if split.startswith(_FLAGALIAS):
            if len(split.split('=')) == 2:
                isAlias = True
                alias = split.split('=')[1]
    commands[commandName] = {
        'argc': 0,
        'level': 0,
        'desc': 'Dynamic command',
        'dynamic': True,
        'isAlias': isAlias,
        'alias': alias,
        'caller': dynamic_caller,
        'output': output
    }

def add_dynamic_command(userName, *args, **kwargs):
    """Write the dynamic command to the database.

    Also calls _add_dynamic_command to add it to the dictionary in memory.
    """
    if not args:
        return ["Error. No arguments."]
    commandName = args[0]
    if commandName in commands:
        return ["Cannot overwrite command {}".format(commandName)]
    if len(args[1:]) == 0:
        return ["Please specify the command output. Use !command add to see usage information."]
    output = ' '.join(args[1:])
    if db.save_dynamic_command(commandName, output):
        _add_dynamic_command(commandName, output)
        return ["Added new command: {}".format(commandName)]
    else:
        return ["An error occured while trying to insert the command into the database."]

def delete_dynamic_command(userName, *args, **kwargs):
    """Remove the specified dynamic command from memory and the database."""
    if not args:
        return ["Error. No arguments."]
    commandName = args[0]
    if commandName not in commands:
        return ["Command does not exist!"]
    if not commands[commandName]['dynamic']:
        return ["Cannot delete built-in commands!"]
    if db.delete_dynamic_command(commandName):
        del commands[commandName]
        return ["Deleted command: {}".format(commandName)]
    else:
        return ["An error occured while trying to delete the command from the database."]

def update_dynamic_command(userName, *args, **kwargs):
    """Modify the specified dynamic command's output in memory and in the database."""
    if not args:
        return ["Error. No arguments."]
    commandName = args[0]
    if commandName not in commands:
        return ["Command does not exist!"]
    if not commands[commandName]['dynamic']:
        return ["Cannot modify built-in commands!"]
    if len(args[1:]) == 0:
        return ["Please specify the new command output. Use !updatecommand to see usage information."]
    output = ' '.join(args[1:])
    if db.update_dynamic_command(commandName, output):
        del commands[commandName]
        _add_dynamic_command(commandName, output)
        return ["Updated command: {}".format(commandName)]
    else:
        return ["An error occured while trying to update the command in the database."]

def _load_dynamic_commands():
    """Fetch commands from the database and load them in memory."""
    coms = db.get_dynamic_commands()
    for command in coms:
        _add_dynamic_command(command[0], command[1])
  
commands = { #Internal pre-loaded commands
    '!bot' : {
        'argc' : 0,
        'level' : 0,
        'desc' : 'Whispers information about the bot to the user.',
        'caller' : bot_info
    },
    '!flipcoin' : {
        'argc' : 0,
        'level' : 0,
        'desc' : 'Settle a bet and flip a coin! Returns heads or tails, randomly.',
        'caller' : flip_coin
    },
    '!raffle' : {
        'argc': -1,
        'level' : 0,
        'desc' : 'Super-command to various raffle related subcommands.',
        'usage': '!raffle <enter|create|draw|cancel> [arguments]',
        'caller': _raffle_subcommands,
        'subcommands': {
            'enter' : {
            'argc' : 0,
            'level' : 0,
            'desc' : 'Join the raffle, if there is one active.',
            'caller' : raffle.enter_user
            },
            'create': {
            'argc' : -1,
            'level' : 1,
            'desc' : 'Start a raffle for the viewers.',
            'usage' : '!raffle create <fee> <raffle prize>',
            'caller' : raffle.start_raffle
            },
            'draw': {
            'argc' : 0,
            'level' : 1,
            'desc' : 'End the raffle, if one is active and randomly choose a winner',
            'caller' : raffle.choose_winner
            },
            'cancel': {
            'argc' : 0,
            'level' : 1,
            'desc' : 'Cancel the raffle, if one is active.',
            'caller' : raffle.cancel_raffle
            }
        }
    },
    '!command' :{
        'argc' : -1,
        'level' : 1,
        'desc' : 'Super-command to various command related subcommands. A mouthful.',
        'usage' : '!command <add|delete|update> [arguments]',
        'caller' : _command_subcommands,
        'subcommands': {
            'add' : {
            'argc' : -1,
            'level' : 1,
            'desc' : 'Add a new dynamic command.',
            'usage' : '!command add <command name> <command output>',
            'caller' : add_dynamic_command
            },
            'delete': {
            'argc' : 1,
            'level' : 1,
            'desc' : 'Delete an existing dynamic command.',
            'usage' : '!command delete <command name>',
            'caller' : delete_dynamic_command
            },
            'update': {
            'argc' : -1,
            'level' : 1,
            'desc' : 'Modify an existing dynamic command\'s output.',
            'usage' : '!command update <command name> <new command output>',
            'caller' : update_dynamic_command
            }

        }
    },
    '!balance':{
        'argc': 0,
        'level': 0,
        'desc': 'Fetch a user\'s currency balance.',
        'caller': get_balance
    },
    '!pay':{
        'argc': 2,
        'level': 0,
        'desc': 'Transfer currency units to another user.',
        'usage': '!pay <recipient> <amount>',
        'caller': pay
    },
    '!give':{
        'argc': 2,
        'level': 1,
        'desc': 'Give currency units to another user.',
        'usage': '!give <recipient> <amount>',
        'caller': give_tokens
    }
}

_load_dynamic_commands()
