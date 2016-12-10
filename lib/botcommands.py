import lib.database as db
from lib.cfg import config
from lib.commands.flipcoin import flip_coin
from lib.commands.raffle import Raffle
from lib.commands.bot import bot_info
from lib.currency import get_balance, pay

raffle = Raffle()
fileName = config['dynamicCommandsFile']

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

def dynamic_caller(userName, *args, **kwargs):
    """Handle a dynamic command.
    
    Called whenever a dynamic command is used
    """
    if kwargs["commandName"]:
        print(commands[kwargs["commandName"]]['output'])
        return [commands[kwargs["commandName"]]['output']]
    return None

def _add_dynamic_command(commandName, output):
    """Add a dynamic command to the command dictionary."""
    if commandName in commands:
        return False
    commands[commandName] = {
        'argc': 0,
        'level': 0,
        'desc': 'Dynamic command',
        'dynamic': True,
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
        return ["Please specify the command output. Use !addcommand to see usage information."]
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
        commands[commandName]['output'] = output
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
        'argc' : 0,
        'level' : 0,
        'desc' : 'Join the raffle, if there is one active.',
        'caller' : raffle.enter_user
    },
    '!makeraffle' : {
        'argc' : -1,
        'level' : 1,
        'desc' : 'Start a raffle for the viewers.',
        'usage' : '!makeraffle <raffle prize>',
        'caller' : raffle.start_raffle
    },
    '!pickwinner' : {
        'argc' : 0,
        'level' : 1,
        'desc' : 'End the raffle, if one is active and randomly choose a winner',
        'caller' : raffle.choose_winner
    },
    '!cancelraffle' : {
        'argc' : 0,
        'level' : 1,
        'desc' : 'Cancel the raffle, if one is active.',
        'caller' : raffle.cancel_raffle
    },
    '!addcommand' :{
        'argc' : -1,
        'level' : 1,
        'desc' : 'Add a new dynamic command.',
        'usage' : '!addcommand <command name> <command output>',
        'caller' : add_dynamic_command
    },
    '!deletecommand' :{
        'argc' : 1,
        'level' : 1,
        'desc' : 'Delete an existing dynamic command.',
        'usage' : '!deletecommand <command name>',
        'caller' : delete_dynamic_command
    },
    '!updatecommand' :{
        'argc' : -1,
        'level' : 1,
        'desc' : 'Modify an existing dynamic command\'s output.',
        'usage' : '!updatecommand <command name> <new command output>',
        'caller' : update_dynamic_command
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
        'desc': 'Give currency units to another user.',
        'usage': '!pay <recipient> <amount>',
        'caller': pay
    }
}

_load_dynamic_commands()
