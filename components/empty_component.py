class EmptyComponent:
    """Empty component, superclass of all components
    defines all necessary abstract methods to be implemented in subclasses
    """

    def __init__(self, bot):
        """Init, this intialization does not do anything
        Args:
            bot (Lepebot): The main bot-instance"""
        self.irc=bot.irc
        self.bot=bot

    def load(self, config):
        """Used by the main bot to load this component
        this method should contain registering all listeners in the ircClient
        and prepare for incomming messages
        Args:
            config (dict): Config for this component"""
        raise NotImplementedError

    def unload(self):
        """Used by the main bot to terminate the bot,
        this method should contain unregistering all listeners from the ircClient
        and prepare for shutting down"""
        raise NotImplementedError

    def get_default_settings(self):
        """Returns the default settings
        Returns:
            dict(key, value): The default settings"""
        raise NotImplementedError

    def on_update_settings(self, keys, settings):
        """Method is called when the settings change
        Args:
            keys (list): List of the changed keys
            settings (dict): Dict(key,value) containing the new values"""
        raise NotImplementedError
