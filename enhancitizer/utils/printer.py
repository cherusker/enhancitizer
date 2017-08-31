# ------------------------------------------------------------------------------
#
# Author:
#   Armin Hasitzka (enhancitizer@hasitzka.com)
#
# Licensed under the MIT license.
#   See LICENSE in the project root for license information.
#
# ------------------------------------------------------------------------------

class Printer(object):
    """Handles the print function"""

    def __init__(self, options):
        self.__options = options

    def welcome(self):
        # TODO: add a nice welcome message
        return self.nl()
    
    def settings(self):
        if not self.__options.print_minimal:
            print('Settings:\n' + \
                  '  project root:  ' + self.__options.project_root_path + '\n' + \
                  '  output folder: ' + self.__options.output_root_path + '\n' + \
                  '  logfiles:')        
            for path in self.__options.logfiles_paths:
                print('    ' + path)
            self.nl()
        return self

    def nl(self):
        print()
        return self

    def just_print(self, stuff):
        """Only use this for very special purposes"""
        print(str(stuff))
        return self

    def task_description(self, description):
        print(str(description))
        return self

    def task_info(self, info):
        if not self.__options.print_minimal:
            print('  ' + str(info))
        return self

    def task_info_debug(self, info):
        if self.__options.print_debug:
            print('  ' + str(info))
        return self

    def bailout(self, message):
        print('error: ' + str(message))
        exit()
