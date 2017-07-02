import time
class PrivmsgCommand:
    """
    Util class to manage commands like !wr for messages sent in a channel,
    has support for cooldown (individual user, global) and mod-only/broadcaster-only too
    """
    def __init__(self, name, func, channel_cooldown=0, user_cooldown=0, mod_only=False, broadcaster_only=False, enabled=True):
        """
        Init a new Command
        Params:
            name (str): Name of the command. Note that the name is automatically prefixed with '!',
                if you want the Command to be executed when the user types in '!wr' in chat,
                name ist 'wr'
            func (function): Function to handle the command, params: (username, channel, message, tags)
            channel_cooldown (int, optional): Number of seconds of cooldown, after the command was used in the channel
            user_cooldown (int, optional): Number of seconds of cooldown, after a user can use this command again
            mod_only(bool, default=False): IF only mods or the broadcaster can use this command
            broadcaster_only(bool, default=False): If only broadcaster can use this command
                enabled(bool, default=True): If the command can be used in chat, otherwise it's useless
        """
        self.name=name
        self.func=func
        self.channel_cooldown=channel_cooldown
        self.user_cooldown=user_cooldown
        self.mod_only=mod_only
        self.broadcaster_only=broadcaster_only
        self.enabled=enabled

class WhisperCommand:
    """
    Util class to manage whisper commands like !uptime,
    has support for cooldown (individual user)
    """
    def __init__(self, name, func, user_cooldown=0):
        """
        Init a new Command
        Params:
            name (str): Name of the command. Note that the name is automatically prefixed with '!',
                if you want the Command to be executed when the user types in '!wr' in chat,
                name ist 'wr'
            func (function): Function to handle the command, params: (username, channel, message, tags)
            user_cooldown (int, optional): Number of seconds of cooldown, after a user can use this command again
        """
        self.name=name
        self.func=func
        self.user_cooldown=user_cooldown

def check_mod(tags):
    """
    Check if a person with these tags is mod
    """
    return 'mod' in tags['badges']
    
def check_broadcaster(tags):
    """
    Check if a person with these tags is the broadcaster
    """
    return 'broadcaster' in tags['badges']

class CommandsHelper:
    def __init__(self):
        #(channel, commandname):last used time
        self.channel_cooldowns={}
        #(channel, username, commandname):last used time
        self.channel_user_cooldowns={}
        #(username, commandname):last used time
        self.user_cooldowns={}
        #commandname:PrivmsgCommand
        self.privmsg_commands={}
        #commandname:WhisperCommand
        self.whisper_commands={}
    
    def add_privmsg_command(self, name, func, channel_cooldown=0, user_cooldown=0, mod_only=False, broadcaster_only=False, enabled=True):
        """
        Add a new privmsg-command
        Params:
            name (str): Name of the command. Note that the name is automatically prefixed with '!',
                if you want the Command to be executed when the user types in '!wr' in chat,
                name ist 'wr'
            func (function): Function to handle the command, params: (username, channel, message, tags)
            channel_cooldown (int, optional): Number of seconds of cooldown, after the command was used in the channel
            user_cooldown (int, optional): Number of seconds of cooldown, after a user can use this command again
            mod_only(bool, default=False): IF only mods or the broadcaster can use this command
            broadcaster_only(bool, default=False): If only broadcaster can use this command
            enabled(bool, default=True): If the command can be used
        """
        self._add_privmsg_command(PrivmsgCommand(name, func, channel_cooldown, user_cooldown, mod_only, broadcaster_only))

    def _add_privmsg_command(self, command):
        self.privmsg_commands[command.name]=command

    def add_whisper_command(self, name, func, user_cooldown=0):
        """
        Add a new whisper-command
        Params:
            name (str): Name of the command. Note that the name is automatically prefixed with '!',
                if you want the Command to be executed when the user types in '!wr' in chat,
                name ist 'wr'
            func (function): Function to handle the command, params: (username, channel, message, tags)
            user_cooldown (int, optional): Number of seconds of cooldown, after a user can use this command again
        """
        self.whisper_commands[name]=WhisperCommand(name, func, user_cooldown)
    
    def remove_privmsg_command(self, name):
        """
        Remove a command by name
        """
        if name in self.privmsg_commands:
            del self.privmsg_commands[name]
    
    def remove_whisper_command(self, name):
        """
        Remove a command by name
        """
        if name in self.whisper_commands:
            del self.whisper_commands[name]
    
    def privmsg_listener(self, username, channel, message, tags):
        if message.startswith('!'):
            split=message[1:].split(' ',1)
            commandname=split[0]
            if len(split)==1:
                rest=''
            else:
                rest=split[1]
            #Search Command
            if not commandname in self.privmsg_commands:
                return
            command=self.privmsg_commands[commandname]
            #Check enabled
            if not command.enabled:
                return
            #Check mod/broadcaster only
            if command.mod_only and not check_mod(tags):
                return
            if command.broadcaster_only and not check_broadcaster(tags):
                return
            #Check cooldowns
            if command.channel_cooldown!=0:
                if (channel, commandname) in self.channel_cooldowns:
                    last=self.channel_cooldowns[(channel,commandname)]
                    #Check if enough time elapsed since last usage
                    if last!=None and (time.time()-last)<command.channel_cooldown:
                        return
                #Update last use
                self.channel_cooldowns[(channel,commandname)]=time.time()
            if command.user_cooldown!=0:
                if (channel, username, commandname) in self.channel_user_cooldowns:
                    last=self.channel_user_cooldowns[(channel,username,commandname)]
                    #Check if enough time elapsed since last usage
                    if last!=None and (time.time()-last)<command.user_cooldown:
                        return
                #Update last use
                self.channel_user_cooldowns[(channel,username,commandname)]=time.time()
            #Call command
            command.func(username=username,channel=channel,message=rest,tags=tags)
    
    def whisper_listener(self, username, message, tags):
        if message.startswith('!'):
            split=message[1:].split(' ',1)
            commandname=split[0]
            if len(split)==1:
                rest=''
            else:
                rest=split[1]
            #Search Command
            if not commandname in self.whisper_commands:
                return
            command=self.whisper_commands[commandname]
            #Check cooldown
            if command.user_cooldown!=0:
                if (username, commandname) in self.user_cooldowns:
                    last=self.user_cooldowns[(username,commandname)]
                    #Check if enough time elapsed since last usage
                    if last!=None and (time.time()-last)<command.user_cooldown:
                        return
                #Update last use
                self.user_cooldowns[(username,commandname)]=time.time()
            #Call command
            command.func(username=username,message=rest,tags=tags)
