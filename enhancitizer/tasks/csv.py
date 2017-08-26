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
import re

from bank.extractor import Report

class TaskCsvSummaryCategory:

    def __init__(self, ):
        pass

class TaskCsvSummary:
    """Summarise the reports and collect the info in CSV files"""

    description = 'Summarising the reports ...'

    csv_file_name = 'summary.csv'
    csv_delimiter = ','

    def setup(self):
        self.csv_files = {}

    def add_row(self, dir_path, row):
        if not dir_path in self.csv_files:
            csv_file_path = dir_path + self.csv_file_name
            csv_file = open(csv_file_path, 'w')
            if csv_file:
                print('  creating ' + csv_file_path)
                self.csv_files[dir_path] = {
                    'file': csv_file,
                    'writer': csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
                }
        self.csv_files.get(dir_path).get('writer').writerow(row)

    def teardown(self):
        for csv_file in self.csv_files.values():
            csv_file.get('file').close()

class TaskTSanCsvSummary(TaskCsvSummary):
    """The TSan way of summarising reports"""

    stack_title_pattern = re.compile('(?P<operation>read|write)\sof\ssize', re.IGNORECASE)

    expected_funcs_per_report = 2

    def process_report(self, meta_report):
        if meta_report.sanitizer == 'ThreadSanitizer' and meta_report.category == 'Data race':

            report = Report(meta_report)
            row = [repr(meta_report.no)]

            func_no = 0
            for stack in report.call_stacks:
                stack_title_search = self.stack_title_pattern.search(stack.title)
                if stack_title_search and len(stack.items) > 0:
                    stack_item = stack.items[0]
                    func_no += 1
                    details = [
                        '?' if not stack_item.src_file_name else stack_item.src_file_name,
                        '?' if not stack_item.func_name else stack_item.func_name,
                        stack_title_search.group('operation').lower()
                    ]
                    row.extend(list(reversed(details) if func_no == 2 else details))
                        
            for i in range(func_no, self.expected_funcs_per_report):
                row.extend(['?', '?', '?'])

            self.add_row(meta_report.dir_path, row)
