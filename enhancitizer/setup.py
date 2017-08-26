# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

from argparse import ArgumentParser
import re

class ArgParser:

    parser = ArgumentParser(description='Find stack traces of Clang\'s sanitizers and generate enhanced versions.')
    parser.add_argument('-v', '--version',
                        dest='show_version',
                        help='Show version information.',
                        action='store_true')
    parser.add_argument('LOGFILE',
                        help='Looking for stack traces in this file.')
    parser.add_argument('OUTPUT-FOLDER',
                        help='Placing enhanced stack traces into this folder.',
                        default='enhancitizer',
                        nargs='?')

    def __init__(self):
        self.show_version = False
        self.logfile_path = None
        self.output_dir_path = None

    def collect(self):
        args = self.parser.parse_args()
        self.show_version = args.show_version
        self.logfile_path = args.LOGFILE
        self.output_dir_path = getattr(args, 'OUTPUT-FOLDER')
        if not re.search('^\.\.?\/', self.output_dir_path):
            self.output_dir_path = './' + self.output_dir_path
        if not re.search('(?:\\|\/)$', self.output_dir_path):
            self.output_dir_path += '/'
        return self
