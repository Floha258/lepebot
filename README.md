# Twitch-Chat-Bot
This is an easy to use and easy to customizable chat bot, feel free to fork and add stuff

## Features
Everything is running locally

- Get wr/pb for any/current game, category and variables
- Set Game/Title/Community
- Add/remove commands with/without individual/global cooldowns
- Display Information about twitch-videos posted in chat
- Answer questions automatically (based on regex), this is also pretty nice for memes
- Display messages every x seconds
- TODO: Purge shortened links automatically
- TODO: Add/remove/approve quotes, get random quotes
- TODO: Display information about youtube-videos posted in chat

# Installation
Clone the repository  
Install all required packages with `pip3 install -r requirements.txt`. If you don't have root privileges or want to install the packages just for you append ` --user` to the command.
There seems to be a problem installing watchdogs on windows, because PyYAML can't be installed [this should help](https://stackoverflow.com/questions/33665181/how-to-install-pyyaml-on-windows-10)

Copy the folder example_config and rename it to config.
### component_config (DEPRECATED)
This config specifies which components are loaded and also sets the config for the components. More about components below. If 'active' is set to `True` the component is loaded, otherwise it isn't.  
Note: This is deprecated, settings should be changed in the `bot.db` directly (created after first start)  
The `active` key is responsible for loading the module, so its value has to be set to 1 to load the specified module.
### twitch_confg
This config contains all important private information to let the bot connect to the twitch chat and interact with the twitch-api.  
`username`: username of you bots twitch-account  
`oauth_token`: token to connect to the twitchchat and api. There is a oath-generator for twitch, that can generate a chat-only token, but make sure to not include the `oauth:`-prefix. `twitchapi.py` has some util methods to generate a token that can also be used for the twitch api  
`twitch_client_id`: To make requests to the twitch api, you need to register a application in your twitch settings under connections, click `Register your application`. The url should be set to localhost, the name doesn't matter  
`twitch_client_secret`: Client secret of you registered application  
`channel`: Channel, the bot should join  
`twitch_id`: Id of the channel, is displayed at startup if left blank

# Startup
change to this directory and run `main_bot.py`, if you want to enabled debug output, set the environmentvariable `DEBUG` to 1

# Commands

There are 2 types of commands:

Commands, that only return a text in the channel (with {username} and {channel} replaced by the correct strings), that are stored in the database and added/deleted via chat commands (see below).

Commands, that are added to the `commands_helper` of the bot, calling functions and doing real actions.

- !wr [gameabbreviation] [category] [;variablename:value] (get the current world record for a game listed on speedrun.com)
- !pb [username] [gameabbreviation] [category] [;variablename:value] (get the pb of the given user by game, category and subcategories defined by the variables)
- !searchgame [game] (searches speedrun.com for abbreviation for the given game to use with the wr command)
- !srcurrent [param] ([mod only] set the current default params for the wr command if it is used without params)
- !sruser [username] ([mod only] set the current default username for the pb command)
- !settitle [title] ([mod only] set a new title for the broadcast)
- !setgame [game] ([mod only] set the game for the broadcast)
- !setcommunity [community] ([mod only] set the community for the broadcast)
- !removecommunity ([mod only] remove the community for the broadcast)
- !uptime (display the time the stream is up)
- !addcmd [name] [response] ([mod only] add new command)
- !setcmd [name] [response] ([mod only] change existing command)
- !setcmdname [oldname] [newname] ([mod only] rename a command)
- !setcmdccd [name] [cooldown] ([mod only] set cooldown for command in channel)
- !setcmducd [name] [cooldown] ([mod only] set cooldown for command for all users)
- !setcmdmodonly [name] [0 or 1] ([mod only] set command mod-only, 1 is yes)
- !setcmdbroadcasteronly [name] [0 or 1] ([mod only] set command broadcaster-only, 1 is yes)
- !setcmdenabled [name] [0 or 1] ([mod only] enable/disable command, 1 is enabled)
- !delcmd [name] ([mod only] delete the command)

# Components
Some components store additional information in the database, you can edit this file (`bot.db`) with a sqlite program. When saving changes, the bot reloads all information in the database.
## speedrun.com (srcomcomp)
Component to display information about PBs, WRs, Games and Categories. In your config you can change the `default-param` to a string used by the !wr command (see above documentation for more detailed explanation about this) and `default-username` to your speedrun.com username.

## commandcomp
See the Commands section above for information, simple commands (only response) are stored in a database, table `commands`.

## follower_notifier
Shout out all new followers

## timedmessagecomp
Send a message at a specified intervall in the chat, currently only configurable directly in the database, table `timedmessages`.  
Columns:

- `id` unique id for each row
- `message` message that should be send periodically
- `inittime` initial waiting time in seconds before sending the message the first time
- `looptime` intervall in seconds when to send the message again and again
- `enabled` 0 means disabled, 1 means enabled

## regexresponse
Send a message in the chat if a message matched a regex, stored in the database, table `regexresponse`. The regex may be any valid python-regex.  
Columns:

- `regex` valid python regex that is checked
- `response` message that is send in the channel if the regex matches
- `cooldown` add a cooldown to the response