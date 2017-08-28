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

from enhancitizer import Enhancitizer
from utils.options import Options

if __name__ == '__main__':
    Enhancitizer(Options().collect()).run()
