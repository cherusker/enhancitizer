# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

from bank.extractor import TSanExtractor
from bank.report import Report

class ReportsBank:
    """Extracts reports from a log file and stores objects of ReportsBankReport"""

    def __init__(self):
        self.meta_reports = []

    def __iter__(self):
        self.iter_position = 0
        return self

    def __next__(self):
        if self.iter_position >= len(self.meta_reports):
            raise StopIteration
        else:
            self.iter_position += 1
            return Report(self.meta_reports[self.iter_position - 1])

    def extract(self, log_file_path, output_dir_path):

        with open(log_file_path, 'r') as log_file:

            # the start patterns matche the 2nd line of a report, hence we have to buffer the line before that
            last_line = ''
            extractors = [
                TSanExtractor(output_dir_path)
            ]

            for line in log_file:
                for extractor in extractors:
                    extractor.extract(last_line, line)
                last_line = line

            log_file.close()

            for extractor in extractors:
                self.meta_reports += extractor.meta_reports

        return self
