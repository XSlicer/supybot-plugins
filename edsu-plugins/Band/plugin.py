"""
Get a band name from Dan's band name list:
"""

import supybot

__revision__ = "$Id$"
__author__ = supybot.authors.unknown
__contributors__ = {}


import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.registry as registry
import supybot.callbacks as callbacks

from urllib import urlencode
from urllib2 import urlopen 
from sgmllib import SGMLParser
from random import randint
from os.path import join, dirname, abspath
import simplejson

def configure(advanced):
    # This will be called by setup.py to configure this module.  Advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Band', True)


conf.registerPlugin('Band')
# This is where your configuration variables (if any) should go.

class Parser ( SGMLParser ): 

    inside = False
    bands = []

    def start_pre(self, attrs):
        self.inside = True

    def end_span(self):
        self.inside = False

    def handle_data(self,data):
        if self.inside:
            bands = data.split("\n")
            for band in bands: 
                self.bands.append(band)

class Band(callbacks.Privmsg):

    def band(self,irc,msg,args):
        """ 
        Get a band name from dchud's list: http://www-personal.umich.edu/~dchud/fng/names.html
        """

        url = urlopen("http://www-personal.umich.edu/~dchud/fng/names.html")
        html = url.read()

        parser = Parser()
        parser.feed(html)

        band = parser.bands[randint(0,len(parser.bands)-1)]
        irc.reply(band)

    def newband(self, irc, msg, args):
        """[add {NEW_BAND}]
        Get a band name from dchud's (cached, JSONified) list or add to the list
        """
        f = join(dirname(abspath(__file__)), 'bands.json')
        jsonfile = open(f, 'r')
        json = simplejson.load(jsonfile)
        jsonfile.close()
        if args[0] == 'add' and len(args) > 1:
            new_band = ' '.join(args[1:]).strip()
            json['bands'].append(new_band)
            jsonfile = open(f, 'w')
            simplejson.dump(json, jsonfile, indent=4)
            jsonfile.close()
            irc.reply("Band '%s' added to list" % new_band, prefixNick=True)
        else:
            band = json['bands'][randint(0, len(json['bands'])-1)]
            irc.reply(band, prefixNick=True)

Class = Band 

# vim:set shiftwidth=4 tabstop=8 expandtab textwidth=78:
