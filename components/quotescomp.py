# Component for adding/managing and randomly showing quotes
from .empty_component import EmptyComponent as _EC
import db_helper
import datetime
import random


class Component(_EC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(self, config):
        db_create_table()
        try:
            self.cooldown = int(config['cooldown'])
        except ValueError:
            self.cooldown = 20

        def _addquote(channel, username, tags, message):
            daynow = '{0:%d.%m.%Y}'.format(datetime.datetime.now())
            quote = Quote(None, message, daynow)
            db_save_quote(quote)
            self.bot.irc.sendprivmsg(
                self.bot.channel,
                'Succesfully saved quote {}'.format(quote.qid))
        self.bot.register_privmsg_command('addquote', _addquote,
                                          mod_only=True, enabled=True)

        def _delquote(channel, username, tags, message):
            try:
                quotenum = int(message)
            except ValueError:
                self.bot.irc.sendprivmsg(self.bot.channel,
                                         'Not a valid number')
            db_delete_quote(quotenum)
            self.bot.irc.sendprivmsg(self.bot.channel,
                    'Succesfully deleted quote #{}'.format(quotenum))
        self.bot.register_privmsg_command('delquote', _delquote,
                                          mod_only=True, enabled=True)

        def _randquote():
            quotecount = db_helper.fetchall(
                'SELECT COUNT(*) FROM `quotes`')[0][0]
            if quotecount == 0:
                return 'No quotes found'
            # Get the quote at a specific position
            quote = Quote.from_db_row(db_helper.fetchall(
                'SELECT * FROM `quotes` LIMIT 1 OFFSET ?',
                (random.randrange(0, quotecount),))[0])
            return _presentquote(quote)

        def _presentquote(quote):
            return '{} [{}]'.format(quote.quote, quote.date)

        def _getquote(channel, username, tags, message):
            if len(message) == 0:
                # get random quote
                self.bot.irc.sendprivmsg(self.bot.channel,
                                         _randquote())
            else:
                try:
                    quotenum = int(message)
                except ValueError:
                    self.bot.irc.sendprivmsg(self.bot.channel,
                                             _randquote())
                quote = db_select_one(quotenum)
                if quote is None:
                    self.bot.irc.sendprivmsg(self.bot.channel,
                                             'Quote not found')
                else:
                    self.bot.irc.sendprivmsg(self.bot.channel,
                                             _presentquote(quote))

        self.bot.register_privmsg_command('quote', _getquote,
                      channel_cooldown=self.cooldown, enabled=True)

    def unload(self):
        self.bot.unregister_privmsg_command('addquote')
        self.bot.unregister_privmsg_command('delquote')
        self.bot.unregister_privmsg_command('quote')

    def get_default_settings(self):
        return {'cooldown': '20'}

    def on_update_settings(self, keys, settings):
        if 'cooldown' in keys:
            try:
                self.cooldown = int(settings['cooldown'])
                quotecommand = self.bot.commands_helper.get_privmsgcommand('quote').channel_cooldown = self.cooldown
            except ValueError:
                pass


class Quote:
    """Class to represent a quote"""

    def __init__(self, qid, quote, date):
        """
        Args:
            qid (int): ID of the quote, set to None for a new quote
            quote (str): Text of the quote ('"haha funny" -nobody')
            date (str): Date the quote was submitted
        """
        self.qid = qid
        self.quote = quote
        self.date = date

    @staticmethod
    def from_db_row(dbrow):
        return Quote(dbrow[0], dbrow[1], dbrow[2])


CREATE_TABLE_STATEMENT = 'CREATE TABLE IF NOT EXISTS `quotes`(' +\
    '`id` INTEGER PRIMARY KEY AUTOINCREMENT, `quote_text` TEXT NOT NULL,' +\
    '`creation_date` TEXT )'

INSERT_TABLE_STATEMENT = 'INSERT INTO `quotes` ' +\
    '(`quote_text`,`creation_date`) VALUES (?,?)'

UPDATE_TABLE_STATEMENT = 'UPDATE `quotes` SET `quote_text`=?,' +\
    '`creation_date`=? WHERE `id`=?'

DELETE_STATEMENT = 'DELETE FROM `quotes` WHERE `id`=?'

SELECT_ALL_STATEMENT = 'SELECT * FROM `quotes`'

SELECT_ONE_STATEMENT = 'SELECT * FROM `quotes` WHERE `id`=?'


def db_create_table():
    db_helper.execute(CREATE_TABLE_STATEMENT)


def db_save_quote(quote):
    """Save the quote, either adds a new quote or
    updates an existing one, based on if the
    qid is None"""
    if quote.qid is None:
        newid = db_helper.execute_return_id(INSERT_TABLE_STATEMENT,
                    (quote.quote, quote.date))
        quote.qid = newid
    else:
        db_helper.execute(UPDATE_TABLE_STATEMENT,
                    (quote.quote, quote.date, quote.qid))


def db_delete_quote(quoteid):
    """Delete a quote based on the given ID (int)"""
    db_helper.execute(DELETE_STATEMENT, (quoteid,))


def db_select_all():
    """Get all quotes in the database"""
    rawquotes = db_helper.fetchall(SELECT_ALL_STATEMENT)
    if rawquotes is None:
        return []
    else:
        return [Quote.from_db_row(row) for row in rawquotes]


def db_select_one(qid):
    """Select the specified quote by the id"""
    rawquote = db_helper.fetchall(SELECT_ONE_STATEMENT, (qid,))
    if rawquote is None or len(rawquote) == 0:
        return None
    else:
        return Quote.from_db_row(rawquote[0])
