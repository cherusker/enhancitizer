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
import os

from bank.extraction import Report

class TaskAddTSanContext:

    description = "Adding TSan context ..."

    stack_depth_max = 3 # max amount of lookups from the top of the call stack

    count_line_indent_pattern = re.compile('^(?P<indent>\s*)[^\s]?')

    tsan_call_stack_pattern = re.compile(
        '^\s*(?:previous\s)?(?:atomic\s)?(?:read|write)\sof\ssize\s\d+\sat\s0x[\da-f]+\sby\s', re.IGNORECASE)
    
    def process_report(self, meta_report):

        if not meta_report.new or meta_report.sanitizer != 'ThreadSanitizer':
            return

        report = Report(meta_report)
        report_file_path = report.meta.file_path
        buffer_file_path = report_file_path + '.ctx'
        print('  adding context to ' + report_file_path)

        with open(buffer_file_path, 'w') as buffer_file:

            buffer_file.write('\n')
            for call_stack in report.call_stacks:
                if self.tsan_call_stack_pattern.search(call_stack.title):
                    buffer_file.write(call_stack.title + '\n\n')
                    for i in range(min(self.stack_depth_max, len(call_stack.items))):
                        self.put_function(buffer_file, call_stack.items[i])

            with open(report_file_path, 'r') as report_file:
                for line in report_file:
                    buffer_file.write(line)
                report_file.close()

            buffer_file.close()

            os.remove(report_file_path)
            os.rename(buffer_file_path, report_file_path)
        
        return self
    
    def put_function(self, buffer_file, item):
        if item.complete():
            # TODO: find full function signature
            func_signature = item.func_name + '(...)'
            affected_line = ''
            affected_line_indent = 0
            with open(item.src_file_path, 'r') as src_file:
                for i, line in enumerate(src_file):
                    if i == item.line_num - 1:
                        count_line_indent = self.count_line_indent_pattern.search(line)
                        affected_line_indent = 0 if not count_line_indent else len(count_line_indent.group('indent'))
                        affected_line = '! ' + line.strip() + '\n'
                src_file.close()
            if affected_line != '':
                buffer_file.write(
                    func_signature + ' {\n' +
                    '  // ...\n' +
                    affected_line + \
                    (' ' * (item.char_pos - affected_line_indent + 1)) + '^\n' + \
                    '  // ...\n' +
                    '}\n\n')
