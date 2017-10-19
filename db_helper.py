import sqlite3
import threading
import os

#Fix multiple thread database access
db_lock=threading.Lock()
debug=bool(os.getenv('DEBUG'))

db=sqlite3.connect('bot.db', check_same_thread=False)
db_change_listeners=[]
_last_total_changes=0
_commit_stop_event=threading.Event()

def _check_write():
    global _last_total_changes
    while True:
        #Waits for 15 seconds but if the event is fired to stop, it terminates
        #Timeout returns False, set the event returns True
        if True == _commit_stop_event.wait(15):
            break
        #Check for changes
        with db_lock:
            if db.total_changes>_last_total_changes:
                print(db.total_changes)
                db.commit()
                _last_total_changes=db.total_changes

threading.Thread(target=_check_write).start()

def execute(*args):
    """
    Execute a sqlite query on the database
    See the sqlite3 python documentation of execute for more information
    """
    with db_lock:
        if debug:
            print('executing',args)
        db.execute(*args)

def fetchall(*args):
    """
    Execute a sqlite query on the database
    See the sqlite3 python documentation of execute for more information
    """
    with db_lock:
        if debug:
            print('fetching',args)
        return db.execute(*args).fetchall()

def commit():
    """
    Writes changes to the database-file
    """
    with db_lock:
        db.commit()

def close():
    """
    Close the connection to the database
    """
    with db_lock:
        db.commit()
        db.close()
        _commit_stop_event.set()

def add_db_change_listener(listener):
    db_change_listeners.append(listener)

def remove_db_change_listener(listener):
    db_change_listeners.remove(listener)