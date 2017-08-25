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

from bank.report import MetaReport
from utils import FileUtils, NameCounter

class Extractor:
    """Base extractor class; has to be inherited in order to make sense"""

    reports_dir_name = 'reports/'

    file_name_length = 5 # zero padding

    def __init__(self, output_dir_path, sanitizer_dir_name):
        self.meta_reports = []
        self.counter = NameCounter()
        self.sanitizer_dir_path = output_dir_path + self.reports_dir_name + sanitizer_dir_name
        self.report_file = None

    def extract_start(self, meta_report):
        meta_report.file_path = self.sanitizer_dir_path + \
                                meta_report.category.lower().replace(' ', '-') + '/' + \
                                repr(meta_report.no).zfill(self.file_name_length) + '.txt'
        self.meta_reports.append(meta_report)
        print('Extractor: ' + \
              'found ' + meta_report.category.lower() + ' #' + repr(meta_report.no) + \
              ' (' + meta_report.sanitizer + ')')
        FileUtils.create_folders(meta_report.file_path)
        self.report_file = open(meta_report.file_path, 'w')

    def extract_continue(self, line):
        if not self.report_file:
            return False
        self.report_file.write(line)
        return True

    def extract_end(self):
        self.report_file.close()
        self.report_file = None

class TSanExtractor(Extractor):
    """Extract ThreadSanitizer reports"""

    sanitizer_dir_name = 'tsan/'

    start_line_pattern = re.compile('^warning:\sthreadsanitizer:\s(?P<category>[a-z\s]+)\s\(', re.IGNORECASE)
    start_last_line_pattern = end_line_pattern = re.compile('^=+$', re.MULTILINE)

    categories = {
        'data race': 'Data race',
        'thread leak': 'Thread leak'
    }

    def __init__(self, output_dir_path):
        super().__init__(output_dir_path, self.sanitizer_dir_name)

    def extract(self, last_line, line):
        if self.extract_continue(line):
            if self.end_line_pattern.search(line):
                self.extract_end()
        else:
            start_line_search = self.start_line_pattern.search(line)
            if start_line_search and self.start_last_line_pattern.search(last_line):
                category = start_line_search.group('category')
                if not category in self.categories:
                    print('TSanExtractor: Unkown category \'' + category + '\'')
                else:
                    category = self.categories[category]
                    no = self.counter.inc(category)
                    self.extract_start(MetaReport(True, 'ThreadSanitizer', category, no))
                    self.extract_continue(last_line + line)

