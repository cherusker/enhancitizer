# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

import os

from bank.extraction import Report, TSanReportExtractor
from options import Options

class ReportsBank:
    """Extracts reports from a log file and stores objects of ReportsBankReport"""

    reports_dir_name = 'reports'

    def __init__(self):
        self.meta_reports = []
        self.reports_dir_path = os.path.join(Options.output_root_path, self.reports_dir_name)
        self.extractors = [
            TSanReportExtractor(self.reports_dir_path)
        ]

    def collect(self):
        """Collect existing reports from the output folder"""
        for extractor in self.extractors:
            extractor.collect()

    def extract(self):
        """Extract new reports from the logfile"""
        # we really only want one walk through large logfiles
        with open(Options.logfile_path, 'r') as logfile:
            last_line = ''
            for line in logfile:
                for extractor in self.extractors:
                    extractor.extract(last_line, line)
                last_line = line
            logfile.close()
            for extractor in self.extractors:
                self.meta_reports.extend(extractor.meta_reports)
