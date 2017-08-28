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

from utils.os import SourceCodeLine

class TaskAddTSanContext(object):

    description = 'Adding TSan context ...'

    __sanitizer_name = 'ThreadSanitizer'
    __supported_categories = ['data race']
    __max_stack_depth = 3 # max amount of lookups from the top of the call stack
    
    def process(self, report):
        if report.new and report.sanitizer == self.__sanitizer_name and report.category in self.__supported_categories:
            report_file_path = report.file_path
            buffer_file_path = report_file_path + '.buffer'
            print('  adding context to ' + str(report))
            with open(buffer_file_path, 'w') as buffer_file:
                buffer_file.write('\n')
                for stack in report.call_stacks:
                    if stack.tsan_data_race.get('type'):
                        buffer_file.write(stack.title + '\n\n')
                        for i in range(min(len(stack.items), self.__max_stack_depth)):
                            if stack.items[i].complete:
                                # TODO: find full function signature
                                func_signature = stack.items[i].func_name + '(...)'
                                line = SourceCodeLine(stack.items[i].src_file_path, stack.items[i].line_num)
                                if line.line:
                                    buffer_file.write(
                                        func_signature + ' {\n' +
                                        '  // ...\n' +
                                        '! ' + line.line + '\n' +
                                        (' ' * (stack.items[i].char_pos - line.indent + 1)) + '^\n' +
                                        '  // ...\n' +
                                        '}\n\n')
                with open(report_file_path, 'r') as report_file:
                    for line in report_file:
                        buffer_file.write(line)
                    report_file.close()
                buffer_file.close()
            os.remove(report_file_path)
            os.rename(buffer_file_path, report_file_path)
