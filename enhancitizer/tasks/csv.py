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
        self.__csv_files.get(dir_path).get('writer').writerow(row)

    def teardown(self):
        for csv_file in self.__csv_files.values():
            csv_file.get('file').close()

class TaskTSanCsvSummary(TaskCsvSummary):
    """The TSan way of summarising reports"""

    __stack_title_pattern = re.compile('(?P<operation>read|write)\sof\ssize', re.IGNORECASE)
    __expected_funcs_per_report = 2

    def process(self, report):
        if report.sanitizer == 'ThreadSanitizer' and report.category == 'data race':
            row = [report.no]
            func_no = 0
            for stack in report.call_stacks:
                stack_title_search = self.__stack_title_pattern.search(stack.title)
                if stack_title_search and len(stack.items) > 0:
                    item = stack.items[0]
                    func_no += 1
                    details = [
                        '?' if not item.src_file_dir_rel_path else item.src_file_dir_rel_path,
                        '?' if not item.src_file_name else item.src_file_name,
                        '?' if not item.func_name else item.func_name,
                        stack_title_search.group('operation').lower()
                    ]
                    # reversing the 2nd function improves the readability of the file
                    row.extend(list(reversed(details) if func_no == 2 else details))
            for i in range(func_no, self.__expected_funcs_per_report):
                row.extend(['?', '?', '?', '?'])
            self._add_row(report.dir_path, row)
