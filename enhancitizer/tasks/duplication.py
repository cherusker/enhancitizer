# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

class TaskEliminateDuplicateReports(object):

    description = 'Eliminating duplicate reports ...'

    __tsan_data_race_max_stack_frames = 3

    def __init__(self, bank):
        self.__bank = bank

    def setup(self):
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
            self.__bailout('unable to analyse', report)
        identifiers = self.__identifiers_funcs.get(report.sanitizer).get(report.category)(report)
        if not identifiers:
            self.__bailout('unable to extract identifiers from', report)
        for identifier in identifiers:
            if identifier in self.__known_identifiers:
                print('  removing ' + str(report))
                self.__duplicate_reports.append(report)
                return
        self.__known_identifiers.extend(identifiers)

    def teardown(self):
        for report in self.__duplicate_reports:
            self.__bank.remove_report(report)

    def __bailout(self, message, report):
        print('  error: ' + message + ' ' + str(report))
        exit()

    def __tsan_data_race_identifiers(self, report):
        fragments = []
        for stack in report.call_stacks:
            if stack.tsan_data_race.get('type'):
                fragment = []
                fragment.append(stack.tsan_data_race.get('type'))
                fragment.append(stack.tsan_data_race.get('bytes'))
                for i in range(min(len(stack.items), self.__tsan_data_race_max_stack_frames)):
                    fragment.append(stack.items[i].src_file_rel_path)
                    fragment.append(stack.items[i].func_name)
                    fragment.append(stack.items[i].line_num)
                    fragment.append(stack.items[i].char_pos)
                fragments.append(':'.join(['?' if not f else str(f) for f in fragment]))
        if len(fragments) == 1:
            return fragments
        if len(fragments) == 2:
            # either way is fine!
            return [fragments[0] + ':' + fragments[1], fragments[1] + ':' + fragments[0]]

    def __tsan_thread_leak_identifiers(self, report):
        for stack in report.call_stacks:
            if stack.tsan_thread_leak.get('thread_name'):
                return [stack.tsan_thread_leak.get('thread_name')]
