import re
import os
import shutil

from utils import Counter

class Extractor:

    issue_start_line_pattern = re.compile('^warning:\sthreadsanitizer:\s([a-z\s]+)\s\(', re.IGNORECASE)
    issue_end_line_pattern = re.compile('^=+$', re.MULTILINE)

    def __init__(self, output_dir_path):
        self.issues_counter = Counter()
        self.output_dir_path = output_dir_path
        self.output_dir_initialized = False

    def init_output_dir(self):
        if self.output_dir_initialized:
            return self;
        if os.path.exists(self.output_dir_path):
            shutil.rmtree(self.output_dir_path)
        os.makedirs(self.output_dir_path)
        self.output_dir_initialized = True
        return self
    
    def extract(self, file_path):

        self.output_dir_initialized = False
        
        copy_from_file = open(file_path, 'r')
        copy_to_file = None
        
        last_line = ''

        for line in copy_from_file:
            if copy_to_file:
                copy_to_file.write(line)
                if self.issue_end_line_pattern.match(line):
                    copy_to_file.close()
                    copy_to_file = None
            else:
                issue_name_search = self.issue_start_line_pattern.search(line)
                if issue_name_search:
                    issue_name = issue_name_search.group(1).lower()
                    issue_no = self.issues_counter.inc(issue_name)
                    print('Extractor: found "' + issue_name + '" (' + repr(issue_no) + ')')
                    self.init_output_dir()
                    copy_to_file = open(self.output_dir_path + \
                                        issue_name.replace(' ', '-') + '-' + repr(issue_no).zfill(3) + \
                                        '.txt',
                                        'w')
                    copy_to_file.write(last_line)
                    copy_to_file.write(line)
            last_line = line

        copy_from_file.close()
        return self
