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

__version__ = '0.1.2'

import os
import shutil
import time

from bank.bank import ReportsBank
from setup import ArgParser
from tasks.context import TaskReportContext
from tasks.stuff import TaskSummary

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

    for task in [
            TaskReportContext(),
            TaskSummary()
    ]:
        if hasattr(task, 'description'):
            print(task.description)
        if hasattr(task, 'setup'):
            task.setup()
        if hasattr(task, 'process_meta'):
            for meta_report in bank.meta_reports:
                task.process_meta(meta_report)
        if hasattr(task, 'process'):
            for report in bank:
                task.process(report)
        if hasattr(task, 'teardown'):
            task.teardown()
        if hasattr(task, 'description'):
            print()

    exit()
    print("Adding context ...")
    contexter = Contexter()
    for report in ReportsBankIterator(bank):
        contexter.add_context_to_file(report.meta.file_path)
    print()

if __name__ == "__main__":
    main()
