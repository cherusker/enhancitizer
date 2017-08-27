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

class TaskCsvSummary(object):
    """Summarise the reports and collect the info in CSV files"""

    description = 'Summarising the reports ...'

    __csv_file_name = 'summary.csv'
    __csv_delimiter = ','

    def setup(self):
        self.__csv_files = {}

    def _add_row(self, dir_path, row):
        if not dir_path in self.__csv_files:
            csv_file_path = os.path.join(dir_path, self.__csv_file_name)
            csv_file = open(csv_file_path, 'w')
            if csv_file:
                print('  creating ' + csv_file_path)
                self.__csv_files[dir_path] = {
                    'file': csv_file,
                    'writer': csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
                }
        self.__csv_files.get(dir_path).get('writer').writerow(['?' if not x else x for x in row])

    def teardown(self):
        for csv_file in self.__csv_files.values():
            csv_file.get('file').close()

class TaskTSanCsvSummary(TaskCsvSummary):
    """The TSan way of summarising reports"""

    __sanitizer_name = 'ThreadSanitizer'
    __supported_categories = ['data race']
    __expected_funcs_per_report = 2

    def process(self, report):
        if report.sanitizer == self.__sanitizer_name and report.category in self.__supported_categories:
            row = [report.no]
            func_no = 0
            for stack in report.call_stacks:
                if stack.tsan_data_race.get('type') and len(stack.items) > 0:
                    func_no += 1
                    details = [
                        stack.items[0].src_file_dir_rel_path,
                        stack.items[0].src_file_name,
                        stack.items[0].func_name,
                        stack.tsan_data_race.get('type'),
                        stack.tsan_data_race.get('bytes')
                    ]
                    # reversing the 2nd function improves the readability of the file
                    row.extend(list(reversed(details) if func_no == 2 else details))
            for i in range(func_no, self.__expected_funcs_per_report):
                row.extend(['?', '?', '?', '?', '?'])
            self._add_row(report.dir_path, row)
