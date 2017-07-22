import sqlite3
import threading
import os

#Fix multiple thread database access
db_lock=threading.Lock()
debug=bool(os.getenv('DEBUG'))

db=sqlite3.connect('bot.db', check_same_thread=False)

def execute(*args):
    with db_lock:
        if debug:
            print('executing',args)
        db.execute(*args)

def fetchall(*args):
    with db_lock:
        if debug:
            print('fetching',args)
        return db.execute(*args).fetchall()

def commit():
        with db_lock:
            db.commit()

def close():
    with db_lock:
        db.commit()
        db.close()
