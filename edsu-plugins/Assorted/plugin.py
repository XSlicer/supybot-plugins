# coding=utf-8

import feedparser
import math
import os
import random
import re
import simplejson
import time
import lxml
import upsidedown
from os.path import join, abspath, dirname
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, StopParsing
from cgi import parse_qs
from datetime import date, datetime
from elementtidy import TidyHTMLTreeBuilder
from int2word import int2word
from random import randint, choice, seed
from urllib import quote, urlencode
from urllib2 import urlopen, urlparse, Request, build_opener, HTTPError
from urlparse import urlparse
from threading import Timer
import csv

from supybot.commands import *
import supybot.callbacks as callbacks

from beck import BeckGenerator
import sheendata

class PollNotFoundException(Exception):
    pass


class Assorted(callbacks.Privmsg):

    def devil(self,irc,msg,args):
        """fetch a random entry from the devil's dictionary at
        http://www.eod.com/devil/archive/ 
        """
        base = 'http://www.eod.com'
        ns = 'http://www.w3.org/1999/xhtml'
        tree = TidyHTMLTreeBuilder.parse(urlopen(base+'/devil/archive/'))

        def is_entry(a):
            if a.attrib.has_key('href') \
                and '/devil/archive/' in a.attrib['href']:
                return True
            return False

        anchors = filter(is_entry, tree.findall('.//{%s}a' % ns))
        anchor = anchors[randint(0, len(anchors)-1)]

        tree = TidyHTMLTreeBuilder.parse(urlopen(base+anchor.attrib['href']))
        word = tree.find('.//{%s}strong' % ns).text

        paras = tree.findall('.//{%(ns)s}blockquote/{%(ns)s}p' % {'ns': ns})
        irc.reply("%s - %s" % (word, paras[0].text.encode('utf8','ignore')))


    def underbelly(self,irc,msg,args):
        """access2005 podcast downloads today
        """
        text = urlopen("http://access2005.library.ualberta.ca/podcast-stats.txt").read().strip()
        irc.reply(text)

    def runoff(self,irc,msg,args):
        """polls code4libcon 2007 runoff votes
        """
        results = self.get_votes(122)
        irc.reply('; '.join(results).encode('utf8'))

    def tshirts(self,irc,msg,args):
        """code4libcon 2007 tshirt votes
        """
        results = self.get_votes(150)
        irc.reply('; '.join(results).encode('utf8'))
    
    def tshirters(self,irc,msg,args):
        """code4libcon 2007 tshirt voters
        """
        results = self.get_voters(150)
        irc.reply(("[%i voters] " % len(results)) + 
            '; '.join(results).encode('utf8'))

    def hosts2008(self,irc,msg,args):
        """code4libcon 2008 host site votes
        """
        results = self.get_votes(164)
        irc.reply('; '.join(results).encode('utf8', 'ignore'))
    
    def hosters(self,irc,msg,args):
        """code4libcon 2008 host site voters
        """
        results = self.get_voters(164)
        irc.reply(("[%i voters] " % len(results)) + 
            '; '.join(results).encode('utf8'))
 
    def votes2007(self,irc,msg,args):
        """polls code4libcon 2007 votes
        """
        results = self.get_votes(120)
        irc.reply('; '.join(results).encode('utf8'))

#    def keynotes2013(self,irc,msg,args):
#      """votes for the 2011 code4libcon keynote 
#      """
#      keynotes = [
#        "Estelle Getty", "Sylvester Stallone", "Yngwie Malmsteen",
#        "Andy Dick", "U. Rex Dumdum", "Michael J. Giarlo", "Ron Paul",
#        "Bacon Salt", "Zoia", "Ima Hogg", "Mark Lemongello", "'anon'",
#        "Trout Fishing in America", "Freddie Skunkcap", "Dick Assman",
#        "Rooster McConaughey", "Hacker John", "Ace Waterwheels"
#      ]
#      n = randint(3,8)
#      people = [keynotes.pop(randint(0, len(keynotes)-1)) for i in range(n)]
#      votes = [randint(1,100) for a in range(0,n)]
#      votes.sort(lambda a,b: cmp(b,a))
#      results = zip(people,votes)
#      msg = ["%s [%i]" % (result[0], result[1]) for result in results]
#      irc.reply('; '.join(msg))

    def hosts2013(self,irc,msg,args):
      """ 
      Shows votes for the next code4libcon. Courtesy of 
      http://www.floydpinkerton.net/fun/citynames.html
      """
      places = [
        "Aces of Diamonds, Florida", "Fearnot, Pennsylvania", "Normal, Illinois",
        "Assawoman, Virginia", "Fifty-Six, Arkansas", "Odd, West Virginia",
        "Bald Head, Maine", "Forks of Salmon, California", "Ogle, Kentucky",
        "Beetown, Wisconsin", "Fort Dick, California", "Okay, Oklahoma",
        "Belcher, New York", "Frankenstein, Missouri", "Panic, Pennsylvania",
        "Ben Hur, Texas", "Footville, Wisconsin", "Peculiar, Missouri",
        "Big Foot, Illinois", "Gaylordsville, Connecticut", "Plain City, Utah",
        "Big Sandy, Wyoming", "Gay Mills, Wisconsin", "Porkey, Pennsylvanania",
        "Blueballs, Pennsylvania", "Gun Barrel City, Texas", "Quiggleville, Pennsylvania",
        "Boring, Maryland", "Hell, Michigan", "Rambo Riviera, Arkansas",
        "Bivalve, California", "Boring, Oregon", "Hicksville, Ohio", "River Styx, Ohio",
        "Buddha, Indiana", "Hooker, Arkansas", "Roachtown, Illinois",
        "Chestnut, Illinois", "Hooker, Oklahoma", "Romance, Arkansas",
        "Chicken, Alaska", "Hornytown, North Carolina", "Rough and Ready, California",
        "Chocalate Bayou, Texas", "Hot Coffee, Mississippi", "Sand Draw, Wyoming",
        "Chugwater, Wyoming", "Hot Water, Mississippi", "Sandwich, Illinois",
        "Climax, North Carolina", "Intercourse, Pennsylvania", "Smackover, Arkansas",
        "Climax, Pennsylvania", "It, Mississippi", "Spread Eagle, Wisconsin",
        "Climax, Saskatchewan", "Jupiter, Florida", "Toad Suck, Arkansas",
        "Cold Foot, Alaska", "Kill Devil Hills, North Carolina", "Umpire, Arkansas",
        "Cold Water, Mississippi", "King Arthur's Court, Michigan", "Uncertain, Texas",
        "Cut-Off, Louisiana", "Koopa, Colorado", "Yazoo, Mississippi",
        "Dickeyville, Wisconsin", "Lawyersville, New York", "Yeehaw Junction, Florida",
        "Ding Dong, Texas", "Lollipop, Texas", 
        "Disco, Tennessee", "Love Ladies, New Jersey", 
        "Dismal, Tennessee", "Magazine, Arkansas", 
        "Dry Fork, Wyoming", "Mars, Pennsylvania", 
        "Eclectic, Alabama", "Monkey's Elbow, Kentucky", 
        "Eek, Alaska", "Muck City, Alabama", 
        "Embarrass, Minnesota", "No Name, Colorado",
        "Gross, Nebraska", "Leaksville-Spray, North Carolina",
        "Poison, Montana", "Dingle, Idaho", "Liberal, Kansas",
      ]
      def rand_places(num, seen=None):
        if seen == None: 
          seen = []
        if num == 0:
          return []
        place = places[randint(0, len(places)-1)]
        if place in seen:
          place = rand_places(1, seen)
        seen.append(place)
        return [place] + rand_places(num-1, seen)
      n = randint(3,8)
      cities = rand_places(n)
      votes = [randint(1,100) for a in range(0,n)]
      votes.sort(lambda a,b: cmp(b,a))
      results = zip(cities,votes)
      msg = []
      for result in results:
        msg.append("%s [%i]" % (result[0], result[1]))
      irc.reply('; '.join(msg))

    def get_votes(self, node_id, brief=True):
        json = urlopen("http://code4lib.org/votes.php?node_id=%i" % node_id).read()
        results = []
        for tally in simplejson.loads(json):
          talk_name = tally['talk_name']
          if brief and not re.match('http', talk_name):
            talk_name = re.sub('( -|[:/.]).*', '', talk_name)
          results.append("%s %s" % (talk_name, tally['votes']))
          if brief and len(results) > 15:
            break
        return results

    def twss(self, irc, msg, args):
        html = urlopen("http://thatswutshesaid.com/").read()
        soup = BeautifulSoup(html)
        twss = soup.find("h1")
        irc.reply(twss.string.encode('utf8'))

    def hench(self, irc, msg, args):
        """Generates an evil henchperson name from http://www.seventhsanctum.com/"""
        html = urlopen("http://www.seventhsanctum.com/generate.php?Genname=evilnamer").read()
        soup = BeautifulSoup(html)
        name = soup.find('div', { 'id': 'colContent' }).find('h2').nextSibling.strip()
        irc.reply(name.encode('utf8'))

    def luther(self, irc, msg, args):
        """Insults from Martin Luther, from http://ergofabulous.org/luther/"""
        html = urlopen("http://ergofabulous.org/luther/").read()
        soup = BeautifulSoup(html)
        luther = soup.find("p", {"class": "larger"})
        irc.reply(luther.string.encode('utf8'))
        
    def foodholiday(self, irc, msg, args):
        datestring = time.strftime('%B %d', time.localtime())
        datere = re.compile('^'+datestring+'\\b')
        html = urlopen("http://www.tfdutch.com/foodh.htm").read()
        soup = BeautifulSoup(html)
        matches = soup.findAll(text = re.compile(datere))
        holidays = [match.parent.parent.parent.find('a').string for match in matches]
        if len(holidays) > 0:
          response = "%s: %s" % (datestring, ', '.join(holidays))
        else:
          response = "No food holidays found for %s" % datestring
        irc.reply(response)
      
    def penny(self, irc, msg, args):
        html = urlopen("http://www.penny-arcade.com/archive/").read()
        soup = BeautifulSoup(html)
        tagcloud = soup.find("ul","tagcloud")
        tags = []
        for tag in tagcloud.findAll('li'):
            tags.append(tag.a.string)
        mytag = tags[randint(0, len(tags))]
        search = urlopen("http://www.penny-arcade.com/archive/?q=" + mytag).read()
        comiclist = BeautifulSoup(search)
        comics = comiclist.findAll("td","content_title")
        links = []
        for td in comics:
            print td.a['href']
            links.append(td.a['href'])
        comic = links[randint(0, len(links))]
        irc.reply("http://www.penny-arcade.com" + comic)
	
    def wine(self, irc, msg, args):
        """
        Wine from 2010 wines of the year list
        """
        f = join(dirname(abspath(__file__)), 'wines.html')
        data = open(f).read()
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        wines = []
        for li in soup.findAll('li'):
            if li.a:
                wines.append((li.a['href'], li.a.string))
        wine = wines[randint(0, len(wines))]
        if len(args) > 0:
            nick = ' '.join(args)
        else:
            nick = msg.nick
        irc.reply("fills a glass with %s for %s (%s)" % (wine[1], nick, wine[0]), action=True)


    def runoffers(self,irc,msg,args):
        """code4libcon 2007 runoff voters
        """
        results = self.get_voters(122)
        irc.reply(("[%i voters] " % len(results)) + 
            '; '.join(results).encode('utf8'))


    def voters2007(self,irc,msg,args):
        """code4libcon 2007 voters
        """
        results = self.get_voters(120)
        irc.reply(("[%i voters] " % len(results)) + 
            '; '.join(results).encode('utf8'))
     
    def get_voters(self, node_id):
        json = urlopen("http://code4lib.org/voters.php?node_id=%d" % node_id).read()
        results = []
        for tally in simplejson.loads(json):
          results.append("%s - %s" % (tally['name'], tally['votes']))
        return results

    def moe(self,irc,msg,args):
        """moe
        """
        ns = 'http://www.w3.org/1999/xhtml'
        url = 'http://www.snpp.com/guides/moe_calls.html'
        root = TidyHTMLTreeBuilder.parse(urlopen(url))

        bolds = root.findall('.//{%s}b' % ns)
        quote = bolds[ randint(0,len(bolds)-1) ]
        irc.reply(quote.text)

    def deli(self,irc,msg,args):
        max = 1
        url = 'http://del.icio.us/rss/popular'
        if (len(args) > 0):
            url += '/' + quote(args[0])
        if (len(args) > 1):
            max = int(args[1])

        feed = feedparser.parse(url)
        count = 0
        reply = ''
        for entry in feed.entries:
            count += 1
            if count > max: break
            reply += '%s - %s ; ' % (entry.title, entry.link)
        irc.reply(reply.encode('utf8'))

    def jihad(self,irc,msg,args):
        """welcomes a fellow jihadist

        http://www.elsewhere.org/cgi-bin/jihad
        """
        url = "http://www.elsewhere.org/cgi-bin/jihad"
        tree = TidyHTMLTreeBuilder.parse(urlopen(url))
        strong = tree.find('.//{http://www.w3.org/1999/xhtml}strong')
        irc.reply("welcome %s!" % strong.text)

    def journal(self,irc,msg,args):
        """randomly sample a journal name
        """
        url = "http://www.code4lib.org/node/86"
        tree = TidyHTMLTreeBuilder.parse(urlopen(url))
        list = tree.find('.//{http://www.w3.org/1999/xhtml}ul')
        names = []
        for name in list:
            names.append(name.text)
        irc.reply(names[randint(0, len(names)-1)])

    def jvotes(self,irc,msg,args):
        """journal name votes
        """
        text = urlopen("http://rsinger.library.gatech.edu/journalnamevote/overbelly_all.php").read().strip()
        irc.reply(text)

    def jvoters(self,irc,msg,args):
        """journal name voters
        """
        text = urlopen("http://rsinger.library.gatech.edu/journalnamevote/voters.php").read().strip()
        irc.reply(text)

    def lastjournal(self,irc,msg,args):
        """last journal name on website
        """
        url = "http://www.code4lib.org/node/86"
        tree = TidyHTMLTreeBuilder.parse(urlopen(url))
        list = tree.find('.//{http://www.w3.org/1999/xhtml}ul')
        names = []
        for name in list:
            names.append(name.text)
        irc.reply(names.pop())
 
    def gc(self,irc,msg,args):
        """google count
        """
        irc.reply(self.count(' '.join(args)))

    def skillz(self,irc,msg,args):
        """generate a fantasy Internet user"""
        attrs = ['Posturing', 'FanFiction', 'SocialMedia', 'Chat', 'LOLCats', 'Piracy', 'Email']
        dev = ', '.join(["%s:%d" % (attr, self.dnd_attr()) for attr in attrs])
        irc.reply(dev)

    def developer(self,irc,msg,args):
        """generate a fantasy developer"""
        attrs = ['Communication', 'BigPicture', 'DetailOriented', 'KungFu', 'GetsStuffDone', 'FlakeFactor', 'JavaAvoidance']
        dev = ', '.join(["%s:%d" % (attr, self.dnd_attr()) for attr in attrs])
        irc.reply(dev)

    def librarian(self,irc,msg,args):
        """generate a fantasy librarian"""
        attrs = ['Management', 'Cataloging', 'Acquisitions', 'Reference',
            'Circulation', 'Systems', 'Research', 'Custodial']
        dev = ', '.join(["%s:%d" % (attr, self.dnd_attr()) for attr in attrs])
        irc.reply(dev)


    def gamma(self,irc,msg,args):
        """generate a gamma world character"""
        attrs = ['Charisma', 'Constitution', 'Dexterity','Intelligence','Mental Strength','Physical Strength']
        pc = ', '.join(["%s:%d" % (attr, self.dnd_attr()) for attr in attrs])
        irc.reply(pc)

    def dnd(self,irc,msg,args):
        """get a d&d character
        """
        irc.reply("strength:%d dexterity:%d constitution:%d intelligence:%d wisdom:%d charisma:%d" % tuple([self.dnd_attr() for i in range(6)]))
    
    def roll(self, s):
        times, die = map(int, s.split('d'))
        return [randint(1, die) for i in range(times)]
 
    def drop_lowest(self, rolls):
        rolls.remove(min(rolls))
        return rolls
 
    def dnd_attr(self):
        return sum(self.drop_lowest(self.roll('4d6')))

    def duel(self,irc,msg,args):
        if len(args) != 2:
            irc.reply("usage: duel thing1 thing2")
            return
        thing1, thing2 = args
        c1 = self.count(thing1)
        c2 = self.count(thing2)
        if c1 > c2:
            irc.reply("%s wins %i to %i" % (thing1, c1, c2))
        elif c1 < c2:
            irc.reply("%s wins %i to %i" % (thing2, c2, c1))
        else:
            irc.reply("%s and %s tied at %i" % (thing1, thing2, c1))

    def indieduel(self,irc,msg,args):
        if len(args) != 2:
            irc.reply("usage: indieduel thing1 thing2")
            return
        thing1, thing2 = args
        c1 = self.count(thing1)
        c2 = self.count(thing2)
        if c1 > c2:
            irc.reply("%s is too mainstream: %i to %i" % (thing1, c1, c2))
        elif c1 < c2:
            irc.reply("%s is too mainstream: %i to %i" % (thing2, c2, c1))
        else:
            irc.reply("%s and %s tied at %i" % (thing1, thing2, c1))

    def count(self,q):
        q = q.replace('"','')
        q = q.replace("'",'')
        r = google.doGoogleSearch(q)
        self.log.info("searching google for %s" % q)
        return r.meta.estimatedTotalResultsCount

    def library(self,irc,msg,args):
        search_url = 'http://www.librarytechnology.org/lwc-processquery.pl'
        query = {}

        # validate
        if len(args) == 0:
            irc.reply("usage: library [institution_name] [city state [country]]")
            return
       
        if len(args) == 1:
            query['Quick'] = args[0]
        elif len(args) == 2:
            query['City'] = args[0]
            query['State'] = args[1]
        if len(args) == 3:
            query['Country'] = args[2]

        url = search_url + '?' + urlencode(query)
        hits = TidyHTMLTreeBuilder.parse(urlopen(url))
  
        results = []
        for p in hits.findall('.//{http://www.w3.org/1999/xhtml}p'):
            if p.attrib.get('class') == 'listing':
                results.append(self.get_library_detail(p))
        if len(results) == 0:
            irc.reply("game over man!")
        else:
            irc.reply(' ; '.join(results).encode('utf8'))

    def get_library_detail(self,p):
        text = self.get_text(p)
        for a in p.findall('.//{http://www.w3.org/1999/xhtml}a'):
            params = parse_qs(urlparse(a.attrib.get('href'))[4])
            if params.has_key('URL'):
                return text + params['URL'][0]
        return text

    def lurkers(self,irc,msg,args):
        """see who looked at the irc-logs on the web today. use 'all' if 
        you want to see non-resolvable ip addresses
        """
        include_ips = False
        if len(args)>0 and args[0]=='all': include_ips = True
        ips = os.popen("grep 'irc-logs/index.php\?' /var/www/code4lib.org/logs/access_log | cut -f 1 -d ' ' | sort | uniq").read().splitlines()
        resolved = []
        for ip in ips:
          if ip == '': continue
          hostname = os.popen('dnsname %s' % ip).read().strip()
          if hostname == '' and include_ips:
            resolved.append(ip)
          elif hostname:
            resolved.append(hostname)
        resolved.sort()
        irc.reply('; '.join(resolved))

    def rnd(self,irc,msg,args):
        """random page from the wikipedia
        """
        # how awful is this, at least we're working on a DOM ...
        # wikipedia seems to not like the User-Agent of urllib2
        url = 'http://en.wikipedia.org/wiki/Special:Random'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)

        # i tried this beautifulsoup stuff when elementtree was being buggy
        # (http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=461629)  gsf
        html_str = html.read()
        try:
            soup = BeautifulSoup(html_str)
        except UnicodeDecodeError, e:
            raise UnicodeDecodeError, "%s.  HTML was %s." % (e, html_str)
        title = soup.title.string

        def strip_tags(elem):
            text_list = []
            for child in elem.recursiveChildGenerator():
                if isinstance(child, unicode):
                    text_list.append(child)
            return ''.join(text_list)

        text = strip_tags(soup.p)

        link_elem = soup.find('a', title=re.compile('^Permanent link.*'))
        link = link_elem['href'].replace('&amp;', '&')

        irc.reply(("%s : %s <http://en.wikipedia.org%s>" % (title, text, link)).encode('utf-8'))
        
    def hillary(self,irc,msg,args):
        url = 'http://www.hillaryismomjeans.com/'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)
        html_str = html.read()
        soup = BeautifulSoup(html_str)
        irc.reply(soup.find('a').string)

    def obama(self,irc,msg,args):
        url = 'http://barackobamaisyournewbicycle.com/'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)
        html_str = html.read()
        soup = BeautifulSoup(html_str)
        irc.reply(soup.find('a').string.strip().upper())

    def isiticedcoffeeweather(self,irc,msg,args):
        if len(args) != 1:
            irc.reply("usage: isiticedcoffeeweather zipcode")
            return
        url = 'http://isiticedcoffeeweather.com/%s' % args[0]
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)
        html_str = html.read()
        soup = BeautifulSoup(html_str)
        irc.reply(soup.find('h2').string.strip().upper())
    
    def wodehouse(self,irc,msg,args):
        """grabs a p.g. wodehouse quote from http://www.drones.com/pgw.cgi"""
        url = 'http://www.drones.com/pgw.cgi'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)
        html_str = html.read()
        soup = BeautifulSoup(html_str)
        irc.reply(soup.find('blockquote').next.replace("\n"," ").strip())

    def get_text(self,e):
        string = ''
        if e.text: string += e.text
        for child in e.getchildren():
            string += self.get_text(child)
        if e.tail: string += e.tail
        string = string.replace("\n",'')
        string = re.sub('\+? Details.','', string)
        return string

    def isitfriday(self, irc, msg, args):
#        irc.reply("If it feels like Friday, it's Friday!")
#        return
        isfriday = "nope."
        dow = date.today().weekday()
        if dow == 4:
            isfriday = "yes!"
        irc.reply(isfriday, prefixNick=True)
        return

    def isit420(self, irc, msg, args):
        irc.reply("uhhhhh, what?")
        return

    def arewethereyet(self, irc, msg, args):
        irc.reply("nope", prefixNick=True)
        return

    def bin2int(self, irc, msg, args, binstring):
        """
        usage: bin2int <bin>
        returns the integer form of a given binary string
        """

        irc.reply(int(binstring, 2), prefixNick=True)
        return

    bin2int = wrap(bin2int, ['text'])

    def nonsense(self, irc, msg, args, nb_words, lang, minl, maxl):
        """
        a generator for pronounceable random words --
        Source: http://ygingras.net/yould --
        Usage: nonsense [num_words] [lang] [min len] [max len] --
        Language codes: en,fr,kjb,fi,nl,de,la
        """
        if nb_words > 10:
            nb_words = 10

        postdata = {}
        postdata['lang'] = lang or 'en'
        postdata['minl'] = minl or 5
        postdata['maxl'] = maxl or 12
        postdata['nb_words'] = nb_words or 1
        postdata = urlencode(postdata)

        try:
            soup = self._url2soup('http://ygingras.net/yould?lang=en', {}, postdata)
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, url), prefixNick=True); return
        except StopParsing, e:
            irc.reply('parsing error %s for %s' % (e.code, url), prefixNick=True); return

        words = soup.find('textarea',{'name':'new_domains'}).string.split()
        words = [w.encode('utf-8') for w in words if isinstance(w, unicode)]
        irc.reply(' '.join(words))

    nonsense = wrap(nonsense, [optional('int'),optional('anything'),optional('int'),optional('int')])

    def hero(self, irc, msg, args, opts, nick):
        """[--sex <male|female|neuter>] [--powers <1..15>] [name] - Generate some random superhero powers
        from http://www.rps.net/cgi-bin/stone/randpower.pl"""
        sexes = { 'male': 0, 'female': 1, 'neuter': 2 }        
        if not nick:
          nick = msg.nick

        sex = 0
        powers = 0
        
        for (opt, arg) in opts:
            if opt == 'sex':
                try:
                  sex = sexes[arg]
                except:
                  sex = 0
            if opt == 'powers':
                powers = arg
          
        if powers > 15:
          irc.error('Maximum of 15 powers allowed.')
        else:
          postdata = {}
          postdata['name'] = nick
          postdata['sex']  = sex
          postdata['numpowers'] = powers
          postdata['weakness'] = 1
          postdata = urlencode(postdata)

          try:
              soup = self._url2soup('http://www.rps.net/cgi-bin/stone/randpower.pl', {}, postdata)
          except HTTPError, e:
              irc.reply('http error %s for %s' % (e.code, url), prefixNick=True); return
          except StopParsing, e:
              irc.reply('parsing error %s for %s' % (e.code, url), prefixNick=True); return

          text = soup.findAll(text=re.compile('\S'))[-1].strip()
          irc.reply(text, prefixNick=False)

    hero = wrap(hero, [getopts({'sex':("literal", ("male","female","neuter")),'powers':'int'}), optional('text')])

    def itr(self,irc,msg,args,continent):
        """
        Usage: itr [continent]
        Returns current traffic index from http://internettrafficreport.com/
        Data available for Asia, Australia, Europe, North America and South America
        (default is North America)
        """

        if not continent:
            continent = 'North America'

        try:
            soup = self._url2soup('http://internettrafficreport.com/')
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, url), prefixNick=True); return
        except StopParsing, e:
            irc.reply('parsing error %s for %s' % (e.code, url), prefixNick=True); return

        region = None
        for row in soup.find('table', attrs={'border': 1}).findAll('tr'):
            if row.find(text=re.compile(continent,re.I)):
                region = row

        if not region:
            irc.reply("No index for %s" % continent)
            return

        ci = region.contents[1].font.b.string
        art = region.contents[2].font.string
        pl = region.contents[3].font.string
        resp = "ITR for %s: Current Index: %s, Avg Response Time: %s, Avg Packet Loss: %s" % (continent,ci,art,pl)
        irc.reply(resp)

    itr = wrap(itr, [optional('text')])

    def haiku(self, irc, msg, args):
        """
        Random haiku from http://www.vikingmud.org/guilds/samurai/?haiku/random
        """
        soup = self._url2soup('http://www.vikingmud.org/guilds/samurai/?haiku/random')
        main = soup.find('td', {'class': 'main'})
        haiku = main.find('i')
        lmb = lambda s: s.string and s.string.strip() or None
        resp = [lmb(x) for x in haiku.contents]
        irc.reply(' / '.join([x for x in resp if x]), prefixNick=False)

    def dance(self, irc, msg, args):
        irc.reply(" o/", prefixNick=False)
        irc.reply("/|", prefixNick=False)
        irc.reply(" >>", prefixNick=False)

    def toast(self, irc, msg, args):
        irc.reply("  o  .   o   o ", prefixNick=False)
        irc.reply("  . o  _o_._'_ ", prefixNick=False)
        irc.reply(" o_.__'\~~~~~/ ", prefixNick=False)
        irc.reply("\~~~~~/ '-.-'  ", prefixNick=False)
        irc.reply(" '-.-'    |   ", prefixNick=False)
        irc.reply("   |     _|_  ", prefixNick=False)
        irc.reply('  _|_   `"""` ', prefixNick=False)
        irc.reply(' `"""`        ', prefixNick=False)

    def pong(self, irc, msg, args):
        irc.reply("|˙         |", prefixNick=False)
        irc.reply("|    ‧     |", prefixNick=False)
        irc.reply("|         .|", prefixNick=False)
        irc.reply("|    .     |", prefixNick=False)
        irc.reply("|.         |", prefixNick=False)
        irc.reply("|    ‧     |", prefixNick=False)
        irc.reply("|          |‧", prefixNick=False)
        irc.reply("I win!", prefixNick=False)

    def grumpycat(self, irc, msg, args):
        irc.reply("  ^  ^  ", prefixNick=False)
        irc.reply("  .  .  ", prefixNick=False)
        irc.reply(" > n <  ", prefixNick=False)
        irc.reply("        ", prefixNick=False)
        irc.reply("  NO    ", prefixNick=False)
      
    def stab(self, irc, msg, args):
      irc.reply("o()xxxx[{::::::*" + ' '.join(args) + "*::::::>", prefixNick=False)
       
    def halfbaked(self, irc, msg, args):
        """
        returns a radom half-baked idea from http://halfbakery.com
        """
        try:
            soup = self._url2soup('http://www.halfbakery.com/random-idea.html')
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, url), prefixNick=True); return
        except StopParsing, e:
            irc.reply('parsing error %s for %s' % (e.code, url), prefixNick=True); return

        idea = soup.find('a', {'name': 'idea'})
        title = idea.h1.string
        try:
            subtitle = idea.parent.find('font', 'fcl').string
            title = '%s -- %s' % (title, subtitle)
        except:
            pass

        irc.reply(title, prefixNick=True)

    def dow(self, irc, msg, args):
        """
        Get the Dow Jones Industrial Average from teh GOOG
        """
        irc.reply(self._cid_quote(983582,args))

    def nasdaq(self, irc, msg, args):
        """
        Get the NASDAQ from teh GOOG
        """
        irc.reply(self._cid_quote(13756934,args))

    def sandp(self, irc, msg, args):
        """
        Get the S&P from teh GOOG
        """
        irc.reply(self._cid_quote(626307,args))

    def ftse(self, irc, msg, args):
        """
        Get the FTSE from teh GOOG
        """
        irc.reply(self._cid_quote(12590587,args))

    def _cid_quote(self, cid, args):
        directions = { '+' : 'up', '-' : 'down' }
        formats = {
          'def' : "%(idx)s; %(sign)s%(diff)s (%(sign)s%(pct)s)",
          'eng' : "The %(name)s is %(direction)s %(diff)s points (%(pct)s) to %(idx)s."
        }
        try:
          format = formats[args[0].lower()[0:3]]
        except:
          format = formats['def']
        
        # TODO: make this so you can use an ticker
        try:
	    soup = self._url2soup("http://finance.google.com/finance?cid=%s" % cid)
	except:
	    return 'Is it possible Google is sending back invalid HTML?'
        data = {}
        try:
            data = {
              'idx' : soup.find(id="ref_%s_l" % cid).string,
              'diff' : soup.find(id="ref_%s_c" % cid).string or '+0',
              'pct' : soup.find(id="ref_%s_cp" % cid).string or '0%',
              'name' : soup.find('h3').string
            }
            data['sign'] = data['diff'][0]
            data['direction'] = directions[data['sign']]
            data['diff'] = data['diff'].strip('+-')
            data['pct'] = data['pct'].strip('()+-')
        except:
            raise
            return 'ruhroh, me no speak google'
        return format % data

    def stock(self, irc, msg, args):
        t = quote(' '.join(args))
        soup = self._url2soup("http://finance.google.com/finance?q=%s" % t)
        match = re.search('var _companyId = (\d+)', str(soup))
        if not match:
            irc.reply("gah, couldn't find stock ticker %s" % t)
            return
        try:
            cid = match.group(1)
            idx = soup.find(id="ref_%s_l" % cid).string.replace('&nbsp;', '')
            p = soup.find(id="ref_%s_cp" % cid).string.replace('&nbsp;', '')
            mktcap = soup.find('span', text="Mkt cap").next.next.string
            pe = soup.find('span', text='P/E').next.next.string
#            hi = soup.find(id="ref_%s_hi" % cid).string.replace('&nbsp;', '')
#            lo = soup.find(id="ref_%s_lo" % cid).string.replace('&nbsp;', '')
#            hi52 = soup.find(id="ref_%s_hi52" % cid).string.replace('&nbsp;','')
#            lo52 = soup.find(id="ref_%s_lo52" % cid).string.replace('&nbsp;','')
            name = ' - '.join(soup.find('title').string.split('-')[0:2]).strip()

#            irc.reply("%s - %s %s high:%s low:%s  high52:%s low52:%s p/e:%s mktcap:%s" % (name, idx, p, hi, lo, hi52, lo52, pe, mktcap))
            irc.reply("%s - %s %s p/e:%s mktcap:%s" % (name, idx, p, pe, mktcap))
        except:
            irc.reply("ruhroh, me no speak google")

    def prez(self, irc, msg, args):
        """
        Returns expected Presedential race results from http://www.electoral-vote.com/
        """
        irc.reply(self._electoral(0))

    def senate(self, irc, msg, args):
        """
        Returns expected Senate race results from http://www.electoral-vote.com/
        """
        irc.reply(self._electoral(1))

    def house(self, irc, msg, args):
        """
        Returns expected House race results from http://www.electoral-vote.com/
        """
        irc.reply(self._electoral(2))

    def _electoral(self, idx):
        soup = self._url2soup("http://www.electoral-vote.com/")
        dems = soup.findAll('span', {'class':'dem'})
        gops = soup.findAll('span', {'class':'gop'})
        ties = gops[idx].next.next
        return ', '.join([x.string.strip() for x in [dems[idx], gops[idx], ties]])

    def debt(self, irc, msg, args):
        """
        Returns current US gross national debt as
        calculated at http://zfacts.com/p/461.html
        """
        # values taken from http://zfacts.com/giz/G05ndc.js on 2008-10-03
        gndstart = 10124225067127.69
        add_debt_per_year = 676 # in $ billions
        add_debt_per_sec = add_debt_per_year*1000000000/(365*24*60*60)
        from_date = datetime(2008, 10, 01, 11, 0, 0)
        now = datetime.now()
        delta = now - from_date
        add_debt = delta.seconds * add_debt_per_sec
        gnd = gndstart + add_debt
        gnd_str = '%.2f' % gnd
        gnd_whole, gnd_decimal = gnd_str.split('.')
        response = '%sdollars and %scents' % (int2word(gnd_whole),
                int2word(gnd_decimal))
        irc.reply(response)

    def lhc(self, irc, msg, args):
        """
        reports how much time is left until the HLC starts smashing reality^Watoms
        """
        targetdate = datetime(2008, 10, 21, 13, 0, 0)
        now = datetime.now()
        delta = targetdate - now
        irc.reply('%d days left' % delta.days)

    def nytags(self, irc, msg, args, **opts):
        url = 'http://api.nytimes.com/svc/timestags/suggest'
        key = 'aa51418354ed1dc2378f9679a04a0f54:14:13476879'
        q = urlencode({'query': ' '.join(args), 'api-key': key})
        json = urlopen("%s?%s" % (url, q)).read()
        tags = simplejson.loads(json)
        result = ', '.join(tags['results'])
        irc.reply(result)
    
    def flu(self, irc, msg, args, loc):
        """
        Estimate of flu search activity for a given region or location. --
        Usage: flu [location] --
        Enter "list" as location for a list of options ---
        Data from http://www.google.org/flutrends/
        """
        try:
            reader = csv.reader(urlopen("http://www.google.org/flutrends/data.txt"))
        except:
            print "Error fetching flu data: ", sys.exc_info()[0]
        data = [row for row in reader if len(row) > 2]
        locations = [x.lower() for x in data[0][1:]]
        if loc == 'list':
            resp = ', '.join(locations)
            irc.reply(resp)
            return
        latest_data = ["%.2f" % float(x) for x in data[-1][1:]]
        previous_data = ["%.2f" % float(x) for x in data[-2][1:]]
        latest = dict(zip(locations, latest_data))
        previous = dict(zip(locations, previous_data))
        if loc.lower() not in latest:
            irc.reply("No data for location: %s" % loc)
        else:
            trend = cmp(latest[loc.lower()], previous[loc.lower()])
            if trend < 0:
                trend = 'down'
            elif trend == 0:
                trend = 'stable'
            else:
                trend = 'up'
            resp = "As of %s the flu search activity index for %s was %s; trend is %s" \
                % (data[-1][0], loc, latest[loc.lower()], trend)
            irc.reply(resp)
    
    flu = wrap(flu, ['text'])

    def orsome(self, irc, msg, args, splitter, s):
        """Usage: orsome [/separator/] string"""
        if not s:
            return
        if splitter:
            items = [x.strip() for x in re.split(splitter, s) if len(x)]
        else:
            items = [x.strip() for x in re.split('\s+', s) if len(x)]
        irc.reply(' or '.join(items), prefixNick=False)
         
    orsome = wrap(orsome, [optional('regexpMatcher'), 'text'])

    def decide(self, irc, msg, args, opts, choices):
        prefix = "go with "
        for opt,arg in opts:
          if opt == 'raw':
            prefix = ""
            
        seed(choices)

        pattern = re.compile('\s+or\s+', re.I)
        clist = re.split(pattern, choices)
        if randint(0, 10) == 0:
            irc.reply("That's a tough one...")
            return
        irc.reply(prefix + clist[randint(0, len(clist)-1)])

        seed()

    decide = wrap(decide, [getopts({'raw':''}),'text'])

    def should(self, irc, msg, args, name, choices):
      choices = re.sub('[^A-Za-z0-9]+$','',choices)
      adverbs = ['','','','totally', 'absolutely', 'probably']
      pattern = re.compile('\s+or(?:\s+should \S+?)?\s+', re.I)
      clist = re.split(pattern, choices)
      if re.match('I',name,re.I):
        name = 'You'
      elif re.match('You',name,re.I):
        name = 'I'
        
      if randint(0, 10) == 0:
          irc.reply("That's a tough one...")
          return
      adverb = random.choice(adverbs)
      if len(adverb) > 0:
        adverb = adverb + ' '
      action = random.choice(clist)
      response = "%s should %s%s." % (name, adverb, action)
      irc.reply(response)
      
    should = wrap(should, ['somethingWithoutSpaces','text'])
      
    def pick(self, irc, msg, args, choices):
    	"""
    	@decide without the niceties 
    	"""
        pattern = re.compile('\s+or\s+', re.I)
        clist = re.split(pattern, choices)
        if randint(0, 10) == 0:
            irc.reply("That's a tough one...")
            return
        irc.reply(clist[randint(0, len(clist)-1)])

    pick = wrap(pick, ['text'])

    def _url2soup(self, url, qsdata={}, postdata=None, headers={}):
        """
        Fetch a url and BeautifulSoup-ify the returned doc
        """
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        headers.update({'User-Agent': ua})
        params = urlencode(qsdata)
        if params:
            if '?' in url:
                url = "%s&%s" % (url,params)
            else:
                url = "%s?%s" % (url,params)
        req = Request(url,postdata,headers)
        doc = urlopen(req)
        data = doc.read()
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        return soup

    def coffee(self, irc, msg, args):
        """
        makes and pours a sensational cup of coffee from the highest rated
        coffees at ttp://www.coffeereview.com/allreviews.cfm?search=1
        """
        f = join(dirname(abspath(__file__)), 'coffee.html')
        data = open(f).read()
        root = lxml.html.soupparser.fromstring(data, convertEntities=False)
        nodes = root.xpath('//div[@class="review_general2"]//h3')
        coffees = [x.text_content() for x in nodes]
        coffee = coffees[randint(0, len(coffees))]
        if len(args) > 0:
            nick = ' '.join(args)
        else:
            nick = msg.nick
        irc.reply("brews and pours a cup of %s, and sends it sliding down the bar to %s" % (coffee, nick), action=True)



    def tea(self, irc, msg, args):
        """
        makes and pours a sensational cup of tea from the highest rated
        teas at http://ratetea.com/highest_rated_teas.php
        """
        soup = self._url2soup('http://ratetea.com/highest_rated_teas.php')
        rows = soup.findAll('tr')[1:]
        teas = [t.a for t in rows]
        tea = teas[randint(0, len(teas)-1)]
        tea_name = tea.string 
        tea_url = "http://ratetea.com" + tea['href']
        if len(args) > 0:
            nick = ' '.join(args)
        else:
            nick = msg.nick
        irc.reply("brews and pours a pot of %s, and sends it sliding down the bar to %s (%s)" % (tea_name, nick, tea_url), action=True)

    def bartender(self, irc, msg, args):
        """
        pours a beer from an archived copy of
        http://web.mit.edu/~tcarlile/www/beer/beerlist.html
        for you
        """
        f = join(dirname(abspath(__file__)), 'beerlist.html')
        data = open(f).read()
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        beers = []
        for li in soup.findAll('li'):
            if li.a:
                beers.append((li.a['href'], li.a.string))
        beer = beers[randint(0, len(beers))]
        if len(args) > 0:
            nick = ' '.join(args)
        else:
            nick = msg.nick
        irc.reply("fills a pint glass with %s, and sends it sliding down the bar to %s (%s)" % (beer[1], nick, beer[0]), action=True)

    def whisky(self, irc, msg, args):
      """
      pours a shot of whisky for you from http://whisky.com/
      """
      raw_html = urlopen('http://whisky.com/select.html').read()
      raw_html = raw_html.replace('<option brands/>','<option>').replace('<option value=>','<option>')
      soup = BeautifulSoup(raw_html)
      menu = []
      for option in soup.findAll('option'):
        try:
          menu.append((option['value'], option.string.replace('_',' ')))
        except KeyError:
          pass
      order = menu[randint(0, len(menu))]
      if len(args) > 0:
        nick = ' '.join(args)
      else:
        nick = msg.nick
      irc.reply("pours a shot of %s and sends it sliding down the bar to %s (http://whisky.com/%s)" % (order[1], nick, order[0]), action=True)

    whiskey = whisky  
    
    def swill(self, irc, msg, args):
      """
      pours...something else.
      """
      catalog = [
        ["forty of", ["Colt 45", "Camo 40", "Black Fist", "Country Club", "Olde English 800", "Mickey's", "Black Bull", 
          "Labatt Blue Dry 7.1", "WildCat", "Molson Dry 6.5/7.5/8.5/10.1", "Private Stock", "Big Bear", "St. Ides", 
          "Steel Reserve 211", "B40 Bull Max", "King Cobra", "Jeremiah Weed", "Hurricane"]],
        ["bottle of", ["Zima", "Extra Dry Champale", "Pink Champale", "Golden Champale", "Night Train", "MD 20/20", "Thunderbird", "Wild Irish Rose", "Cisco Red"]],
        ["can of Sparks", ["", "Light","Plus","Red","Stinger"]],
        ["bottle of Smirnoff Ice", ["Watermelon","Wild Grape","Passionfruit","Mango","Triple Black","Pomegranate Fusion",
          "Arctic Berry", "Green Apple Bite","Strawberry Acai","Pineapple","Raspberry Burst"]]
      ]
      menu = []
      package,options = catalog[randint(0, len(catalog)-1)]
      for option in options:
        menu.append(('%s %s' % (package, option)).strip())
      if len(args) > 0:
        nick = ' '.join(args)
      else:
        nick = msg.nick
      order = menu[randint(0, len(menu)-1)]
      irc.reply("grabs a %s and sends it sliding down the bar to %s" % (order, nick), action=True)
      
    def anon(self, irc, msg, args):
        """
        Spits out random nonsense from 'anon,' that loveable idiot of a troll
        """
        trolls = ["Hey Roy, get a life.",
                  "Did OCLC put co-option of code4lib in your performance review for 2009?",
                  "you don't belong to code4lib, since you acted in an unwelcome fashion there and were shunned accordingly.",
                  "How about enabling comments over on your site, Winer of the library world?",
                  "Roy's a big boy--think he can speak to OCLC's desire to act like Microsoft and assert dominance over an informal organization",
                  "Follow the money on the code4libcon Google group",
                  "Awesome, hypocrisy.",
                  "Let's say that OCLC and code4lib is about as awesome as DSpace plus HP.",
                  "OCLC as largest code4lib sponsor=death",
                  "Roy as OCLC shill=shame for LJ and code4lib",
                  "Roy=saint, or Joe of Arc since leaving CDL?",
                  "court fool of the library world",
                  "aren't you on strike or something?",
                  "Hey Roy, what does OCLC think about code4lib?",
                  "the community voted the ridiculous Ohio location down, so it does know what sponsorship is, indeed",
                  "Isn't Ohio the state that doesn't know the difference between a business and a non-profit cooperative?",
                  "OCLC is using Roy and its money to influence a loose collective in the process of expanding.",
                  "are you affiliated with OCLC?",
                  "But you don't now--you're a vendor.",
                  "May as well post an OCLC ad, since you're shilling for their services in your presentation.",
                  "Oh, does this benefit WorldCat Local?",
                  "RFP's exist because libraries are public. The Oh Can Libraries Concede trust would prefer otherwise, I'm sure",
                  "if channels matter, then why not community dot oclc dot org slash roy?",
                  "Nice OCLC shill, Roy."
                  ]
        troll = trolls[randint(0, len(trolls)-1)]
        irc.reply(troll, prefixNick=True)

    def _diebold_tallies(self, tally='', year=''):
        """ Gets a tally from the diebold-o-tron """
        base_url = 'http://vote.code4lib.org/election/'
        tallies = {
            'keynotes': {'2009': '4',
                         '2010': '11',
                         '2011': '16',
                         '2012': '20',
			 '2013': '23'},
            'necode4lib': {'2008': '5'},
            'tshirts': {'2009': '8',
	    	        '2010': '14',
                        '2011': '18'},
            'hosts': {'2009': '3',
                      '2010': '9',
                      '2011': '15'},
            'talks': {'2008': '2', 
                      '2009': '7',
                      '2010': '13',
                      '2011': '17',
                      '2012': '21',
                      '2013': '24'},
            'logo': {'2008': '6'}
        }
        try:
            poll_number = tallies[tally][year]
        except KeyError:
            raise PollNotFoundException("tally or year not found")
        poll_url = base_url + 'results/' + poll_number
        vote_url = base_url + poll_number 
        from socket import setdefaulttimeout
        setdefaulttimeout(60)
        try:
            json = urlopen(Request(poll_url, None, {'Accept': 'application/json'})).read()
        except HTTPError, e:
            raise PollNotFoundException("%s" % e)
        json = re.sub(r'\\[0-9A-fa-f]{3}', '', json)
        try:
            votes = simplejson.loads(json)
        except UnicodeDecodeError:
            votes = simplejson.loads(json.decode('ascii', 'ignore'))
        votes.sort(cmp=lambda x,y: int(y['score'])-int(x['score']))
        tallies = [(vote['title'], vote['score']) for vote in votes]
        return tallies, vote_url

    def talks2013(self, irc, msg, args):
        """ 
        Gets tally of talk votes for 2012 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("talks", "2013")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for talk votes in 2013: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))
            irc.reply("Voting link: %s" % vote_url)

    def talks2012(self, irc, msg, args):
        """ 
        Gets tally of talk votes for 2012 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("talks", "2012")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for talk votes in 2012: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))
            irc.reply("Voting link: %s" % vote_url)

    def talks2011(self, irc, msg, args):
        """ 
        Gets tally of talk votes for 2011 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("talks", "2011")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for talk votes in 2011: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))
            irc.reply("Voting link: %s" % vote_url)

    def talks2010(self, irc, msg, args):
        """ 
        Gets tally of talk votes for 2010 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("talks", "2010")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for talk votes in 2010: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))

    def talks2009(self, irc, msg, args):
        """ 
        Gets tally of talk votes for 2009 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("talks", "2009")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for talk votes in 2009: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))

    def tshirts2009(self, irc, msg, args):
        """ 
        Gets tally of t-shirt votes for 2009 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("tshirts", "2009")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for t-shirt votes in 2009: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))

    def tshirts2010(self, irc, msg, args):
        """ 
        Gets tally of t-shirt votes for 2010 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("tshirts", "2010")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for t-shirt votes in 2010: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))

    def tshirts2011(self, irc, msg, args):
        """ 
        Gets tally of t-shirt votes for 2011 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("tshirts", "2011")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for t-shirt votes in 2011: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))

    def bubble2009(self, irc, msg, args):
        """ 
        List talks that are within 4 ranks of the cutoff range for the 2009 conference
        """
        cutoff = 22
        try:
            tallies, vote_url = self._diebold_tallies("talks", "2009")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for talk votes in 2009: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies[cutoff-3:cutoff+2])).encode('utf-8'))

    def talks2008(self, irc, msg, args):
        """ 
        Gets tally of talk votes for 2008 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("talks", "2008")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for talk votes in 2008: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))


    def logo2008(self, irc, msg, args):
        """ 
        Gets tally of logo votes for 2008
        """
        try:
            tallies, vote_url = self._diebold_tallies("logo", "2008")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for logos in 2008: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))

    def hosts2009(self, irc, msg, args):
        """ 
        Gets tally of host votes for 2009 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("hosts", "2009")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for hosts in 2009: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))

    def hosts2010(self, irc, msg, args):
        """ 
        Gets tally of host votes for 2010 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("hosts", "2010")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for hosts in 2010: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))

    def hosts2011(self, irc, msg, args):
        """ 
        Gets tally of host votes for 2011 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("hosts", "2011")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for hosts in 2011: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))

    def hosts2012(self, irc, msg, args):
        """
        Gets tally of host votes for 2012 conference
        """
        irc.reply("Seattle [*]")

    def keynotes2009(self, irc, msg, args):
        """ 
        Gets tally of keynoter votes for 2009 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("keynotes", "2009")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for keynotes in 2009: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))

    def keynotes2010(self, irc, msg, args):
        """ 
        Gets tally of keynoter votes for 2010 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("keynotes", "2010")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for keynotes in 2010: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))

    def keynotes2011(self, irc, msg, args):
        """ 
        Gets tally of keynoter votes for 2011 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("keynotes", "2011")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for keynotes in 2011: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))
            irc.reply("Have you voted? %s" % vote_url)

    def keynotes2012(self, irc, msg, args):
        """ 
        Gets tally of keynoter votes for 2012 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("keynotes", "2012")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for keynotes in 2012: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))
            irc.reply("Have you voted? %s" % vote_url)

    def keynotes2013(self, irc, msg, args):
        """ 
        Gets tally of keynoter votes for 2012 conference
        """
        try:
            tallies, vote_url = self._diebold_tallies("keynotes", "2013")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for keynotes in 2013: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))
            irc.reply("Have you voted? %s" % vote_url)

    #def hosts2013(self, irc, msg, args):
    #  irc.reply("I'm sorry. That request involves dates after December 21, 2012, and is therefore not worth any of my precious remaining time.")
      
    #talks2013 = keynotes2013 = tshirts2013 = hosts2013

    def once(self, irc, msg, args, s):
        irc.reply("%s once.... Once." % s, prefixNick=False)

    once = wrap(once, ['text'])

    def inaworld(self, irc, msg, args, s):
        irc.reply("In a world... %s..." % s, prefixNick=False)

    inaworld = wrap(inaworld, ['text'])

    def cluephone(self, irc, msg, args, who):
        """
        Rings the cluephone. Is it for you?
        """
        irc.reply("BBRRRRrrringgg! It's for %s" % who, prefixNick=False)

    cluephone = wrap(cluephone, ['text'])

    def necode4lib(self, irc, msg, args):
        """ 
        Gets tally of location votes for 2008 New England code4lib conference 
        """
        try:
            tallies, vote_url = self._diebold_tallies("necode4lib", "2008")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for necode4lib in 2008: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))

    def reminder(self, irc, msg, args, nick, seconds, note):
        """
        Set a timer to remind you to do something - Usage: reminder seconds [note]
        """
        note = note or "This is your reminder to do that thing"

        def remind():
            if nick:
                irc.reply("DING DING DING! " + note, to=nick)
            else:
                irc.reply("DING DING DING! " + note)

        t = Timer(float(seconds), remind)
        t.start()
        irc.reply("OK. I'll remind you in %s seconds" % seconds)

    reminder = wrap(reminder, [optional('nickInChannel'), 'int', optional('text')])

    def cowbell(self, irc, msg, args):
        """<text>
        adds more cowbell!
        """
        cowbell = " *cowbell* "
        if len(args) > 1:
            s = cowbell.join(args)
        elif len(args) == 1:
            s = re.compile(r' ').sub(cowbell, args[0])
        else:
            s = cowbell
        irc.reply(s, prefixNick=True)

    def sheen(self, irc, msg, args):
        """
        Melting your face off.
        """
        quote = unicode(sheendata.quotes[randint(0, len(sheendata.quotes))])
        irc.reply(quote.encode('utf-8'), prefixNick=False)

    def slowclap(self, irc, msg, args):
        """
        Show your heartfelt appreciation (or mockery) of an
        underdog who surprises everyone with his or her 
        classiness, gumption and/or dancing ability
        """
        irc.reply("*clap*", prefixNick=False)
        time.sleep(1)
        irc.reply("*clap*", prefixNick=False)
        time.sleep(1)
        irc.reply("*clap*", prefixNick=False)
        time.sleep(1)
        irc.reply("*clap*", prefixNick=False)
    
    def excuse(self, irc, msg, args):
        """
        returns the excuse of the day  http://meyerweb.com/feeds/excuse/
        """

	ns = 'http://www.w3.org/1999/xhtml'
	url = 'http://meyerweb.com/feeds/excuse/'
	xpathLite = ('{%s}body/{%s}div/{%s}div/{%s}p' % (ns, ns, ns, ns))
        try:
            tree = TidyHTMLTreeBuilder.parse(urlopen(url));
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, url), prefixNick=True)
            return
        except StopParsing, e:
            irc.reply('parsing error %s for %s' % (e.code, url), prefixNick=True)
            return

        excuseNode = tree.find(xpathLite)
        
        excuseStr = excuseNode.text
        irc.reply('My excuse for today is "%s"' % excuseStr, prefixNick=True)

    def swineflu(self, irc, msg, args):
        soup = self._url2soup('http://www.cdc.gov/swineflu/?s_cid=swineFlu_outbreak_internal_001')
        cases = soup.find('td', text=re.compile('\d+ cases')).string
        deaths = soup.find('td', text=re.compile('\d+ death')).string
        irc.reply(('Total: %s, %s' % (cases, deaths)) + '; <http://icanhaz.com/swine-flu>')

    def bar(self, irc, msg, args):
        qhash = md5("%s%s%s%d" % ('zoia','random_by_author','william shakespeare', 1))
        url = 'http://quotesdaddy.com/api/zoia/'

    def blues(self, irc, msg, args, trouble):
        """
        sing your troubles away
        """
        song = "I woke up this morning / %s / I woke up this morning / Lord, %s" \
            % (trouble, trouble)
        irc.reply(song, prefixNick=False)

    blues = wrap(blues, ['text'])

    def tdih(self, irc, msg, args):
        """
        Get a piece of computing history from http://www.computerhistory.org/tdih. 
        """
        url = 'http://www.computerhistory.org/tdih'
        soup = self._url2soup(url)
        try:
            # kinda fragile, but whatevs
            h3 = soup.find('h3')
            date = h3.string
            title = h3.nextSibling.nextSibling.string
            text = h3.nextSibling.nextSibling.nextSibling.nextSibling.string
            msg = "[%s] %s - %s" % (date, title, text)
        except RuntimeError, e:
            msg = "d'oh something is b0rk3n: %s" % e
        irc.reply(msg.encode('utf-8'))

    history = tdih

    def snow(self, irc, msg, args):
        flake = """
           o      
      o    :    o 
        '.\'/.'   
        :->@<-:   
        .'/.\'.   
      o    :    o 
           o    
        """
        for line in flake.split("\n"):
            if line: 
                irc.reply(line, prefixNick=False)

    def pony(self, irc, msg, args, who):
        """
        zOMG PONieZ!!
        """
        pony = """      ,//) 
    ,;;' \ 
  ,;;' ( '\ 
      / '\_)"""
        if who:
            who = who + "'s"
        else:
            who = 'yours'

        for line in pony.split("\n"):
            if line: 
                irc.reply(line, prefixNick=False)
        resp = '^^ not %s' % who
        irc.reply(resp, prefixNick=False)

    pony = wrap(pony, [optional('text')])

    def _random_nick(self, irc, msg, args, channel):
        # Modified from Channel.nicks
        #
        # Make sure we don't elicit information about private channels to
        # people or channels that shouldn't know
        if 's' in irc.state.channels[channel].modes and \
               msg.args[0] != channel and \
               (ircutils.isChannel(msg.args[0]) or \
                msg.nick not in irc.state.channels[channel].users):
            irc.error("You don't have access to that information.")
        return choice(list(irc.state.channels[channel].users))

    def someone(self, irc, msg, args, channel):
        """[<channel>]

        Returns a random nick from <channel>.  <channel> is only necessary if the
        message isn't sent in the channel itself.
        """
        irc.reply(self._random_nick(irc, msg, args, channel).strip(), prefixNick=False)

    someone = wrap(someone, ['inChannel'])

    def _personalize(self,matchobj):
      replacements = { 'your': 'my', 'my': 'your', 'you': 'me', 'me': 'you' }
      return replacements[matchobj.group(0)]
      
    def who(self, irc, msg, args, channel, question):
      """[<channel>] <question>

      Answers <question> with a random nick from <channel>.  <channel> is only 
      necessary if the message isn't sent in the channel itself.
      """
      subject = self._random_nick(irc, msg, args, channel)
      predicate = re.sub("[^A-Za-z0-9]+$",'',question)
      predicate = re.sub("\\b(your?|me|my)\\b",self._personalize,predicate)
      predicate = re.sub("\\$whose",subject + "'s",predicate)
      predicate = re.sub("\\$who",subject,predicate)
      irc.reply("%s %s." % (subject, predicate), prefixNick=False)
      
    who = wrap(who, ['inChannel', 'text'])

    def whose(self, irc, msg, args, channel, question):
      subject = self._random_nick(irc, msg, args, channel)
      predicate = re.sub("[^A-Za-z0-9]+$",'',question)
      predicate = re.sub("\\b(your?|me|my)\\b",self._personalize,predicate)
      predicate = re.sub("\\$whose",subject + "'s",predicate)
      predicate = re.sub("\\$who",subject,predicate)
      irc.reply("%s's %s" % (subject, predicate), prefixNick=False)
      
    whose = wrap(whose, ['inChannel', 'text'])

    def compliment(self, irc, msg, args, who):
        """[<who>]
        
        Delivers surreal compliments from the The Surrealist Compliment Generator 
        (http://madsci.org/cgi-bin/cgiwrap/~lynn/jardin/SCG)
        """
        url = 'http://madsci.org/cgi-bin/cgiwrap/~lynn/jardin/SCG'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)
        html_str = html.read()
        soup = BeautifulSoup(html_str)
        text = soup.find('h2').string.replace("\n"," ").strip()
        if who is None:
          irc.reply(text, prefixNick=True)
        else:
          irc.reply(who + ": " + text, prefixNick=False)

    compliment = wrap(compliment, [optional('text')])

    def isitwhiskytime(self, irc, msg, args):
      affirmatives = ['Yes!','Always!','You need to ask?','When is it not?','Yes! (Duh!)']
      irc.reply(affirmatives[randint(0, len(affirmatives)-1)], prefixNick=True)

    isitwhiskeytime = isitwhiskytime

    def stanford(self, irc, msg, args, channel):
      """[<channel>]
      Assign users to groups for a fun recreation of the Stanford Prison Experiment!"""
      nicks = list(irc.state.channels[channel].users)
      prisoners = []
      guards = []
      for nick in nicks:
        if (randint(0,1) == 0) or nick == 'mbklein':
          prisoners.append(nick)
        else:
          guards.append(nick)
      irc.reply('PRISONERS: ' + ', '.join(prisoners), prefixNick=False)
      irc.reply('GUARDS: ' + ', '.join(guards), prefixNick=False)
      irc.reply('SHORTIMERS: mbklein', prefixNick=False)

    stanford = wrap(stanford, ['inChannel'])

    def kayfabe(self, irc, msg, args, channel):
      """[<channel>]
      Assign pro wrestling alignments"""
      nicks = list(irc.state.channels[channel].users)
      groups = [[],[]]
      for nick in nicks:
        groups[randint(0,1)].append(nick)
      irc.reply('FACES: ' + ', '.join(groups[0]), prefixNick=False)
      irc.reply('HEELS: ' + ', '.join(groups[1]), prefixNick=False)
      
    kayfabe = wrap(kayfabe, ['inChannel'])

    def shake(self, irc, msg, args, who):
        """[<who>]
        
        Deliver a Shakespearean insult (from http://www.pangloss.com/seidel/Shaker/index.html)"""
        text = None
        while text == None:
            try:
                soup = self._url2soup('http://www.pangloss.com/seidel/Shaker/index.html?')
            except HTTPError, e:
                irc.reply('http error %s for %s' % (e.code, url), prefixNick=True); return
            except StopParsing, e:
                irc.reply('parsing error %s for %s' % (e.code, url), prefixNick=True); return
            text = soup.find('font').string.replace("\n"," ").strip()
            attribution = soup.find('b')
            if attribution != None:
                text += " [%s]" % attribution.string
            
        if who is None:
          irc.reply(text, prefixNick=True)
        else:
          irc.reply(who + ": " + text, prefixNick=False)
    shake = wrap(shake, [optional('text')])

    def professor(self, irc, msg, args, first, last):
        """<first_name> <last_name>
        
        Generate your Professor Poopypants name"""
        f1 = {'A': 'poopsie', 'B': 'lumpy', 'C': 'buttercup', 'D': 'gidget', 'E': 'crusty', 'F': 'greasy', 'G': 'fluffy', 'H': 'cheeseball', 'I': 'chim-chim', 'J': 'stinky', 'K': 'flunky', 'L': 'boobie', 'M': 'pinky', 'N': 'zippy', 'O': 'goober', 'P': 'doofus', 'Q': 'slimy', 'R': 'loopy', 'S': 'snotty', 'T': 'tulefel', 'U': 'dorkey', 'V': 'squeezit', 'W': 'oprah', 'X': 'skipper', 'Y': 'dinky', 'Z': 'zsa-zsa'}
        l1 = {'A': 'apple', 'B': 'toilet', 'C': 'giggle', 'D': 'burger', 'E': 'girdle', 'F': 'barf', 'G': 'lizard', 'H': 'waffle', 'I': 'cootie', 'J': 'monkey', 'K': 'potty', 'L': 'liver', 'M': 'banana', 'N': 'rhino', 'O': 'bubble', 'P': 'hamster', 'Q': 'toad', 'R': 'gizzard', 'S': 'pizza', 'T': 'gerbil', 'U': 'chicken', 'V': 'pickle', 'W': 'chuckle', 'X': 'tofu', 'Y': 'gorilla', 'Z': 'stinker'}
        l2 = {'A': 'head', 'B': 'mouth', 'C': 'face', 'D': 'nose', 'E': 'tush', 'F': 'breath', 'G': 'pants', 'H': 'shorts', 'I': 'lips', 'J': 'honker', 'K': 'butt', 'L': 'brain', 'M': 'tushie', 'N': 'chunks', 'O': 'hiney', 'P': 'biscuits', 'Q': 'toes', 'R': 'buns', 'S': 'fanny', 'T': 'sniffer', 'U': 'sprinkles', 'V': 'kisser', 'W': 'squirt', 'X': 'humperdinck', 'Y': 'brains', 'Z': 'juice'}
        fname = f1[first[2].upper()]
        lname = l1[last[1].upper()] + l2[last[3].upper()]
        name = ('%s %s' % (fname, lname)).title()
        irc.reply(name.encode('utf-8'), prefixNick=True)
    professor = wrap(professor, ['somethingWithoutSpaces','somethingWithoutSpaces'])

    def chucknorris(self, irc, msg, args):
      """Grab a random Chuck Norris fact from http://www.chucknorrisfacts.com/"""
      soup = self._url2soup('http://www.chucknorrisfacts.com/all-chuck-norris-facts')
      # Ugliest scrape ever. Just go with it.
      max_page = int(dict(soup.findAll('li',{'class' : re.compile(r'\bpager-last\b')})[0].findChildren()[0].attrs)['href'].split('=')[1])
      page = randint(0,max_page)
      soup = self._url2soup('http://www.chucknorrisfacts.com/all-chuck-norris-facts?page=%d' % (page))
      facts = soup.findAll('div',{'class' : 'views-field-title'})
      fact = (''.join(facts[randint(0,len(facts)-1)].findAll('a',text=True))).strip()
      irc.reply(fact.encode('utf-8'), prefixNick=True)
      
    def arch(self, irc, msg, args, thing):
        """THE ARCHITECT SAYS THINGS"""
        if thing is None:
            irc.reply('pulls string...', action=True, prefixNick=False)
            irc.reply('THE ARCHITECT SAYS...BLAH BLAH BLAH BLAH BLAH.', prefixNick=False)
        else:
            irc.reply('THE ARCHITECT ' + thing.upper().encode('utf-8'), prefixNick=False)
    arch = wrap(arch, [optional('text')])

    def beck(self, irc, msg, args):
      """Generate a Glenn Beck conspiracy theory. Stolen from http://politicalhumor.about.com/library/bl-glenn-beck-conspiracy.htm"""
      irc.reply(BeckGenerator().generate().encode('utf-8'), prefixNick=True)

    def pac(self, irc, msg, args):
        """Generate a name for your PAC and turn on the $$ pipe! (via http://is.gd/i6vKS)"""
        opener = build_opener()
        opener.addheaders = [('Accept', 'application/json')]
        data = simplejson.load(opener.open('http://pacgenerator.sunlightfoundation.com/generate'))
        pacname = data['superpac']['name']
        irc.reply(pacname.encode('utf-8', 'ignore'))
    
    def redact(self, irc, msg, args, opts, text):
      """--chance [num]
      
      Randomly redact a piece of text, blacking out 1 in <chance> non-stopwords. (Default: 1 in 4)"""
      chance = 4
      for (opt, arg) in opts:
          if opt == 'chance':
              chance = arg
              
      stop_words = ['a','able','about','across','after','all','almost','also','am','among','an',
        'and','any','are','as','at','be','because','been','but','by','can','cannot',
        'could','dear','did','do','does','either','else','ever','every','for','from',
        'get','got','had','has','have','he','her','hers','him','his','how','however',
        'i','if','in','into','is','it','its','just','least','let',
        'may','me','might','most','must','my','neither','no','nor','not','of','off',
        'often','on','only','or','other','our','said','say','says',
        'she','should','since','so','some','than','that','the','their','them','then',
        'there','these','they','this','tis','to','too','twas','us','wants','was','we',
        'were','what','when','where','which','while','who','whom','why','will','with',
        'would','yet','you','your']
      words = []
      for word in text.split():
        if (randint(1,chance) == 1) and (word.lower() not in stop_words):
          words.append(re.sub(ur'\w','█',word,re.UNICODE))
        else:
          words.append(word)
      irc.reply(' '.join(words))
    redact = wrap(redact, [getopts({'chance':'int'}), 'text'])

    def _google_search(self,q):
      json = urlopen("http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s" % quote(q)).read()
      response = simplejson.loads(json)
      if len(response['responseData']['results']) == 0:
        response['responseData']['cursor']['estimatedResultCount'] = 0
      return response
    
    def intensify(self, irc, msg, args, opts, adjective):
      """[--graph|--raw] [(--prefix|--suffix) <phrase>...] <adjective>
      
      Calculate the frequency with which <adjective> is intensified as described in http://xkcd.com/798/
      (--raw: show raw counts; --graph: display as a lame graph; --prefix/--suffix: use custom intensifiers)"""
      
      graph = False
      raw = False
      intensifiers = []
  
      for (opt,arg) in opts:
          if opt == 'prefix':
            intensifiers.append(arg + ' %s')
          if opt == 'suffix':
            intensifiers.append('%s ' + arg)
          if opt == 'raw':
            raw = True
          if opt == 'graph':
            graph = True

      if len(intensifiers) == 0:
        intensifiers = ['fucking %s','%s as shit']
      
      taken = []        
      def _find_key(string, taken):
        for char in string.replace('%s','').strip():
          if not char.upper() in taken:
            taken.append(char.upper())
            return(char.upper())

      counter = lambda q: float(self._google_search('"%s"' % (q))['responseData']['cursor']['estimatedResultCount'])
      adjective_alone = counter(adjective)
      counts = { 'RAW' : { 'count' : adjective_alone } }
      for phrase in intensifiers:
        c = counter((phrase % adjective).replace(' ','+'))
        counts[phrase] = { 'count' : c, 'phrase' : phrase % adjective, 'marker' : _find_key(phrase, taken) }
        if c > 0:
          counts[phrase]['scale'] = math.log(c/adjective_alone)
          counts[phrase]['string'] = '%.2f' % counts[phrase]['scale']
        else:
          counts[phrase]['scale'] = 0
          counts[phrase]['string'] = 'NaN'

      if graph:
        graph_str = bytearray('-' * 40)
        for phrase in intensifiers:
          pos = int(counts[phrase]['scale'] * 2)
          if graph_str[pos] != 45:
            graph_str[pos] = '*'
          else:
            graph_str[pos] = counts[phrase]['marker']
        irc.reply('[-20]%s[0]' % str(graph_str))
      elif raw:
        response = ["'%s': %d" % (adjective, counts['RAW']['count'])]
        for phrase in intensifiers:
          response.append("'%(phrase)s': %(count)d (%(string)s)" % counts[phrase])
        irc.reply('; '.join(response))
      else:
        response = []
        for phrase in intensifiers:
          response.append("'%(phrase)s': %(string)s" % counts[phrase])
        irc.reply('; '.join(response))
    intensify = wrap(intensify, [getopts({'graph':'','raw':'','prefix':'something','suffix':'something'}), 'text'])

    def complain(self, irc, msg, args, topic):
      pgraphs = 1
      gender = 'c'
      
      opener = build_opener()
      html = opener.open("http://www.pakin.org/complaint?" + urlencode({ 'firstname' : topic, 'pgraphs' : pgraphs, 'gender' : gender }))
      html_str = html.read()
      soup = BeautifulSoup(html_str, convertEntities=BeautifulSoup.HTML_ENTITIES)
      irc.reply(' '.join(map(lambda x: ' '.join(x.findAll(text=True)), soup.findAll('p', limit=pgraphs))).encode('utf-8'), prefixNick=False)
    complain = wrap(complain, ['text'])

    def haverfood(self, irc, msg, args):
        """get the name of a food according to Parks and Recreation's Tom Haverford from http://tomhaverfoods.com/"""
        text = None
        while text == None:
            try:
                soup = self._url2soup('http://tomhaverfoods.com')
            except HTTPError, e:
                irc.reply('http error %s for %s' % (e.code, url), prefixNick=True); return
            except StopParsing, e:
                irc.reply('parsing error %s for %s' % (e.code, url), prefixNick=True); return
            food = soup.find('a')
            text = food.find('p').string + food.find('h2').string
            text = text.replace("\n"," ").strip()
    
        irc.reply(text, prefixNick=True)

    def quakes(self, irc, msg, args, opts, loc):
      """[--min <magnitude>] [<location>]
      List recent earthquakes (optionally near <location>, with magnitude >= <magnitude> [default: 3.5]) from the USGS Atom feed"""
      url = "http://quakes.heroku.com/catalogs/7day-M2.5.json"
      minq = 3.5
      for (opt, arg) in opts:
        if opt == 'min':
          minq = arg
      
      if (loc != None):
        pref = 'Closest quakes (>=%.2f) to %s in the past 7 days: ' % (minq,loc)
        url = url + ("?sort=distance&from=%s" % (loc))
      else:
        pref = 'Quakes (>=%.2f) in the past 7 days: ' % (minq)
        
      json = urlopen(url).read()
      feed = simplejson.loads(json)
      responses = []
      for q in feed:
        if q['magnitude'] >= minq:
          if loc != None:
            s = "%.2f, %.1fmi away (%s, %s ago)" % (q['magnitude'], q['distance']['mi'], q['location'], q['age']['string'])
          else:
            s = "%.2f, %s (%s ago)" % (q['magnitude'], q['location'], q['age']['string'])
          responses.append(s)
        
      irc.reply(pref + '; '.join(responses))
    quakes=wrap(quakes,[getopts({'min':'float'}), optional('text')])

    def occupy(self, irc, msg, args, this, that):
      """1% of <this> controls 99% of <that>"""
      irc.reply(("1%% of the %s control 99%% of the %s" % (this, that)).encode('utf8'), prefixNick=False)
    occupy=wrap(occupy,['something','something'])

    def bitch(self, irc, msg, args, what):
      """It's a plugin, bitches!"""
      irc.reply(u'%s, bitches!' % re.sub(r'[.!?,;:]+$','',what))
    bitch=wrap(bitch,['text'])
    
    def cocktail(self, irc, msg, args):
      """[<who>]
      Mix a random cocktail from http://www.cocktaildb.com/"""
      
      if len(args) > 0:
          nick = ' '.join(args)
      else:
          nick = msg.nick
      req = Request(url='http://www.cocktaildb.com/index?_action_randomRecipe=1')
      resp = urlopen(req)
      soup = BeautifulSoup(resp.read())
      desc = soup.find('meta',{'name':'description'})['content']
      (drink,rest) = re.compile('\s*:\s*').split(desc)
      ingredients = re.compile('\s*,\s*').split(rest)
      last = ingredients.pop()
      if re.compile('[aeiouAEIOU]').match(drink) is None:
        article = 'a'
      else:
        article = 'an'

      text = u'mixes %s and %s to make %s %s, and sends it sliding down the bar to %s (%s)' % (u', '.join(ingredients), last, article, drink, nick, resp.url)
      irc.reply(text.encode('utf-8'), action=True)
    
    def compliment(self, irc, msg, args, who):
        """[<who>]
        Pulls an emergency compliment from http://emergencycompliment.com/"""

        if who is None:
            who = msg.nick
        json = urlopen("http://emergencycompliment.com/js/compliments.js").read()
        compliments = simplejson.loads(re.search('(\[.+\])',json.replace("\n",'')).group(0))
        text = random.choice(compliments)['phrase']
        response = "%s: %s" % (who, text)
        irc.reply(response, prefixNick=False)

    compliment = wrap(compliment,[optional('text')])

    def sortinghat(self, irc, msg, args, who):
        options = ['Gryffindor', 'Ravenclaw', 'Hufflepuff', 'Slytherin']
        if who is None:
            who = msg.nick
        house = random.choice(options)
        irc.reply('Hmm... %s... Let me see now... %s!' % (who, house.upper()), prefixNick=False)

    sortinghat = wrap(sortinghat,[optional('text')])

    def helperz(self, irc, msg, args, who):
        irc.reply("Translation Party is hiring, you know.")

    def rly(self, irc, msg, args, what):
        reply = "%s%s?... Really?%s" % (
            bool(random.getrandbits(1)) and 'Seriously, ' or '',
            what,
            bool(random.getrandbits(1)) and '... REALLY?' or ''
            )
        irc.reply(reply)

    rly = wrap(rly, ['text'])

    def isitrainingin(self, irc, msg, args, where):
        """[<location>]
        Ask http://isitraining.in/<location>"""

        html = urlopen("http://isitraining.in/" + where).read()
        soup = BeautifulSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        answer = soup.find('h1').find(text=True)
        exegesis = re.sub(r'\s+', ' ', ' '.join(soup.find('h2').findAll(text=True)))
        response = u'%s. (%s)' % (answer, exegesis)
        irc.reply(response.encode('utf8'), prefixNick=True)

    isitrainingin = wrap(isitrainingin, ['text'])

    def flip(self, irc, msg, args):
        """Flip a table"""

        if args:
            string = upsidedown.transform(' '.join(args).decode('utf8'))
        else:
            string = u'┻━┻'

        irc.reply(u'╯°□°╯︵{table}'.format(table=string).encode('utf8'), prefixNick=False)

    def deflip(self, irc, msg, args):
        """Puts a table back in place"""

        if args:
            string = upsidedown.transform(' '.join(args).decode('utf8'))
        else:
            string = u'┬──┬'

        irc.reply(u'{table}◡ﾉ(° -°ﾉ)'.format(table=string).encode('utf8'), prefixNick=False)

    def schmipsum(self, irc, msg, args, source, length):
        """<shakespeare|bible|jane_austen|lewis_carroll|patents|nixon_tapes|college_essays|mission_statements|beatrix_potter|frankenstein> <length>
        Generates filler text from real sources, courtesy of schmipsum.com"""

        json = urlopen("http://www.schmipsum.com/ipsum/%s/%d" % (source,length)).read()
        response = simplejson.loads(json)
        ipsum = re.sub(r'\s+', ' ', response['ipsum'])
        irc.reply(ipsum.encode('utf8'))

    schmipsum = wrap(schmipsum, [('literal',('shakespeare','bible','jane_austen','lewis_carroll','patents','nixon_tapes','college_essays','mission_statements','beatrix_potter','frankenstein')), 'int'])
Class = Assorted
