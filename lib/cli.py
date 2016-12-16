from lib.irc import irc

def bot_send_message(args):
    message = ' '.join(args)
    irc.queue_out_messages(message)

_commands = {
    'say' : bot_send_message
}
def interpret_command(msg):
    """Takes a line of input from the console and handles the command."""
    msg = msg.split()
    command = msg[0].lower()
    args = msg[1:]
    if command in _commands.keys():
        _commands[command](args)
    else:
        print("Invalid command :(")



