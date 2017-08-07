from config.twitch_config import twitch_client_id, twitch_client_secret, oauth_token, twitch_id
import requests
import json

class TwitchApi:

    def __init__(self,secret=None,token=None):
        self.client_id=twitch_client_id
        self.client_secret=twitch_client_secret
        self.oauth_token=oauth_token
        self.twitch_id=twitch_id
        self.twitch_base_url='https://api.twitch.tv/kraken/'
        
    def get_headers(self, auth=False, other_headers={}):
        """Returns all header for making a successfull request to the twitch api
        Param:
            auth (bool): if authorization is required"""
        headers={'Client-ID':self.client_id, 'Accept':'application/vnd.twitchtv.v5+json'}
        if auth:
            headers['Authorization']='OAuth '+self.oauth_token
        headers.update(other_headers)
        return headers
    
    def generate_oauth_url(self):
        """
        Generates an url to copy in your browser. If you visit this side, twitch will ask you
        to verify that you want to give your own applications these priviledges.
        After you click accept you get redirected to localhost
        (This will most likely result in a not found)
        Now you have to copy the string between "code=" and "&scopes" and insert it to
        the "get_oauth_for_token"-method of this class. The result is the oauth_token
        you need to store in you twitch_config.py
        """
        return "https://api.twitch.tv/kraken/oauth2/authorize?client_id={clientid}&redirect_uri=http://localhost&response_type=code&scope=channel_editor+chat_login".format(clientid=self.client_id)
        
    def get_oauth_from_token(self,token):
        return requests.post("https://api.twitch.tv/kraken/oauth2/token?client_id={clientid}&client_secret={clientsecret}&code={token}&grant_type=authorization_code&redirect_uri=http://localhost".format(clientid=self.client_id,clientsecret=self.client_secret,token=token)).json()['access_token']
        
    def search_game(self, query):
        """
        Returns one matching game or None if twitch couldn't find one
        """
        result = requests.get(self.twitch_base_url+'search/games', params={'query':query, 'limit':'1'}, headers=self.get_headers()).json()
        if result['games']==None:
            return None
        else:
            return result['games'][0]

    def get_user(self, username):
        """
        Returns user for the given name or None if the given username doesn't exist
        """
        result=requests.get(self.twitch_base_url+'users', params={'login':username}, headers=self.get_headers()).json()
        if len(result['users'])==0:
            return None
        else:
            return result['users'][0]

    def get_stream(self, stream_id):
        """
        Returns a stream for the given id or None if it doesn't exist
        """
        result = requests.get(self.twitch_base_url+'streams/'+stream_id, headers=self.get_headers())
        if result.status_code != 200:
            return None
        return result.json()['stream']

    def get_community(self, name):
        """
        Get community by name
        Returns:
            The matching community, None if no is found
        """
        
        response = requests.get(self.twitch_base_url+'communities?name='+name, headers=self.get_headers())
        if response.status_code != 200:
            return None
        return response.json()
    
    def get_video(self, video_id):
        """
        Get a twitch video (highlight, past broadcast or upload) by id
        """
        response = requests.get(self.twitch_base_url+'videos/'+video_id, headers=self.get_headers())
        if response.status_code != 200:
            return None
        else:
            return response.json()

    def getfollow(self, user_id, channel_id):
        """
        Get a follow object for the given user_id and channel_id
        Params:
            user_id (str): ID of the user
            channel_id (str): ID of the channel
        Returns:
            Json returned by the twitch api, None if user
            doesn't follow the channel
        """
        response = requests.get(self.twitch_base_url+'users/{}/follows/channels/{}'.format(user_id, channel_id), headers=self.get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def getfollowers(self, user_id, limit):
        """Get the latest followers from the specified user
        Params:
            user_id (str): ID of the user
            limit (int): number of followers to display
        Returns:
            Json returned from the twitch api or None if a Error was returned
        """
        response = requests.get(self.twitch_base_url+'channels/{channel}/follows?limit={limit}'.format(channel=user_id, limit=limit), headers=self.get_headers())
        if response.status_code==200:
            return response.json()
        else:
            return None

    def set_game(self, user_id, name):
        """
        Updates the channels currently played game
        Returns:
            The Request-Response
        """
        return requests.put(self.twitch_base_url+'channels/'+user_id, data=json.dumps({"channel": {"game": name}}), headers=self.get_headers(auth=True, other_headers={'Content-Type': 'application/json'}))
    
    def set_title(self, user_id, title):
        """
        Updates the channels title
        Returns:
            The Request-Response
        """
        return requests.put(self.twitch_base_url+'channels/'+user_id, data=json.dumps({"channel": {"status": title}}), headers=self.get_headers(auth=True, other_headers={'Content-Type': 'application/json'}))

    def set_game_title(self, user_id, game, title):
        """
        Update the channels game and title
        Returns:
            The Request-Response
        """
        return requests.put(self.twitch_base_url+'channels/'+user_id, data=json.dumps({"channel": {"status": title, "game": game}}), headers=self.get_headers(auth=True, other_headers={'Content-Type': 'application/json'}))

    def set_community(self, user_id, communityid):
        """
        Update the channels Community
        Params:
            communityid (str): ID of the community
        Returns:
            The Request-Response (204 is correct status code)
        """
        return requests.put(self.twitch_base_url+'channels/'+user_id+'/community/'+communityid, headers=self.get_headers(auth=True))
        
    def remove_community(self, user_id):
        """
        Update the channels Community
        Params:
            communityid (str): ID of the community
        Returns:
            The Request-Response (204 is correct status code)
        """
        return requests.delete(self.twitch_base_url+'channels/'+user_id+'/community', headers=self.get_headers(auth=True))
