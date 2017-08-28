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

import utils.os

class TaskCompactReports(object):

    description = 'Compacting reports ...'

    def setup(self):
        # sanitizer.category.count
        self.__data = {}

    def process(self, report):
        sanitizer = report.sanitizer
        category = report.category
        orig_no = report.no
        if not self.__data.get(sanitizer):
            self.__data.update({ sanitizer: {} })
        if not self.__data.get(sanitizer).get(category):
            self.__data.get(sanitizer).update({ category: 0 })
        self.__data.get(sanitizer)[category] += 1
        new_no = self.__data.get(sanitizer).get(category)
        if new_no != orig_no:
            orig_report_str = str(report)
            new_file_path = utils.os.report_file_path(os.path.dirname(report.file_path), new_no)
            os.rename(report.file_path, new_file_path)
            report.no = new_no
            report.file_path = new_file_path
            print('  renaming: ' + orig_report_str + ' -> ' + str(report))
