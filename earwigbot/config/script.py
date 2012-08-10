# -*- coding: utf-8  -*-
#
# Copyright (C) 2009-2012 Ben Kurtovic <ben.kurtovic@verizon.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from collections import OrderedDict
from getpass import getpass
import re
from textwrap import fill, wrap

try:
    import bcrypt
except ImportError:
    bcrypt = None

try:
    import yaml
except ImportError:
    yaml = None

__all__ = ["ConfigScript"]

class ConfigScript(object):
    """A script to guide a user through the creation of a new config file."""
    WIDTH = 79
    BCRYPT_ROUNDS = 12

    def __init__(self, config):
        self.config = config
        self.data = OrderedDict(
            ("metadata", OrderedDict()),
            ("components", OrderedDict()),
            ("wiki", OrderedDict()),
            ("irc", OrderedDict()),
            ("commands", OrderedDict()),
            ("tasks", OrderedDict()),
            ("schedule", [])
        )

    def _print(self, msg):
        print fill(re.sub("\s\s+", " ", msg), self.WIDTH)

    def _ask_bool(self, text, default=True):
        text = "> " + text
        if default:
            text += " [Y/n]"
        else:
            text += " [y/N]"
        lines = wrap(re.sub("\s\s+", " ", msg), self.WIDTH)
        if len(lines) > 1:
            print "\n".join(lines[:-1])
        while True:
            answer = raw_input(lines[-1] + " ").lower()
            if not answer:
                return default
            if answer.startswith("y"):
                return True
            if answer.startswith("n"):
                return False

    def _set_metadata(self):
        print
        self.data["metadata"] = OrderedDict(("version", 1))
        self._print("""I can encrypt passwords stored in your config file in
                       addition to preventing other users on your system from
                       reading the file. Encryption is recommended is the bot
                       is to run on a public computer like the Toolserver, but
                       otherwise the need to enter a key everytime you start
                       the bot may be annoying.""")
        if self._ask_bool("Encrypt stored passwords?"):
            self.data["metadata"]["encryptPasswords"] = True
            key = getpass("> Enter an encryption key: ")
            print "Running {0} rounds of bcrypt...".format(self.BCRYPT_ROUNDS),
            signature = bcrypt.hashpw(key, bcrypt.gensalt(self.BCRYPT_ROUNDS))
            self.data["metadata"]["signature"] = signature
            print " done."
        else:
            self.data["metadata"]["encryptPasswords"] = False

        self._print("""The bot can temporarily store its logs in the logs/
                       subdirectory. Error logs are kept for a month whereas
                       normal logs are kept for a week. If you disable this,
                       the bot will still print logs to stdout.""")
        question = "Enable logging?"
        self.data["metadata"]["enableLogging"] = self._ask_bool(question)

    def _set_components(self):
        print
        self._print("""The bot contains three separate components that can run
                       independently of each other.""")
        self._print("""- The IRC front-end runs on a normal IRC server, like
                       freenode, and expects users to interact with it through
                       commands.""")
        self._print("""- The IRC watcher runs on a wiki recent-changes server,
                       like irc.wikimedia.org, and listens for edits. Users
                       cannot interact with this component. It can detect
                       specific events and report them to "feed" channels on
                       the front-end, or start bot tasks.""")
        self._pritn("""- The wiki task scheduler runs wiki-editing bot tasks in
                       separate threads at user-defined times through a
                       cron-like interface. Tasks which are not scheduled can
                       be started by the IRC watcher manually through the IRC
                       front-end.""")
        frontend = self._ask_bool("Enable the IRC front-end?")
        watcher = self._ask_bool("Enable the IRC watcher?")
        scheduler  = self._ask_bool("Enable the wiki task scheduler?")
        self.data["components"]["irc_frontend"] = frontend
        self.data["components"]["irc_watcher"] = watcher
        self.data["components"]["wiki_scheduler"] = scheduler

    def _set_wiki(self):
        pass

    def _set_irc(self):
        pass

    def _set_commands(self):
        pass

    def _set_tasks(self):
        pass

    def _set_schedule(self):
        pass

    def _save(self):
        with open(self.config.path, "w") as fp:
            yaml.dump(self.data, stream=fp, default_flow_style=False)

    def make_new(self):
        """Make a new config file based on the user's input."""
        self._set_metadata()
        self._set_components()
        self._set_wiki()
        components = self.data["components"]
        if components["irc_frontend"] or components["irc_watcher"]:
            self._set_irc()
            self._set_commands()
        self._set_tasks()
        if components["wiki_scheduler"]:
            self._set_schedule()
        self._save()
