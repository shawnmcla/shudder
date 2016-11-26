from lib.cfg import config

#Command !bot

def bot_info(userName, *args, **kwargs):
    """Whisper information about the bot to the user"""
    return ["/w {} {} is powered by the open-source project: PLACEHOLDERNAME!\
    To learn more about it or even contribute, visit the GitHub repository:\
     {}".format(userName, config['botName'], config['sourceRepository'])]