# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

from utils import NameCounter

class TaskSummary:
    """Print various stats about the reports"""
    
    def setup(self):
        self.counter = NameCounter()

    def process_meta(self, meta_report):
        self.counter.inc(meta_report.category + ' (' + meta_report.sanitizer + ')')

    def teardown(self):
        print('Summary:')
        if len(self.counter.data) < 1:
            print('  nothing found')
        else:
            for name, count in self.counter.data.items():
                print('  ' + name + ': ' + repr(count))
        print()
        
