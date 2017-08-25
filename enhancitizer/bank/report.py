# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

class MetaReport:
    """A trade-off between memory consumption and file interactions to store important information"""

    def __init__(self, new, sanitizer, category, no, file_path=''):
        self.new = new
        self.sanitizer = sanitizer
        self.category = category
        self.no = no
        self.file_path = file_path

class Report:
    """Wraps around objects of MetaReport and knows all the details"""

    def __init__(self, meta_report):
        self.meta = meta_report
