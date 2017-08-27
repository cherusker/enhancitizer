# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

from collections import OrderedDict
import os

import utils.os
from utils.os import SourceCodeLine

class TaskBuildSkeleton(object):

    description = 'Building a skeleton ...'

    __root_dir_name = 'skeleton'
    __tsan_data_race_max_stack_depth = 3

    def __init__(self, options):
        # src_file_path.line.reports
        self.__data = OrderedDict()
        self.__add_funcs = {
            'ThreadSanitizer': {
                'data race': self.__add_tsan_data_race
            }
        }
        self.__root_dir_path = os.path.join(options.output_root_path, self.__root_dir_name)

    def setup(self):
        utils.os.makedirs(self.__root_dir_path, True)

    def process(self, report):
        if self.__add_funcs.get(report.sanitizer, {}).get(report.category):
            self.__add_funcs.get(report.sanitizer, {}).get(report.category)(report)

    def __add(self, report, stack_item):
        if stack_item.complete:
            file_rel_path = stack_item.src_file_rel_path
            line_num = stack_item.line_num
            if not file_rel_path in self.__data:
                self.__data.update({ file_rel_path: {} })
            if not line_num in self.__data.get(file_rel_path):
                self.__data.get(file_rel_path).update({ line_num: [] })
            # TODO: filter duplicate reports
            self.__data.get(file_rel_path).get(line_num).append({
                'report': report,
                'stack_item': stack_item
            })

    def __add_tsan_data_race(self, report):
        for stack in report.call_stacks:
            if stack.tsan_data_race.get('type'):
                for i in range(min(len(stack.items), self.__tsan_data_race_max_stack_depth)):
                    self.__add(report, stack.items[i])

    def teardown(self):
        for src_file_path, lines in self.__data.items():
            skeleton_file_path = os.path.join(self.__root_dir_path, src_file_path + '.skeleton')
            print('  creating ' + skeleton_file_path + ' (' + str(len(lines)) + ' lines)')
            utils.os.makedirs(os.path.dirname(skeleton_file_path))
            last_func_name = None
            with open(skeleton_file_path, 'w') as skeleton_file:
                for line_num, items in sorted(lines.items(), key=lambda l: l[0]):
                    func_name = None
                    line = None
                    line_pos = []
                    line_reports = []
                    for i, item in enumerate(items):
                        stack_item = item.get('stack_item')
                        if i < 1:
                            func_name = stack_item.func_name
                            line = SourceCodeLine(stack_item.src_file_path, stack_item.line_num)
                        line_pos.append(stack_item.char_pos - line.indent - 1)
                        line_reports.append({ 'pos': stack_item.char_pos - line.indent - 1, 'str': str(item.get('report'))  })
                    if func_name != last_func_name:
                        if last_func_name:
                            skeleton_file.write('}\n\n')
                        skeleton_file.write('...\n\n' + func_name + '(...) {\n  ...\n\n')
                        last_func_name = func_name
                    skeleton_file.write('  ' + line.line + '\n  ')
                    for pos in range(max(line_pos) + 1):
                        skeleton_file.write(' ' if not pos in line_pos else '^')
                    skeleton_file.write('\n')
                    for line_report in sorted(line_reports, key=lambda lr: lr.get('pos')):
                        skeleton_file.write('  ' + ' ' * line_report.get('pos') + '|--> ' + line_report.get('str') + '\n')
                    skeleton_file.write('\n  ...\n')
                if last_func_name:
                    skeleton_file.write('}\n\n...')
                skeleton_file.close()
