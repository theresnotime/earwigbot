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

__all__ = ["ConfigNode"]

class ConfigNode(object):
    def __iter__(self):
        for key in self.__dict__:
            yield key

    def __getitem__(self, item):
        return self.__dict__.__getitem__(item)

    def _dump(self):
        data = self.__dict__.copy()
        for key, val in data.iteritems():
            if isinstance(val, ConfigNode):
                data[key] = val._dump()
        return data

    def _load(self, data):
        self.__dict__ = data.copy()

    def _decrypt(self, cipher, intermediates, item):
        base = self.__dict__
        for inter in intermediates:
            try:
                base = base[inter]
            except KeyError:
                return
        if item in base:
            ciphertext = base[item].decode("hex")
            base[item] = cipher.decrypt(ciphertext).rstrip("\x00")

    def get(self, *args, **kwargs):
        return self.__dict__.get(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def iterkeys(self):
        return self.__dict__.iterkeys()

    def itervalues(self):
        return self.__dict__.itervalues()

    def iteritems(self):
        return self.__dict__.iteritems()
