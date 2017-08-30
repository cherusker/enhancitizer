# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

import os
import re
import shutil

def makedirs(dir_path, empty=False):
    """Guarantees that dir_path is an (empty) directory after this function is done"""
    if os.path.isfile(dir_path):
        os.remove(dir_path)
    elif os.path.isdir(dir_path) and empty:
        shutil.rmtree(dir_path)
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

def report_file_path(dir_path, report_no):
    return os.path.join(dir_path, str(report_no).zfill(5) + '.report')

class SourceCodeLine(object):
    """Represents one line of a source code file"""

    __count_indent_pattern = re.compile('^(?P<indent>\s*)[^\s]?')

    def __init__(self, file_path, num):
        self.file_path = file_path
        self.num = num
        self.__line = None
        self.__indent = None

    @property
    def line(self):
        if not self.__line:
            self.__extract()
        return self.__line

    @property
    def indent(self):
        if not self.__indent:
            self.__extract()
        return self.__indent

    def __extract(self):
        with open(self.file_path, 'r') as src_file:
            for i, line in enumerate(src_file):
                if i == self.num - 1:
                    count_indent = self.__count_indent_pattern.search(line)
                    self.__indent = 0 if not count_indent else len(count_indent.group('indent'))
                    self.__line = line.strip()
                    break
            src_file.close()
