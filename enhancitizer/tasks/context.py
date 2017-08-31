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

from utils.files import SourceCodeLine
from utils.printer import Printer

class TaskAddTSanContext(object):

    description = 'Adding TSan context ...'

    __supported_sanitizer_name_short = 'tsan'
    __supported_category_names = ['data race']
    __max_stack_frames = 3 # max amount of lookups from the top of the call stack
    
    def setup(self, options):
        self.__printer = Printer(options)

    def process(self, report):
        if report.is_new and \
           report.sanitizer.name_short == self.__supported_sanitizer_name_short and \
           report.category_name in self.__supported_category_names:
            report_file_path = report.file_path
            buffer_file_path = report_file_path + '.buffer'
            self.__printer.task_info('adding context to ' + str(report))
            with open(buffer_file_path, 'w') as buffer_file:
                buffer_file.write('\n')
                for stack in report.call_stacks:
                    if 'tsan_data_race_type' in stack.special:
                        buffer_file.write(stack.title + '\n\n')
                        for i in range(min(len(stack.frames), self.__max_stack_frames)):
                            if stack.frames[i].complete:
                                # TODO: find full function signature
                                func_signature = stack.frames[i].func_name + '(...)'
                                line = SourceCodeLine(stack.frames[i].src_file_path, stack.frames[i].line_num)
                                if line.line:
                                    buffer_file.write(
                                        func_signature + ' {\n' +
                                        '  // ...\n' +
                                        '! ' + line.line + '\n' +
                                        (' ' * (stack.frames[i].char_pos - line.indent + 1)) + '^\n' +
                                        '  // ...\n' +
                                        '}\n\n')
                with open(report_file_path, 'r') as report_file:
                    for line in report_file:
                        buffer_file.write(line)
                    report_file.close()
                buffer_file.close()
            os.remove(report_file_path)
            os.rename(buffer_file_path, report_file_path)
