from supybot.commands import *
from random import choice
import supybot.callbacks as callbacks

class Fixit(callbacks.Plugin):

    verbs = ['attackclone', 'bootstrap', 'tweetybird', 'architect', 
           'merge', 'compile', 'boilerstrap', 'git push', 'fork',
           'configure', 'hash', 'salt', 'commit', 'echo', 'version',
           'create value for', 'facet', 're-index', 'relevance-rank',
           'monkeypatch', 'scrape', 'install', 'mashup', 'integrate',
           'snippet', 'wikify', 'network', 'proxy', 'toggle', 'reboot',
           'visualize', 'federate', 'curate', 'gamify', 'crowdsource',
           'scale up', 'cloud-host', 'progressively enhance', 
           'open-source', 'havisham', 'refactor', 'empower',
           'continuously deploy', 'inject', 'mock', 'BBM me',
           'face-time', 'migrate', 'nextgen', 'panoramically photograph',
           'SMS', 'shibbolize', 'hack', 'munge', 'yak-shave', 'rebase',
           'polish', 'fastfail', 'serialize', 'queue up', 'shard',
           'replicate', 'index', 'transliterate', 'subclass',
           'superclass', 'catalog', 'interleave', 'mesh'
    ]
    
    nouns = ['framework', 'html5', 'rubygem', 'shawarma', 'web app', 
           'nodefiddle', 'node.js', 'responsive design', 'SSID',
           'Apache', 'command line', 'supybot', 'repo', 'regexp',
           'model instance', 'heroku', 'EC2 instance', 'Islandora',
           'lambda function', 'RESTful JSON API', 'Solr', 'cloud', 
           'data', 'Drupal module', 'OAI-PMH', 'metadata', 'schema',
           'Blacklight', 'tweetybird', 'social media', 'backbone',
           'cross-universe compatibility', 'boilerstrap', 'html9',
           'beautifulsoup', 'failwhale', 'mashup', 'cookie', 'dongle',
           'discovery layer', 'architecture', 'github', 'zoia',
           'jquery', 'network', 'transistor', 'PDP-11', 'Fortran',
           'analytics', 'Z39.50', 'skunkworks', 'hadoop', 'persona',
           'web scale cloud ILS', 'scalability', 'singularity',
           'semantic web', 'triplestore', 'SFX', 'Fedora', 'Umlaut',
           u'\xdcml\xe4\xfct', 'pip', 'AbstractSingletonProxyFactoryBean',
           'platform', 'persistent database', 'user', 'Cucumber',
           'beans', 'analytics', 'bitcoin', 'test harness', 
           'unit tests', 'dependency', 'QR codes', 'plugin','backend',
           'frontend','middleware','CAS', 'robots', 'robots.txt',
           'hackfest', 'encoding', 'utf8', 'MARC8', 'pumpkins', 
           'pumpkin patch', 'turd', 'web hook', 'callback', 'shard',
           'hydra head', 'fulltext', 'diacritics', 'EAD',
           'Mechanical Turk', 'quine relay', 'INTERCAL', 'mesh network',
           'octothorpe', 'time machine'
    ]
    
    def fixit(self, irc, msg, args):
      """
      Get advice for solving your intractable tech problems.
      """
      
      verb = choice(self.verbs)
      object = choice(self.nouns)
      tool = choice(self.nouns)
      advice = "Just "+verb+" the "+object+" with your "+tool+"."
      irc.reply(advice, prefixNick=True)

    def mynewstartup(self, irc, msg, args, who):
      """
      Your new business plan.  It is genius.  It cannot fail.
      """
      
      if who is None:
        owner = "Your"
      else:
        owner = "%s's" % who

      verb = choice(self.verbs)
      simile = choice(self.nouns)
      awesomesauce = choice(self.nouns)
      
      if simile[0] in ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']:
        article = " an "
      else:
        article = " a "
      genius_plan = "%s new startup? It's like%s%s, but you %s it with your %s" % (owner, article, simile, verb, awesomesauce)
      irc.reply(genius_plan, prefixNick=True)

    mynewstartup = wrap(mynewstartup, [ optional('text') ])
    startup = mynewstartup
    
Class = Fixit
