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

from utils.printer import Printer

class TaskAnalyseReports(object):
    """Analyse reports and add (special) data"""

    description = 'Analysing reports ...'

    __tsan_data_race_global_location_pattern = re.compile(
        '^  location is global \'(?P<global_location>.+)\' of size \d', re.IGNORECASE)

    def setup(self, options):
        self.__printer = Printer(options)
        self.__analysing_funcs = {
            'tsan': {
                'data race': self.__tsan_analyse_data_race
            }
        }

    def process(self, report):
        if self.__analysing_funcs.get(report.sanitizer.name_short, {}).get(report.category_name):
            self.__analysing_funcs[report.sanitizer.name_short][report.category_name](report)

    def __tsan_analyse_data_race(self, report):
        with open(report.file_path, 'r') as report_file:
            for line in report_file:
                search = self.__tsan_data_race_global_location_pattern.search(line)
                if search:
                    self.__printer.task_info('found global location of ' + str(report))
                    report.special['tsan_data_race_global_location'] = search.group('global_location')
            report_file.close()
