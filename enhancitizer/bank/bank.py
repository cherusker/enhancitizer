# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

from copy import copy
import os

from .extraction import TSanReportExtractor

class ReportsBank(object):
    """Extracts reports from a log file and stores objects of ReportsBankReport"""

    __reports_dir_name = 'reports'

    def __init__(self, options):
        self.__options = options
        self.__reports = []
        self.__iter_pos = 0
        self.__reports_dir_path = os.path.join(options.output_root_path, self.__reports_dir_name)
        self.__extractors = [
            TSanReportExtractor(options, self.__reports_dir_path)
        ]

    def __iter__(self):
        self.__iter_pos = 0
        return self

    def __next__(self):
        if self.__iter_pos >= len(self.__reports):
            raise StopIteration
        else:
            self.__iter_pos += 1
            # return a copy to remove call stacks automatically after possible usage
            return copy(self.__reports[self.__iter_pos - 1])

    def collect_reports(self):
        """Collect existing reports from the output folder"""
        return
        for extractor in self.__extractors:
            extractor.collect()

    def extract_reports(self):
        """Extract new reports from the logfile"""
        # we really only want one walk through large logfiles
        with open(self.__options.logfile_path, 'r') as logfile:
            last_line = ''
            for line in logfile:
                for extractor in self.__extractors:
                    extractor.extract(last_line, line)
                last_line = line
            logfile.close()
            for extractor in self.__extractors:
                self.__reports.extend(extractor.reports)
