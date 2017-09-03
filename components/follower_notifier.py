from .empty_component import EmptyComponent as _EC
from config.twitch_config import twitch_id, channel
import requests
import threading

class Component(_EC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop_event=threading.Event()
    
    def load(self):
        self.stop_event.clear()
        try:
            raw_follows=self.bot.twitch_api.getfollowers(twitch_id,10)
            if raw_follows==None:
                self.old_follow_list=None
            else:
                self.old_follow_list=[follow['user']['_id'] for follow in raw_follows['follows']]
        except requests.ConnectionError:
            print('Connection error in follower_notifier')
            self.old_follow_list=None
            
        def _check():
            while True:
                #Waits for 25 seconds but if the event is fired to stop, it terminates
                #Timeout returns False, set the event returns True
                if True == self.stop_event.wait(25):
                    break
                try:
                    raw_current_follows=self.bot.twitch_api.getfollowers(twitch_id,10)
                except requests.ConnectionError:
                    print('Connection error in follower_notifier')
                    continue
                #Just ignore temporary errors
                if raw_current_follows==None:
                    continue
                current_follows=raw_current_follows['follows']
                if self.old_follow_list!=None:
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
