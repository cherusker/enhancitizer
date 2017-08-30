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
from tasks.analysing import TaskAnalyseReports
from tasks.blacklist import TaskCreateTSanBlacklist
from tasks.compaction import TaskCompactReports
from tasks.context import TaskAddTSanContext
from tasks.csv import TaskTSanCsvSummary
from tasks.duplication import TaskEliminateDuplicateReports
from tasks.skeleton import TaskBuildSkeleton
from tasks.stuff import TaskSummary
from utils.printer import Printer
from utils.utils import StopWatch

class Enhancitizer(object):
    
    def __init__(self, options):
        self.__options = options
        self.__printer = Printer(options)
        self.__tasks = []

    def add_tasks(self, task):
        """Add additional tasks that will be executed after the main tasks"""
        self.__tasks.append(task)

    def run(self):
        """Run the enhancitizer"""
        bank = ReportsBank(self.__options)
        self.__printer.welcome() \
                      .nl() \
                      .settings() \
                      .nl() \
                      .task_description('Collecting existing reports ...')
        watch = StopWatch().start()
        bank.collect_reports()
        self.__printer.task_debug_info('execution time: ' + str(watch)) \
                      .nl() \
                      .task_description('Extracting new reports ...')
        watch.start()
        for path in self.__options.logfiles_paths:
            bank.extract_reports(path)
        self.__printer.task_debug_info('execution time: ' + str(watch)).nl()
        tasks = [
            TaskEliminateDuplicateReports(bank), # should be the first thing
            TaskCompactReports(), # after the elimination, before "real" tasks
            TaskAnalyseReports(), # after the elimination, before "real" tasks
            TaskCreateTSanBlacklist(),
            TaskBuildSkeleton(),
            TaskTSanCsvSummary(),
            TaskAddTSanContext(), # should run late to speed up stack parsing of the previous tasks
            TaskSummary() # should be the last thing
        ]
        tasks.extend(self.__tasks)
        for task in tasks:
            watch.start()
            if hasattr(task, 'description'):
                self.__printer.task_description(task.description)
            if hasattr(task, 'setup'):
                task.setup(self.__options)
            if hasattr(task, 'process'):
                for report in bank:
                    task.process(report)
            if hasattr(task, 'teardown'):
                task.teardown()
            if hasattr(task, 'description'):
                self.__printer.task_debug_info('execution time: ' + str(watch)).nl()
