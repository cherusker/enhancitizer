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

from bank.extraction import Report
from options import Options
from utils import FileUtils

class TaskCreateBlacklist:
    """Base class for creating blacklists; can be inherited to make more sense"""

    blacklists_dir_path = 'blacklists'

    def __init__(self, sanitizer_name, stack_title_pattern, blacklist_file_name):
        self.sanitizer_name = sanitizer_name
        self.stack_title_pattern = stack_title_pattern
        self.blacklist_file_path = os.path.join(Options.output_root_path, self.blacklists_dir_path, blacklist_file_name)

    def setup(self):
        self.data = OrderedDict()

    def process_report(self, meta_report):
        if meta_report.sanitizer == self.sanitizer_name:
            for stack in Report(meta_report).call_stacks:
                stack_item = stack.items[0]
                if self.stack_title_pattern.search(stack.title) and stack_item.complete():
                    file_name = stack_item.src_file_name
                    func_name = stack_item.func_name
                    if not file_name in self.data:
                        print('  adding ' + func_name)
                        self.data[file_name] = { func_name }
                    elif not func_name in self.data[file_name]:
                        print('  adding ' + func_name)
                        self.data[file_name].add(func_name)

    def teardown(self):
        print('  creating ' + self.blacklist_file_path)
        FileUtils.create_folders(self.blacklist_file_path)
        with open(self.blacklist_file_path, 'w') as blacklist_file:
            for file_name, func_names in sorted(self.data.items(), key=lambda d: d[0]):
                blacklist_file.write('\n# ' + file_name + ' #\n\n')
                for func_name in func_names:
                    blacklist_file.write('fun:' + func_name + '\n')
            blacklist_file.close()

class TaskCreateTSanBlacklist(TaskCreateBlacklist):

    description = 'Creating TSan blacklist ...'

    tsan_sanitizer_name = 'ThreadSanitizer'
    tsan_stack_title_pattern = re.compile('(?:read|write)\sof\ssize', re.IGNORECASE)
    tsan_blacklist_file_name = 'clang-tsan-blacklist'

    def __init__(self):
        super().__init__(self.tsan_sanitizer_name, self.tsan_stack_title_pattern, self.tsan_blacklist_file_name)
