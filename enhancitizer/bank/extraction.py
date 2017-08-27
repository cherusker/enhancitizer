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

import utils.os
from utils.utils import NameCounter

class Report(object):
    """A trade-off between memory consumption and file interactions"""

    def __init__(self, options, new, sanitizer, category, no, file_path):
        self.__options = options
        self.new = bool(new)
        self.sanitizer = sanitizer
        self.category = category
        self.no = int(no)
        self.dir_path = os.path.dirname(file_path)
        self.file_path = file_path
        self.__call_stacks = None # lazy initialisation

    @property
    def call_stacks(self):
        if not self.__call_stacks:
            self.__call_stacks = ReportCallStackExtractor(self.__options).extract(self).call_stacks
        return self.__call_stacks

    @call_stacks.deleter
    def call_stacks(self):
        self.__call_stacks = None

    def __str__(self):
        return self.category + ' #' + str(self.no) + ' (' + self.sanitizer + ')'

    def __repr__(self):
        return 'MetaReport { ' + \
            'new: ' + repr(self.new) + ', ' + \
            'sanitizer: ' + repr(self.sanitizer) + ', ' + \
            'category: ' + repr(self.category) + ', ' + \
            'no: ' + repr(self.no) + ', ' + \
            'dir_path: ' + repr(self.dir_path) + ', ' + \
            'file_path: ' + repr(self.file_path) + \
            'call_stacks: ' + repr(self.call_stacks) + '" }'

class ReportCallStack(object):
    """A call stack"""

    def __init__(self, title):
        self.title = title
        self.items = []
        self.tsan_data_race = {
            'type': None, # 'read' | 'write'
            'bytes': 0
        }
        self.tsan_thread_leak = {
            'thread_name': None
        }

    def __repr__(self):
        return 'ReportCallStack { ' + \
            'title: ' + repr(self.title) + ', ' + \
            'items: ' + repr(self.items) + ', ' + \
            'tsan_data_race: ' + repr(self.tsan_data_race) + ', ' + \
            'tsan_thread_leak: ' + repr(self.tsan_thread_leak) + ' }'

class ReportCallStackItem(object):
    """A specific function call on a call stack"""

    def __init__(self, options, func_name, src_file_path, line_num, char_pos):
        self.func_name = func_name
        self.src_file_path = src_file_path
        self.src_file_rel_path = None if not src_file_path else os.path.relpath(src_file_path, options.project_root_path)
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

    @property
    def complete(self):
        """True, if all attributes != None"""
        return bool(self.func_name and \
                    self.src_file_path and \
                    self.line_num and \
                    self.char_pos)

class ReportExtractor(object):
    """Base extractor class; has to be inherited in order to make sense"""

    __file_name_length = 5 # zero padding
    __report_file_name_pattern = re.compile('^(?P<no>\d{' + str(__file_name_length) + '})\.report$', re.IGNORECASE)

    def __init__(self, options, reports_dir_path):
        self.__options = options
        self.reports = []
        self.__counter = NameCounter()
        self.__reports_dir_path = reports_dir_path
        self.__report_file = None

    def _extract_start(self, report):
        utils.os.makedirs(os.path.dirname(report.file_path))
        self.__report_file = open(report.file_path, 'w')

    def _extract_continue(self, line):
        if not self.__report_file:
            return False
        self.__report_file.write(line)
        return True

    def _extract_end(self):
        self.__report_file.close()
        self.__report_file = None

    def __get_category_dir_path(self, category):
        return os.path.join(self.__reports_dir_path, category.lower().replace(' ', '-'))

    def __get_report_file_path(self, category, no):
        return os.path.join(
            self.__get_category_dir_path(category), str(no).zfill(self.__file_name_length) + '.report')

    def _make_and_add_report(self, new, sanitizer, category, no=None):
        if no == None:
            no = self.__counter.inc(category)
        elif self.__counter.get(category) < no:
            self.__counter.set(category, no)
        report = Report(self.__options, new, sanitizer, category, no, self.__get_report_file_path(category, no))
        print('  adding ' + str(report))
        self.reports.append(report)
        return report

    def _collect_reports(self, sanitizer_name, category):
        dir_path = self.__get_category_dir_path(category)
        if os.path.isdir(dir_path):
            for file_name in sorted(os.listdir(dir_path)):
                report_file_name_search = self.__report_file_name_pattern.search(file_name)
                if report_file_name_search:
                    self._make_and_add_report(
                        False, sanitizer_name, category, int(report_file_name_search.group('no')))

class TSanReportExtractor(ReportExtractor):
    """Extract ThreadSanitizer reports"""

    __sanitizer_name = 'ThreadSanitizer'
    __sanitizer_dir_name = 'tsan'
    __categories = ['data race', 'thread leak']

    __start_line_pattern = re.compile('^warning:\sthreadsanitizer:\s(?P<category>[a-z\s]+)\s\(', re.IGNORECASE)
    __start_last_line_pattern = re.compile('^={18}$', re.MULTILINE)
    __end_line_pattern = __start_last_line_pattern

    def __init__(self, options, reports_dir_path):
        super(TSanReportExtractor, self).__init__(options, os.path.join(reports_dir_path, self.__sanitizer_dir_name))

    def collect(self):
        for category in self.__categories:
            self._collect_reports(self.__sanitizer_name, category)

    def extract(self, last_line, line):
        if self._extract_continue(line):
            if self.__end_line_pattern.search(line):
                self._extract_end()
        else:
            start_line_search = self.__start_line_pattern.search(line)
            if start_line_search and self.__start_last_line_pattern.search(last_line):
                category = start_line_search.group('category').lower()
                if not category in self.__categories:
                    print('  unkown category "' + category + '"')
                    exit()
                else:
                    report = self._make_and_add_report(True, 'ThreadSanitizer', category)
                    self._extract_start(report)
                    self._extract_continue(last_line + line)

class ReportCallStackExtractor(object):
    """Extract call stackss"""

    __stack_item_pattern = re.compile(
        '^\s{4}\#\d+\s' +
        '(?:\<null\>|(?P<func_name>[a-z\d_]+))\s' +
        '(?:\<null\>|(?P<src_file_path>[a-z\d/\-\.]+):(?P<line_num>\d+):(?P<char_pos>\d+))',
        re.IGNORECASE)
    __tsan_data_race_title_pattern = re.compile(
        '^(?:previous\s)?(?:atomic\s)?' +
        '(?P<type>read|write)\sof\ssize\s(?P<bytes>\d+)\s' +
        'at\s0x[\da-f]+\sby\s', re.IGNORECASE)
    __tsan_thread_leak_title_pattern = re.compile('^thread\s(?P<name>.+)\s\(tid=\d+', re.IGNORECASE)

    def __init__(self, options):
        self.call_stacks = []
        self.__options = options
        self.__add_context = {
            'ThreadSanitizer': self.__add_tsan_context
        }

    def extract(self, report):
        with open(report.file_path, 'r') as report_file:
            add_context = self.__add_context.get(report.sanitizer)
            stack = None
            last_line = ''
            for line in report_file:
                item_search = self.__stack_item_pattern.search(line)
                if stack:
                    if not self.__add_item_from_search(stack, item_search):
                        if add_context:
                            add_context(stack)
                        self.call_stacks.append(stack)
                        stack = None
                elif item_search:
                    stack = ReportCallStack(last_line.strip())
                    self.__add_item_from_search(stack, item_search)
                last_line = line
            report_file.close()
        return self

    def __add_item_from_search(self, stack, search):
        if not stack or not search:
            return False
        stack.items.append(ReportCallStackItem(
            self.__options,
            search.group('func_name'),
            search.group('src_file_path'),
            search.group('line_num'),
            search.group('char_pos')))
        return True

    def __add_tsan_context(self, stack):
        search = self.__tsan_data_race_title_pattern.search(stack.title)
        if search:
            stack.tsan_data_race['type'] = search.group('type').lower()
            stack.tsan_data_race['bytes'] = int(search.group('bytes'))
            return
        search = self.__tsan_thread_leak_title_pattern.search(stack.title)
        if search:
            stack.tsan_thread_leak['thread_name'] = search.group('name')
