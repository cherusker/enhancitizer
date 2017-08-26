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
import re

from utils import FileUtils, NameCounter

class MetaReport:
    """A trade-off between memory consumption and file interactions to store important information"""

    def __init__(self, new, sanitizer, category, no, file_path=''):
        self.new = bool(new)
        self.sanitizer = sanitizer
        self.category = category
        self.no = int(no)
        self.dir_path = os.path.dirname(file_path)
        self.file_path = file_path

    def __repr__(self):
        return 'MetaReport { ' + \
            'new: ' + repr(self.new) + ', ' + \
            'sanitizer: "' + repr(self.sanitizer) + '", ' + \
            'category: "' + repr(self.category) + '", ' + \
            'no: ' + repr(self.no) + ', ' + \
            'dir_path: "' + self.dir_path + '", ' + \
            'file_path: "' + self.file_path + '" }'

class Report:
    """Wraps around objects of MetaReport and knows all the details"""

    def __init__(self, meta_report):
        self.meta = meta_report
        extractor = ReportCallStackExtractor()
        with open(meta_report.file_path, 'r') as report_file:
            last_line = ''
            for line in report_file:
                extractor.extract(last_line, line)
                last_line = line
            report_file.close()
        self.call_stacks = extractor.call_stacks

    def __repr__(self):
        return 'Report { ' + \
            'meta: ' + repr(self.meta) + ', ' + \
            'call_stacks: ' + repr(self.call_stacks) + ' }'

class ReportCallStack:
    """A call stack"""

    def __init__(self, title):
        self.title = title
        self.items = []

    def __repr__(self):
        return 'ReportCallStack { ' + \
            'title: "' + repr(self.title) + '", ' + \
            'items: ' + repr(self.items) + ' }'

class ReportCallStackItem:
    """A specific function call on a call stack"""

    def __init__(self, func_name, src_file_path, line_num, char_pos):
        self.func_name = func_name
        self.src_file_path = src_file_path
        self.src_file_name = None if not src_file_path else os.path.basename(src_file_path)
        self.line_num = None if not line_num else int(line_num)
        self.char_pos = None if not char_pos else int(char_pos)

    def __repr__(self):
        return 'ReportCallStackItem { ' + \
            'func_name: "' + repr(self.func_name) + '", ' + \
            'src_file_path: "' + repr(self.src_file_path) + '", ' + \
            'src_file_name: "' + repr(self.src_file_name) + '", ' + \
            'line_num: ' + repr(self.line_num) + ', ' + \
            'char_pos: ' + repr(self.char_pos) + ' }'

    def complete(self):
        """True, if all attributes != None"""
        return bool(self.src_file_path and self.func_name and self.line_num and self.char_pos)

class ReportExtractor:
    """Base extractor class; has to be inherited in order to make sense"""

    reports_dir_name = 'reports/'

    file_name_length = 5 # zero padding

    def __init__(self, output_dir_path, sanitizer_dir_name):
        self.meta_reports = []
        self.counter = NameCounter()
        self.sanitizer_dir_path = output_dir_path + self.reports_dir_name + sanitizer_dir_name
        self.report_file = None

    def extract_start(self, meta_report):
        meta_report.dir_path = self.sanitizer_dir_path + meta_report.category.lower().replace(' ', '-') + '/'
        meta_report.file_path = meta_report.dir_path + repr(meta_report.no).zfill(self.file_name_length) + '.report'
        self.meta_reports.append(meta_report)
        print('  found ' + meta_report.category.lower() + ' #' + repr(meta_report.no) + \
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

class TSanReportExtractor(ReportExtractor):
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

class ReportCallStackExtractor:
    """Extract call stackss"""

    stack_item_pattern = re.compile('^\s{4}\#\d+\s' +
                                    '(?:\<null\>|(?P<func_name>[a-z\d_]+))\s' +
                                    '(?:\<null\>|' +
                                    '(?P<src_file_path>[a-z\d/\-\.]+):' +
                                    '(?P<line_num>\d+):' +
                                    '(?P<char_pos>\d+))',
                                    re.IGNORECASE)

    def __init__(self):
        self.current_call_stack = None
        self.call_stacks = []

    def extract(self, last_line, line):
        stack_item_search = self.stack_item_pattern.search(line)
        if self.current_call_stack:
            if not self.add_item_from_search(stack_item_search):
                self.call_stacks.append(self.current_call_stack)
                self.current_call_stack = None
        elif stack_item_search:
            self.current_call_stack = ReportCallStack(last_line.strip())
            self.add_item_from_search(stack_item_search)

    def add_item_from_search(self, stack_item_search):
        if not self.current_call_stack or not stack_item_search:
            return False
        self.current_call_stack.items.append(ReportCallStackItem(
            stack_item_search.group('func_name'),
            stack_item_search.group('src_file_path'),
            stack_item_search.group('line_num'),
            stack_item_search.group('char_pos')))
        return True
