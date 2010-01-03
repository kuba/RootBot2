# -*- coding: utf-8 -*-

import json
from datetime import timedelta
import urllib

from zope.interface import Interface, implements

from twisted.application import service
from twisted.internet import defer, reactor
from twisted.web.client import getPage

from rootbot.statobot import StatobotClientFactory


class IRootBotService(Interface):
    def getStats(server):
        """ Return long formatted stats for given server """

    def getShortStats():
        """ Return short formatted stats for all servers"""

    def getLongStats():
        """ Return long formatted stats for all servers"""

    def shortenURL(link):
        """ Return deferred returning shortened URL """


class RootBotService(service.Service):
    implements(IRootBotService)

    def __init__(self, servers, shortener_login, shortener_api_key):
        """
        Connect to stat servers and start to monitor them.
        
        """
        self.shortener_login = shortener_login
        self.shortener_api_key = shortener_api_key
        TIMER = 5 # seconds
        TIMEOUT = 4
        self.servers = {}
        for server in servers:
            name = server['name']
            short = server['short']
            ip = server['ip']
            port = server['port']

            f = StatobotClientFactory(name, short, ip, TIMER, TIMEOUT)
            reactor.connectTCP(ip, port, f)
            self.servers[name] = f

    def getServer(self, name):
        """
        Return a server's factory by given name.

        """
        return self.servers[name]

    def getShortStats(self):
        stats = []
        for server in self.servers.values():
            s = server.getCurrentStats()
            stats.append(server.short+'->'+s.formatShort())
        return ' | '.join(stats)

    def getLongStats(self):
        stats = []
        for server in self.servers.values():
            s = server.getCurrentStats()
            stats.append('*%s* %s' % (server.name, s.formatLong()))
        return stats

    def getStats(self, server_name):
        server = self.getServer(server_name)
        stats = server.getCurrentStats()
        return stats.formatLong()

    def shortened(self, raw):
        response = json.loads(raw)
        r = response['results']
        for s in r:
            a = r[s]['shortUrl']
            return a.encode('utf-8')

    def shortenURL(self, link):
        qs = {'version' : '2.0.1',
              'login' : self.shortener_login,
              'apiKey' : self.shortener_api_key,
              'longUrl' : link}
        d = getPage('http://api.bit.ly/shorten?' + urllib.urlencode(qs))
        d.addCallback(self.shortened)
        return d
