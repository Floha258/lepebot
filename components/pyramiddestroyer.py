from .empty_component import EmptyComponent as _EC


"""
Death to all pyramid attempts :)
"""
class Component(_EC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def load(self, config):
        self.message = config['message']
        self.lastuser = ''
        self.lastmessage = ''
        # alternating so we can bust a lot of messages
        self.irc.messagespreader.add(self.pyramiddestroyer)
    
    def unload(self):
        self.irc.messagespreader.remove(self.pyramiddestroyer)

    def get_default_settings(self):
        return {'message': ':) '}

    def on_update_settings(self, keys, settings):
        if 'message' in keys:
            self.message = settings['message']

    def pyramiddestroyer(self, channel, message, tags, username):
        message = message.replace('.', '').replace(',', '').replace('  ', ' ').strip()
        if username == self.lastuser and \
           (self.lastmessage+' '+self.lastmessage) == message:
            self.irc.sendprivmsg(channel,
                                 self.message.format(username=username))
        self.lastuser = username
        self.lastmessage = message
