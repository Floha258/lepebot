import db_helper
import json


# Idea: store settings in the database and NOT in a static file (file is left there for backwards compatibility)
# Table sheme: module (TEXT) | key (TEXT) | value (TEXT)

class Setting:
    def __init__(self, module, key, value=None):
        self.module = module
        self.key = key
        self.value = value

    @staticmethod
    def from_db_row(component, settings):
        for key, value in settings.items:
            return Setting(component, key, value)

    def __lt__(self, other):
        return (self.module, self.value) < (other.module, other.value)

    def __le__(self, other):
        return (self.module, self.value) <= (other.module, other.value)

    def __eq__(self, other):
        return (self.module, self.value) == (other.module, other.value)

    def __ne__(self, other):
        return (self.module, self.value) != (other.module, other.value)

    def __gt__(self, other):
        return (self.module, self.value) > (other.module, other.value)

    def __ge__(self, other):
        return (self.module, self.value) >= (other.module, other.value)

    def __str__(self):
        return 'Module: {}, Value: {}'.format(self.module, self.value)


INSERT_STATEMENT = 'INSERT INTO `settings`(`module`,`key`,`value`) VALUES (?,?,?)'
UPDATE_STATEMENT = 'UPDATE `settings` SET `value`=? WHERE `module`=? AND `key`=?'
REPLACE_STATEMENT = 'REPLACE INTO `settings` (`module`,`key`,`value`) VALUES (?,?,?)'
DELETE_STATEMENT = 'DELETE FROM `settings` WHERE `module`=? AND `key`=?'
SELECT_FOR_MODULE_KEY = 'SELECT * FROM `settings` WHERE `module`=? AND `key`=?'
SELECT_FOR_MODULE = 'SELECT * FROM `settings` WHERE `module`=?'
SELECT_ALL = 'SELECT * FROM `settings`'


def db_create_table():
    with open("db.json", x) as file:
        file.write(json.dumps(
            {
                "settings":
                    {}
            }
        ))


def db_read_json():
    """
    reads the json
    Returns:
        A dictionary of the read json
    """

    with open("db.json", r) as file:
        return json.load(file)

def db_write_json(db):
    """
    writes a given dictionary to the json file
    Args:
        db (Dictionary): A dictionary of the database to write to the json file
    """

    with open("db.json", x) as file:
        json.dumps(db)
        return True
    print("Could not write to db file, something went wrong: JSON to write {}".format(dic))
    return


def db_insert_setting(setting):
    """
    Args:
        setting (Setting): The setting to insert into the database
    """

    dic = db_read_json()
    settings = dic["settings"]
    if setting.module in settings:
        comp = settings[setting.module]
        comp[setting.key] = setting.value
    else:
        comp = dic()
        comp[setting.key] = setting.value
    settings[setting.module] = comp
    dic["settings"] = settings
    db_write_json(dic)
    # db_helper.execute(INSERT_STATEMENT, (setting.module, setting.value))


def db_update_setting(setting):
    """
    Args:
        setting (Setting): The setting to update in the database (if it exists, nothing happens otherwise)
    """
    db_helper.execute(UPDATE_STATEMENT, (setting.value, setting.module))


def db_replace_setting(setting):
    """
    Args:
        setting (Setting): The setting to replace in the database
    """
    db_helper.execute(REPLACE_STATEMENT, (setting.module, setting.value))


def db_delete_setting(setting):
    """
    Args:
        setting (Setting): The setting that is deleted
    """
    db_helper.execute(DELETE_STATEMENT, setting.module)


def db_select_for_module_key(module, key):
    """
    Args:
        module (str): The module name from the setting to load
        key (str): The key name from the setting to load
    Returns:
        (Setting): The matching setting or None
    """
    result = db_helper.fetchall(SELECT_FOR_MODULE_KEY, module)
    if len(result) == 0:
        return None
    else:
        return Setting.from_db_row(result[0])


def db_select_for_module(module):
    """
    Args:
        module (str): The module name from the setting to load
    Returns:
        list(Setting): List of all matching Settings
    """
    result = db_helper.fetchall(SELECT_FOR_MODULE, (module,))
    return list(map(Setting.from_db_row, result))


def db_select_all():
    """
    Returns:
        list(Setting): List of all Settings
    """
    with open("db.json", r) as file:
        result = json.load(file).settings
    allsettings = list()
    for component, settings in result["settings"]:
        allsettings.append(Setting.from_db_row(component, settings))
    return allsettings
    #return list(map(Setting.from_db_row, result["settings"]))


def generate_diff(olddic, newdic):
    """Generates the differences between two lists of settings
    Args:
        oldlist(list:Settings): Dic of the old settings
        newlist(list:Settings): Dic of the new settings
    Returns:
        list(tuple): return a list of tuples, including the old and the new Setting if they changed,
                     if a new setting was created (None, newsetting) is in the list"""

    # Converting Dics into list for comparison
    oldlist = []
    for component, settings in olddic.items:
        for key, value in settings.items:
            oldlist.append(Setting(component, key, value))

    newlist = []
    for component, settings in newdic.items:
        for key, value in settings.items:
            newlist.append(Setting(component, key, value))

    sortedold = sorted(oldlist)
    sortednew = sorted(newlist)
    oldindex = 0
    newindex = 0
    difflist = []
    while True:
        if oldindex >= len(oldlist):
            for setting in sortednew[newindex:]:
                difflist.append((None, setting))
            break

        if newindex >= len(newlist):
            for setting in sortedold[oldindex:]:
                difflist.append((setting, None))
            break

        if sortedold[oldindex]['key'] > sortednew[newindex]['key']:
            difflist.append((None, sortednew[newindex]))
            newindex += 1
            continue

        if sortedold[oldindex]['key'] < sortednew[newindex]['key']:
            difflist.append((sortedold[oldindex], None))
            oldindex += 1
            continue

        if sortedold[oldindex].value != sortednew[newindex].value:
            difflist.append((sortedold[oldindex], sortednew[newindex]))
        oldindex += 1
        newindex += 1
    return difflist
