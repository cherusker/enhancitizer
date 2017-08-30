# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

import csv
import os
import re

from utils.printer import Printer

class TaskCsvSummary(object):
    """Summarise the reports and collect the info in CSV files"""

    description = 'Summarising the reports ...'

    __csv_file_name = 'summary.csv'
    __csv_delimiter = ','

    def _setup(self, options):
        self.__printer = Printer(options)
        self.__csv_files = {}

    def _add_row(self, dir_path, row):
        if not dir_path in self.__csv_files:
            csv_file_path = os.path.join(dir_path, self.__csv_file_name)
            csv_file = open(csv_file_path, 'w')
            if csv_file:
                self.__printer.task_info('creating ' + csv_file_path)
                self.__csv_files[dir_path] = {
                    'file': csv_file,
                    'writer': csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
                }
        self.__csv_files[dir_path]['writer'].writerow([str(cell) for cell in row])

    def teardown(self):
        for csv_file in self.__csv_files.values():
            csv_file['file'].close()

class TaskTSanCsvSummary(TaskCsvSummary):
    """The TSan way of summarising reports"""

    __sanitizer_name = 'ThreadSanitizer'
    __supported_categories = ['data race']
    __expected_funcs_per_report = 2
    __field_names = ['folder', 'file', 'function', 'op', 'size']

    def setup(self, options):
        self._setup(options)
        self.__header_row = ['id'] + \
                            self.__field_names + \
                            list(reversed(self.__field_names)) + \
                            ['global location']

    def process(self, report):
        if report.sanitizer == self.__sanitizer_name and report.category in self.__supported_categories:
            if self.__header_row:
                self._add_row(report.dir_path, self.__header_row)
                self.__header_row = None
            row = [report.no]
            func_no = 0
            for stack in report.call_stacks:
                if 'tsan_data_race_type' in stack.special and len(stack.frames) > 0:
                    func_no += 1
                    details = [
                        stack.frames[0].src_file_dir_rel_path,
                        stack.frames[0].src_file_name,
                        stack.frames[0].func_name,
                        stack.special.get('tsan_data_race_type'),
                        stack.special.get('tsan_data_race_bytes')
                    ]
                    # reversing the 2nd function improves the readability of the file
                    row.extend(list(reversed(details) if func_no == 2 else details))
            for i in range(func_no, self.__expected_funcs_per_report):
                row.extend([None, None, None, None, None])
            row = ['?' if not cell else cell for cell in row]
            row.append(report.special.get('tsan_data_race_global_location', ''))
            self._add_row(report.dir_path, row)
