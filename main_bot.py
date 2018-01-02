#!/usr/bin/python3 -i

from config.twitch_config import username, oauth_token, channel
#component config file is deprecated
try:
    from config.component_config import config as component_config
except:
    component_config=None
from twitchircclient import TwitchIrcClient, MockIrcClient
from twitchapi import TwitchApi
from commands_helper import CommandsHelper
import db_helper
import settings_db
import importlib, os
import glob
from os.path import dirname, basename, isfile
from collections import defaultdict

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
            
            #Database connection:
            self.database=db_helper
            
            #Get all settings
            settings_db.db_create_table()
            self.settings=settings_db.db_select_all()

            #create main instance of the ircConnection
            if self.mock:
            #TODO
                self.irc = MockIrcClient(username,oauth_token, debug=self.debug)
            else:
                self.irc = TwitchIrcClient(username, "oauth:"+oauth_token,debug=self.debug)
            
            #Detect all components in the component directory (but not the default empty component)
            files=glob.glob('components/*.py')
            componentnames=[basename(f)[:-3] for f in files if isfile(f) and not f.endswith('empty_component.py')]
                        
            #Load components
            self.components={}
            defaultsettings=[]
            for compname in componentnames:
                self.components[compname]=importlib.import_module('components.'+compname).Component(self)
                defaultsettings.append(settings_db.Setting(compname,'active','0'))
                for key, value in self.components[compname].get_default_settings().items():
                    defaultsettings.append(settings_db.Setting(compname, key, value))

            #Apply legacy settings file
            if component_config!=None:
                filesettings=[]
                for comp, setts in component_config['components'].items():
                    filesettings.append(settings_db.Setting(comp,'active','1' if setts['active'] else '0'))
                    if 'config' in setts:
                        for key, value in setts['config'].items():
                            filesettings.append(settings_db.Setting(comp, key, value))
                difference=settings_db.generate_diff(self.settings, filesettings)
                for actual, default in difference:
                    if actual is None:
                        self.settings.append(default)
                        settings_db.db_insert_setting(default)
                    
            #Apply defaults
            difference=settings_db.generate_diff(self.settings, defaultsettings)
            for actual, default in difference:
                if actual is None:
                    self.settings.append(default)
                    settings_db.db_insert_setting(default)

            #Init maybe useful variables
            self.channel=channel
            self.username=username
            
            #Set up up util for easy use of commandnames in privmsg and whisper
            self.privmsg_commands={}
            self.whisper_commands={}
            
            #Set up TwitchApi
            self.twitch_api=TwitchApi()
            
            #Set up CommandsHelper
            self.commands_helper=CommandsHelper()
            self.irc.messagespreader.add(self.commands_helper.privmsg_listener)
            self.irc.whisperspreader.add(self.commands_helper.whisper_listener)

            dictsettings=Lepebot.settingslist_to_dict(self.settings)
            
            #Set up the Components
            for compname, component in self.components.items():
                if dictsettings[compname]['active']=='1':
                    print('loaded '+compname)
                    component.load(dictsettings[compname])
                else:
                    print('component {} is not active'.format(compname))

            #Join the specified channel and start the connection
            self.irc.create_connection()
            self.irc.join(channel)

            #Register database change hook
            db_helper.add_db_change_listener(self._databaseupdate)

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

        @staticmethod
        def settingslist_to_dict(settingslist):
            dictsettings=defaultdict(dict)
            for setting in settingslist:
                dictsettings[setting.module][setting.key]=setting.value
            return dictsettings
            
        def _databaseupdate(self):
            newsettings=settings_db.db_select_all()
            settingsdiff=settings_db.generate_diff(self.settings,newsettings)
            if len(settingsdiff)==0:
                return
            self.settings=newsettings
            changedsettings=(set_tup[1] for set_tup in settingsdiff if not set_tup[1] is None)
            settingsdict=Lepebot.settingslist_to_dict(changedsettings)
            for modname, settings in settingsdict.items():
                if 'active' in settings:
                    if settings['active']=='1':
                        #component is now active! Get all settings from this module and load it
                        compsettings=Lepebot.settingslist_to_dict(settings_db.db_select_for_module(modname))
                        self.components[modname].load(compsettings[modname])
                    else:
                        #unload component
                        self.components[modname].unload()
                else:
                    self.components[modname].on_update_settings(settings.keys(),settings)
            
    bot=Lepebot()
