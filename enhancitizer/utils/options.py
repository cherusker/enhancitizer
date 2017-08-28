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

class Options(object):

    __usage_file_path = 'docs/usage.txt'

    def __init__(self):
        self.show_version = False
        self.project_root_path = None
        self.logfile_path = None
        self.output_root_path = None

    def collect(self):
        """Collect and validate command line arguments, then return self"""

        parser = ArgumentParser(usage=SUPPRESS)
        parser.add_argument('-v', '--version',
                            dest='show_version',
                            action='store_true')
        parser.add_argument('PROJECT-ROOT',
                            default=None,
                            nargs='?')
        parser.add_argument('LOGFILE',
                            default=None,
                            nargs='?')
        parser.add_argument('OUTPUT-FOLDER',
                            default='enhancitizer',
                            nargs='?')
        args, unknown = parser.parse_known_args()

        self.show_version = args.show_version
        self.project_root_path = self.__absolute_path(getattr(args, 'PROJECT-ROOT'))
        self.logfile_path = self.__absolute_path(args.LOGFILE)
        self.output_root_path = self.__absolute_path(getattr(args, 'OUTPUT-FOLDER'))

        if self.show_version:
            # TODO: get the version string from __init__.py
            print('\nenhancitizer version 0.0.0\n')
            exit()
        if not self.project_root_path or not self.logfile_path or not self.output_root_path:
            self.__show_usage()
        if not os.path.isdir(self.project_root_path):
            print('\nError: PROJECT-ROOT is no valid directory.')
            self.__show_usage()
        if not os.path.isfile(self.logfile_path):
            print('\nError: LOGFILE is no valid file.')
            self.__show_usage()
        if os.path.isfile(self.output_root_path):
            print('\nError: OUTPUT-FOLDER is a file.')
            self.__show_usage()
        if not os.path.isdir(self.output_root_path):
            try:
                os.makedirs(self.output_root_path)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

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
