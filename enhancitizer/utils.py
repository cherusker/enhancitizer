# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

class NameCounter:
    """Counts values with certain names"""
    
    def __init__(self):
        self.data = {}

    def inc(self, name):
        """Increases the count of name and returns the increased value"""
        if name in self.data:
            self.data[name] += 1
        else:
            self.data[name] = 1
        return self.data[name]
