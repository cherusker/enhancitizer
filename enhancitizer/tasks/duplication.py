# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

from utils.printer import Printer

class TaskEliminateDuplicateReports(object):

    description = 'Eliminating duplicate reports ...'

    __tsan_data_race_max_stack_frames = 3

    def __init__(self, bank):
        self.__bank = bank

    def setup(self, options):
        self.__printer = Printer(options)
        self.__duplicate_reports = []
        self.__identifiers_funcs = {
            'ThreadSanitizer': {
                'data race': self.__tsan_data_race_identifiers,
                'thread leak': self.__tsan_thread_leak_identifiers
            }
        }
        # TODO: split into separate lists for sanitizers and categories for better performance
        self.__known_identifiers = []

    def process(self, report):
        if not self.__identifiers_funcs.get(report.sanitizer, {}).get(report.category):
            self.__printer.bailout('unable to analyse ' + str(report))
        identifiers = self.__identifiers_funcs[report.sanitizer][report.category](report)
        if not identifiers:
            self.__printer.bailout('unable to extract identifiers from ' + str(report))
        for identifier in identifiers:
            if identifier in self.__known_identifiers:
                self.__printer.task_info('removing ' + str(report))
                self.__duplicate_reports.append(report)
                return
        self.__known_identifiers.extend(identifiers)

    def teardown(self):
        for report in self.__duplicate_reports:
            self.__bank.remove_report(report)

    def __tsan_data_race_identifiers(self, report):
        fragments = []
        for stack in report.call_stacks:
            if 'tsan_data_race_type' in stack.special:
                fragment = [
                    stack.special.get('tsan_data_race_type'),
                    stack.special.get('tsan_data_race_bytes')
                ]
                for i in range(min(len(stack.frames), self.__tsan_data_race_max_stack_frames)):
                    fragment.extend([
                        stack.frames[i].src_file_rel_path,
                        stack.frames[i].func_name,
                        stack.frames[i].line_num,
                        stack.frames[i].char_pos
                    ])
                fragments.append(':'.join(['?' if not f else str(f) for f in fragment]))
        if len(fragments) == 1:
            return fragments
        if len(fragments) == 2:
            # either way is fine!
            return [fragments[0] + ':' + fragments[1], fragments[1] + ':' + fragments[0]]

    def __tsan_thread_leak_identifiers(self, report):
        for stack in report.call_stacks:
            if stack.special.get('tsan_thread_leak_thread_name'):
                return [stack.special['tsan_thread_leak_thread_name']]
