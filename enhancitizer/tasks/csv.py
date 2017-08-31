# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

import csv
import os
import re

import utils.files
from utils.printer import Printer

class TaskCreateCsvSummaries(object):
    """Summarise the reports and collect the info in CSV files"""

    description = 'Summarising the reports ...'

    __csv_base_dir_name = 'summaries'
    __csv_file_ending = '.csv'
    __csv_delimiter = ','

    __tsan_data_race_expected_funcs_per_report = 2

    def setup(self, options):
        self.__printer = Printer(options)
        self.__csv_base_dir_path = os.path.join(options.output_root_path, self.__csv_base_dir_name)
        utils.files.makedirs(self.__csv_base_dir_path)
        self.__controls = {
            'tsan': {
                'data race': {
                    'header_func': self.__header_tsan_data_race,
                    'process_func': self.__process_tsan_data_race
                }
            }
        }

    def process(self, report):
        sanitizer_name_short = report.sanitizer.name_short
        category_name = report.category_name
        controls = self.__controls.get(sanitizer_name_short, {}).get(category_name)
        if controls:
            if not 'csv' in controls:
                csv_file_path = os.path.join(
                    self.__csv_base_dir_path,
                    sanitizer_name_short + '-' +
                    category_name.lower().replace(' ', '-') +
                    self.__csv_file_ending)
                csv_file = open(csv_file_path, 'w')
                if csv_file:
                    self.__printer.task_info('creating ' + csv_file_path)
                    controls['csv'] = {
                        'file': csv_file,
                        'writer': csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
                    }
                if 'header_func' in controls:
                    self.__write_row(sanitizer_name_short, category_name, controls['header_func']())
            if 'process_func' in controls:
                self.__write_row(sanitizer_name_short, category_name, controls['process_func'](report))

    def teardown(self):
        for categories in self.__controls.values():
            for controls in categories.values():
                controls['csv']['file'].close()

    def __write_row(self, sanitizer_name_short, category_name, row):
        csv = self.__controls.get(sanitizer_name_short, {}).get(category_name, {}).get('csv')
        if csv and row:
            csv['writer'].writerow([str(cell) for cell in row])

    def __header_tsan_data_race(self):
        field_names = ['folder', 'file', 'function', 'op', 'size']
        return ['id'] + field_names + list(reversed(field_names)) + ['global location']

    def __process_tsan_data_race(self, report):
        row = [report.number]
        func_count = 0
        for stack in report.call_stacks:
            if 'tsan_data_race_type' in stack.special and len(stack.frames) > 0:
                func_count += 1
                details = [
                    stack.frames[0].src_file_dir_rel_path,
                    stack.frames[0].src_file_name,
                    stack.frames[0].func_name,
                    stack.special.get('tsan_data_race_type'),
                    stack.special.get('tsan_data_race_bytes')
                ]
                # reversing the 2nd function improves the readability of the file
                row.extend(list(reversed(details) if func_count == 2 else details))
        for i in range(func_count, self.__tsan_data_race_expected_funcs_per_report):
            row.extend([None, None, None, None, None])
        row = ['?' if not cell else cell for cell in row]
        row.append(report.special.get('tsan_data_race_global_location', ''))
        return row
