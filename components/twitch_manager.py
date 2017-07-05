from .empty_component import EmptyComponent as _EC
from .twitchapi import TwitchApi
from datetime import datetime
from util import format_time

class Component(_EC):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ta=TwitchApi()
    
    def load(self):
        def setgame(username, message, channel, tags):
            response=self.ta.set_game(self.ta.twitch_id, message)
            if response.status_code==200:
                self.irc.sendprivmsg(channel, 'Updated Game')
                    
        self.bot.register_privmsg_command('setgame',setgame, mod_only=True)
        def settitle(username, message, channel, tags):
            response=self.ta.set_title(self.ta.twitch_id, message)
            if response.status_code==200:
                self.irc.sendprivmsg(channel, 'Updated Title')
                    
        self.bot.register_privmsg_command('settitle',settitle, mod_only=True)
        def setcommunity(username, message, channel, tags):
            found_community=self.ta.get_community(message)
            if found_community!=None:
                response = self.ta.set_community(self.ta.twitch_id, found_community['_id'])
                if response.status_code==204:
                    self.irc.sendprivmsg(channel, 'Updated Community')
        self.bot.register_privmsg_command('setcommunity',setcommunity, mod_only=True)
        def removecommunity(username, message, channel, tags):
            response = self.ta.remove_community(self.ta.twitch_id)
            if response.status_code==204:
                self.irc.sendprivmsg(channel, 'Removed Community')
        self.bot.register_privmsg_command('removecommunity',removecommunity, mod_only=True)
        def uptime(username, message, channel, tags):
            stream = self.ta.get_stream(self.ta.twitch_id)
            if stream == None:
                #Not live
                return
            start = datetime.strptime(stream['created_at'],'%Y-%m-%dT%H:%M:%SZ')
            delta = datetime.utcnow()-start
            self.irc.sendprivmsg(channel, '@{user}, I\'ve been live for {time}'.format(user=username, time=format_time(int(delta.total_seconds()))))
            
        self.bot.register_privmsg_command('uptime',uptime)
        if self.ta.twitch_id == None:
            self.ta.twitch_id=self.ta.get_user(self.bot.channel)['_id']
            print('Your twitch_id is:'+self.ta.twitch_id)
    
    def unload(self):
        self.bot.unregister_privmsg_command('setgame')
        self.bot.unregister_privmsg_command('settitle')
        self.bot.unregister_privmsg_command('setcommunity')
        self.bot.unregister_privmsg_command('removecommunity')
        self.bot.unregister_privmsg_command('uptime')
