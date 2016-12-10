import lib.database as db
from lib.cfg import currencyConfig
from lib.twitch import get_viewers
_users = {}

def load_from_db():
    """Load the currency table from the database."""
    result = db.get_users_currency_table()
    for res in result:
        print("Loaded: {} with {} currency unit things".format(res[0], res[1]))
        _users[res[0]] = res[1]

def test():
    """Delete soon ok"""
    users = get_viewers()
    for user in users:
        if user not in _users:
            _users[user] = 0
        else:
            _users[user] += 1

def write_to_db():
    """Update/Insert currency balances to the database."""
    db.update_users_currency_table(_users)

def get_balance(userName, *args, **kwargs):
    """Get the currency balance for the specified user."""
    if userName not in _users:
        return False
    return ["{0}'s balance is: {1} {2}".format(userName, _users[userName], currencyConfig['currencyName'])]
