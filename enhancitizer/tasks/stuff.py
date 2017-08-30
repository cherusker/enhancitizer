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

from utils.printer import Printer

class TaskSummary(object):
    """Print various stats about the reports"""
    
    def setup(self, options):
        self.__printer = Printer(options)
        # sanitizer.category.(new|old)
        self.__data = OrderedDict()

    def process(self, report):
        sanitizer_name = report.sanitizer
        category_name = report.category
        if not sanitizer_name in self.__data:
            self.__data[sanitizer_name] = OrderedDict()
        if not category_name in self.__data[sanitizer_name]:
            self.__data[sanitizer_name][category_name] = { 'new': 0, 'old': 0 }
        self.__data[sanitizer_name][category_name]['new' if report.new else 'old'] += 1

    def teardown(self):
        self.__printer.task_description('Summary:')
        if len(self.__data) < 1:
            self.__printer.task_info('nothing found')
        else:
            for sanitizer_name, categories in sorted(self.__data.items(), key=lambda s: s[0]):
                self.__printer.just_print('  ' + sanitizer_name + ':')
                for category_name, count in sorted(categories.items(), key=lambda c: c[0]):
                    new = count['new']
                    self.__printer.just_print('    ' + category_name + ': ' +
                          str(count['old'] + new) + ' (' + str(new) + ' new)')
        self.__printer.nl()
