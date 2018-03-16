#!/usr/bin/python3

from requests_oauthlib import OAuth2Session
from config.twitch_config import twitch_client_id, twitch_client_secret
import json
import settings_db, db_helper

if __name__ == '__main__':
    redirect_uri = 'http://localhost'
    scope = ['channel_editor', 'chat_login']
    oauth = OAuth2Session(twitch_client_id, redirect_uri=redirect_uri,
                          scope=scope)
    authorization_url, state = oauth.authorization_url(
        'https://id.twitch.tv/oauth2/authorize')
    print('Please visit this URL and authorize access: {}'.format(authorization_url))
    response = input('Paste the full callback URL here:\n')
    if response[4] != 's':
        # dirty fix of a not https URL. It's localhost :shrug:
        response = 'https'+response[4:]
    token = oauth.fetch_token(
        'https://id.twitch.tv/oauth2/token',
        authorization_response=response,
        client_secret=twitch_client_secret)
    settings_db.db_create_table()
    settings_db.db_replace_setting(
        settings_db.Setting('main', 'oauth_token', json.dumps(token)))
    db_helper.commit()
    db_helper.close()
