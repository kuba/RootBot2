from pkg_resources import Requirement, resource_filename

def initConfig(config_filename):
    template_file = resource_filename(Requirement.parse("RootBot"), "rootbot.conf_tmpl")
    template = open(template_file).read()
    conf = open(config_filename, 'w')
    conf.write(template)
    conf.close()
    return True
