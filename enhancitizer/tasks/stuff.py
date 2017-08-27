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

class TaskSummary(object):
    """Print various stats about the reports"""
    
    def setup(self):
        # sanitizer.category.(new|old)
        self.__data = OrderedDict()

    def process(self, report):
        sanitizer_name = report.sanitizer
        category_name = report.category
        if not sanitizer_name in self.__data:
            self.__data.update({ sanitizer_name: OrderedDict() })
        if not category_name in self.__data.get(sanitizer_name):
            self.__data.get(sanitizer_name).update({ category_name: { 'new': 0, 'old': 0 } })
        self.__data.get(sanitizer_name).get(category_name)['new' if report.new else 'old'] += 1

    def teardown(self):
        print('Summary:')
        if len(self.__data) < 1:
            print('  nothing found')
        else:
            for sanitizer_name, categories in sorted(self.__data.items(), key=lambda s: s[0]):
                print('  ' + sanitizer_name + ':')
                for category_name, count in sorted(categories.items(), key=lambda c: c[0]):
                    new = count.get('new')
                    print('    ' + category_name + ': ' +
                          str(count.get('old') + new) + ' (' + str(new) + ' new)')
        print()
