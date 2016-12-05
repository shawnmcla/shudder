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
  