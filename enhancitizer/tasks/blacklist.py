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

from utils import FileUtils

class TaskCreateBlacklist(object):
    """Base class for creating blacklists; can be inherited to make more sense"""

    __blacklists_dir_path = 'blacklists'

    def __init__(self, options, sanitizer_name, stack_title_pattern, blacklist_file_name):
        self.__sanitizer_name = sanitizer_name
        self.__stack_title_pattern = stack_title_pattern
        self.__blacklist_file_path = os.path.join(
            options.output_root_path, self.__blacklists_dir_path, blacklist_file_name)

    def setup(self):
        self.__data = OrderedDict()

    def process(self, report):
        if report.sanitizer == self.__sanitizer_name:
            for stack in report.call_stacks:
                item = stack.items[0]
                if self.__stack_title_pattern.search(stack.title) and item.complete:
                    file_name = item.src_file_name
                    func_name = item.func_name
                    if not file_name in self.__data:
                        self.__data[file_name] = set()
                    print('  adding ' + func_name)
                    self.__data.get(file_name).add(func_name)

    def teardown(self):
        print('  creating ' + self.__blacklist_file_path)
        FileUtils.create_folders(self.__blacklist_file_path)
        with open(self.__blacklist_file_path, 'w') as blacklist_file:
            for file_name, func_names in sorted(self.__data.items(), key=lambda d: d[0]):
                blacklist_file.write('\n# ' + file_name + ' #\n\n')
                for func_name in func_names:
                    blacklist_file.write('fun:' + func_name + '\n')
            blacklist_file.close()

class TaskCreateTSanBlacklist(TaskCreateBlacklist):

    description = 'Creating TSan blacklist ...'

    __tsan_sanitizer_name = 'ThreadSanitizer'
    __tsan_stack_title_pattern = re.compile('(?:read|write)\sof\ssize', re.IGNORECASE)
    __tsan_blacklist_file_name = 'clang-tsan-blacklist'

    def __init__(self, options):
        super(TaskCreateTSanBlacklist, self).__init__(options,
                         self.__tsan_sanitizer_name,
                         self.__tsan_stack_title_pattern,
                         self.__tsan_blacklist_file_name)
