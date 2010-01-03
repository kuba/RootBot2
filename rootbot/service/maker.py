import yaml
import sys
from zope.interface import implements

from twisted.application import internet, service
from twisted.application.service import IServiceMaker
from twisted.python import usage
from twisted.plugin import IPlugin

from rootbot.service import RootBotService
from rootbot.irc import IIRCClientFactory

from rootbot.deploy import initConfig

class ConfigOptions(usage.Options):
    optParameters = [
        ['config', 'c', 'rootbot.conf', "Config file."],
        ]

class InitOptions(ConfigOptions):
    pass

class RunOptions(ConfigOptions):
    pass

class Options(usage.Options):
    subCommands = [['init', None, InitOptions, "Initialize config."],
                   ['run', None, RunOptions, "Run bot."]]


class RootBotServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "rootbot"
    description = "Run RootBot2!"
    options = Options

    def makeService(self, options):
        if options.subCommand == 'init':
            initConfig(options.subOptions['config'])
            print "You can now edit your config."
            print "When you're done try:"
            print "twistd rootbot init -c %s" % options.subOptions['config']
            sys.exit()
        elif options.subCommand == 'run':
            return self.runRootBot(options.subOptions)
        else:
            print options.getUsage()
            sys.exit()

    def runRootBot(self, options):
        try:
            config_file = open(options['config'], 'r')
        except IOError:
            print "Specified config file (%s) does not exist!" % options['config']
            print "To create one, invoke `twistd rootbot init`" % options['config']
            sys.exit()
        config = yaml.load(config_file)

        servers = config['servers']
        shortener_login = config['shortener']['login']
        shortener_api_key = config['shortener']['api_key']

        s = service.MultiService()
        rootbot = RootBotService(servers, shortener_login, shortener_api_key)

        # IRC RootBot
        if config['transports'].has_key('irc'):
            configirc = config['transports']['irc']
            irc = IIRCClientFactory(rootbot)
            irc.nickname = configirc['nick']
            irc.password = configirc['password']
            irc.channel = configirc['channel']
            ircserver = configirc['server']
            ircbot = internet.TCPClient(ircserver, 6667, irc)
            ircbot.setServiceParent(s)
        return s
