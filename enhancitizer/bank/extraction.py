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

from options import Options
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
            'sanitizer: ' + repr(self.sanitizer) + ', ' + \
            'category: ' + repr(self.category) + ', ' + \
            'no: ' + repr(self.no) + ', ' + \
            'dir_path: "' + repr(self.dir_path) + '", ' + \
            'file_path: "' + repr(self.file_path) + '" }'

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
        self.src_file_rel_path = None if not src_file_path else os.path.relpath(src_file_path, Options.project_root_path)
        self.src_file_name = None if not src_file_path else os.path.basename(src_file_path)
        self.src_file_dir_rel_path = None if not src_file_path else os.path.dirname(self.src_file_rel_path)
        self.line_num = None if not line_num else int(line_num)
        self.char_pos = None if not char_pos else int(char_pos)

    def __repr__(self):
        return 'ReportCallStackItem { ' + \
            'func_name: "' + repr(self.func_name) + '", ' + \
            'src_file_path: "' + repr(self.src_file_path) + '", ' + \
            'src_file_rel_path: "' + repr(self.src_file_rel_path) + '", ' + \
            'src_file_name: "' + repr(self.src_file_name) + '", ' + \
            'src_file_dir_rel_path: "' + repr(self.src_file_dir_rel_path) + '", ' + \
            'line_num: ' + repr(self.line_num) + ', ' + \
            'char_pos: ' + repr(self.char_pos) + ' }'

    def complete(self):
        """True, if all attributes != None"""
        return bool(self.func_name and self.src_file_path and self.src_file_rel_path and self.line_num and self.char_pos)

class ReportExtractor:
    """Base extractor class; has to be inherited in order to make sense"""

    file_name_length = 5 # zero padding
    report_file_name_pattern = re.compile('^(?P<no>\d{' + str(file_name_length) + '})\.report$', re.IGNORECASE)

    def __init__(self, reports_dir_path):
        self.meta_reports = []
        self.counter = NameCounter()
        self.reports_dir_path = reports_dir_path
        self.report_file = None

    def get_category_dir_path(self, category):
        return os.path.join(self.reports_dir_path, category.lower().replace(' ', '-'))

    def get_report_file_path(self, category, no):
        return os.path.join(
            self.get_category_dir_path(category), repr(no).zfill(self.file_name_length) + '.report')

    def make_and_add_meta_report(self, new, sanitizer, category, no=None):
        if no == None:
            no = self.counter.inc(category)
        elif self.counter.get(category) < no:
            self.counter.set(category, no)
        print('  found ' + category + ' #' + repr(no) + ' (' + sanitizer + ')')
        meta_report = MetaReport(new, sanitizer, category, no, self.get_report_file_path(category, no))
        self.meta_reports.append(meta_report)
        return meta_report

    def extract_start(self, meta_report):
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

    sanitizer_name = 'ThreadSanitizer'
    sanitizer_dir_name = 'tsan'

    start_line_pattern = re.compile('^warning:\sthreadsanitizer:\s(?P<category>[a-z\s]+)\s\(', re.IGNORECASE)
    start_last_line_pattern = end_line_pattern = re.compile('^={18}$', re.MULTILINE)

    categories = ['data race', 'thread leak']

    def __init__(self, reports_dir_path):
        super().__init__(os.path.join(reports_dir_path, self.sanitizer_dir_name))

    def collect(self):
        for category in self.categories:
            dir_path = self.get_category_dir_path(category)
            if os.path.isdir(dir_path):
                for file_name in sorted(os.listdir(dir_path)):
                    report_file_name_search = self.report_file_name_pattern.search(file_name)
                    if report_file_name_search:
                        self.make_and_add_meta_report(
                            False, self.sanitizer_name, category, int(report_file_name_search.group('no')))

    def extract(self, last_line, line):
        if self.extract_continue(line):
            if self.end_line_pattern.search(line):
                self.extract_end()
        else:
            start_line_search = self.start_line_pattern.search(line)
            if start_line_search and self.start_last_line_pattern.search(last_line):
                category = start_line_search.group('category').lower()
                if not category in self.categories:
                    print('  unkown category "' + category + '"')
                    exit()
                else:
                    meta_report = self.make_and_add_meta_report(True, 'ThreadSanitizer', category)
                    self.extract_start(meta_report)
                    self.extract_continue(last_line + line)

class ReportCallStackExtractor:
    """Extract call stackss"""

    stack_item_pattern = re.compile(
        '^\s{4}\#\d+\s' +
        '(?:\<null\>|(?P<func_name>[a-z\d_]+))\s' +
        '(?:\<null\>|(?P<src_file_path>[a-z\d/\-\.]+):(?P<line_num>\d+):(?P<char_pos>\d+))',
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
