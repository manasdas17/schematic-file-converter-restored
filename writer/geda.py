#!/usr/bin/env python
#
# Basic Strategy
# 0) converted file will be store in subdirectory [TODO]
# 1) create subdirectory, symbol and project file [TODO]
# 2) Write each component into a .sym file [TODO]
# 3) Write component instances to .sch file [TODO]
# 4) Store net segments at the end of .sch file [TODO]

import os


class GEDA:
    """ The gEDA Format Writer """

    def __init__(self):
        self.offset = None

        self.project_dirs = {
            'symbol': None,
            'project': None,
        }

    def write(self, design, filename):
        """ Write the design to the gEDA format """

        f = open(filename, "w")
        # Write!
        f.close()
        return

    def create_project_files(self, filename):
        project_dir = os.path.dirname(filename)
        symbol_dir = os.path.join(project_dir, 'symbols')

        if not os.path.exists(symbol_dir):
            os.mkdir(symbol_dir)

        ## create project file to allow gEDA find symbol files
        project_file = 'gafrc'
        fh = open(os.path.join(project_dir, 'gafrc'), 'w')
        fh.write('(component-library "./symbols")')
        fh.close()

        self.project_dirs['symbol'] = symbol_dir
        self.project_dirs['project'] = project_dir 

