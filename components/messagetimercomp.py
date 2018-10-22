from .empty_component import EmptyComponent as _EC
import threading
import db_helper
from config.twitch_config import channel

class Component(_EC):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db_helper.execute(CREATE_TABLE_STATEMENT)
        self.timedmessages=list()
        db_helper.add_db_change_listener(self.db_reload)
    
    def load(self,config):
        self.timedmessages=db_get_all()
        for tm in self.timedmessages:
            if tm.enabled:
                tm.start(self.irc, channel)
    
    def unload(self):
        for tm in self.timedmessages:
            tm.stop()

    def get_default_settings(self):
        return {}

    def on_update_settings(self, keys, settings):
        pass
    
    def db_reload(self):
        for tm in self.timedmessages:
            tm.stop()
        self.timedmessages=db_get_all()
        for tm in self.timedmessages:
            if tm.enabled:
                tm.start(self.irc, channel)


class TimedMessage:
    def __init__(self, id, message, inittime, looptime, enabled):
        """
        Constructor
        Params:
            id (int): ID
            message (str): message that is sent periodically
            inittime (int): waittime before sending the first message
            looptime (int): time before the message is sent again
            enabled (bool): Whether or not the TimedMessage is enabled
        """
        self.id=id
        self.message=message
        self.inittime=inittime
        self.looptime=looptime
        self.enabled=enabled
        self.initwait=threading.Event()
        self.loopwait=threading.Event()
    
    def start(self, irc, channel):
        self.initwait.clear()
        self.loopwait.clear()
        def run():
            if self.initwait.wait(self.inittime) == True:
                return
            while True:
                irc.sendprivmsg(channel, self.message)
                if self.loopwait.wait(self.looptime) == True:
                    return
            
        self._runthread=threading.Thread(target=run)
        self._runthread.start()
    
    def stop(self):
        self.initwait.set()
        self.loopwait.set()
    
    @staticmethod
    def from_db_row(row):
        return TimedMessage(id=row[0], message=row[1], inittime=row[2], looptime=row[3], enabled= (row[4] == 1))

CREATE_TABLE_STATEMENT="CREATE TABLE IF NOT EXISTS `timedmessages` (`id` INTEGER PRIMARY KEY AUTOINCREMENT,"\
  +"`message` TEXT NOT NULL DEFAULT '', `inittime` INTEGER NOT NULL DEFAULT 0, `looptime` INTEGER NOT NULL DEFAULT 0, `enabled` INTEGER NOT NULL DEFAULT 0)"

SELECT_STATEMENT="SELECT * FROM `timedmessages` WHERE `id`=?"
SELECT_ALL_STATEMENT="SELECT * FROM `timedmessages`"
INSERT_STATEMENT="INSERT INTO `timedmessages` (`message`,`inittime`,`looptime`,`enabled`) VALUES (?,?,?,?);"\
  +"SELECT last_insert_rowid() FROM `timedmessages` LIMIT 1"
UPDATE_STATEMENT="UPDATE `timedmessages` SET `message`=?, `inittime`=?,`looptime`=?,`enabled`=? WHERE `id`=?"
DELETE_STATEMENT="DELETE FROM `timedmessages` WHERE `id`=?"

def db_get_all():
    return list(map(TimedMessage.from_db_row,db_helper.fetchall(SELECT_ALL_STATEMENT)))

def db_get(id):
    result=db_helper.fetchall(SELECT_STATEMENT,(id,))
    if len(result)>0:
        return TimedMessage.from_db_row(result[0])
    else:
        return None

def db_insert(tm):
    tm.id=db_helper.fetchall(INSERT_STATEMENT, (tm.message, tm.inittime, tm.looptime, 1 if tm.enabled else 0))[0][0]

def db_update(tm):
    db_helper.execute(UPDATE_STATEMENT, (tm.message, tm.inittime, tm.looptime, 1 if tm.enabled else 0, tm.id))

def db_delete(tm):
    db_helper.execute(DELETE_STATEMENT, (tm.id,))
