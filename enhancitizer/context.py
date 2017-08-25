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

class Contexter:

    stack_depth_max = 3 # max amount of lookups from the top of the call stack

    stack_item_pattern = re.compile('^\s*\#(?P<depth>\d+)\s+' +
                                    '(?P<func_name>[a-z\d_]+)\s+' +
                                    '(?P<src_file_path>[a-z\d/\-\.]+):' +
                                    '(?P<line_num>\d+):' +
                                    '(?P<char_pos>\d+)',
                                    re.IGNORECASE)

    count_line_indent_pattern = re.compile('^(?P<indent>\s*)[^\s]?')

    start_stack_lookup_tsan_pattern = re.compile(
        '^\s*(?:previous\s)?(?:read|write)\sof\ssize\s\d+\sat\s0x[\da-f]+\sby\s', re.IGNORECASE)
    
    def add_context_to_file(self, orig_file_path):

        print('Contexter: adding context to ' + orig_file_path)

        context_file_path = orig_file_path + '.ctx'
        with open(context_file_path, 'w') as context_file:
            context_file.write('\n')

            with open(orig_file_path, 'r') as orig_file:
                stack_lookup = False # lookup is limited to "special" stack traces
                for line in orig_file:
                    if not stack_lookup:
                        stack_lookup = self.start_stack_lookup(line)
                    else:
                        stack_item = self.stack_item_pattern.search(line)
                        if stack_item and int(stack_item.group('depth')) < self.stack_depth_max:
                            context_file.write(self.get_context_function(
                                stack_item.group('src_file_path'),
                                stack_item.group('func_name'),
                                int(stack_item.group('line_num')),
                                int(stack_item.group('char_pos'))))
                            # stack_lookup = True
                        else:
                            stack_lookup = False
                orig_file.close()
                
            with open(orig_file_path, 'r') as orig_file:
                for line in orig_file:
                    context_file.write(line)
                orig_file.close()

            context_file.close()

            os.remove(orig_file_path)
            os.rename(context_file_path, orig_file_path)
        
        return self

    def start_stack_lookup(self, line):
        return bool(self.start_stack_lookup_tsan_pattern.search(line))
    
    def get_context_function(self, src_file_path, func_name, line_num, char_pos):
        # TODO: find full function signature
        func_signature = func_name + '(...)'
        affected_line = ''
        affected_line_indent = 0
        with open(src_file_path, 'r') as src_file:
            for i, line in enumerate(src_file):
                if i == line_num - 1:
                    count_line_indent = self.count_line_indent_pattern.search(line)
                    affected_line_indent = 0 if not count_line_indent else len(count_line_indent.group('indent'))
                    affected_line = '! ' + line.strip() + '\n'
            src_file.close()
        return '' if affected_line == '' else \
            func_signature + ' {\n' + \
            '  // ...\n' + \
            affected_line + \
            (' ' * (char_pos - affected_line_indent + 1)) + '^\n' + \
            '  // ...\n' + \
            '}\n' + \
            '\n'
