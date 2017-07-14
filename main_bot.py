from config.twitch_config import username, oauth_token, channel
from config.component_config import config as component_config
from twitchircclient import TwitchIrcClient, MockIrcClient
from components import twitchapi
from commands_helper import CommandsHelper
import db_helper
import importlib, os

if __name__=='__main__':
    class Lepebot:
        """
        Instance of the bot to share access to all components, utils for the
        database and irc
        """
        
        def __init__(self):
            """Init a new bot """
            self.debug=bool(os.getenv('DEBUG'))
            self.mock=bool(os.getenv('MOCK'))
            
            #Init maybe useful variables
            self.channel=channel
            self.username=username
            
            #create main instance of the ircConnection
            if self.mock:
            #TODO
                self.irc = MockIrcClient(username,oauth_token, debug=self.debug)
            else:
                self.irc = TwitchIrcClient(username, "oauth:"+oauth_token,debug=self.debug)
            
            #Set up up util for easy use of commandnames in privmsg and whisper
            self.privmsg_commands={}
            self.whisper_commands={}
            
            #Set up TwitchApi
            self.twitch_api=twitchapi.TwitchApi()
            
            #Set up CommandsHelper
            self.commands_helper=CommandsHelper()
            self.irc.messagespreader.add(self.commands_helper.privmsg_listener)
            self.irc.whisperspreader.add(self.commands_helper.whisper_listener)
            
            #Set up and load all components
            self.components={}
            comps=component_config['components']
            for comp in comps.keys():
                if comps[comp]['active'] == True:
                    if 'config' in comps[comp]:
                        conf = comps[comp]['config']
                    else:
                        conf={}
                    try:
                        mod = importlib.import_module('components.'+comp)
                        comp_inst=mod.Component(self, conf)
                        self.components[comp]=comp_inst
                        comp_inst.load()
                        print('successfully loaded component '+comp)
                    except Exception as e:
                        print('Error loading module '+comp+':\n',e)
            
            #Database connection:
            self.database=db_helper
            
            #Join the specified channel and start the connection
            self.irc.create_connection()
            self.irc.join(channel)

        def register_privmsg_command(self, name, func, channel_cooldown=0, user_cooldown=0, mod_only=False, broadcaster_only=False, enabled=True):
            """
            Add a new privmsg-command
            Params:
                name (str): Name of the command. Note that the name is automatically prefixed with '!',
                    if you want the Command to be executed when the user types in '!wr' in chat,
                    name ist 'wr'
                func (function): Function to handle the command, params: (username, channel, message, tags)
                channel_cooldown (int, optional): Number of seconds of cooldown, after the command was used in the channel
                user_cooldown (int, optional): Number of seconds of cooldown, after a user can use this command again
                mod_only(bool, default=False): IF only mods or the broadcaster can use this command
                broadcaster_only(bool, default=False): If only broadcaster can use this command
                enabled(bool, default=True): If the command can be used in chat, otherwise it's useless
            """
            self.commands_helper.add_privmsg_command(name, func, channel_cooldown, user_cooldown, mod_only, broadcaster_only, enabled)

        def register_whisper_command(self, name, func, user_cooldown=0):
            """
            Add a new whisper-command
            Params:
                name (str): Name of the command. Note that the name is automatically prefixed with '!',
                    if you want the Command to be executed when the user types in '!wr' in chat,
                    name ist 'wr'
                func (function): Function to handle the command, params: (username, channel, message, tags)
                user_cooldown (int, optional): Number of seconds of cooldown, after a user can use this command again
            """
            self.commands_helper.add_whisper_command(name, func, user_cooldown)
        
        def unregister_privmsg_command(self, name):
            self.commands_helper.remove_privmsg_command(name)
            
        def unregister_whisper_command(self, name):
            self.commands_helper.remove_whisper_command(name)

        def shutdown(self):
            for name, component in self.components.items():
                try:
                    component.unload()
                except Exception as e:
                    print('Error unloading module '+name+':\n',e)
            self.irc.shutdown()
            self.database.close()
            
    bot=Lepebot()
