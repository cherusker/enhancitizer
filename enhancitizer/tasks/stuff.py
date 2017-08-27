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

class TaskSummary(object):
    """Print various stats about the reports"""
    
    def setup(self):
        self.counter = NameCounter()

    def process(self, report):
        self.counter.inc(report.category + ' (' + report.sanitizer + ')')

    def teardown(self):
        print('Summary:')
        if len(self.counter.data) < 1:
            print('  nothing found')
        else:
            for name, count in self.counter.data.items():
                print('  ' + name + ': ' + str(count))
        print()
        
