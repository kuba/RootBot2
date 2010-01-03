import re

from zope.interface import Interface, implements

from twisted.internet import protocol
from twisted.words.protocols import irc
from twisted.python import components

from rootbot.service import IRootBotService

class IRCUser(object):
    pass


class IRCReplyBot(irc.IRCClient):
    """
    IRC Bot, have fun!

    """
    def connectionMade(self):
        """
        Set nickname and password to authenticate
        to irc services when connection is made.

        """
        self.nickname = self.factory.nickname
        self.password = self.factory.password
        irc.IRCClient.connectionMade(self)

    def signedOn(self):
        """
        Join channel when signed on.

        """
        channel = self.factory.channel
        self.join(channel)

    def privmsg(self, user, channel, msg):
        """
        Gets called we get *any* message from server.

        :param user: user!@host
        :type user: :class:`string`

        :param channel: Public channel or PM
        :type channel: :class:`str`

        :param msg: Message written to :attr:`channel`
        :type msg: :class:`str`

        """
        user = user.split('!')[0]

        if self.nickname.lower() == channel.lower():
            self.handlePrivateMessage(user, channel, msg)
        elif msg.startswith(self.nickname + ':'):
            direct = msg[len(self.nickname + ':'):].strip()
            self.handleDirectMessage(user, channel, direct)
        else:
            self.handlePublicMessage(user, channel, msg)

    def handlePrivateMessage(self, user, channel, msg):
        """
        Called when we get private meassage.

        """
        pass

    def handleDirectMessage(self, user, channel, msg):
        """
        Called when we get direct message on the public channel,
        like ':attr:`nickname`:.

        """
        if re.match('s$', msg):
            stats = self.factory.getShortStats()
            self.msg(channel, stats)
        elif re.match('stat$', msg):
            for stat in self.factory.getLongStats():
                self.msg(channel, stat)

    def handlePublicMessage(self, user, channel, msg):
        """
        Called when public message is sent to channel, runs filters.

        """
        self.filters = [self.pastebin, self.ujeb]

        for filter in self.filters:
            msg = filter(user, channel, msg)
            if msg is None:
                break

    def pastebin(self, user, channel, msg):
        """
        Check if message doesn't contain unwated pastie-like service url.

        .. todo: check for abuse, eg. kick user after 3 times

        """
        pastebin = re.compile('https?://(' +\
            'pastebin\.com|' + \
            'wklej\.to|' + \
            'paste\.pocoo\.org|' + \
            'pastebin\.pl|' + \
            'codepad\.org|' + \
            'pastebin\.ca|' + \
            'pastie\.org|' + \
            'pastebin\.4programmers\.net)')
        if pastebin.search(msg):
            self.msg(channel, 'I will kick you, Bastard! wklej.org RULEZZZZ')
            return
        return msg

    def ujeb(self, user, channel, msg):
        """
        Check if message contains url and try to trim it!

        If trimmed message is longer that original one,
        don't send it to channel.

        """
        http = re.compile('(https?://[^\s]+)')
        if http.search(msg):
            for url in http.findall(msg):
                ujebany = self.factory.shortenURL(url)
                ujebany.addCallback(
                    lambda u: len(u) < len(url) and self.msg(channel, u)
                    )
        return msg


class IIRCClientFactory(Interface):
    """
    Interface for IRC Client Factory

    """

    def getStats(server):
        """ Return long formatted stats for given server """

    def getShortStats():
        """ Return short formatted stats for all servers"""

    def getLongStats():
        """ Return long formatted stats for all servers"""


class IRCClientFactoryFromService(protocol.ReconnectingClientFactory):
    """
    Adapter which creates IRC client factory from service.

    """
    implements(IIRCClientFactory)

    protocol = IRCReplyBot
    nickname = None
    password = None
    channel = None

    def __init__(self, service):
        self.service = service

    def getStats(self, server):
        return self.service.getStats(server)

    def getShortStats(self):
        return self.service.getShortStats()

    def getLongStats(self):
        return self.service.getLongStats()

    def shortenURL(self, link):
        return self.service.shortenURL(link)

components.registerAdapter(IRCClientFactoryFromService,
                           IRootBotService,
                           IIRCClientFactory)
