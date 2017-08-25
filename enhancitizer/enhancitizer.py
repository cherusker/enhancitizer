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

__version__ = '0.1.0'

import os
import time

from context import Contexter
from extract import Extractor
from setup import ArgParser

def main():

    arg_parser = ArgParser().collect()

    if arg_parser.show_version:
        print('version: ' + __version__)
        exit()

    if not arg_parser.logfile_path or not arg_parser.output_dir_path:
        ArgParser.parser.print_help()

    # TODO: check logfile_path
    # TODO: create output_dir

    print('\nSettings:\n  logfile: ' + arg_parser.logfile_path + '\n  output folder: ' + arg_parser.output_dir_path + '\n')

    issues_info = Extractor(arg_parser.output_dir_path) \
                  .extract(arg_parser.logfile_path) \
                  .issues_counter.data

    print()
    
    contexter = Contexter()
    if os.path.exists(arg_parser.output_dir_path):
        for file_name in sorted(os.listdir(arg_parser.output_dir_path)):
            contexter.add_context_to_file(arg_parser.output_dir_path + file_name)

    print('\nSummary:')
    if len(issues_info) < 1:
        print('  nothing found')
    else:
        for name in sorted(issues_info):
            print('  ' + name + ': ' + repr(issues_info[name]))

    print()

if __name__ == "__main__":
    main()
