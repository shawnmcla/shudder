"""Defines methods used for the bot's currency system."""

import lib.database as db
from lib.cfg import currencyConfig
from lib.twitch import get_viewers, user_online
from lib.timedevents import register_event

_users = dict()
_USECURRENCY = currencyConfig['useCurrency']
_CURRENCYNAME = currencyConfig['currencyName']
_GIVEPERVIEWTIME = currencyConfig['giveTokensPerViewTime']
_TOKENSPERMINUTE = currencyConfig['tokensPerMinute']
_GIVEPERMESSAGE = currencyConfig['giveTokensPerMessage']
_TOKENSPERMESSAGE = currencyConfig['tokensPerMessage']
_GIVEFOLLOWBONUS = currencyConfig['giveFollowBonus']
_FOLLOWBONUS = currencyConfig['followBonus']

def _load_from_db():
    """Load the currency table from the database."""
    result = db.get_users_currency_table()
    for res in result:
        print("Loaded: {} with {} currency unit things".format(res[0], res[1]))
        _users[res[0]] = res[1]

def _write_to_db():
    """Update/Insert currency balances to the database."""
    db.update_users_currency_table(_users)

def _get_balance(username):
    if username not in _users:
        _users[username] = 0
    return _users[username]

def _add_tokens(username, amount):
    """Add the specified amount of tokens to the user's balance"""
    if username not in _users:
        _users[username] = amount
    else:
        _users[username] += amount
    return True

def _remove_tokens(username, amount):
    """Remove the specified amount of tokens from the user's balance.

    Returns True if successful, False if user had no record in the table
    or did not have enough tokens.
    """
    if username not in _users:
        return False
    else:
        if _users[username] < amount:
            return False
        else:
            _users[username] -= amount
            return True

def _transfer_tokens(userFrom, userTo, amount):
    if amount <= 0:
        return (False, "Pay amount must be greater than zero.")
    if userFrom == userTo:
        return (False, "Can't pay yourself!")
    if _get_balance(userFrom) < amount:
        return (False, "You do not have enough {}.".format(_CURRENCYNAME))
    if userTo not in get_viewers():
        return (False, "{} is not a valid recipient.".format(userTo))
    else:
        _remove_tokens(userFrom, amount)
        _add_tokens(userTo, amount)
        return (True, "User {} transferred {} {} to {}.".format(userFrom,
                                                                amount, _CURRENCYNAME, userTo))

def _give_tokens_per_minute():
    amount = _TOKENSPERMINUTE
    for username in get_viewers():
        if username not in _users:
            _users[username] = amount
        else:
            _users[username] += amount

# Chat Commands
def get_balance(userName, *args, **kwargs):
    """Get the currency balance for the specified user."""
    if userName not in _users:
        return False
    return ["{0}'s balance is: {1} {2}".format(userName, _users[userName], _CURRENCYNAME)]

def pay(userName, *args, **kwargs):
    """Get the currency balance for the specified user."""
    userTo = args[0]
    try:
        amount = int(args[1])
    except ValueError:
        return False
    result = _transfer_tokens(userName, userTo.lower(), amount)
    if result[0]:
        return [result[1]]
    return ["/w {} {}".format(userName, result[1])]

def give_tokens(userName, *args, **kwargs):
    """Add tokens to the specified user."""
    userTo = args[0]
    if not user_online(userName):
        return False
    try:
        amount = int(args[1])
    except ValueError:
        return False
    _add_tokens(userTo, amount)
    return ["{} was granted {} {} by {}!".format(
        userTo, amount, _CURRENCYNAME, userName
    )]


# CALL BEFORE USING MODULE
def initialize_currency_system():
    """Load records from database and register timedevents."""
    if _USECURRENCY:
        _load_from_db()
        register_event(_write_to_db, 600)
        if _GIVEPERVIEWTIME:
            register_event(_give_tokens_per_minute, 60)
    else:
        return False
