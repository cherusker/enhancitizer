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

    def __init__(self, options):
        self.__reports = []
        self.__iter_pos = 0
        self.__extractors = [
            TSanReportExtractor(options)
        ]

    def __iter__(self):
        self.__iter_pos = 0
        return self

    def __next__(self):
        if self.__iter_pos > 1:
            # don't keep the call stacks; they would waste a huge amount of memory
            del self.__reports[self.__iter_pos - 1].call_stacks
        if self.__iter_pos >= len(self.__reports):
            raise StopIteration
        else:
            self.__iter_pos += 1
            return self.__reports[self.__iter_pos - 1]

    def collect_reports(self):
        """Collect existing reports from the output folder"""
        for extractor in self.__extractors:
            extractor.collect()
            self.__reports.extend(extractor.reports)

    def extract_reports(self, logfile_path):
        """Extract new reports from the logfile"""
        # we really only want one walk through large logfiles
        with open(logfile_path, 'r') as logfile:
            last_line = ''
            for line in logfile:
                for extractor in self.__extractors:
                    extractor.extract(last_line, line)
                last_line = line
            logfile.close()
            for extractor in self.__extractors:
                self.__reports.extend(extractor.reports)

    def remove_report(self, report):
        """Deletes the report file and removes the report from the bank"""
        os.remove(report.file_path)
        self.__reports.remove(report)
