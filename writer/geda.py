#!/usr/bin/env python
#
# Basic Strategy
# 0) converted file will be store in subdirectory [TODO]
# 1) create subdirectory, symbol and project file [TODO]
# 2) Write each component into a .sym file [TODO]
# 3) Write component instances to .sch file [TODO]
# 4) Store net segments at the end of .sch file [TODO]

## v 20110115 2
## C 40000 40000 0 0 0 title-B.sym
## T 50300 40900 9 10 1 0 0 0 1
## title text

import os
import types

from core.shape import Point


class GEDAWriterError(Exception):
    pass


class GEDA:
    """ The gEDA Format Writer """

    ## gEDA grid size is 100mils
    ## to 10px in openjson format 
    SCALE_FACTOR = 10

    def __init__(self):
        ## offset used as bottom left origin as default
        ## in gEDA when starting new file
        self.offset = Point(40000, 40000)

        self.project_dirs = {
            'symbol': None,
            'project': None,
        }

    def write(self, design, filename):
        """ Write the design to the gEDA format """
        ##TODO(elbaschid): setup project environment
        self.create_project_files(filename)

        ##TODO(elbaschid): create symbol files for components
        self.create_symbols(design.components)

        ##TODO(elbaschid): generate schematic from design
        output = self.create_schematic_file(design)

        f = open(filename, "w")
        f.write('\n'.join(output))
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

    def create_symbols(self, components):
        raise NotImplementedError()

    def write_component_to_file(self, component):
        raise NotImplementedError()

    def create_nets(self, nets):
        raise NotImplementedError()

    def write_schematic_file(self, design):
        output = []

        ## create page frame & write name and owner 
        output.extend(
            self.create_title(design.design_attributes)
        )

        ##TODO(elbaschid): create component instances

        ##TODO(elbaschid): create nets

        return output

    def create_title(self, design_attributes):
        title_data = ['v 20110115 2',]

        title_data.append(
            self.create_component(self.offset.x, self.offset.y, 'title-B.sym')
        )
        title_data.append(
            self.create_text(1390, 10, design_attributes.owner, size=10)
        )
        title_data.append(
            self.create_text(1010, 8, design_attributes.name, size=20)
        )

        ## set coordinates at offset for design attributes
        for key, value in design_attributes.attributes:
            visibility = 1  

            if key.startswith('_'):
                visibility = 0
                key = key[1:]    

            attribute_text = '%s=%s' % (key, value)

            title_data.append(
                self.create_text(
                    self.to_mils(0),
                    self.to_mils(0),
                    attribute_text,
                    visibility=visibility
                )
            )

        return title_data

    def create_component(self, x, y, basename, selectable=0, angle=0, mirror=0):
        return 'C %d %d %d %d %d %s' % (
            self.to_mils(x),
            self.to_mils(y),
            selectable,
            angle,
            mirror,
            basename
        )

    def create_text(self, text, x, y, size=10, visibility=1, show_name_value=1,
            angle=0, alignment=0):

        if isinstance(text, basestring):
            numlines = text.split('\n')

        assert(isinstance(text, types.ListType))

        text_line =  'T %d %d %d %d %d %d %d %d %d %d' % (
            self.to_mils(x) + self.offset.x,
            self.to_mils(y) + self.offset.y,
            color,
            size,
            visibility,
            show_name_value,
            angle, 
            alignment, 
            len(text),
        )
        return [text_line] + text

    def to_mils(self, px):
        return self.offset.x + (px * self.SCALE_FACTOR)

    def conv_coords(self, x, y):
        return (
            (self.offset.x + x) * self.SCALE_FACTOR,
            (self.offset.y + y) * self.SCALE_FACTOR,
        )
