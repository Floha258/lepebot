import db_helper

#Idea: store settings in the database and NOT in a static file (file is left there for backwards compatibility)
#Table sheme: module (TEXT) | key (TEXT) | value (TEXT)

class Setting:
    def __init__(self, module, key, value=None):
        self.module=module
        self.key=key
        self.value=value
    
    @staticmethod
    def from_db_row(dbrow):
        return Setting(dbrow[0], dbrow[1], dbrow[2])

    def __lt__(self, other):
        return (self.module, self.key, self.value)<(other.module, other.key, other.value)

    def __le__(self, other):
        return (self.module, self.key, self.value)<=(other.module, other.key, other.value)

    def __eq__(self, other):
        return (self.module, self.key, self.value)==(other.module, other.key, other.value)

    def __ne__(self, other):
        return (self.module, self.key, self.value)!=(other.module, other.key, other.value)

    def __gt__(self, other):
        return (self.module, self.key, self.value)>(other.module, other.key, other.value)

    def __ge__(self, other):
        return (self.module, self.key, self.value)>=(other.module, other.key, other.value)

    def keygt(self, other):
        return (self.module, self.key)>(other.module, other.key)

    def keylt(self, other):
        return (self.module, self.key)<(other.module, other.key)
    
    def keyeq(self, other):
        return (self.module, self.key)==(other.module, other.key)

    def __str__(self):
        return 'Module: {}, Key: {}, Value: {}'.format(self.module, self.key, self.value)

CREATE_TABLE_STATEMENT='CREATE TABLE IF NOT EXISTS `settings` ( `module` TEXT NOT NULL, `key` TEXT NOT NULL, `value` TEXT, PRIMARY KEY(`module`,`key`) )'
INSERT_STATEMENT='INSERT INTO `settings`(`module`,`key`,`value`) VALUES (?,?,?)'
UPDATE_STATEMENT='UPDATE `settings` SET `value`=? WHERE `module`=? AND `key`=?'
REPLACE_STATEMENT='REPLACE INTO `settings` (`module`,`key`,`value`) VALUES (?,?,?)'
DELETE_STATEMENT='DELETE FROM `settings` WHERE `module`=? AND `key`=?'
SELECT_FOR_MODULE_KEY='SELECT * FROM `settings` WHERE `module`=? AND `key`=?'
SELECT_FOR_MODULE='SELECT * FROM `settings` WHERE `module`=?'
SELECT_ALL='SELECT * FROM `settings`'

def db_create_table():
    db_helper.execute(CREATE_TABLE_STATEMENT)

def db_insert_setting(setting):
    """
    Args:
        setting (Setting): The setting to insert into the database
    """
    db_helper.execute(INSERT_STATEMENT, (setting.module, setting.key, setting.value))

def db_update_setting(setting):
    """
    Args:
        setting (Setting): The setting to update in the database (if it exists, nothing happens otherwise)
    """
    db_helper.execute(UPDATE_STATEMENT, (setting.value, setting.module, setting.key))

def db_replace_setting(setting):
    """
    Args:
        setting (Setting): The setting to replace in the database
    """
    db_helper.execute(REPLACE_STATEMENT, (setting.module, setting.key, setting.value))

def db_delete_setting(setting):
    """
    Args:
        setting (Setting): The setting that is deleted
    """
    db_helper.execute(DELETE_STATEMENT, (setting.module, setting.key))
    
def db_select_for_module_key(module, key):
    """
    Args:
        module (str): The module name from the setting to load
        key (str): The key name from the setting to load
    Returns:
        (Setting): The matching setting or None
    """
    result=db_helper.fetchall(SELECT_FOR_MODULE_KEY, (module, key))
    if len(result)==0:
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
    result=db_helper.fetchall(SELECT_FOR_MODULE, (module,))
    return list(map(Setting.from_db_row, result))

def db_select_all():
    """
    Returns:
        list(Setting): List of all Settings
    """
    result=db_helper.fetchall(SELECT_ALL)
    return list(map(Setting.from_db_row, result))

def generate_diff(oldlist, newlist):
    """Generates the differences between two lists of settings
    Args:
        oldlist(list:Settings): List of the old settings
        newlist(list:Settings): List of the new settings
    Returns:
        list(tuple): return a list of tuples, including the old and the new Setting if they changed,
                     if a new setting was created (None, newsetting) is in the list"""
    sortedold=sorted(oldlist)
    sortednew=sorted(newlist)
    oldindex=0
    newindex=0
    difflist=[]
    while True:
        if oldindex>=len(oldlist):
            for setting in sortednew[newindex:]:
                difflist.append((None,setting))
            break

        if newindex>=len(newlist):
            for setting in sortedold[oldindex:]:
                difflist.append((setting,None))
            break

        if sortedold[oldindex].keygt(sortednew[newindex]):
            difflist.append((None,sortednew[newindex]))
            newindex+=1
            continue

        if sortedold[oldindex].keylt(sortednew[newindex]):
            difflist.append((sortedold[oldindex],None))
            oldindex+=1
            continue

        if sortedold[oldindex].value!=sortednew[newindex].value:
            difflist.append((sortedold[oldindex],sortednew[newindex]))
        oldindex+=1
        newindex+=1
    return difflist
