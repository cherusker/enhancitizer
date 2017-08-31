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

import utils.files
from utils.printer import Printer
from utils.skeleton import Skeleton

class TaskBuildSkeleton(object):

    description = 'Building the skeleton ...'

    __root_dir_name = 'skeleton'
    __tsan_data_race_max_stack_depth = 3

    def setup(self, options):
        self.__root_dir_path = os.path.join(options.output_root_path, self.__root_dir_name)
        utils.files.makedirs(self.__root_dir_path, True)
        self.__printer = Printer(options)
        self.__skeletons = {}
        self.__add_funcs = {
            'tsan': {
                'data race': self.__add_tsan_data_race
            }
        }

    def process(self, report):
        if report.category_name in self.__add_funcs.get(report.sanitizer.name_short, {}):
            self.__add_funcs[report.sanitizer.name_short][report.category_name](report)

    def __add(self, report, stack_frame_id, stack_frame):
        if stack_frame.complete:
            file_rel_path = stack_frame.src_file_rel_path
            line_num = stack_frame.line_num
            if not file_rel_path in self.__skeletons:
                self.__skeletons[file_rel_path] = Skeleton(stack_frame.src_file_path)
            self.__skeletons[file_rel_path].mark(
                stack_frame.line_num, stack_frame.char_pos, str(report) + ' - frame #' + str(stack_frame_id))

    def __add_tsan_data_race(self, report):
        for stack in report.call_stacks:
            if 'tsan_data_race_type' in stack.special:
                for i in range(min(len(stack.frames), self.__tsan_data_race_max_stack_depth)):
                    self.__add(report, i, stack.frames[i])

    def teardown(self):
        for src_file_path, skeleton in self.__skeletons.items():
            skeleton_file_path = os.path.join(self.__root_dir_path, src_file_path + '.skeleton')
            self.__printer.task_info(
                'creating ' + skeleton_file_path + ' (' + str(skeleton.marked_lines_count) + ' lines)')
            utils.files.makedirs(os.path.dirname(skeleton_file_path))
            with open(skeleton_file_path, 'w') as skeleton_file:
                skeleton.write(skeleton_file)
                skeleton_file.close()
