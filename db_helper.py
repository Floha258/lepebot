import sqlite3
import threading

db=sqlite3.connect('bot.db')

lock=threading.Lock()

def execute(*args):
    with lock:
        db.execute(*args)
        db.commit()

def fetchall(*args):
    with lock:
        return db.execute(*args).fetchall()
