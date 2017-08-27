# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

import time

from bank.bank import ReportsBank
from tasks.blacklist import TaskCreateTSanBlacklist
from tasks.context import TaskAddTSanContext
from tasks.csv import TaskTSanCsvSummary
from tasks.duplication import TaskEliminateDuplicates
from tasks.skeleton import TaskBuildSkeleton
from tasks.stuff import TaskSummary
from utils.utils import StopWatch

class Enhancitizer(object):
    
    def __init__(self, options):
        self.__options = options
        self.__tasks = []

    def add_tasks(self, task):
        """Add additional tasks that will be executed after the main tasks"""
        self.__tasks.append(task)

    def run(self):
        """Run the enhancitizer"""
        # TODO: add a nice welcome message
        print('\nSettings:\n' + \
              '  project root:  ' + self.__options.project_root_path + '\n' + \
              '  logfile:       ' + self.__options.logfile_path + '\n' + \
              '  output folder: ' + self.__options.output_root_path + '\n')
        bank = ReportsBank(self.__options)
        print('Collecting existing reports ...')
        watch = StopWatch().start()
        bank.collect_reports()
        print('  execution time: ' + str(watch) + '\n\n'
              'Extracting new reports ...')
        watch.start()
        bank.extract_reports()
        print('  execution time: ' + str(watch) + '\n')
        tasks = [
            TaskEliminateDuplicates(bank),
            TaskCreateTSanBlacklist(self.__options),
            TaskTSanCsvSummary(),
            TaskBuildSkeleton(self.__options),
            # add the context rather late in the game to speed up the parsing of the previous tasks
            TaskAddTSanContext(),
            TaskSummary()
        ]
        tasks.extend(self.__tasks)
        for task in tasks:
            watch.start()
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
                print('  execution time: ' + str(watch) + '\n')
