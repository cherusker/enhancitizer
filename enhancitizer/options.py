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
import re

from utils import FileUtils

class Options:

    usage_file_path = 'docs/usage.txt'

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

    show_version = False
    project_root_path = None
    logfile_path = None
    output_root_path = None

    def collect():
        """Collect and validate command line arguments, then return self"""
        args, unknown = Options.parser.parse_known_args()
        Options.show_version = args.show_version
        Options.project_root_path = FileUtils.absolute_path(getattr(args, 'PROJECT-ROOT'))
        Options.logfile_path = FileUtils.absolute_path(args.LOGFILE)
        Options.output_root_path = FileUtils.absolute_path(getattr(args, 'OUTPUT-FOLDER'))

    def show_usage():
        """Show usage message and exit"""
        with open(Options.usage_file_path) as usage:
            print('\n' + usage.read())
            usage.close()
        exit()
