class EmptyComponent:
    """Empty component, superclass of all components
    defines all necessary abstract methods to be implemented in subclasses
    """

    def __init__(self, bot, config):
        """Init
        Args:
            bot (Lepebot): The main bot-instance
            config (dict): Config for this component"""
        self.irc=bot.irc
        self.bot=bot
        self.config=config

    def load(self):
        """Used by the main bot to load this component
        this method should contain registering all listeners in the ircClient
        and prepare for incomming messages"""
        raise NotImplementedError

    def unload(self):
        """Used by the main bot to terminate the bot,
        this method should contain unregistering all listeners from the ircClient
        and prepare for shutting down"""
        raise NotImplementedError
