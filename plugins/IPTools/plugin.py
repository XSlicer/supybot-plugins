###
# Copyright (c) 2009, Michael B. Klein
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import xml.etree.ElementTree as ET
from urllib2 import urlopen
from socket import gethostbyname

class IPTools(callbacks.Plugin):
    """IP address utilities."""
    
    def locate(self, irc, msg, args, ip):
      """<ip> - Looks up geolocation information about the given 
      IP address from http://www.ip-adress.com/ip_tracer/"""

      tree = ET.parse(urlopen('http://freegeoip.net/xml/' + ip))
      root = tree.getroot()
      
      irc.reply("Country: " + root[2].text + ", State/Province: " + \
                root[4].text + ", City: " + root[5].text + ", ZIP: " + \
                root[6].text,prefixNick=True)
    locate = wrap(locate, ['ip'])
    
    def lookup(self, irc, msg, args, hostname):
      """<hostname> - Looks up the IP address of a hostname"""
      
      try:
        irc.reply(gethostbyname(hostname),prefixNick=True)
      except:
        irc.reply('Unknown host: ' + hostname,prefixNick=True)
    lookup = wrap(lookup, ['text'])
      
Class = IPTools


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
