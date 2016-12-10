import sqlite3

"""Module facilitating reading and writing to the database.
"""

_DBNAME = 'data/db.sqlite'
_QUERIES = {
    'createTables':[
    "CREATE TABLE IF NOT EXISTS dynamiccommands(id INTEGER PRIMARY KEY, name TEXT, output TEXT)",
    "CREATE TABLE IF NOT EXISTS users(name TEXT PRIMARY KEY, currency INTEGER)"
    ],
    'getDynamicCommands':'''
    SELECT name, output FROM dynamiccommands
    ''',
    'deleteDynamicCommand':'''
    DELETE FROM dynamiccommands WHERE name = ?
    ''',
    'saveDynamicCommand':'''
    INSERT INTO dynamiccommands(name, output) VALUES(?,?)
    ''',
    'updateDynamicCommand':'''
    UPDATE dynamiccommands SET output = ? WHERE name = ?
    ''',
    'getUsers':'''
    SELECT * FROM users
    ''',
    'getUserCurrency':'''
    SELECT currency FROM users WHERE name = ?
    ''',
    'updateUserCurrency':'''
    INSERT OR REPLACE INTO users (name, currency) VALUES (?,?)
    '''
}

def initialize_database():
    with sqlite3.connect(_DBNAME) as db:
        for query in _QUERIES['createTables']:
            db.execute(query)
        db.commit()
    print("Done initializing Database!")

def get_dynamic_commands():
    with sqlite3.connect(_DBNAME) as db:
        cursor = db.cursor()
        cursor.execute(_QUERIES['getDynamicCommands'])
        return cursor.fetchall()
    return False

def get_users_currency_table():
    with sqlite3.connect(_DBNAME) as db:
        cursor = db.cursor()
        cursor.execute(_QUERIES['getUsers'])
        return cursor.fetchall()
    return False

def update_users_currency_table(users):
    with sqlite3.connect(_DBNAME) as db:
        cursor = db.cursor()
        for key, value in users.items():
            cursor.execute(_QUERIES['updateUserCurrency'], (key, value))
        return True
    return False

def get_user_currency(name):
    with sqlite3.connect(_DBNAME) as db:
        cursor = db.cursor()
        cursor.execute(_QUERIES['getUserCurrency'], (name,))

def delete_dynamic_command(name):
    with sqlite3.connect(_DBNAME) as db:
        cursor = db.cursor()
        cursor.execute(_QUERIES['deleteDynamicCommand'], (name,))
        db.commit()
        return True
    return False

def save_dynamic_command(name, output):
    with sqlite3.connect(_DBNAME) as db:
        cursor = db.cursor()
        cursor.execute(_QUERIES['saveDynamicCommand'], (name, output))
        db.commit()
        return True
    return False

def update_dynamic_command(name, output):
    with sqlite3.connect(_DBNAME) as db:
        cursor = db.cursor()
        cursor.execute(_QUERIES['updateDynamicCommand'], (name,output))
        db.commit()
        return True
    return False
