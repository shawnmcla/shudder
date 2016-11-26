import os.path
from lib.cfg import config
from lib.commands.flipcoin import flip_coin
from lib.commands.raffle import Raffle
from lib.commands.bot import bot_info


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
        'caller': dynamic_caller,
        'output': output
    }

def add_dynamic_command(userName, *args, **kwargs):
    """Write the dynamic command to the disk.

    Also calls _add_dynamic_command to add it to the dictionary
    """
    if not args:
        return ["wtf fam"]
    commandName = args[0]
    if commandName in commands:
        return ["Cannot overwrite command {}".format(commandName)]
    if len(args[1:]) == 0:
        return ["Please specify the command output. Use !addcommand to see usage information."]
    output = ' '.join(args[1:])
    with open(fileName, 'a') as file:
        file.write("{} {}\n".format(commandName, output))
    _add_dynamic_command(commandName, output)
    return ["Added new command: {}".format(commandName)]

def _load_dynamic_commands():
    """Open the dynamic commands file and load them in memory."""
    f = open(fileName, 'a')
    f.close()
    with open(fileName, 'r') as file:
        coms = file.readlines()
        for command in coms:
            _add_dynamic_command(command.split()[0], ' '.join(command.split()[1:]))

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
    }
    
}

_load_dynamic_commands()
