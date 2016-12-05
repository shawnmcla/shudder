import sqlite3

"""Module facilitating reading and writing to the database.
"""

_DBNAME = 'data/db.sqlite'
_QUERIES = {
    'createTables':'''
    CREATE TABLE IF NOT EXISTS dynamiccommands(id INTEGER PRIMARY KEY, name TEXT, output TEXT)
    ''',
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
    '''
}

def initialize_database():
    with sqlite3.connect(_DBNAME) as db:
        db.execute(_QUERIES['createTables'])
        db.commit()
    print("Done initializing Database!")

def get_dynamic_commands():
    with sqlite3.connect(_DBNAME) as db:
        cursor = db.cursor()
        cursor.execute(_QUERIES['getDynamicCommands'])
        return cursor.fetchall()

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
