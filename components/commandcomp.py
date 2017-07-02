#Make and edit commands that are stored in a database
from .empty_component import EmptyComponent as _EC
import db_helper
from commands_helper import PrivmsgCommand

class Component(_EC):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands={}
        for command in db_get_all_commands():
            self.bot.commands_helper._add_privmsg_command(command.to_privmsg_command(self.irc))
    
    def load(self):
        pass
    
    def unload(self):
        pass
    
    def add_command(self, name, response):
        command=Command(name, response)
        #Check if already exists or return false
        if db_get_command(name) == None:
            db_add_command(command)
        else:
            return False
        self.bot.commands_helper._add_privmsg_command(command.to_privmsg_command())

    def set_response(self, name, response):
        if db_get_command(name) == None:
            return False
        self.bot.commands_helper.privmsg_commands[name].func=lambda username, channel, message, tags:self.irc.sendprivmsg(channel,response.format(channel=channel, username=username))
        db_set_response(name, response)
        return True

    def set_channel_cooldown(self, name, channel_cooldown):
        if db_get_command(name) == None:
            return False
        self.bot.commands_helper.privmsg_commands[name].channel_cooldown=channel_cooldown
        db_set_channel_cooldown(name, channel_cooldown)
        return True

    def set_user_cooldown(self, name, user_cooldown):
        if db_get_command(name) == None:
            return False
        self.bot.commands_helper.privmsg_commands[name].user_cooldown=user_cooldown
        db_set_user_cooldown(name, user_cooldown)
        return True

    def set_mod_only(self, name, mod_only):
        if db_get_command(name) == None:
            return False
        self.bot.commands_helper.privmsg_commands[name].mod_only=mod_only
        db_set_mod_only(name, mod_only)
        return True

    def set_broadcaster_only(self, name, broadcaster_only):
        if db_get_command(name) == None:
            return False
        self.bot.commands_helper.privmsg_commands[name].broadcaster_only=broadcaster_only
        db_set_broadcaster_only(name, broadcaster_only)
        return True

    def set_enabled(self, name, enabled):
        if db_get_command(name) == None:
            return False
        self.bot.commands_helper.privmsg_commands[name].enabled=enabled
        db_set_enabled(name, enabled)
        return True

    def remove_command(self, name):
        if db_get_command(name) == None:
            return False
        self.bot.commands_helper.privmsg_commands[name].enabled=enabled
        db_remove_command(name)
        return True


class Command:
    """
    Represents a command that prints out a text if a !command is done in chat
    """
    def __init__(self, name, response, channel_cooldown=0, user_cooldown=0, mod_only=False, broadcaster_only=False, enabled=True):
        self.name=name
        self.response=response
        self.channel_cooldown=channel_cooldown
        self.user_cooldown=user_cooldown
        self.mod_only=mod_only
        self.broadcaster_only=broadcaster_only
        self.enabled=enabled

    @staticmethod
    def from_db_tuple(t):
        return Command(t[0],t[1],t[2],t[3],t[4]==1,t[5]==1,t[6]==1)
    
    def to_privmsg_command(self,irc):
        return PrivmsgCommand(self.name, lambda username, channel, message, tags:irc.sendprivmsg(channel,self.response.format(channel=channel, username=username)),
            self.channel_cooldown, self.user_cooldown, self.mod_only, self.broadcaster_only, self.enabled)

CREATE_TABLE_STATEMENT='CREATE TABLE IF NOT EXISTS `commands` (`name` TEXT NOT NULL, `response` TEXT NOT NULL DEFAULT\'\', '\
    +'`channel_cooldown` INTEGER NOT NULL DEFAULT 0, `user_cooldown` INTEGER NOT NULL DEFAULT 0,'\
    +'`mod_only` INTEGER NOT NULL DEFAULT 0, `broadcaster_only` INTEGER NOT NULL DEFAULT 0, `enabled` INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(name) )'

INSERT_STATEMENT='INSERT INTO `commands` (`name`, `response`, `channel_cooldown`, `user_cooldown`, `mod_only`, `broadcaster_only`, `enabled`) VALUES (?,?,?,?,?,?,?)'

UPDATE_STATEMENT='UPDATE `commands` SET `response`=?, `channel_cooldown`=?, `user_cooldown`=?, `mod_only`=?, `broadcaster_only`=?, `enabled`=? WHERE `name`=?'

ALTER_RESPONSE_STATEMENT='UPDATE `commands` SET `response`=? WHERE `name`=?'

ALTER_CHANNEL_COOLDOWN_STATEMENT='UPDATE `commands` SET `channel_cooldown`=? WHERE `name`=?'

ALTER_USER_COOLDOWN_STATEMENT='UPDATE `commands` SET `user_cooldown`=? WHERE `name`=?'

ALTER_MOD_ONLY_STATEMENT='UPDATE `commands` SET `mod_only`=? WHERE `name`=?'

ALTER_BROADCASTER_ONLY_STATEMENT='UPDATE `commands` SET `broadcaster_only`=? WHERE `name`=?'

ALTER_ENABLED_STATEMENT='UPDATE `commands` SET `enabled`=? WHERE `name`=?'

REMOVE_STATEMENT='DELETE FROM `commands` WHERE `name`=?'

GET_ALL_STATEMENT='SELECT * FROM `commands`'

GET_STATEMENT='SELECT * FROM `commands` WHERE `name`=?'
def db_create_command_table():
    db_helper.execute(CREATE_TABLE_STATEMENT)

def db_add_command(command):
    db_helper.execute(INSERT_STATEMENT, (command.name, command.response, command.channel_cooldown, command.user_cooldown, command.mod_only, command.broadcaster_only, command.enabled))

def db_update_command(command):
    db_helper.execute(UPDATE_STATEMENT, (command.response, command.channel_cooldown, command.user_cooldown, command.mod_only, command.broadcaster_only, command.enabled, command.name))

def db_set_response(name, response):
    db_helper.execute(ALTER_RESPONSE_STATEMENT,(response, name))

def db_set_channel_cooldown(name, channel_cooldown):
    db_helper.execute(ALTER_CHANNEL_COOLDOWN_STATEMENT,(channel_cooldown, name))

def db_set_user_cooldown(name, user_cooldown):
    db_helper.execute(ALTER_USER_COOLDOWN_STATEMENT,(user_cooldown, name))

def db_set_mod_only(name, mod_only):
    db_helper.execute(ALTER_MOD_ONLY_STATEMENT,(mod_only, name))

def db_set_broadcaster_only(name, broadcaster_only):
    db_helper.execute(ALTER_BROADCASTER_ONLY_STATEMENT,(broadcaster_only, name))

def db_set_enabled(name, enabled):
    db_helper.execute(ALTER_ENABLED_STATEMENT,(enabled, name))

def db_remove_command(name):
    db_helper.execute(REMOVE_STATEMENT,(name,))

def db_get_all_commands():
    return map(Command.from_db_tuple,db_helper.fetchall(GET_ALL_STATEMENT))

def db_get_command(name):
    found = list(map(Command.from_db_tuple,db_helper.fetchall(GET_STATEMENT,(name,))))
    if len(found)==0:
        return None
    else:
        return found[0]
