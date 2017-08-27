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

class TaskEliminateDuplicates(object):

    description = 'Eliminating duplicate reports ...'

    __tsan_data_race_fragment_stack_pattern = re.compile(
        '(?P<identifier>(?:read|write)\sof\ssize\s\d+)\sat\s0x', re.IGNORECASE)
    __tsan_data_race_fragments_max_stack_depth = 3
    __tsan_leaking_thread_fragment_pattern = re.compile('^(?P<identifier>.+)\s\(tid=', re.IGNORECASE)

    def __init__(self, bank):
        self.__bank = bank

    def setup(self):
        self.__duplicate_reports = []
        self.__fragments_funcs = {
            'ThreadSanitizer': {
                'data race': self.__tsan_data_race_fragments,
                'thread leak': self.__tsan_thread_leak_fragments
            }
        }
        # TODO: split into separate lists for sanitizers and categories for better performance
        self.__identifiers = []

    def process(self, report):
        if not self.__fragments_funcs.get(report.sanitizer, {}).get(report.category):
            self.__bailout(report.sanitizer, report.category, report.no)
        identifier = ':'.join(
            str('?' if not x else x).lower()
            for x in self.__fragments_funcs.get(report.sanitizer).get(report.category)(report))
        if not identifier:
            self.__bailout(report.sanitizer, report.category, report.no)
        if identifier in self.__identifiers:
            print('  removing ' + str(report))
            self.__duplicate_reports.append(report)
        else:
            self.__identifiers.append(identifier)

    def teardown(self):
        for report in self.__duplicate_reports:
            self.__bank.remove_report(report)

    def __bailout(self, sanitizer, category, no):
        print('  error: unable to analyse ' + category + ' #' + str(no) + ' (' + sanitizer + ')')
        exit()

    def __tsan_data_race_fragments(self, report):
        fragments = []
        for stack in report.call_stacks:
            identifer_stack_search = self.__tsan_data_race_fragment_stack_pattern.search(stack.title)
            if identifer_stack_search:
                fragments.append(identifer_stack_search.group('identifier'))
                items = stack.items
                for i in range(0, min(len(items), self.__tsan_data_race_fragments_max_stack_depth)):
                    fragments.append(items[i].src_file_rel_path)
                    fragments.append(items[i].func_name)
                    fragments.append(items[i].line_num)
                    fragments.append(items[i].char_pos)
        return fragments

    def __tsan_thread_leak_fragments(self, report):
        for stack in report.call_stacks:
            identifier_search = self.__tsan_leaking_thread_fragment_pattern.search(stack.title)
            if identifier_search:
                return [identifier_search.group('identifier')]
        return []
