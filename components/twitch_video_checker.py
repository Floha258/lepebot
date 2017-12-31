from .empty_component import EmptyComponent as _EC
import re

TWITCHVIDEO=re.compile('(?:(?:https?://)?www.)?twitch.tv/[a-zA-Z0-9_]+/(?:v/)?(v?[0-9]+)')

class Component(_EC):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def load(self,config):
        def listener(channel, username, message, tags):
            found=TWITCHVIDEO.findall(message)
            if len(found)==0:
                return
            else:
                videostrings=map(lambda v:'{} by {}'.format(v['title'],v['channel']['name']),filter(lambda v:v!=None,map(self.bot.twitch_api.get_video,found)))
                joined=', '.join(videostrings)
                if len(joined)==0:
                    return
                else:
                    self.irc.sendprivmsg(channel, '{} linked: {}'.format(username,joined))
                
        self.listener=listener
        self.irc.messagespreader.add(self.listener)
        
    
    def unload(self):
        self.irc.messagespreader.remove(self.listener)

    def get_default_settings(self):
        return {}

    def on_change_settings(self, keys, settings):
        pass
    
