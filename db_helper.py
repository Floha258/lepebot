import sqlite3
import threading
import os
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print('watchdog is not installed, install it using `pip3 install watchdog`, use it with `--user` if necessary')
    os.exit(1)

#Fix multiple thread database access
db_lock=threading.Lock()
debug=bool(os.getenv('DEBUG'))

db=sqlite3.connect('bot.db', check_same_thread=False)
db_change_listeners=[]

def pr():
    print('testestest')

db_change_listeners.append(pr)
_last_total_changes=0
#Set to true if changes were committed to the database, causing a file change
_expect_file_change=False
_commit_stop_event=threading.Event()

def _check_write():
    global _last_total_changes
    global _expect_file_change
    while True:
        #Waits for 15 seconds but if the event is fired to stop, it terminates
        #Timeout returns False, set the event returns True
        if True == _commit_stop_event.wait(15):
            break
        #Check for changes
        with db_lock:
            if db.total_changes>_last_total_changes:
                print(db.total_changes)
                _expect_file_change=True
                db.commit()
                _last_total_changes=db.total_changes

threading.Thread(target=_check_write).start()

path = '.'
class EH(FileSystemEventHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def on_modified(self, event):
        global _expect_file_change
        if not event.is_directory and event.src_path.endswith('bot.db'):
            if not _expect_file_change:
                for listener in db_change_listeners:
                    listener()
            _expect_file_change=False

event_handler = EH()
observer = Observer()
observer.schedule(event_handler, path, recursive=False)
observer.start()

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