import re
import requests
from .empty_component import EmptyComponent as _EC

class Component(_EC):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def load(self,config):
        def msglistener(channel, username, message, tags):
            num=None
            try:
                num=int(message.strip())
            except:
                pass
            if num is None:
                fact=self.get_random_fact()
            else:
                fact=self.get_fact(int(num))
            if fact:
                self.bot.irc.sendprivmsg(self.bot.channel,fact)
        self.bot.register_privmsg_command('fact',msglistener)
    
    def unload(self):
        self.bot.unregister_privmsg_command('fact')

    def get_default_settings(self):
        return {}

    def on_change_settings(self, keys, settings):
        pass
    

#def whisperlistener(username, message, tags):
#    if username=='lepelog':
#        join_match=join_regex.match(message)
#        if join_match:
#            irc.join(join_match.group('channel'))
#            irc.sendwhisper(username, 'joined succcessfully')
#            return
#        part_match=part_regex.match(message)
#        if part_match:
#            irc.part(part_match.group('channel'))
#            irc.sendwhisper(username, 'parted succcessfully')
#            return

    def get_random_fact(self):
        response=requests.get('http://numbersapi.com/random')
        if response.status_code==200:
            return response.text
        else:
            return None

    def get_fact(self,num):
        response=requests.get('http://numbersapi.com/%s'%num)
        if response.status_code==200:
            return response.text
        else:
            return None
