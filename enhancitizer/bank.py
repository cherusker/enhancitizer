# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

import re

from utils import NameCounter

class MetaReport:
    """A trade-off between memory consumption and file interactions to store important information"""

    def __init__(self, category, no, file_path):
        self.category = category
        self.no = no
        self.file_path = file_path

class Report:
    """Wraps around objects of MetaReport and knows all the details"""

    def __init__(self, meta_report):
        self.meta = meta_report

class ReportsBankIterator:
    """Used to iterate over an object of ReportsBank and returns objects of Report"""
    
    def __init__(self, reports_bank):
        self.meta_reports = reports_bank.meta_reports
        self.position = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.position >= len(self.meta_reports):
            raise StopIteration
        else:
            self.position += 1
            return Report(self.meta_reports[self.position - 1])
    
class ReportsBank:
    """Extracts reports from a log file and stores objects of ReportsBankReport"""
    
    report_start_line_pattern = re.compile('^warning:\sthreadsanitizer:\s(?P<report_category>[a-z\s]+)\s\(', re.IGNORECASE)
    report_end_line_pattern = re.compile('^=+$', re.MULTILINE)

    def __init__(self):
        self.meta_reports = []
        self.reports_counter = NameCounter()

    def extract(self, log_file_path, output_dir_path):

        with open(log_file_path, 'r') as copy_from_file:

            # as the pattern matches the 2nd line of a report, we have to buffer the line before that
            last_line = '' 
            copy_to_file = None

            for line in copy_from_file:
                if copy_to_file:
                    copy_to_file.write(line)
                    if self.report_end_line_pattern.match(line):
                        copy_to_file.close()
                        copy_to_file = None
                else:
                    report_name_search = self.report_start_line_pattern.search(line)
                    if report_name_search:
                        report_category = report_name_search.group('report_category').lower()
                        report_no = self.reports_counter.inc(report_category)
                        report_file_path = output_dir_path + \
                                           report_category.replace(' ', '-') + '-' + repr(report_no).zfill(3) + \
                                           '.txt'
                        self.meta_reports.append(MetaReport(report_category, report_no, report_file_path))
                        print('ReportsBank: found "' + report_category + '" (' + repr(report_no) + ')')
                        copy_to_file = open(report_file_path, 'w')
                        copy_to_file.write(last_line + line)
                last_line = line

            copy_from_file.close()
            if copy_to_file:
                copy_to_file.close()

        return self
