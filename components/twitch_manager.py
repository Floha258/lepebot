from .empty_component import EmptyComponent as _EC
from datetime import datetime
from util import format_time, format_time_delta

class Component(_EC):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def load(self, config):
        def setgame(username, message, channel, tags):
            response=self.bot.twitch_api.set_game(self.bot.twitch_api.twitch_id, message)
            if response.status_code==200:
                self.irc.sendprivmsg(channel, 'Updated Game')
            else:
                print('Error:', response.text)
                    
        self.bot.register_privmsg_command('setgame',setgame, mod_only=True)
        def getgame(username, message, channel, tags):
            channelobj=self.bot.twitch_api.get_channel(self.bot.twitch_api.twitch_id)
            if channelobj==None:
                self.irc.sendprivmsg(channel, 'Error')
            else:
                self.irc.sendprivmsg(channel, '@{} current game: {}'.format(username,channelobj['game']))
        self.bot.register_privmsg_command('getgame',getgame,channel_cooldown=15)
        def settitle(username, message, channel, tags):
            response=self.bot.twitch_api.set_title(self.bot.twitch_api.twitch_id, message)
            if response.status_code==200:
                self.irc.sendprivmsg(channel, 'Updated Title')
            else:
                print('Error:', response.text)
                    
        self.bot.register_privmsg_command('settitle',settitle, mod_only=True)
        def gettitle(username, message, channel, tags):
            channelobj=self.bot.twitch_api.get_channel(self.bot.twitch_api.twitch_id)
            if channelobj==None:
                self.irc.sendprivmsg(channel, 'Error')
            else:
                self.irc.sendprivmsg(channel, '@{} current title: {}'.format(username,channelobj['status']))
        self.bot.register_privmsg_command('gettitle',gettitle,channel_cooldown=15)
        def setcommunity(username, message, channel, tags):
            found_community=self.bot.twitch_api.get_community(message)
            if found_community!=None:
                response = self.bot.twitch_api.set_community(self.bot.twitch_api.twitch_id, found_community['_id'])
                if response.status_code==204:
                    self.irc.sendprivmsg(channel, 'Updated Community')
                else:
                    print('Error:', response.text)
        self.bot.register_privmsg_command('setcommunity',setcommunity, mod_only=True)
        def removecommunity(username, message, channel, tags):
            response = self.bot.twitch_api.remove_community(self.bot.twitch_api.twitch_id)
            if response.status_code==204:
                self.irc.sendprivmsg(channel, 'Removed Community')
            else:
                print('Error:', response.text)
        self.bot.register_privmsg_command('removecommunity',removecommunity, mod_only=True)
        def uptime(username, message, channel, tags):
            stream = self.bot.twitch_api.get_stream(self.bot.twitch_api.twitch_id)
            if stream == None:
                #Not live
                return
            start = datetime.strptime(stream['created_at'],'%Y-%m-%dT%H:%M:%SZ')
            delta = datetime.utcnow()-start
            self.irc.sendprivmsg(channel, '@{user}, I\'ve been live for {time}'.format(user=username, time=format_time(int(delta.total_seconds()))))
            
        self.bot.register_privmsg_command('uptime',uptime, channel_cooldown=15)
        def followage(username, message, channel, tags):
            user_id=tags['user-id']
            follow = self.bot.twitch_api.getfollow(user_id, self.bot.twitch_api.twitch_id)
            if follow == None:
                self.irc.sendprivmsg(channel, 'You don\'t follow me @{} BibleThump'.format(username))
            else:
                followed_since=datetime.strptime(follow['created_at'],'%Y-%m-%dT%H:%M:%SZ')
                followed_diff=datetime.utcnow()-followed_since
                self.irc.sendprivmsg(channel, 'You follow me for {} @{}'.format(format_time_delta(followed_diff),username))
        self.bot.register_privmsg_command('followage',followage,user_cooldown=20)
        if self.bot.twitch_api.twitch_id == None:
            self.bot.twitch_api.twitch_id=self.bot.twitch_api.get_user(self.bot.channel)['_id']
            print('Your twitch_id is:'+self.bot.twitch_api.twitch_id)
    
    def unload(self):
        self.bot.unregister_privmsg_command('setgame')
        self.bot.unregister_privmsg_command('settitle')
        self.bot.unregister_privmsg_command('getgame')
        self.bot.unregister_privmsg_command('gettitle')
        self.bot.unregister_privmsg_command('setcommunity')
        self.bot.unregister_privmsg_command('removecommunity')
        self.bot.unregister_privmsg_command('uptime')
        self.bot.unregister_privmsg_command('followage')

    def get_default_settings(self):
        return {}

    def on_update_settings(self, keys, settings):
        pass
    
