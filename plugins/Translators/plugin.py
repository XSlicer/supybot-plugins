import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import re

class Translators(callbacks.Privmsg):
    def canuck(self, irc, msg, args):
        """translates text into a Canadian dialect
        """
        text = ' '.join(args)
        text = re.sub(r'out', 'oat', text)
        text = re.sub(r'ouch', 'oach', text)
        text = re.sub(r'ache', 'awchee', text)
        irc.reply(text + "  eh?", prefixNick=True)

    def mccainize(self, irc, msg, args):
        """translates text into McCain speechifyin'
        """
        irc.reply(re.sub(r'^', 'my friends, ', ' '.join(args)), prefixNick=True)

    def dick(self, irc, msg, args):
        """disclaims your desire to be a dick
        """
        #irc.reply("whatever d00d", prefixNick=True)
        irc.reply("I don't mean to be a dick, but " + ' '.join(args), prefixNick=True)
        
    def edsu(self, irc, msg, args):
        """states edsu's attitude on selfsame plugin command
        """
        irc.reply("edsu finds this supremely annoying, but " + ' '.join(args), prefixNick=True)

    def mjg(self, irc, msg, args):
        """truncates your statement and steers it towards delicious pork products
        """
        irc.reply("%s... OMG! Bacon!" % ' '.join(args)[:20])
        

Class = Translators

