# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

from collections import OrderedDict
import time

class StopWatch(object):
    """Counts the time between start() and str() and formats the output string"""

    __units = ['s', 'ms', 'us', 'ns', 'ps']

    def __init__(self):
        self.__time = None

    def start(self):
        self.__time = time.time()
        return self

    def __str__(self):
        t = 0 if not self.__time else time.time() - self.__time
        if t <= 0:
            return '0 s'
        u = 0
        while t < 1 and u < len(self.__units) - 1:
            t *= 1000
            u += 1
        return str(round(t)) + ' ' + self.__units[u]

class NameCounter(object):
    """Counts values with certain names and keeps an alphabetical order"""
    
    def __init__(self):
        self.data = OrderedDict()

    def inc(self, name):
        """Increases the counter of name and returns the increased value"""
        if name in self.data:
            self.data[name] += 1
        else:
            self.data[name] = 1
            self.data = OrderedDict(sorted(self.data.items(), key=lambda t: t[0]))
        return self[name]

    def get(self, name):
        """Returns the count of name (0 for nonexisting namea)"""
        return self.data.get(name, 0)

    def set(self, name, value):
        """Sets the counter of name and returns the value"""
        if name in self.data:
            self.data[name] = value
        else:
            self.data[name] = value
            self.data = OrderedDict(sorted(self.data.items(), key=lambda t: t[0]))
        return self.data[name]
