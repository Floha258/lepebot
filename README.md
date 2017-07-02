# Twitch-Chat-Bot
This is an easy to use and easy to customizable chat bot, feel free to fork and add stuff

## Features
Everything is running locally
-Get wr for any game, category and variables
-Set Game/Title
-Add/remove commands with/without individual/global cooldowns
-TODO: Purge shortened links automatically
-TODO: Set community
-TODO: Get wr/pb for the current game
-TODO: Add/remove/approve quotes, get random quotes
-TODO: Answer questions automatically (based on regex)

# Installation
Clone the repository  
Install all required packages with `pip3 install -r requirements.txt`. If you don't have root privileges or want to install the packages just for you append ` --user` to the command.

Copy the folder example_config and rename it to config.
### component_config
This config specifies which components are loaded and also sets the config for the components. More about components below. If 'active' is set to `True` the component is loaded, otherwise it isn't.
### twitch_confg
This config contains all important private information to let the bot connect to the twitch chat and interact with the twitch-api.  
`username`: username of you bots twitch-account  
`oauth_token`: token to connect to the twitchchat and api. There is a oath-generator for twitch, that can generate a chat-only token, but make sure to not include the `oauth:`-prefix. `twitchapi.py` has some util methods to generate a token that can also be used for the twitch api  
`twitch_client_id`: To make requests to the twitch api, you need to register a application in your twitch settings under connections, click `Register your application`. The url should be set to localhost, the name doesn't matter  
`twitch_client_secret`: Client secret of you registered application  
`channel`: Channel, the bot should join  
`twitch_id`: Id of the channel, is displayed at startup if left blank