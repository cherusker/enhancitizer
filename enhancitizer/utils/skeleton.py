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
import re

class Skeleton(object):

    __additional_lines_count = 3 # amount of lines to include before and after marked lines
    __normalised_tab_width = 4 # 1 tab = x spaces

    __line_indent_pattern = re.compile('^(?P<indent>\s*)(?P<content>.*)$')
    __whitespace_pattern = re.compile('\s')
    __tab_pattern = re.compile('\t')

    def __init__(self, src_file_path):
        self.__src_file_path = src_file_path
        self.__exported_line_nums = []
        # line_num.char_pos.texts
        self.__data = {}

    @property
    def marked_lines_count(self):
        return len(self.__data)

    def mark(self, line_num, char_pos, text):
        self.__exported_line_nums.extend([i
                  for i in range(line_num - self.__additional_lines_count, line_num + self.__additional_lines_count + 1)
                  if i >= 0 and not i in self.__exported_line_nums])
        if not line_num in self.__data:
            self.__data[line_num] = OrderedDict()
        if not char_pos in self.__data[line_num]:
            self.__data[line_num][char_pos] = []
        if not text in self.__data[line_num][char_pos]:
            self.__data[line_num][char_pos].append(text)
            
    def __line_indicator(self, padding, text=''):
        """Returns a string that has text followed by ':' and padded with whitespaces"""
        text = str(text)
        return text + (':' if text else ' ') + ' ' * (padding - len(text))
        
    def __normalise_line(self, line):
        """Returns a tuple: added_chars_count, normalised_line (foreach \t = '    ')"""
        search = self.__line_indent_pattern.search(line)
        if not search:
            return 0, line
        indent = search.group('indent')
        normalised_indent = self.__tab_pattern.sub(' ' * self.__normalised_tab_width, indent)
        return len(normalised_indent) - len(indent), \
            normalised_indent + self.__whitespace_pattern.sub(' ', search.group('content'))

    def write(self, output_file):
        """Put this skeleton into output_file with is an opened file with the right to write"""
        with open(self.__src_file_path, 'r') as src_file:
            padding = len(str(max(self.__exported_line_nums))) + 1
            last_line_num = None
            for i, line in enumerate(src_file):
                line_num = i + 1 # source code lines start with 1 and not with 0
                if line_num in self.__exported_line_nums:
                    if last_line_num and line_num - last_line_num > 1:
                        output_file.write('\n...\n\n')
                    added_chars_count, normalised_line = self.__normalise_line(line)
                    if line.strip():
                        output_file.write(
                            self.__line_indicator(padding, line_num) + normalised_line + '\n')
                    line_data = self.__data.get(line_num)
                    if line_data:
                        output_file.write(self.__line_indicator(padding))
                        all_char_pos = line_data.keys()
                        for char_pos in range(1, max(all_char_pos) + added_chars_count + 1):
                            output_file.write('^' if char_pos - added_chars_count in all_char_pos else ' ')
                        output_file.write('\n')
                        for char_pos, texts in sorted(line_data.items(), key=lambda d: d[0]):
                            additional_padding = ' ' * (added_chars_count + char_pos - 1)
                            texts_len = len(texts)
                            for i, text in enumerate(sorted(texts)):
                                output_file.write(
                                    self.__line_indicator(padding) + additional_padding +
                                    ('\'' if i == texts_len - 1 else '|') +
                                    '--> ' + text + '\n')
                        output_file.write('\n')
                    last_line_num = line_num
            src_file.close()
