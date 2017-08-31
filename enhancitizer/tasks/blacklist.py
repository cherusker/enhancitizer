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

    __blacklists_dir_name = 'blacklists'
    __blacklist_file_ending = '.blacklist'

    def _setup(self, options, sanitizer_name_short):
        self.__blacklist_file_path = os.path.join(
            options.output_root_path, self.__blacklists_dir_name,
            'clang-' + sanitizer_name_short + self.__blacklist_file_ending)
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

    __supported_sanitizer_name_short = 'tsan'
    __supported_category_names = ['data race']

    def setup(self, options):
        self._setup(options, self.__supported_sanitizer_name_short)

    def process(self, report):
        if report.sanitizer.name_short == self.__supported_sanitizer_name_short and \
           report.category_name in self.__supported_category_names:
            for stack in report.call_stacks:
                if 'tsan_data_race_type' in stack.special:
                    self._add_stack_frame(stack.frames[0])
