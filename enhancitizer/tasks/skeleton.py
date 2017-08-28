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
from utils.skeleton import Skeleton

class TaskBuildSkeleton(object):

    description = 'Building the skeleton ...'

    __root_dir_name = 'skeleton'
    __tsan_data_race_max_stack_depth = 3

    def __init__(self, options):
        self.__root_dir_path = os.path.join(options.output_root_path, self.__root_dir_name)
        self.__skeletons = OrderedDict()
        self.__add_funcs = {
            'ThreadSanitizer': {
                'data race': self.__add_tsan_data_race
            }
        }

    def setup(self):
        utils.os.makedirs(self.__root_dir_path, True)

    def process(self, report):
        if self.__add_funcs.get(report.sanitizer, {}).get(report.category):
            self.__add_funcs.get(report.sanitizer).get(report.category)(report)

    def __add(self, report, stack_frame_id, stack_frame):
        if stack_frame.complete:
            file_rel_path = stack_frame.src_file_rel_path
            line_num = stack_frame.line_num
            if not file_rel_path in self.__skeletons:
                self.__skeletons.update({ file_rel_path: Skeleton(stack_frame.src_file_path) })
            self.__skeletons.get(file_rel_path).mark(
                stack_frame.line_num, stack_frame.char_pos, str(report) + ' - frame #' + str(stack_frame_id))

    def __add_tsan_data_race(self, report):
        for stack in report.call_stacks:
            if stack.tsan_data_race.get('type'):
                for i in range(min(len(stack.items), self.__tsan_data_race_max_stack_depth)):
                    self.__add(report, i, stack.items[i])

    def teardown(self):
        for src_file_path, skeleton in self.__skeletons.items():
            skeleton_file_path = os.path.join(self.__root_dir_path, src_file_path + '.skeleton')
            print('  creating ' + skeleton_file_path + ' (' + str(skeleton.marked_lines_count) + ' lines)')
            utils.os.makedirs(os.path.dirname(skeleton_file_path))
            with open(skeleton_file_path, 'w') as skeleton_file:
                skeleton.write(skeleton_file)
                skeleton_file.close()
