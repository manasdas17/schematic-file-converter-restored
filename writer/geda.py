#!/usr/bin/env python
#
# Basic Strategy
# 0) converted file will be store in subdirectory [TODO]
# 1) create subdirectory, symbol and project file [TODO]
# 2) Write each component into a .sym file (even EMBEDDED components) [TODO]
# 3) Write component instances to .sch file [TODO]
# 4) Store net segments at the end of .sch file

import os
import types

from core import shape
from core import components
from core.shape import Point
from core.annotation import Annotation

import parser.geda

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

    def __init__(self, symbol_dirs=None, auto_include=False):
        ## add flag to allow for auto inclusion
        if symbol_dirs is None:
            symbol_dirs = []

            if auto_include is True:
                symbol_dirs += [
                    '/usr/share/gEDA/sym',
                    '/usr/local/share/gEDA/sym',
                ]

        self.known_symbols = parser.geda.find_symbols(symbol_dirs)

        ## offset used as bottom left origin as default
        ## in gEDA when starting new file
        self.offset = Point(0, 0)
        self.component_library = None

        ##NOTE: special attributes that are processed
        ## separately and will not be used as regular attributes
        self.ignored_attributes = [
            '_prefix',
            '_suffix',
            '_refdes',
            '_name',
            '_geda-imported',
        ]

        self.project_dirs = {
            'symbol': None,
            'project': None,
        }

    def set_offset(self, point):
        ## create an offset of 5 grid squares from origin (0,0)
        self.offset.x = point.x - 500
        self.offset.y = point.y - 500

    def write(self, design, filename):
        """ Write the design to the gEDA format """
        self.component_library = dict()

        ## setup project environment
        self.create_project_files(filename)

        ## create symbol files for components writing all symbols
        ## to local 'symbols' directory. Symbols that are available
        ## in provided directories are ignored and referenced.
        self._create_symbols(design.components)

        ## generate commands for schematic file from design
        ## output is a list of lines 
        output = self.write_schematic_file(design)

        f = open(filename, "w")
        f.write(self.commands_to_string(output))
        f.close()
        return

    def create_project_files(self, filename):
        project_dir = os.path.dirname(filename)
        symbol_dir = os.path.join(project_dir, 'symbols')

        if not os.path.exists(symbol_dir):
            os.mkdir(symbol_dir)

        ## create project file to allow gEDA find symbol files
        project_file = os.path.join(project_dir, 'gafrc')
        if not os.path.exists(project_file):
            fh = open(os.path.join(project_dir, 'gafrc'), 'w')
            fh.write('(component-library "./symbols")')
            fh.close()
        else:
            print "gafrc file exists. Please make sure it contains following line:"
            print "(component-library './symbols')"

        self.project_dirs['symbol'] = symbol_dir
        self.project_dirs['project'] = project_dir 

    def write_schematic_file(self, design):
        output = []

        ## create page frame & write name and owner 
        output += self._create_schematic_title(design.design_attributes)

        ## create component instances
        output += self.generate_instances(design.component_instances)

        ## create gEDA commands for all nets
        output += self.generate_net_commands(design.nets)

        return output

    def generate_instances(self, component_instances):
        commands = []

        for instance in component_instances:
            ## retrieve symbol for instance
            component_symbol = self.component_library[(
                instance.library_id, 
                instance.symbol_index
            )]

            component_annotations = []

            ## create component instance for every symbolattribute
            for symbol_attribute in instance.symbol_attributes:
                commands += self._create_component(
                    symbol_attribute.x,
                    symbol_attribute.y,
                    angle=symbol_attribute.rotation,
                    basename=component_symbol,
                )

                component_annotations += symbol_attribute.annotations

            for annotation in component_annotations:
                commands += self._convert_annotation(annotation)
        
            commands.append('{')
            commands += self._create_attribute(
                'refdes', 
                instance.instance_id,
                symbol_attribute.x,
                symbol_attribute.y,
                visibility=0,
            )
            attr_x, attr_y = symbol_attribute.x, symbol_attribute.y
            for key, value in instance.attributes.items():
                attr_x, attr_y = attr_x+10, attr_y+10
                commands += self._create_attribute(key, value, attr_x, attr_y)
            commands.append('}')

        return commands

    def write_component_to_file(self, library_id, component):
        ##NOTE: extract and remove gEDA internal attribute
        geda_imported = component.attributes.get('_geda_imported', 'false')
        geda_imported = (geda_imported == "true")

        _prefix = component.attributes.get('_prefix', '')
        _suffix = component.attributes.get('_suffix', '')

        component.attributes['_refdes'] = '%s?%s' % (_prefix, _suffix)

        symbol_filename = None
        if geda_imported:
            ##check if component is known sym file in OS dirs
            symbol_name = component.name.replace('EMBEDDED', '') 
            symbol_filename = "%s.sym" %  symbol_name
            self.component_library[(library_id, 0)] = symbol_filename

            if symbol_name in self.known_symbols:
                return 

        ## write symbol file for each symbol in component
        for sym_idx, symbol in enumerate(component.symbols):

            symbol_attr = "_symbol_%d_0" % sym_idx
            if symbol_attr in component.attributes:
                prefix = component.attributes[symbol_attr]
                del component.attributes[symbol_attr]
            else:
                prefix = component.name

            if not geda_imported:
                prefix = prefix.replace(' ', '_')
                symbol_filename = "%s-%d.sym" % (prefix, sym_idx)
            
            commands = []
            for body in symbol.bodies:
                commands += self.generate_body_commands(body)

            ## write commands to file
            path = os.path.join(
                self.project_dirs['symbol'],
                symbol_filename
            )
            fout = open(path, 'w')
            fout.write(self.commands_to_string(commands))
            fout.close()

            ## required for instantiating components later
            self.component_library[(library_id, sym_idx)] = symbol_filename

    def commands_to_string(self, commands):
        commands = ['v 20110115 2'] + commands
        return '\n'.join(commands)

    def generate_body_commands(self, body):
        commands = []
        
        if self.is_valid_path(body):
            commands += self._create_path(body)
        else:
            for shape in body.shapes:
                method_name = '_convert_%s' % shape.type
                if hasattr(self, method_name):
                    commands += getattr(self, method_name)(shape)
                else:
                    raise GEDAWriterError(
                        "invalid shape '%s' in component" % shape.type
                    )

        ## create commands for pins
        for pin_seq, pin in enumerate(body.pins):
            commands += self._create_pin(pin_seq, pin)

        return commands

    def generate_net_commands(self, nets):
        commands = []
        
        for net in nets:

            ## check if '_name' attribute carries net name 
            if net.attributes.has_key('_name') and net.attributes['_name']:
                net.attributes['netname'] = net.attributes['_name']

            elif len(net.annotations) > 0:
                ## assume that the first annotation is net name
                annotation = net.annotations[0]
                net.attributes['netname'] = annotation.value
                net.annotations.remove(annotation)

            ## parse annotations into text commands
            for annotation in net.annotations:
                commands += self._create_text(
                    annotation.value,
                    annotation.x,
                    annotation.y,
                    rotation=annotation.rotation
                )
            
            ## generate list of segments from net points
            ## prevent segments from being added twice (reverse)
            segments = set()
            for start_id, start_pt in net.points.items():
                for end_id in start_pt.connected_points:
                    if (end_id, start_id) not in segments:
                        segments.add((start_id, end_id)) 

            attributes = dict(net.attributes)
            for segment in segments:
                start_id, end_id = segment

                ## prevent zero-length segements from being written
                if net.points[start_id].x == net.points[end_id].x \
                    and net.points[start_id].y == net.points[end_id].y:
                    ## the same point is defined twice
                    continue

                commands += self._create_segment(
                    net.points[start_id],
                    net.points[end_id],
                    attributes=attributes
                )

                ## it's enough to store net name only in first element
                if attributes is not None:
                    attributes = None

        return commands

    def _create_schematic_title(self, design_attributes):
        commands = []

        commands += self._create_component(
            self.offset.x, 
            self.offset.y, 
            'title-B.sym'
        )

        if design_attributes.metadata.owner:
            commands += self._create_text(
                design_attributes.metadata.owner, 
                self.offset.x+1390, 
                self.offset.y+10, 
                size=10
            )

        if design_attributes.metadata.name:
            commands += self._create_text(
                design_attributes.metadata.name, 
                self.offset.x+1010, 
                self.offset.y+80, 
                size=20
            )

        if design_attributes.metadata.license:
            commands += self._create_attribute(
                '_use_license',
                design_attributes.metadata.license, 
                self.offset.x, 
                self.offset.y, 
            )
         

        ## set coordinates at offset for design attributes
        attr_x, attr_y = self.offset.x, self.offset.y
        for key, value in design_attributes.attributes.items():
            commands += self._create_attribute(
                key, value, 
                attr_x, 
                attr_y,
            )
            attr_x, attr_y = attr_x+10, attr_y+10

        return commands

    def _create_symbols(self, components):
        for library_id, component in components.components.items():
            self.write_component_to_file(library_id, component)

    def _create_component(self, x, y, basename, selectable=0, angle=0, mirror=0):
        x, y = self.conv_coords(x, y)
        return [
            'C %d %d %d %d %d %s' % (
                x, y,
                selectable,
                self.conv_angle(angle),
                mirror,
                basename
            )
        ]

    def _create_attribute(self, key, value, x, y, **kwargs):
        if key in self.ignored_attributes:
            return []

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

        alignment = self.ALIGNMENT[kwargs.get('alignment', 'left')]
        text_line =  'T %d %d %d %d %d %d %d %d %d' % (
            self.x_to_mils(x),
            self.y_to_mils(y),
            kwargs.get('color', GEDAColor.TEXT_COLOR),
            kwargs.get('size', 10),
            kwargs.get('visibility', 1),
            1, #show_name_value is always '0'
            self.conv_angle(kwargs.get('angle', 0)),
            alignment,
            len(text),
        )
        return [text_line] + text

    def _create_pin(self, pin_seq, pin):
        assert(issubclass(pin.__class__, components.Pin))

        connected_x, connected_y = pin.p2.x, pin.p2.y
        
        command = ['P %d %d %d %d %d %d %d' % (
            self.x_to_mils(connected_x),
            self.y_to_mils(connected_y),
            self.x_to_mils(pin.p1.x),
            self.y_to_mils(pin.p1.y),
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
                alignment=pin.label.align,
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

    def _convert_annotation(self, annotation):
        assert(issubclass(annotation.__class__, Annotation))
    
        if annotation.value.startswith('{{'):
            return []

        return self._create_text(
            annotation.value,
            annotation.x,
            annotation.y,
            angle=annotation.rotation,
            visibility=annotation.visible,
        )

    def _convert_arc(self, arc):
        assert(issubclass(arc.__class__, shape.Arc))

        x, y = self.conv_coords(arc.x, arc.y)
        start_angle = self.conv_angle(arc.start_angle)

        sweep_angle = self.conv_angle(arc.end_angle) - start_angle
        if sweep_angle < 0:
            sweep_angle = 360 + sweep_angle

        return [
            'A %d %d %d %d %d %d 10 0 0 -1 -1' % (
                x, y,
                self.to_mils(arc.radius),
                start_angle, 
                sweep_angle,
                GEDAColor.GRAPHIC_COLOR,
            )
        ]

    def _convert_circle(self, circle):
        assert(issubclass(circle.__class__, shape.Circle))

        center_x, center_y = self.conv_coords(circle.x, circle.y)
        return [
            'V %d %d %d 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1' % (
                center_x,
                center_y,
                self.to_mils(circle.radius)
            )
        ]

    def _convert_rounded_rectangle(self, rect):
        return self._convert_rectangle(rect)

    def _convert_rectangle(self, rect):
        assert(issubclass(rect.__class__, (shape.Rectangle, shape.RoundedRectangle)))
        top_x, top_y = self.conv_coords(rect.x, rect.y)
        width, height = self.to_mils(rect.width), self.to_mils(rect.height)
        ## gEDA uses bottom-left corner as rectangle origin
        return [
            'B %d %d %d %d 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1' % (
                (top_x - height),
                top_y,
                width,
                height
            )
        ]

    def _convert_line(self, line):
        assert(issubclass(line.__class__, shape.Line))

        start_x, start_y = self.conv_coords(line.p1.x, line.p1.y)
        end_x, end_y = self.conv_coords(line.p2.x, line.p2.y)
        return [
            'L %d %d %d %d 3 10 0 0 -1 -1' % (
                start_x, 
                start_y,
                end_x, 
                end_y
            )
        ]

    def _convert_label(self, label):
        assert(issubclass(label.__class__, shape.Label))
        return self._create_text(
            label.text,
            label.x, 
            label.y,
            alignment=label.align,
            angle=label.rotation,
        )

    def _create_segment(self, np1, np2, attributes=None):
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

    def _convert_polygon(self, polygon):
        num_lines = len(polygon.points)+1 ##add closing command to polygon
        commands = ['H 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1 %d' % num_lines]

        start_x, start_y = polygon.points[0].x, polygon.points[0].y
        commands.append('M %d,%d' % self.conv_coords(start_x, start_y))

        for point in polygon.points[1:]:
            commands.append('L %d,%d' % self.conv_coords(point.x, point.y))

        commands.append('z') #closes the polygon

        return commands

    def _create_path(self, path):
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

        path_command = 'H 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1 %d' % num_lines
        return [path_command] + command + close_command

    def _convert_bezier(self, curve):
        assert(issubclass(curve.__class__, shape.BezierCurve))
        p1_x, p1_y = self.conv_coords(curve.p1.x, curve.p1.y)
        c1_x, c1_y = self.conv_coords(curve.control1.x, curve.control1.y)

        p2_x, p2_y = self.conv_coords(curve.p2.x, curve.p2.y)
        c2_x, c2_y = self.conv_coords(curve.control2.x, curve.control2.y)
        command= [
            'H 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1 2',
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

    def to_mils(self, value):
        return value * self.SCALE_FACTOR

    def y_to_mils(self, py):
        value = (py - self.offset.y) * self.SCALE_FACTOR 
        return value

    def x_to_mils(self, px):
        value = (px - self.offset.x) * self.SCALE_FACTOR 
        return value

    def conv_angle(self, angle, steps=1):
        converted_angle = int(angle * 180)
        return (converted_angle // int(steps)) * steps

    def conv_coords(self, x, y):
        return (
            self.x_to_mils(x),
            self.y_to_mils(y)
        )
