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

from core import shape
from core import components
from core.shape import Point

class GEDAColor:
    BACKGROUND_COLOR = 0
    PIN_COLOR = 1 
    NET_ENDPOINT_COLOR = 2
    GRAPHIC_COLOR = 3
    NET_COLOR = 4
    ATTRIBUTE_COLOR = 5
    LOGIC_BUBBLE_COLOR = 6
    DOTS_GRID_COLOR = 7
    DETACHED_ATTRIBUTE_COLOR = 8
    TEXT_COLOR = 9
    BUS_COLOR = 10
    SELECT_COLOR = 11
    BOUNDINGBOX_COLOR = 12
    ZOOM_BOX_COLOR = 13
    STROKE_COLOR = 14
    LOCK_COLOR = 15


class GEDAWriterError(Exception):
    pass


class GEDA:
    """ The gEDA Format Writer """

    ## gEDA grid size is 100mils
    ## to 10px in openjson format 
    SCALE_FACTOR = 10

    ALIGNMENT = {
        'left': 0,
        'center': 3,
        'right': 4,
    }

    def __init__(self):
        ## offset used as bottom left origin as default
        ## in gEDA when starting new file
        self.offset = Point(0, 0)

        self.project_dirs = {
            'symbol': None,
            'project': None,
        }

    def write(self, design, filename):
        """ Write the design to the gEDA format """
        ##TODO(elbaschid): get offset from design bounds

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

    def _create_title(self, design_attributes):
        title_data = ['v 20110115 2',]

        ##TODO(elbaschid): use offset from design bounds
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
            attribute = self._create_attribute(key, value, x, y)

            title_data.append(attribute)

        return title_data

    def _create_component(self, x, y, basename, selectable=0, angle=0, mirror=0):
        return 'C %d %d %d %d %d %s' % (
            self.to_mils(x),
            self.to_mils(y),
            selectable,
            angle,
            mirror,
            basename
        )

    def _create_attribute(self, key, value, x, y, **kwargs):

        ## make private attribute invisible in gEDA
        if key.startswith('_'): 
            key = key[1:]
            kwargs['visibility'] = 0

        text = "%s=%s" % (str(key), str(value))
        
        kwargs['color'] = GEDAColor.ATTRIBUTE_COLOR

        return self._create_text(text, x, y, **kwargs)

    def _create_text(self, text, x, y, **kwargs):
        
        if isinstance(text, basestring):
            text = text.split('\n')

        assert(isinstance(text, types.ListType))

        text_line =  'T %d %d %d %d %d %d %d %d %d' % (
            self.to_mils(x) + self.offset.x,
            self.to_mils(y) + self.offset.y,
            kwargs.get('color', GEDAColor.TEXT_COLOR),
            kwargs.get('size', 10),
            kwargs.get('visibility', 1),
            0, #show_name_value is always '0'
            self.conv_angle(kwargs.get('angle', 0)),
            kwargs.get('alignment', 0),
            len(text),
        )
        return [text_line] + text

    def _create_pin(self, pin_seq, pin):
        assert(issubclass(pin.__class__, components.Pin))

        connected_x, connected_y = pin.p2.x, pin.p2.y
        
        command = ['P %d %d %d %d %d %d %d' % (
            self.to_mils(connected_x),
            self.to_mils(connected_y),
            self.to_mils(pin.p1.x),
            self.to_mils(pin.p1.y),
            GEDAColor.PIN_COLOR,
            0, #pin type is always 0
            0, #first point is active/connected pin
        )]

        command.append('{')

        if pin.label is not None:
            attribute = self._create_attribute(
                'pinlabel',
                pin.label.text, 
                pin.label.x,
                pin.label.y,
                alignment=self.ALIGNMENT[pin.label.align],
                angle=pin.label.rotation
            )
            command += attribute

        command += self._create_attribute(
            'pinseq', 
            pin_seq, 
            connected_x+10,
            connected_y+10,
            visibility=0,
        )
        command += self._create_attribute(
            'pinnumber', 
            pin.pin_number, 
            connected_x+10,
            connected_y+20,
            visibility=0,
        )

        command.append('}')
        return command

    def _create_arc(self, arc):
        assert(issubclass(arc.__class__, shape.Arc))

        x, y = self.conv_coords(arc.x, arc.y)
        start_angle = self.conv_angle(arc.start_angle)

        sweep_angle = self.conv_angle(arc.end_angle) - start_angle
        if sweep_angle < 0:
            sweep_angle = 360 + sweep_angle

        return [
            'A %d %d %d %d %d %d %d %d %d %d %d' % (
                x, y,
                self.to_mils(arc.radius),
                start_angle, 
                sweep_angle,
                GEDAColor.GRAPHIC_COLOR,
                0, 0, 0, -1, -1 ## default style values
            )
        ]

    def _create_circle(self, circle):
        assert(issubclass(circle.__class__, shape.Circle))

        center_x, center_y = self.conv_coords(circle.x, circle.y)
        return [
            'V %d %d %d 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1' % (
                center_x,
                center_y,
                self.to_mils(circle.radius)
            )
        ]

    def _create_box(self, rect):
        assert(issubclass(rect.__class__, (shape.Rectangle, shape.RoundedRectangle)))
        top_x, top_y = self.conv_coords(rect.x, rect.y)
        width, height = self.to_mils(rect.width), self.to_mils(rect.height)
        ## gEDA uses bottom-left corner as rectangle origin
        return [
            'B %d %d %d %d 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1' % (
                (top_x - height),
                top_y,
                width,
                height
            )
        ]

    def _create_line(self, line):
        assert(issubclass(line.__class__, shape.Line))

        start_x, start_y = self.conv_coords(line.p1.x, line.p1.y)
        end_x, end_y = self.conv_coords(line.p2.x, line.p2.y)
        return [
            'L %d %d %d %d 3 0 0 0 -1 -1' % (
                start_x, 
                start_y,
                end_x, 
                end_y
            )
        ]

    def _create_segment(self, np1, np2=None, attributes=None):
        if np2 is None:
            np1, np2 = np1
        
        np1_x, np1_y = self.conv_coords(np1.x, np1.y)
        np2_x, np2_y = self.conv_coords(np2.x, np2.y)
        command = [
            'N %d %d %d %d %d' % (
                np1_x, np1_y,
                np2_x, np2_y,
                GEDAColor.NET_COLOR
            )
        ]

        if attributes is not None:
            command.append('{')
            for key, value in attributes.items():
                command += self._create_attribute(
                    key, 
                    value, 
                    np1.x+10, 
                    np1.y+10
                )
            command.append('}')

        return command

    def _create_path(self, path):
        if issubclass(path.__class__, shape.Polygon):
            num_lines = len(path.points)+1 ##add closing command to path
            command= ['H 3 0 0 0 -1 -1 1 -1 -1 -1 -1 -1 %d' % num_lines]

            start_x, start_y = path.points[0].x, path.points[0].y
            command.append('M %d,%d' % self.conv_coords(start_x, start_y))

            for point in path.points[1:]:
                command.append('L %d,%d' % self.conv_coords(point.x, point.y))

            command.append('z') #closes the path

        elif issubclass(path.__class__, shape.BezierCurve):
            command = self._create_bezier_curve(path)

        elif issubclass(path.__class__, components.Body):
            ## line will be modified at the end
            #command= ['H 3 0 0 0 -1 -1 1 -1 -1 -1 -1 -1 %d']

            num_lines = 1

            shapes = list(path.shapes) #create new list to be able to modify

            start_shape = shapes[0]
            current_x, current_y = self.conv_coords(
                start_shape.p1.x, 
                start_shape.p1.y
            )
            start_x, start_y = current_x, current_y
            command = ['M %d,%d' % (start_x, start_y)]

            close_command = []

            ## check if last element is line back to starting point
            end_shape = shapes[-1]
            if end_shape.type == 'line':
                if end_shape.p2.x == start_shape.p1.x \
                    and end_shape.p2.y == start_shape.p1.y:
                    ## discard line and close path instead
                    close_command = ['z']
                    shapes.remove(end_shape)
                    num_lines += 1
                    
            for shape_obj in shapes:
                if shape_obj.type == 'line':
                    current_x, current_y = self.conv_coords(
                        shape_obj.p2.x,
                        shape_obj.p2.y
                    )
                    command.append("L %d,%d" % (current_x, current_y))

                elif shape_obj.type == 'bezier':
                    c1_x, c1_y = self.conv_coords(
                        shape_obj.control1.x, 
                        shape_obj.control1.y
                    )
                    c2_x, c2_y = self.conv_coords(
                        shape_obj.control2.x, 
                        shape_obj.control2.y
                    )
                    current_x, current_y = self.conv_coords(
                        shape_obj.p2.x, 
                        shape_obj.p2.y
                    )

                    command += [
                        'C %d,%d %d,%d %d,%d' % (
                            c1_x, c1_y, 
                            c2_x, c2_y,
                            current_x, current_y
                        )
                    ]

                else:
                    raise GEDAWriterError(
                        "shape type '%s' can not be used to create path" % shape_obj.type
                    )

                num_lines += 1

            path_command = 'H 3 0 0 0 -1 -1 1 -1 -1 -1 -1 -1 %d' % num_lines
            command = [path_command] + command + close_command

        else:
            raise GEDAWriterError(
                "unrecognised path object '%s' found" % path.__class__
            )

        return command

    def _create_bezier_curve(self, curve):
        assert(issubclass(curve.__class__, shape.BezierCurve))
        p1_x, p1_y = self.conv_coords(curve.p1.x, curve.p1.y)
        c1_x, c1_y = self.conv_coords(curve.control1.x, curve.control1.y)

        p2_x, p2_y = self.conv_coords(curve.p2.x, curve.p2.y)
        c2_x, c2_y = self.conv_coords(curve.control2.x, curve.control2.y)
        command= [
            'H 3 0 0 0 -1 -1 1 -1 -1 -1 -1 -1 2',
            'M %d,%d' % (p1_x, p1_y),
            'C %d,%d %d,%d %d,%d' % (c1_x, c1_y, c2_x, c2_y, p2_x, p2_y)
        ]

        return command

    def is_valid_path(self, body):
        assert(issubclass(body.__class__, components.Body))

        current_pt = body.shapes[0].p1
        for shape_obj in body.shapes:
            if shape_obj.type not in ['line', 'bezier']:
                return False
            
            if not (current_pt.x == shape_obj.p1.x \
                and current_pt.y == shape_obj.p1.y):
                return False

            current_pt = shape_obj.p2

        return True 

    def to_mils(self, px):
        return self.offset.x + (px * self.SCALE_FACTOR)

    def conv_angle(self, angle, steps=1):
        converted_angle = int(angle * 180)
        return (converted_angle // int(steps)) * steps

    def conv_coords(self, x, y):
        return (
            (self.offset.x + x) * self.SCALE_FACTOR,
            (self.offset.y + y) * self.SCALE_FACTOR,
        )
