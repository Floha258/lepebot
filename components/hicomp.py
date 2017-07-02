#More for testing than for everything else...
from .empty_component import EmptyComponent as _EC

class Component(_EC):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(self.config)
    
    def load(self):
        def sayhi(channel, username, tags, message):
            self.irc.sendprivmsg(channel,'HI @'+username)
        def whisperhi(username, message, tags):
            self.irc.sendwhisper(username, 'OpieOP')
        self.bot.register_privmsg_command('hi',sayhi, channel_cooldown=5, user_cooldown=10)
        self.bot.register_whisper_command('hi',whisperhi,user_cooldown=10)
    
    def unload(self):
        self.bot.unregister_privmsg_command('hi')
        self.bot.unregister_whisper_command('hi')
