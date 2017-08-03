from .empty_component import EmptyComponent as _EC
import db_helper
import re
import time

#Table structure of regexresponse
#regex: string (primary key), response: string ({username} and {channel} are replaced with the corresponding strings), cooldown: int (in seconds, means channel cooldown)

CREATE_TABLE_STATEMENT='CREATE TABLE IF NOT EXISTS `regexresponse` (`regex` TEXT NOT NULL, `response` TEXT NOT NULL, `cooldown` INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(regex))'
INSERT_STATEMENT='INSERT INTO `regexresponse` (`regex`, `response`, `cooldown`) VALUES (?,?,?)'
UPDATE_REGEX_STATEMENT='UPDATE `regexresponse` SET `regex`=? WHERE `regex`=?'
UPDATE_COOLDOWN_STATEMENT='UPDATE `regexresponse` SET `cooldown`=? WHERE `regex`=?'
UPDATE_RESPONSE_STATEMENT='UPDATE `regexresponse` SET `response`=? WHERE `regex`=?'
DELETE_STATEMENT='DELETE FROM `regexresponse` WHERE `regex`=?'
SELECT_ALL_STATEMENT='SELECT * FROM `regexresponse`'
SELECT_ONE_STATEMENT='SELECT * FROM `regexresponse` WHERE `regex`=?'

class Component(_EC):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regres=[]
        #(channel,regex):lasttimeused
        self.cooldowns={}
        def _msglistener(channel, username, message, tags):
            for regres in self.regres:
                if regres.regex.match(message) != None:
                    #Check cooldown
                    if regres.cooldown!=0:
                        if (channel, regres.regex) in self.cooldowns:
                            last=self.cooldowns[(channel,regres.regex)]
                            #Check if enough time elapsed since last usage
                            if last!=None and (time.time()-last)<regres.cooldown:
                                continue
                        #Update last use
                        self.cooldowns[(channel,regres.regex)]=time.time()
                    self.irc.sendprivmsg(channel, regres.response)
                    return
        self.msglistener=_msglistener

    def load(self):
        db_helper.execute(CREATE_TABLE_STATEMENT)
        self.regres=db_get_all()
        self.irc.messagespreader.add(self.msglistener)
    
    def unload(self):
        self.irc.messagespreader.remove(self.msglistener)
    
    def regres_reload(self):
        self.regres=db_get_all()

class RegexResponse:
    def __init__(self, regex, response, cooldown):
        self.regex=re.compile(regex)
        self.response=response
        self.cooldown=cooldown
    
    @staticmethod
    def fromdbtuple(dbtuple):
        return RegexResponse(*dbtuple)

def db_add_regex(regres):
    db_helper.execute(INSERT_STATEMENT,(regres.regex, regres.response, regres.cooldown))

def db_update_regex(regres):
    db_helper.execute(UPDATE_REGEX_STATEMENT,(regres.response, regres.cooldown, regres.regex))

def db_set_name(old, new):
    db_helper.execute(UPDATE_REGEX_STATEMENT,(new,old))

def db_get_all():
    all=db_helper.fetchall(SELECT_ALL_STATEMENT)
    return list(map(RegexResponse.fromdbtuple,all))