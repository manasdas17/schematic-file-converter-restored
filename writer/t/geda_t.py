
import os
import unittest
import StringIO
import shutil

from core.net import NetPoint
from core import shape
from core import components 

import parser.geda 

from writer.geda import GEDA
from parser.openjson import JSON

class TestGEDA(unittest.TestCase):

    def setUp(self):
        self.geda_writer = GEDA()
        self.oj_parser = JSON()

    def test_converter_methods(self):
        """ Test if converter methods are available for all known
            shapes in the core. 
        """
        shape_types = [
            'line', 
            'bezier',
            'label',
            'rectangle',
            'rounded_rectangle',
            'circle',
            'polygon',
        ]

        for typ in shape_types:
            self.assertTrue(hasattr(self.geda_writer, "_convert_"+typ))

    def test_create_project_files(self):
        """ Test creating project files in the directory derived from the
            output filename. Should try to create *gafrc* file and *symbol*
            directory.
        """
        geda_filename = '/tmp/test_geda.sch'

        self.geda_writer.create_project_files(geda_filename)

        self.assertEquals(
            self.geda_writer.project_dirs['project'], 
            '/tmp'
        )
        self.assertEquals(
            self.geda_writer.project_dirs['symbol'], 
            '/tmp/symbols'
        )
        self.assertTrue(os.path.exists('/tmp/gafrc'))
        
        fh = open('/tmp/gafrc', 'r')
        data = ''.join(fh.readlines())
        fh.close()
        self.assertEquals(data, '(component-library "./symbols")') 

    def test_write_schematic_file(self):
        """ Reads the gEDA *simple_example* file into a design using the
            gEDA parser, writes the result to a gEDA file and reads it into
            a new design. Both designs are then compared regarding their 
            respective components, instances and nets.
        """
        sym_dir = '/tmp/sym'

        if os.path.exists('/tmp/converted.sch'):
            os.remove('/tmp/converted.sch')

        if os.path.exists(sym_dir):
            shutil.rmtree(sym_dir)

        geda_parser = parser.geda.GEDA(
            symbol_dirs=['test/geda/simple_example/symbols', '/usr/share/gEDA/sym'],
        )
        geda_parser.set_offset(shape.Point(0, 0))
        simple_design = geda_parser.parse(
            'test/geda/simple_example/simple_example.sch'
        )

        geda_writer = GEDA(auto_include=True)
        geda_writer.write(simple_design, '/tmp/converted.sch')

        converted_design = geda_parser.parse(
            '/tmp/converted.sch'
        )

        ## parse design again to make sure it is a clean slate
        geda_parser = parser.geda.GEDA(
            symbol_dirs=['test/geda/simple_example/symbols', '/usr/share/gEDA/sym'],
        )
        geda_parser.set_offset(shape.Point(0, 0))
        simple_design = geda_parser.parse(
            'test/geda/simple_example/simple_example.sch'
        )

        ##compare nets
        self.assertItemsEqual(
            [(net.net_id, len(net.points)) for net in simple_design.nets], 
            [(net.net_id, len(net.points)) for net in converted_design.nets]
        )

        snets = dict([(net.net_id, net) for net in simple_design.nets]) 
        cnets = dict([(net.net_id, net) for net in converted_design.nets]) 

        for snet_id, snet in snets.items():
            cnet = cnets[snet_id]

            spoints = dict([(pt.point_id, pt) for pt in snet.points.values()]) 
            cpoints = dict([(pt.point_id, pt) for pt in cnet.points.values()]) 
            self.assertItemsEqual(spoints.keys(), cpoints.keys())

            for spoint_id, spoint in spoints.items():
                cpoint = cpoints[spoint_id]

                self.assertEquals(spoint.x, cpoint.x)
                self.assertEquals(spoint.y, cpoint.y)

        ## compare component library
        self.assertItemsEqual(
            simple_design.components.components.keys(),
            converted_design.components.components.keys()
        )

        for lib_id in simple_design.components.components:
            scomponent = simple_design.components.components[lib_id]
            ccomponent = converted_design.components.components[lib_id]

            self.assertEquals(scomponent.name, ccomponent.name)
            self.assertEquals(scomponent.attributes, ccomponent.attributes)

            self.assertEquals(len(scomponent.symbols), 1)
            self.assertEquals(
                len(scomponent.symbols), 
                len(ccomponent.symbols)
            )

            self.assertEquals(len(scomponent.symbols[0].bodies), 1)
            self.assertEquals(
                len(scomponent.symbols[0].bodies), 
                len(ccomponent.symbols[0].bodies)
            )
            sbody = scomponent.symbols[0].bodies[0]
            cbody = ccomponent.symbols[0].bodies[0]

            self.assertEquals(len(sbody.shapes), len(cbody.shapes))
            self.assertEquals(len(sbody.pins), len(cbody.pins))

            for spin, cpin in zip(sbody.pins, cbody.pins):
                self.assertEquals(spin.p1.x, cpin.p1.x)
                self.assertEquals(spin.p1.x, cpin.p1.x)
                self.assertEquals(spin.p2.y, cpin.p2.y)
                self.assertEquals(spin.p2.y, cpin.p2.y)
                self.assertEquals(spin.label.text, cpin.label.text)

            for sshape, cshape in zip(sbody.shapes, cbody.shapes):
                self.assertEquals(sshape.type, cshape.type)

        ## compare component instances
        scomp_instances = dict([(comp.instance_id, comp) for comp in simple_design.component_instances])
        ccomp_instances = dict([(comp.instance_id, comp) for comp in converted_design.component_instances])

        for instance_id in scomp_instances:
            sinst = scomp_instances[instance_id]
            cinst = ccomp_instances[instance_id]
            
            self.assertEquals(sinst.instance_id, cinst.instance_id)
            self.assertEquals(sinst.library_id, cinst.library_id)
            self.assertEquals(sinst.symbol_index, cinst.symbol_index)

            self.assertEquals(
                sinst.symbol_attributes[0].x, 
                cinst.symbol_attributes[0].x
            )
            self.assertEquals(
                sinst.symbol_attributes[0].y, 
                cinst.symbol_attributes[0].y
            )
            self.assertEquals(
                sinst.symbol_attributes[0].rotation, 
                cinst.symbol_attributes[0].rotation
            )

    def test_write_component_to_file(self):
        """ Tests writing a component to a symbol file. """
        sym_dir = '/tmp/sym'
        if os.path.exists(sym_dir):
            shutil.rmtree(sym_dir)

        os.mkdir(sym_dir)

        self.geda_writer.set_offset(shape.Point(-500, -500))

        self.geda_writer.component_library = dict()
        self.geda_writer.project_dirs['symbol'] = sym_dir 

        simple_design = self.oj_parser.parse('test/openjson/simple.upv')

        library_id = '0000000000000001'
        component = simple_design.components.components[library_id]
        commands = self.geda_writer.write_component_to_file(library_id, component)

        component_library = self.geda_writer.component_library
        self.assertEquals(len(component_library), 4)

        self.assertEquals(
            component_library,
            {
                (library_id, 0): 'Flag_1-0.sym', 
                (library_id, 1): 'Flag_2-1.sym', 
                (library_id, 2): 'GND-2.sym', 
                (library_id, 3): 'VCC-3.sym'
            } 
        )
        self.assertEquals(
            sorted(os.listdir(sym_dir)),
            ['Flag_1-0.sym', 'Flag_2-1.sym', 'GND-2.sym', 'VCC-3.sym']
        )

        if os.path.exists(sym_dir):
            shutil.rmtree(sym_dir)

        os.mkdir(sym_dir)

        self.geda_writer = GEDA(auto_include=True)
        self.geda_writer.component_library = dict()
        self.geda_writer.project_dirs['symbol'] = sym_dir 

        geda_parser = parser.geda.GEDA(
            symbol_dirs=['test/geda/simple_example/symbols', '/usr/share/gEDA/sym'],
        )
        converted_design = geda_parser.parse(
            'test/geda/simple_example/simple_example.sch'
        )

        library_id = 'opamp'
        component = converted_design.components.components[library_id]
        commands = self.geda_writer.write_component_to_file(library_id, component)

        component_library = self.geda_writer.component_library
        self.assertEquals(len(component_library), 1)

        self.assertEquals(
            component_library,
            {
                (library_id, 0): 'opamp.sym', 
            } 
        )
        library_id = 'capacitor-1'
        component = converted_design.components.components[library_id]
        commands = self.geda_writer.write_component_to_file(library_id, component)

        component_library = self.geda_writer.component_library
        self.assertEquals(len(component_library), 2)

        self.assertEquals(
            component_library,
            {
                ('opamp', 0): 'opamp.sym', 
                (library_id, 0): 'capacitor-1.sym', 
            } 
        )
        self.assertEquals(
            sorted(os.listdir(sym_dir)),
            ['opamp.sym']
        )


    def test_generate_net_commands(self):
        """ Tests creating commands for nets that can then be 
            written to the schematic file. 
        """
        design = self.oj_parser.parse('test/geda/nets_exported.upv')

        self.geda_writer.set_offset(design.bounds()[0])

        commands = self.geda_writer.generate_net_commands(design.nets)
        self.assertTrue(len(commands) > 0)

        segment_count = 0
        for command in commands:
            if command.startswith('N '):
                segment_count += 1

        self.assertEquals(segment_count, 21) 

        env_count = 0
        for command in commands:
            if command.startswith('{'):
                env_count += 1
        self.assertEquals(env_count, 4) 

        commands += [
            'v 20110115 2\n',
        ]
        geda_parser = parser.geda.GEDA()
        new_design = geda_parser.parse_schematic(
            StringIO.StringIO('\n'.join(commands))
        )
        self.assertEquals(len(design.nets), len(new_design.nets))


    def test_create_component(self):
        """ Tests creating components from various gEDA commands. """
        component = self.geda_writer._create_component(0, 0, 'test-1.sym')
        self.assertEquals(
            component,
            ['C 0 0 0 0 0 test-1.sym']
        )

    def test_create_attribute(self):
        """ Tests creating attribute commands. """
        attribute = self.geda_writer._create_attribute('_refdes', 'U1', 0, 0) 
        self.assertEquals(
            attribute,
            []
        )
        attribute = self.geda_writer._create_attribute('_private_attr', 'U1', 0, 0) 
        self.assertEquals(
            attribute,
            ['T 0 0 5 10 0 1 0 0 1', 'private_attr=U1']
        )
        attribute = self.geda_writer._create_attribute('attr', 'U1', 0, 0, size=25) 
        self.assertEquals(
            attribute,
            ['T 0 0 5 25 1 1 0 0 1', 'attr=U1']
        )

    def test_create_text(self):
        """ Tests creating text commands. """
        text = self.geda_writer._create_text('some text', 0, 0)
        self.assertEquals(len(text), 2)
        self.assertEquals(
            text,
            ['T 0 0 9 10 1 1 0 0 1', 'some text']
        )

        text = self.geda_writer._create_text(
            "some text\nmulti line\ntext", 
            0, 0, size=25, visibility=0, 
            alignment='right',
        )
        self.assertEquals(len(text), 4)
        self.assertEquals(
            text,
            ['T 0 0 9 25 0 1 0 4 3', "some text", "multi line", "text"]
        )

    def test_create_pin(self):
        """ Tests creating pin commands. """
        pin = components.Pin('E', (0, 0), (0, 30))
        command = self.geda_writer._create_pin(1, pin) 

        self.assertEquals(
            command,
            [
                'P 0 300 0 0 1 0 0', 
                '{',
                'T 100 400 5 10 0 1 0 0 1',
                'pinseq=1',
                'T 100 500 5 10 0 1 0 0 1',
                'pinnumber=E',
                '}'
            ]
        )

        label = shape.Label(10, 0, 'p1', 'left', 0.5)

        pin = components.Pin('E', (0, 0), (0, 30), label=label)
        command = self.geda_writer._create_pin(1, pin) 

        self.assertEquals(
            command,
            [
                'P 0 300 0 0 1 0 0', 
                '{',
                'T 100 0 5 10 1 1 90 0 1',
                'pinlabel=p1',
                'T 100 400 5 10 0 1 0 0 1',
                'pinseq=1',
                'T 100 500 5 10 0 1 0 0 1',
                'pinnumber=E',
                '}'
            ]
        )


    def test_convert_arc(self):
        """ Tests converting Arc objects to arc commands."""
        arc = shape.Arc(0, 0, 0.0, 0.7, 30)
        command = self.geda_writer._convert_arc(arc)
        
        self.assertEquals(
            command,
            ['A 0 0 300 0 125 3 10 0 0 -1 -1'] 
        )

        arc = shape.Arc(200, 400, 1.0, 0.5, 10)
        command = self.geda_writer._convert_arc(arc)
        
        self.assertEquals(
            command,
            ['A 2000 4000 100 180 270 3 10 0 0 -1 -1'] 
        )

        arc = shape.Arc(200, 400, 0.2, 0.1, 10)
        command = self.geda_writer._convert_arc(arc)
        
        self.assertEquals(
            command,
            ['A 2000 4000 100 36 342 3 10 0 0 -1 -1'] 
        )

    def test_convert_circle(self):
        """ Tests converting Circle objects to circle commands."""
        circle = shape.Circle(0, 0, 300)
        command = self.geda_writer._convert_circle(circle)

        self.assertEquals(
            command,
            ['V 0 0 3000 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1']
        )

        circle = shape.Circle(10, 30, 10)
        command = self.geda_writer._convert_circle(circle)

        self.assertEquals(
            command,
            ['V 100 300 100 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1']
        )

    def test_convert_rectangle(self):
        """ Tests converting Rectancle and RoundedRectangle
            objects to box commands.
        """
        rect = shape.Rectangle(0, 0, 40, 50)
        command = self.geda_writer._convert_rectangle(rect)

        self.assertEquals(
            command,
            ['B -500 0 400 500 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1']
        )

        rect = shape.Rectangle(100, 50, 150, 30)
        command = self.geda_writer._convert_rectangle(rect)

        self.assertEquals(
            command,
            ['B 700 500 1500 300 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1']
        )

        rect = shape.RoundedRectangle(0, 0, 40, 50, 0.5)
        command = self.geda_writer._convert_rounded_rectangle(rect)

        self.assertEquals(
            command,
            ['B -500 0 400 500 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1']
        )

        rect = shape.RoundedRectangle(100, 50, 150, 30, 0.1)
        command = self.geda_writer._convert_rounded_rectangle(rect)

        self.assertEquals(
            command,
            ['B 700 500 1500 300 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1']
        )

    def test_convert_line(self):
        """ Tests converting Line objects to line commands. """
        line = shape.Line((0, 0), (0, 50))
        command = self.geda_writer._convert_line(line)
        self.assertEquals(
            command,
            ['L 0 0 0 500 3 10 0 0 -1 -1']
        )

        line = shape.Line((20, 40), (-20, 40))
        command = self.geda_writer._convert_line(line)
        self.assertEquals(
            command,
            ['L 200 400 -200 400 3 10 0 0 -1 -1']
        )

        line = shape.Line((20, 40), (-30, 50))
        command = self.geda_writer._convert_line(line)
        self.assertEquals(
            command,
            ['L 200 400 -300 500 3 10 0 0 -1 -1']
        )

    def test_convert_label(self):
        """ Tests converting Lable objects to label commands. """
        label = shape.Label(0, 0, 'test label', 'center', 0.0)
        command = self.geda_writer._convert_label(label)
        self.assertEquals(
            command,
            [
                'T 0 0 9 10 1 1 0 3 1',
                'test label'
            ]
        )

        label = shape.Label(0, 0, 'test label', 'left', 0.5)
        command = self.geda_writer._convert_label(label)
        self.assertEquals(
            command,
            [
                'T 0 0 9 10 1 1 90 0 1',
                'test label'
            ]
        )

    def test_create_segment(self):
        """ Tests creating segment commands from NetPoint objects. """
        np1 = NetPoint('0a0', 0, 0)
        np2 = NetPoint('0a10', 0, 10)
        self.assertEquals(
            self.geda_writer._create_segment(np1, np2),
            ['N 0 0 0 100 4']
        )
        np1 = NetPoint('100a40', 100, 40)
        np2 = NetPoint('50a40', 50, 40)
        attrs = {'netname': 'test_net'}
        self.assertEquals(
            self.geda_writer._create_segment(np1, np2, attributes=attrs),
            [
                'N 1000 400 500 400 4',
                '{',
                'T 1100 500 5 10 1 1 0 0 1',
                'netname=test_net',
                '}',
            ]
        )

    def test_convert_polygon(self):
        """ Tests converting Polygon objects to path commands."""
        polygon = shape.Polygon()
        polygon.add_point((0, 0))
        polygon.add_point((100, 200))
        polygon.add_point((150, 200))
        polygon.add_point((200, 100))

        self.assertEquals(
            self.geda_writer._convert_polygon(polygon),
            [
                'H 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1 5',
                'M 0,0',
                'L 1000,2000',
                'L 1500,2000',
                'L 2000,1000',
                'z'
            ]
        )
    
    def test_convert_bezier(self):
        """ Tests converting BezierCurve objects to path commands. """
        curve = shape.BezierCurve((9, -10), (11, -10), (3, -12), (17, -12))

        self.assertEquals(
            self.geda_writer._convert_bezier(curve),
            [
                'H 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1 2',
                'M 30,-120',
                'C 90,-100 110,-100 170,-120',
            ]
        )

    def test_create_path(self):
        """ Test creating path commands from Body objects. """
        shapes = [
            shape.Line((10, 10), (50, 10)),
            shape.BezierCurve((70, 10), (80, 30), (50, 10), (80, 40)),
            shape.BezierCurve((80, 50), (70, 70), (80, 40), (50, 70)),
            shape.Line((50, 70), (10, 70)),
        ]
        
        body = components.Body()
        body.shapes = shapes

        self.assertEquals(
            self.geda_writer._create_path(body),
            [
                'H 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1 5',
                'M 100,100',
                'L 500,100',
                'C 700,100 800,300 800,400',
                'C 800,500 700,700 500,700',
                'L 100,700',
            ]
        )

        body.add_shape(shape.Line((10, 70), (10, 10)))

        self.assertEquals(
            self.geda_writer._create_path(body),
            [
                'H 3 10 0 0 -1 -1 0 -1 -1 -1 -1 -1 6',
                'M 100,100',
                'L 500,100',
                'C 700,100 800,300 800,400',
                'C 800,500 700,700 500,700',
                'L 100,700',
                'z',
            ]
        )

    def test_is_valid_path(self):
        """ Tests if Body objects contain valid paths."""
        shapes = [
            shape.Line((10, 10), (50, 10)), #L 500,100
            shape.BezierCurve((70, 10), (80, 30), (50, 10), (80, 40)), #C 700,100 800,300 800,400
            shape.BezierCurve((80, 50), (70, 70), (80, 40), (50, 70)), #C 800,500 700,700 500,700
            shape.Line((50, 70), (10, 70)), #L 100,700
        ]
        
        body = components.Body()
        body.shapes = shapes
        self.assertTrue(self.geda_writer.is_valid_path(body))

        body.add_shape(shape.Line((10, 70), (10, 10)))
        self.assertTrue(self.geda_writer.is_valid_path(body))

        shapes = [
            shape.Line((10, 10), (50, 10)), #L 500,100
            shape.BezierCurve((70, 10), (80, 30), (50, 10), (80, 40)), #C 700,100 800,300 800,400
            shape.Line((50, 70), (10, 70)), #L 100,700
        ]
        body.shapes = shapes
        self.assertFalse(self.geda_writer.is_valid_path(body))

        body.add_shape(shape.Circle(0, 0, 10))
        self.assertFalse(self.geda_writer.is_valid_path(body))

    def test_conv_angle(self):
        """ Test conversion of angles from pi radians to degrees. """
        angle_samples = [
            # angle, steps, expected result
            (0.0, 1, 0),
            (0.0, 10.0, 0),
            (0.5, 90, 90),
            (0.7,  1, 125), 
            (0.7,  90, 90), 
            (1.8,  1, 324), 
            (1.5,  1, 270), 
            (1.5,  90, 270),
        ]

        for angle, steps, expected in angle_samples:
            self.assertEquals(
                self.geda_writer.conv_angle(angle, steps), 
                expected
            )

