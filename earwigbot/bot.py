# -*- coding: utf-8  -*-
#
# Copyright (C) 2009-2012 by Ben Kurtovic <ben.kurtovic@verizon.net>
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

import threading
from time import sleep, time

from earwigbot.commands import CommandManager
from earwigbot.config import BotConfig
from earwigbot.irc import Frontend, Watcher
from earwigbot.tasks import task_manager

__all__ = ["Bot"]

class Bot(object):
    """
    The Bot class is the core of EarwigBot, essentially responsible for
    starting the various bot components and making sure they are all happy. An
    explanation of the different components follows:

    EarwigBot has three components that can run independently of each other: an
    IRC front-end, an IRC watcher, and a wiki scheduler.
    * The IRC front-end runs on a normal IRC server and expects users to
      interact with it/give it commands.
    * The IRC watcher runs on a wiki recent-changes server and listens for
      edits. Users cannot interact with this part of the bot.
    * The wiki scheduler runs wiki-editing bot tasks in separate threads at
      user-defined times through a cron-like interface.
    """

    def __init__(self, root_dir):
        self.config = BotConfig(root_dir)
        self.logger = logging.getLogger("earwigbot")
        self.commands = CommandManager(self)
        self.tasks = None
        self.frontend = None
        self.watcher = None

        self.component_lock = threading.Lock()
        self._keep_looping = True

    def _start_irc_components(self):
        if self.config.components.get("irc_frontend"):
            self.logger.info("Starting IRC frontend")
            self.frontend = Frontend(self)
            threading.Thread(name=name, target=self.frontend.loop).start()

        if self.config.components.get("irc_watcher"):
            self.logger.info("Starting IRC watcher")
            self.watcher = Watcher(self)
            threading.Thread(name=name, target=self.watcher.loop).start()

    def _start_wiki_scheduler(self):
        def wiki_scheduler():
            while self._keep_looping:
                time_start = time()
                task_manager.schedule()
                time_end = time()
                time_diff = time_start - time_end
                if time_diff < 60:  # Sleep until the next minute
                    sleep(60 - time_diff)

        if self.config.components.get("wiki_scheduler"):
            self.logger.info("Starting wiki scheduler")
            threading.Thread(name=name, target=wiki_scheduler).start()

    def _stop_irc_components(self):
        if self.frontend:
            self.frontend.stop()
        if self.watcher:
            self.watcher.stop()

    def _loop(self):
        while self._keep_looping:
            with self.component_lock:
                if self.frontend and self.frontend.is_stopped():
                    self.frontend = Frontend(self)
                    threading.Thread(name=name, target=self.frontend.loop).start()
                if self.watcher and self.watcher.is_stopped():
                    self.watcher = Watcher(self)
                    threading.Thread(name=name, target=self.watcher.loop).start()
            sleep(5)

    def run(self):
        self.config.load()
        self.config.decrypt(config.wiki, "password")
        self.config.decrypt(config.wiki, "search", "credentials", "key")
        self.config.decrypt(config.wiki, "search", "credentials", "secret")
        self.config.decrypt(config.irc, "frontend", "nickservPassword")
        self.config.decrypt(config.irc, "watcher", "nickservPassword")       
        self.commands.load()     
        self._start_irc_components()
        self._start_wiki_scheduler()
        self._loop()

    def restart(self):
        with self.component_lock:
            self._stop_irc_components()
            self.config.load()
            self.commands.load()
            self._start_irc_components()

    def stop(self):
        self._stop_irc_components()
        self._keep_looping = False
        sleep(3)  # Give a few seconds to finish closing IRC connections
