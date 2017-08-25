# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

class Counter:

    def __init__(self):
        self.data = {}

    # increase name and get the increased value
    def inc(self, name):
        if name in self.data:
            self.data[name] += 1
        else:
            self.data[name] = 1
        return self.data[name]
