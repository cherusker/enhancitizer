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

__version__ = '0.1.4'

import os

from bank.bank import ReportsBank
from options import Options
from tasks.blacklist import TaskCreateTSanBlacklist
from tasks.context import TaskAddTSanContext
from tasks.csv import TaskTSanCsvSummary
from tasks.stuff import TaskSummary

def main():

    Options.collect()

    if Options.show_version:
        print('\nenhancitizer version ' + __version__ + '\n')
        exit()

    if not Options.project_root_path or not Options.logfile_path or not Options.output_root_path:
        Options.show_usage()

    if not os.path.isdir(Options.project_root_path):
        print('\nError: PROJECT-ROOT is no valid directory.')
        Options.show_usage()

    if not os.path.isfile(Options.logfile_path):
        print('\nError: LOGFILE is no valid file.')
        Options.show_usage()

    if os.path.isfile(Options.output_root_path):
        print('\nError: OUTPUT-FOLDER is a file.')
        Options.show_usage()

    if not os.path.isdir(Options.output_root_path):
        try:
            os.makedirs(Options.output_root_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    # TODO: add a nice welcome message?

    print('\nSettings:\n' + \
          '  project root:  ' + Options.project_root_path + '\n' + \
          '  logfile:       ' + Options.logfile_path + '\n' + \
          '  output folder: ' + Options.output_root_path + '\n')

    bank = ReportsBank()
    print("Collecting existing reports ...")
    bank.collect()
    print("\nExtracting new reports ...")
    bank.extract()
    print()

    for task in [
            TaskCreateTSanBlacklist(),
            TaskTSanCsvSummary(),
            # add the context rather late in the game to speed up the parsing of the previous tasks
            TaskAddTSanContext(),
            TaskSummary()
    ]:
        if hasattr(task, 'description'):
            print(task.description)
        if hasattr(task, 'setup'):
            task.setup()
        if hasattr(task, 'process_report'):
            for meta_report in bank.meta_reports:
                task.process_report(meta_report)
        if hasattr(task, 'teardown'):
            task.teardown()
        if hasattr(task, 'description'):
            print()

if __name__ == "__main__":
    main()
