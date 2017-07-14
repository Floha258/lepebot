import sqlite3
import threading

#Connection objects can't be used within mutiple threads, so a connection for every thread is needed
#tid=thread-id
db_connections={}
def get_con_for_id(tid):
    if tid in db_connections:
        return db_connections[tid]
    else:
        con=sqlite3.connect('bot.db')
        db_connections[tid]=con
        return con

def execute(*args):
    db=get_con_for_id(threading.get_ident())
    db.execute(*args)
    db.commit()

def fetchall(*args):
    db=get_con_for_id(threading.get_ident())
    return db.execute(*args).fetchall()

def close():
    for tid,con in db_connections.items():
        con.close()
