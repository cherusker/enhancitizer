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

class NameCounter:
    """Counts values with certain names and keeps an alphabetical order"""
    
    def __init__(self):
        self.data = OrderedDict()

    def inc(self, name):
        """Increases the count of name and returns the increased value"""
        if name in self.data:
            self.data[name] += 1
        else:
            self.data.update({name: 1})
            self.data = OrderedDict(sorted(self.data.items(), key=lambda t: t[0]))
        return self.data[name]

class FileUtils:
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
