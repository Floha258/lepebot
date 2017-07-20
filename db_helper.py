import sqlite3
import threading

#Connection objects can't be used within mutiple threads, so a connection for every thread is needed
#tid=thread-id
db_connections={}
#last write (thread-id)  to reduce commits on the database
db_last_write=-1
def get_con_for_id(tid):
    if tid in db_connections:
        return db_connections[tid]
    else:
        con=sqlite3.connect('bot.db')
        db_connections[tid]=con
        return con

def execute(*args):
    tid = threading.get_ident()
    db=get_con_for_id(tid)
    db.execute(*args)
    _commit(tid)

def fetchall(*args):
    db=get_con_for_id(threading.get_ident())
    return db.execute(*args).fetchall()

def _commit(tid):
    """Check if commit is needed"""
    global db_last_write
    if db_last_write == -1:
        db_last_write = tid
    elif db_last_write != tid:
        db_connections[db_last_write].commit()
        db_last_write=tid
    

def close():
    if db_last_write != -1:
        db_connections[db_last_write].commit()
    for tid,con in db_connections.items():
        con.close()
