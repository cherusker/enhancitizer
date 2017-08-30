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

import utils.files
from utils.printer import Printer

class TaskCompactReports(object):

    description = 'Compacting reports ...'

    def setup(self, options):
        self.__printer = Printer(options)
        # sanitizer.category.count
        self.__data = {}

    def process(self, report):
        sanitizer = report.sanitizer
        category = report.category
        orig_no = report.no
        if not sanitizer in self.__data:
            self.__data[sanitizer] = {}
        if not category in self.__data[sanitizer]:
            self.__data[sanitizer][category] = 0
        self.__data[sanitizer][category] += 1
        new_no = self.__data[sanitizer][category]
        if new_no != orig_no:
            orig_report_str = str(report)
            new_file_path = utils.files.report_file_path(os.path.dirname(report.file_path), new_no)
            os.rename(report.file_path, new_file_path)
            report.no = new_no
            report.file_path = new_file_path
            self.__printer.task_info('renaming: ' + orig_report_str + ' -> ' + str(report))
