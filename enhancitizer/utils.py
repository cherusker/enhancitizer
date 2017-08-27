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
import os

class NameCounter(object):
    """Counts values with certain names and keeps an alphabetical order"""
    
    def __init__(self):
        self.data = OrderedDict()

    def inc(self, name):
        """Increases the counter of name and returns the increased value"""
        if name in self.data:
            self.data[name] += 1
        else:
            self.data.update({ name: 1 })
            self.data = OrderedDict(sorted(self.data.items(), key=lambda t: t[0]))
        return self.get(name)

    def get(self, name):
        """Returns the count of name (0 for nonexisting namea)"""
        return self.data.get(name, 0)

    def set(self, name, value):
        """Sets the counter of name and returns the value"""
        if name in self.data:
            self.data[name] = value
        else:
            self.data.update({ name: value })
            self.data = OrderedDict(sorted(self.data.items(), key=lambda t: t[0]))
        return self.get(name)

class FileUtils(object):
    """Collection to deal with files"""

    def create_folders(file_path):
        """Creates necessary folders in order to write file_path"""
        dirname = os.path.dirname(file_path)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
