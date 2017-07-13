import requests
from datetime import timedelta
from .empty_component import EmptyComponent as _EC
from util import format_time

class Component(_EC):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(self.config)
        self.default_param=self.config['default-param']
    
    def load(self):
        def wr(channel, username, tags, message):
            self.irc.sendprivmsg(channel,self.getwrstr(message))
        self.bot.register_privmsg_command('wr',wr)
        def gamesearch(channel, username, tags, message):
            self.irc.sendprivmsg(channel,self.srgamesearch(message))
        self.bot.register_privmsg_command('searchgame',gamesearch)
        def srcurrent(channel, username, tags, message):
            self.default_param=message
        self.bot.register_privmsg_command('srcurrent',srcurrent,mod_only=True)
    
    def getwrstr(self, params):
        """Returns the wrstring from the given command"""
        params=params.strip()
        if len(params)==0:
            params=self.default_param
        game, cat, varis = parse_game_cat_var_cached(params)
        if game == None:
            return 'Game not found'
        if cat == None:
            return 'Availiable categories are: '+', '.join(cate.name for cate in game.categories)
        name, time=getwr(game.id, cat.id, varis)
        if name==None:
            return 'No record'
        varstring=','.join(var.name+':'+val[1] for var, val in varis)
        if varstring != '':
            varstring='('+varstring+')'
        return 'The wr for '+game.name+': '+cat.name+' '+varstring+' is '+time+' by '+name
    
    def srgamesearch(self, query):
        """
        Search for max 5 Games by a query to get the name and the abbreviation
        """
        games=searchgame(query)
        if len(games)==0:
            return 'No Game found'
        else:
            return ', '.join(name + '(' + abb + ')' for name, abb in games)
        
    def unload(self):
        self.bot.unregister_privmsg_command('wr')
        self.bot.unregister_privmsg_command('searchgame')
        self.bot.unregister_privmsg_command('srcurrent')

gamecache={}

class Variable:
    def __init__(self, data):
        self.name=data["name"].lower()
        self.id=data["id"]
        self.default=data["values"]["default"]
        self.scope=data["scope"]["type"]
        self.category=data["category"]
        self.values=[(value[0],value[1]['label'].lower()) for value in data["values"]["values"].items()]
    
    def __repr__(self):
        return self.name+' '+str(self.values)

class Category:
    def __init__(self, data):
        self.name=data["name"].lower()
        self.id=data["id"]
        self.variables=[]

class Game:
    def __init__(self, data):
        self.name=data["names"]["international"]
        self.id=data["id"]
        self.abbreveation=data["abbreviation"].lower()
        #Only include categories for the game and not for levels
        self.categories=[Category(catdata) for catdata in data["categories"]["data"] if catdata['type']=='per-game']
        self.variables=[]
        for var in data["variables"]["data"]:
            variable=Variable(var)
            #Include varibles for the whole game here
            if variable.category == None and (variable.scope == 'global' or variable.scope == 'full-game'):
                self.variables.append(variable)
            else:
                #Variables for individual categories
                for cat in self.categories:
                    if cat.id == variable.id:
                        cat.variables.append(variable)
                        break

def searchgame(query):
    """
    Searches sppedrun.com games for the given string
    Returns:
        list of (gamename, gameabbreviation)
    """
    response=_requests_get_srcomapi('games', params={'_bulk':1,'name':query,'max':5})
    return [(game['names']['international'],game['abbreviation']) for game in response.json()['data']]
    

def getgamecached(gameabb):
    """Returns a Game-object that is either cached or retrieved from speedrun.com"""
    if gameabb in gamecache:
        return gamecache[gameabb]
    else:
        response = _requests_get_srcomapi('games/{abb}?embed=variables,categories'.format(abb=gameabb))
        if response.status_code == 200:
            game=Game(response.json()['data'])
            gamecache[gameabb]=game
            return game
        else:
            return None

def parse_game_cat_var_cached(toparse):
    """Parses the input and returns a game, a categorie and given variables,
    but can also just return a game or a game and a category
    Params:
        toparse (str): gameabbreviation followed by an optional category and ';'
            followed by optional and multiple ';'-seperated variable-pairs like variablename:variablevalue.
            Example: BotW All Dungeons; Amiibo:No Amiibo
    Returns:
        Game, Category, list of (Variable, (valueid, valuename))
    """ 
    if len(toparse)==0:
        return None, None, None
    split=toparse.split(' ',1)
    gameabb=split[0]
    game=getgamecached(gameabb)
    if game == None:
        return None, None, None
    if len(split)==1:
        return game, None, None
    split=split[1].split(";")
    catname=split[0]
    for cat in game.categories:
        if cat.name.lower()==catname.lower():
            category=cat
            break
    else:
        return game, None, None
    #parse variables
    variables=list()
    for varpart in split[1:]:
        varname, varvalue = varpart.split(':')
        varname=varname.strip().lower()
        varvalue=varvalue.strip().lower()
        found=_varsearch(game.variables, varname, varvalue)
        if found != None:
            variables.append(found)
        else:
            found=_varsearch(category.variables, varname, varvalue)
            if found != None:
                variables.append(found)
         
    return game, category, variables

def getwr(gameid, categoryid, variables):
    """
    Get the wr for a category in a game with variables
    Params:
        gameid (str): ID of the game
        categoryid (str): ID of the category
        variables (list of (Variable, (valueid, valuename))): Variables to include, can be an empty list
    Returns:
        name(str), time(str)
        Name of the runner and the time
    """
    varstring=''
    for var, val in variables:
        varstring+='&var-'+var.id+'='+val[0]
    response=_requests_get_srcomapi('leaderboards/{gameid}/category/{catid}?top=1&embed=players{vars}'.format(gameid=gameid,catid=categoryid,vars=varstring))
    if response.status_code != 200:
        return None, None
    data=response.json()['data']
    if len(data['runs'])==0:
        return None, None
    run=data['runs'][0]['run']
    time=run['times']['primary_t']
    formated_time=format_time(time)
    player=data['players']['data'][0]
    if player['rel']=='guest':
        name=player['name']
    else:
        name=player['names']['international']
    return name, formated_time

def _varsearch(varis, varname, varvalue):
    for var in varis:
        if var.name==varname:
            for val in var.values:
                if val[1]==varvalue:
                    return (var, val)
    return None

def _requests_get_srcomapi(url, **kwargs):
    """
    Sends a requests to the srcomapi, (prefixed with speedrun.com/api/v1/)
    returns the result from requests
    """
    return requests.get('http://www.speedrun.com/api/v1/'+url, headers={'User-Agent':'lepebot/17.42.99'},**kwargs)
