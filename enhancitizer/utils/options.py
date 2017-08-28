# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

from argparse import ArgumentParser, SUPPRESS
import os
import re
import shutil

import utils.os

class Options(object):

    __usage_file_path = 'docs/usage.txt'

    def __init__(self):
        self.project_root_path = None
        self.output_root_path = None
        self.logfiles_paths = None
        self.start_clean = False
        self.show_version = False

    def collect(self):
        """Collect and validate command line arguments, then return self"""

        parser = ArgumentParser(usage=SUPPRESS)
        parser.add_argument('--clean',
                            dest='start_clean',
                            action='store_true')
        parser.add_argument('-v', '--version',
                            dest='show_version',
                            action='store_true')
        parser.add_argument('project_root_path',
                            default=None,
                            nargs='?')
        parser.add_argument('output_root_path',
                            default=None,
                            nargs='?')
        parser.add_argument('logfiles_paths',
                            nargs='*')
        args, unknown = parser.parse_known_args()
        self.project_root_path = self.__absolute_path(args.project_root_path)
        self.output_root_path = self.__absolute_path(args.output_root_path)
        self.logfiles_paths = [self.__absolute_path(path) for path in args.logfiles_paths]
        self.start_clean = args.start_clean
        self.show_version = args.show_version
        if self.show_version:
            # TODO: get the version string from __init__.py
            print('\nenhancitizer version 0.0.0\n')
            exit()
        if not self.project_root_path or not self.output_root_path:
            self.__show_usage()
        if not os.path.isdir(self.project_root_path):
            print('\nError: PROJECT-ROOT is no valid directory.')
            self.__show_usage()
        if os.path.isfile(self.output_root_path):
            print('\nError: OUTPUT-FOLDER is a file.')
            self.__show_usage()
        if self.start_clean and os.path.isdir(self.output_root_path):
            shutil.rmtree(self.output_root_path)
        if not os.path.isdir(self.output_root_path):
            utils.os.makedirs(self.output_root_path)
        paths = self.logfiles_paths
        self.logfiles_paths = []
        while len(paths) > 0:
            path = paths.pop()
            if os.path.isfile(path):
                if not path in self.logfiles_paths:
                    self.logfiles_paths.append(path)
            elif os.path.isdir(path):
                paths.extend([os.path.join(path, name) for name in os.listdir(path)])
            else:
                print('\nError: Unable to extract LOGFILES from ' + path  + '.')
                self.__show_usage()
        self.logfiles_paths = sorted(self.logfiles_paths)
        return self

    def __absolute_path(self, path):
        """Converts file_path to a path string that contains "/" (no "\") and a trailing /"""
        return None if not path else os.path.abspath(os.path.expanduser(path))

    def __show_usage(self):
        """Show usage message and exit"""
        with open(self.__usage_file_path) as usage:
            print('\n' + usage.read())
            usage.close()
        exit()
