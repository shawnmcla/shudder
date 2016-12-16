"""Holds various configuration variables."""

_CFG_FILE_NAME = "shudder.cfg"

config = {
    'host' : 'irc.chat.twitch.tv',
    'port' : 6667,
    'username' : None,
    'password' : None,
    'apiKey' :  None,
    'channelName' : None,
    'apiUrl' : 'https://api.twitch.tv/kraken/',
    'messageRate' : 20/30,
    'botName' : None,
    'messageOnConnect' : False,
    'connectMessage' : 'MrDestructoid Bot Online MrDestructoid',
    'modCacheTimeout' : 30,
    'sourceRepository' : 'https://github.com/shawnmcla/shudder',
    'DEBUG' : False
}

currencyConfig = {
    'useCurrency': True,
    'currencyName': 'Leks',
    'giveTokensPerViewTime': True,
    'tokensPerMinute': 1,
    'giveTokensPerMessage': True,
    'tokensPerMessage': 1,
    'giveFollowBonus': True,
    'followBonus': 100
}

def read_config_from_file():
    """Read configuration values from config file"""
    with open(_CFG_FILE_NAME, "r") as cfile:
        lines = cfile.readlines(5000)
        for line in lines:
            line = line.strip()
            if line and line[0] != "#":
                split = line.split("=")
                if len(split) != 2:
                    print("Error in config line: {}".format(line))
                    return False
                name = split[0].strip()
                value = split[1].strip()
                if name not in config:
                    print("Error in config line: {}\nInvalid config key '{}'".format(line, name))
                    return False
                config[name] = value
    return True
