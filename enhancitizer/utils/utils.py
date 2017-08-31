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
