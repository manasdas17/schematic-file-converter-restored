""" The KiCAD Format Writer """

import time

from os.path import splitext

from parser.kicad import MATRIX2ROTATION

ROTATION2MATRIX = dict((v, k) for k, v in MATRIX2ROTATION.items())


class KiCAD(object):
    """ The KiCAD Format Writer """

    def write(self, design, filename, library_filename=None):
        """ Write the design to the KiCAD format """

        if library_filename is None:
            library_filename = splitext(filename)[0] + '-cache.lib'

        self.write_library(design, library_filename)

        f = open(filename, "w")

        self.write_header(f, design)
        self.write_libs(f, library_filename)
        self.write_eelayer(f)
        self.write_descr(f, design)
        for inst in design.component_instances:
            self.write_instance(f, inst)
        for net in design.nets:
            self.write_net(f, net)
        self.write_footer(f)

        f.close()


    def write_header(self, f, design):
        """ Write a kiCAD schematic file header """
        f.write('EESchema Schematic File Version 2  date ')
        self.write_header_date(f, design)


    def write_header_date(self, f, design):
        """ Write the date portion of a kiCAD schematic header """
        bdt = time.localtime(design.design_attributes.metadata.updated_timestamp)
        f.write(time.strftime('%a %d %b %Y %H:%M:%S %p ', bdt))
        if time.daylight and bdt.tm_isdst:
            f.write(time.tzname[1])
        else:
            f.write(time.tzname[0])
        f.write('\n')


    def write_libs(self, f, library_filename):
        """ Write the LIBS section of a kiCAD schematic """
        f.write('LIBS:%s\n' % (splitext(library_filename)[0],))


    def write_eelayer(self, f):
        """ Write the EELAYER block of a kiCAD schematic """
        f.write('EELAYER 25  0\n')
        f.write('EELAYER END\n')


    def write_descr(self, f, design):
        """ Write the description block of a kiCAD schematic """
        bdt = time.localtime(design.design_attributes.metadata.updated_timestamp)
        datestr = time.strftime('%d %b %Y', bdt).lower()
        f.write('''\
$Descr A4 11700 8267
encoding utf-8
Sheet 1 1
Title ""
Date "%s"
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
''' % (datestr,))


    def write_instance(self, f, inst):
        """ Write a $Comp component to a kiCAD schematic """
        f.write('$Comp\n')
        f.write('L %s %s\n' % (inst.library_id, inst.instance_id))
        f.write('U 1 1 00000000\n')
        f.write('P %d %d\n' % (inst.symbol_attributes[0].x,
                               inst.symbol_attributes[0].y))
        f.write('\t1    %d %d\n' % (inst.symbol_attributes[0].x,
                                    inst.symbol_attributes[0].y))
        f.write('\t%d    %d    %d    %d\n' %
                ROTATION2MATRIX[inst.symbol_attributes[0].rotation])
        f.write('$EndComp\n')


    def write_net(self, f, net):
        """ Write a Net as kiCAD Wires and Connections """
        segments = set() # ((x,y),(x,y))

        for point in net.points.values():
            for point2_id in point.connected_points:
                point2 = net.points[point2_id]
                seg = [(point.x, point.y), (point2.x, point2.y)]
                seg.sort() # canonical order
                segments.add(tuple(seg))

        for seg in segments:
            f.write('Wire Wire Line\n')
            f.write('\t%d %d %d %d\n' % (seg[0][0], seg[0][1],
                                         seg[1][0], seg[1][1]))


    def write_footer(self, f):
        """ Write the kiCAD schematic footer """
        f.write('$EndSCHEMATC\n')


    def write_library(self, design, filename):
        """ Write out a kiCAD cache library to the given filename """
        f = open(filename, 'w')
        self.write_library_header(f, design)
        for cpt in design.components.components.itervalues():
            self.write_library_component(f, cpt)
        self.write_library_footer(f)
        f.close()


    def write_library_header(self, f, design):
        """ Write the header line for a kiCAD cache library """
        f.write('EESchema-LIBRARY Version 2.3  Date: ')
        self.write_header_date(f, design)
        f.write('#encoding utf-8\n')


    def write_library_component(self, f, cpt):
        """ Write a single component to a kiCAD cache library """
        ref = cpt.attributes.get('_prefix', 'U')
        f.write('#\n')
        f.write('# ' + cpt.name + '\n')
        f.write('#\n')
        f.write('DEF %s %s 0 30 Y Y 1 F N\n' % (cpt.name, ref))
        f.write('F0 "%s" 0 0 60 H V L CNN\n' % (ref,))
        f.write('F1 "%s" 0 60 60 H V L CNN\n' % (cpt.name,))
        self.write_library_component_body(f, cpt.symbols[0].bodies[0])
        f.write('ENDDEF\n')


    def write_library_component_body(self, f, body):
        """ Write the DRAW portion (shapes and pins) of a kiCAD component """
        f.write('DRAW\n')

        for shape in body.shapes:
            self.write_shape(f, shape)

        for pin in body.pins:
            self.write_pin(f, pin)

        f.write('ENDDRAW\n')


    def write_shape(self, f, shape):
        """ Write a Shape to a kiCAD cache library """
        if shape.type == 'arc':
            # convert pi radians to tenths of degrees
            start = round(shape.start_angle * 1800)
            end = round(shape.end_angle * 1800)
            f.write('A %d %d %d %d %d 0 1 0 N\n' %
                    (shape.x, shape.y, shape.radius, start, end))
        elif shape.type == 'circle':
            f.write('C %d %d %d 0 1 0 N\n' % (shape.x, shape.y, shape.radius))
        elif shape.type == 'polygon':
            f.write('P %d 1 0 0 ' % (len(shape.points),))
            for point in shape.points:
                f.write('%d %d ' % (point.x, point.y))
            f.write('N\n')
        elif shape.type == 'rectangle':
            f.write('S %d %d %d %d 0 1 0 N\n' %
                    (shape.x, shape.y, shape.x + shape.width,
                     shape.y + shape.height))
        elif shape.type == 'label':
            angle = round(shape.rotation * 1800)
            align = shape.align[0].upper()
            f.write('T %d %d %d 20 0 0 0 %s Normal 0 %s C\n' %
                    (angle, shape.x, shape.y,
                     shape.text.replace(' ', '~'), align))


    def write_pin(self, f, pin):
        """ Write a Pin to a kiCAD cache library """
        x, y = pin.p2.x, pin.p2.y

        if x == pin.p1.x: # vertical
            length = y - pin.p1.y
            if length > 0:
                direction = 'U' # up
            else:
                direction = 'D' # down
        else:
            length = x - pin.p1.x
            if length > 0:
                direction = 'L' # left
            else:
                direction = 'R' # right

        f.write('X ~ %s %d %d %d %s 60 60 1 1 B\n' %
                (pin.pin_number, x, y, length, direction))


    def write_library_footer(self, f):
        """ Write a kiCAD library file footer """
        f.write('#\n#End Library\n')
