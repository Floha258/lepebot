from .empty_component import EmptyComponent as _EC
from config.twitch_config import twitch_id, channel
import threading
import time

class Component(_EC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop_event=threading.Event()
    
    def load(self):
        self.old_follow_list=[follow['user']['_id'] for follow in self.bot.twitch_api.getfollowers(twitch_id,10)['follows']]
        def _check():
            while True:
                #Waits for 25 seconds but if the event is fired to stop, it determinates
                #Timeout returns False, set the event returns True
                if True == self.stop_event.wait(25):
                    break
                current_follows=self.bot.twitch_api.getfollowers(twitch_id,10)['follows']
                self.process_change(self.old_follow_list, current_follows)
                self.old_follow_list=[follow['user']['_id'] for follow in current_follows]
        threading.Thread(target=_check).start()
    
    def unload(self):
        self.stop_event.set()
    
    def process_change(self, old, new):
        #Try to find one of the old id's in the new follower list
            _break=False
            for old_id in old:
                for i,follow in enumerate(new):
                    if follow['user']['_id']==old_id:
                        _break=True
                        if i>0:
                            self.shoutout(new[:i])
                        break
                if _break:
                    break
    
    def shoutout(self,follows):
        print(follows)
        if len(follows)==1:
            msg='Thanks for the follow <3 '+follows[0]['user']['name']+'!'
            self.bot.irc.sendprivmsg(channel, msg)
            #print(msg)
        else:
            names=', '.join(follow['user']['name'] for follow in follows)
            msg='Thanks for the follows <3 '+names+'!'
            self.bot.irc.sendprivmsg(channel, msg)
            #print(msg)
