#!/usr/bin/env python3

# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

__version__ = '0.1.1'

import os
import shutil
import time

from bank import ReportsBank, ReportsBankIterator
from context import Contexter
from setup import ArgParser

def main():

    arg_parser = ArgParser().collect()

    if arg_parser.show_version:
        print('version: ' + __version__)
        exit()

    if not arg_parser.logfile_path or not arg_parser.output_dir_path:
        ArgParser.parser.print_help()

    # TODO: check logfile_path (within ArgParser?)

    if os.path.exists(arg_parser.output_dir_path):
        # TODO: ask to overwrite
        shutil.rmtree(arg_parser.output_dir_path)
    os.makedirs(arg_parser.output_dir_path)

    # TODO: add a nice welcome message?

    print('\nSettings:\n  logfile: ' + arg_parser.logfile_path + '\n  output folder: ' + arg_parser.output_dir_path + '\n')

    print("Extracting files ...")
    bank = ReportsBank().extract(arg_parser.logfile_path, arg_parser.output_dir_path)
    print()

    # TODO: implement passes
    
    print("Adding context ...")
    contexter = Contexter()
    for report in ReportsBankIterator(bank):
        contexter.add_context_to_file(report.meta.file_path)
    print()

    # TODO: implement the summary as a pass
    print('Summary:')
    reports_info = bank.reports_counter.data
    if len(reports_info) < 1:
        print('  nothing found')
    else:
        for name in sorted(reports_info):
            print('  ' + name + ': ' + repr(reports_info[name]))
    print()

if __name__ == "__main__":
    main()
