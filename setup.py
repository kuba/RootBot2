from setuptools import setup, find_packages

setup(
        name="RootBot",
        version="0.1dev",

        packages=find_packages(),
        data_files = [('twisted/plugins', ['twisted/plugins/rootbot_plugin.py']), ('.', ['rootbot.conf_tmpl'])],
        include_package_data = True,

        zip_safe = False,

        install_requires = ['twisted>=8.2.0',
                            'PyYAML>=3.09',
                            'Statobot>=0.1dev'],

        author = "Jakub Warmuz",
        author_email = "jakub.warmuz@gmail.com",
        description = "Bot for http://rootnode.net related services.",
        keywords = "bot irc rootnode",
)
