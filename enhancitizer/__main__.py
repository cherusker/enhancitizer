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

from bank.bank import ReportsBank
from options import Options
from tasks.blacklist import TaskCreateTSanBlacklist
from tasks.context import TaskAddTSanContext
from tasks.csv import TaskTSanCsvSummary
from tasks.duplication import TaskEliminateDuplicates
from tasks.stuff import TaskSummary

def main():

    options = Options().collect()

    # TODO: add a nice welcome message

    print('\nSettings:\n' + \
          '  project root:  ' + options.project_root_path + '\n' + \
          '  logfile:       ' + options.logfile_path + '\n' + \
          '  output folder: ' + options.output_root_path + '\n')

    bank = ReportsBank(options)
    print("Collecting existing reports ...")
    bank.collect_reports()
    print("\nExtracting new reports ...")
    bank.extract_reports()
    print()

    for task in [
        TaskEliminateDuplicates(bank),
        TaskCreateTSanBlacklist(options),
        TaskTSanCsvSummary(),
        # add the context rather late in the game to speed up the parsing of the previous tasks
        TaskAddTSanContext(),
        TaskSummary()
    ]:
        if hasattr(task, 'description'):
            print(task.description)
        if hasattr(task, 'setup'):
            task.setup()
        if hasattr(task, 'process'):
            for report in bank:
                task.process(report)
        if hasattr(task, 'teardown'):
            task.teardown()
        if hasattr(task, 'description'):
            print()

if __name__ == "__main__":
    main()
