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
import re

import utils.files
from utils.printer import Printer

class TaskCreateBlacklist(object):
    """Base class for creating blacklists; can be inherited to make more sense"""

    __blacklists_dir_path = 'blacklists'

    def _setup(self, options, sanitizer_name):
        self.__blacklist_file_path = os.path.join(
            options.output_root_path, self.__blacklists_dir_path,
            'clang-' + sanitizer_name.lower() + '-blacklist')
        # dir_name.file_name.func_name
        self.__printer = Printer(options)
        self.__data = OrderedDict()

    def _add_stack_frame(self, frame):
        if frame.complete:
            dir_name = frame.src_file_dir_rel_path
            file_name = frame.src_file_name
            func_name = frame.func_name
            if not dir_name in self.__data:
                self.__data[dir_name] = OrderedDict()
            if not file_name in self.__data[dir_name]:
                self.__data[dir_name][file_name] = []
            if not func_name in self.__data[dir_name][file_name]:
                self.__data[dir_name][file_name].append(func_name)
            self.__printer.task_info('adding ' + func_name + ' (' + frame.src_file_rel_path + ')')

    def teardown(self):
        self.__printer.task_info('creating ' + self.__blacklist_file_path)
        utils.files.makedirs(os.path.dirname(self.__blacklist_file_path))
        with open(self.__blacklist_file_path, 'w') as blacklist_file:
            for dir_name, files in sorted(self.__data.items(), key=lambda d: d[0]):
                blacklist_file.write(
                    '# --------------------------------------------------------------------------- #\n' +
                    '#   ' + dir_name + (' ' * (74 - len(dir_name)))+ '#\n' +
                    '# --------------------------------------------------------------------------- #\n\n')
                for file_name, func_names in sorted(files.items(), key=lambda f: f[0]):
                    blacklist_file.write('# ' + file_name + ' #\n\n')
                    for func_name in sorted(func_names):
                        blacklist_file.write('fun:' + func_name + '\n')
                    blacklist_file.write('\n')
            blacklist_file.close()

class TaskCreateTSanBlacklist(TaskCreateBlacklist):

    description = 'Creating TSan blacklist ...'

    __sanitizer_name = 'ThreadSanitizer'
    __supported_categories = ['data race']

    def setup(self, options):
        self._setup(options, self.__sanitizer_name)

    def process(self, report):
        if report.sanitizer == self.__sanitizer_name and report.category in self.__supported_categories:
            for stack in report.call_stacks:
                if 'tsan_data_race_type' in stack.special:
                    self._add_stack_frame(stack.frames[0])
