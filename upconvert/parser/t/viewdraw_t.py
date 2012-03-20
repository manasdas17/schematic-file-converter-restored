""" Tests for the ViewDraw parser """

import unittest
from inspect import getargspec
from upconvert.parser.viewdraw import FileStack, ViewDrawBase, ViewDrawSym, ViewDrawSch

from upconvert.core.annotation import Annotation
from upconvert.core.shape import Label, Point
from math import sin, cos, pi

_real_fs_init  = FileStack.__init__

def stub_file_stack():
    """ stub in a constructor that doesn't depend on the filesystem """
    def fake_init(self, filename):
        self.f = iter([])
        self.fstack = []
        self.line = 0
    FileStack.__init__ = fake_init

def unstub_file_stack():
    """ return to the proper FileStack constructor. """
    FileStack.__init__ = _real_fs_init

    
class FileStackTests(unittest.TestCase):
    """ Tests for the file reader used by the parser """

    def setUp(self):
        stub_file_stack()
        self.fs = FileStack('test')


    def tearDown(self):
        unstub_file_stack()
        del self.fs


    def test_subpop(self):
        """Ensure subpop() can iterate through the simplest case"""
        self.fs.f = iter(['test\n', 'foo\n', 'bar\n', 'baz\n'])
        for i, line in enumerate(['test', 'foo', 'bar', 'baz']):
            self.assertEqual(self.fs.line, i)
            self.assertEqual(self.fs.subpop(), line + '\n')
            self.assertEqual(self.fs.line, i + 1)
        self.assertRaises(StopIteration, self.fs.subpop)


    def test_line_continuation(self):
        """Test that line continuations are re-assembled correctly"""
        self.assertEqual(self.fs.continuation('foo\n', ' bar\n'), 'foo bar\n')
        self.assertEqual(self.fs.continuation('foo\n', '+ bar\n'), 'foobar\n')


    def test_next(self):
        """Test for iterator functionality, with a continuation"""
        self.fs.f = iter(['foo\n', 'bar\n', ' baz\n', 'garr\n'])
        for i, line in zip([1, 3, 4], ['foo', 'bar baz', 'garr']):
            self.assertEqual(self.fs.next(), line)
            self.assertEqual(self.fs.line, i)
        self.assertRaises(StopIteration, self.fs.next)


    def test_push(self):
        """Test pushing lines back on to the stack"""
        self.fs.f = iter([])
        for i, line in zip([-1, -2, -3], ['baz', 'bar', 'foo']):
            # push them on backwards because it's a stack
            self.fs.push(line)
            self.assertEqual(self.fs.line, i)
        self.assertEqual(list(self.fs), ['foo', 'bar', 'baz'])


class ViewDrawBaseTests(unittest.TestCase):
    """ Tests for functionality shared between parsers """
    
    def setUp(self):
        stub_file_stack()
        self.base = ViewDrawBase('foo')
        self.base.stream = FileStack('bar')

    def tearDown(self):
        unstub_file_stack()
        del self.base

    def test_base_init(self):
        self.assertEqual(self.base.filename, 'foo')

    def test_parser_dispatch(self):
        """ Check that the parsers used have the proper call signatures """
        valid_cmds = 'A L |R V Z c b T a l'.split()
        for cmd in valid_cmds:
            parser  = self.base.parsenode(cmd)
            # make sure it only needs two argument (self, args)
            self.assertEqual(len(getargspec(parser)[0]), 2)
        # currently not testing invalid commands, their behaviour can be
        # considered 'undefined'

    def test_label(self):
        """ Test basic label parsing """
        args = '2 3 12 0 # # # # this is a text label'
        # `#` args are unhandled, but may be in the future
        k, v = self.base.parse_label(args)
        self.assertEqual(k, 'annot')
        self.assertTrue(isinstance(v, Annotation))
        self.assertEqual(v.x, 2)
        self.assertEqual(v.y, 3)
        self.assertEqual(v.value, 'this is a text label')

    def test_annot(self):
        """ Test basic Annotation parsing """
        args = '2 3 12 0 1'
        text = 'foo=bar baz'
        pairs = (('0', text),
                 ('1', text),
                 ('2', 'foo'),
                 ('3', 'bar baz'))
        for viz, val in pairs:
            k, v = self.base.parse_annot(' '.join([args, viz, text]))
            self.assertEqual(k, 'annot')
            self.assertEqual(v.x, 2)
            self.assertEqual(v.y, 3)
            if viz is '0':
                self.assertFalse(v.visible)
            else:
                self.assertTrue(v.visible)
            self.assertEqual(v.value, val)

    def test_revision(self):
        """ Test the file revision datetime parser """
        k, v = self.base.parse_rev('timedate')
        self.assertEqual(k, 'annot')
        self.assertEqual(v.value, 'rev=timedate')
        self.assertFalse(v.visible)
        self.assertEqual(v.x, 0)
        self.assertEqual(v.y, 0)
        self.assertEqual(v.rotation, 0)

    def test_circle(self):
        """ Test parsing a simple circle """
        posargs = '1 2 3'
        negargs = '-6 -7 8'
        k, v = self.base.parse_circle(posargs)
        self.assertEqual(k, 'shape')
        self.assertEqual(v.type, 'circle')
        self.assertEqual((v.x, v.y), (1, 2))
        self.assertEqual(v.radius, 3)

        k, v = self.base.parse_circle(negargs)
        self.assertEqual(k, 'shape')
        self.assertEqual(v.type, 'circle')
        self.assertEqual((v.x, v.y), (-6, -7))
        self.assertEqual(v.radius, 8)

    def test_box(self):
        """ Test for a simple rectangle """
        k, v = self.base.parse_box('2 4 7 8')
        self.assertEqual(k, 'shape')
        self.assertEqual(v.type, 'rectangle')
        self.assertEqual((v.x, v.y), (2, 4))
        self.assertEqual(v.height, (8 - 4))
        self.assertEqual(v.width, (7 - 2))

        k, v = self.base.parse_box('1 3 -5 -6')
        self.assertEqual(k, 'shape')
        self.assertEqual(v.type, 'rectangle')
        self.assertEqual((v.x, v.y), (1, 3))
        self.assertEqual(v.width, -5 - 1)
        self.assertEqual(v.height, -6 - 3)

    def test_text(self):
        """ Test text labels """
        k, v = self.base.parse_text('3 4 # # # hello world')
        self.assertEqual(k, 'shape')
        self.assertEqual(v.type, 'label')
        self.assertEqual((v.x, v.y), (3, 4))
        self.assertEqual(v.text, 'hello world')

    def test_version(self):
        """ Test format version parser """
        k, v = self.base.parse_ver('51')
        self.assertEqual(k, 'fileversion')
        self.assertEqual(v, '51')

    def test_line_one_seg(self):
        """One line segment, from (2,3) to (4,7)"""
        k, v = self.base.parse_line('2 1 3 4 7')
        self.assertEqual(k, 'lines')
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0].type, 'line')
        p1, p2 = v[0].p1, v[0].p2
        self.assertEqual(p1, Point(1, 3))
        self.assertEqual(p2, Point(4, 7))

    def test_line_multi_seg(self):
        """A multi-segment line, should become many Line objects"""
        pts = [(2, 1), (4, 5), (8, 7), (9, 2)]
        pts_text = ' '.join([str(p1) + ' ' + str(p2) for p1, p2 in pts])
        k, v = self.base.parse_line(str(len(pts)) + ' ' + pts_text)
        self.assertEqual(k, 'lines')
        self.assertEqual(len(v), len(pts) - 1)
        # line segments returned out of order, or with p1/p2 swapped, would be
        # acceptable. The test would need to change for that.
        for i, line in enumerate(v):
            self.assertEqual(line.type, 'line')
            self.assertEqual(Point(pts[i]), line.p1)
            self.assertEqual(Point(pts[i + 1]), line.p2)

    def test_arc(self):
        """ Test multiple arc segment constructions """
        x_c, y_c, radius = 2, 3, 50
        angles = ((0., 0.5, 1.),
                  (1.5, 0., 0.5),
                  (1., 1.25, 1.5))
        def angle2xy(theta):
            return [int(round(sin(theta * pi) * radius + x_c)),
                    int(round(cos(theta * pi) * radius + y_c))]
        def reflang(theta):
            return (theta + 0.5) % 2.0

        for ang in (angles):
            print ang
            pts = sum([angle2xy(th) for th in ang], [])

            k, v = self.base.parse_arc(' '.join([str(p) for p in pts]))
            print v.json()
            self.assertEqual(k, 'shape')
            self.assertEqual(v.type, 'arc')
            # allow for points to be off by up to one unit, to account for
            # rounding error in calculating center point, radius.
            self.assertTrue(abs(v.x - x_c) <= 1)
            self.assertTrue(abs(v.y - y_c) <= 1)
            self.assertTrue(abs(v.radius - radius) <= 1)
            self.assertTrue(abs(reflang(v.start_angle) - (ang[0])) < 0.01)
            self.assertTrue(abs(reflang(v.end_angle) - (ang[2])) < 0.01)

class ViewDrawSymTests(unittest.TestCase):
    """ Tests for ViewDraw library symbol files """

    def setUp(self):
        stub_file_stack()
        self.sym = ViewDrawSym('library/', 'file.1')
        self.sym.stream = FileStack(self.sym.filename)

    def tearDown(self):
        unstub_file_stack()
        del self.sym

    def test_parser_dispatch(self):
        """ Check that the parsers used have the proper call signatures """
        valid_cmds = 'Y U P L'.split()
        for cmd in valid_cmds:
            parser  = self.sym.parsenode(cmd)
            # make sure it only needs two argument (self, args)
            self.assertEqual(len(getargspec(parser)[0]), 2)
        # currently not testing invalid commands, their behaviour can be
        # considered 'undefined'

    def test_sym_type(self):
        """ Test symbol type extraction, based on found documents """
        for i, txt in enumerate(['composite', 'module', 'annotate', 'pin',
                               'power', 'unknown']):
            k, v = self.sym.parse_type(str(i))
            self.assertEqual(k, 'attr')
            self.assertEqual(v, ('symtype', txt))

    def test_attr_key_val(self):
        """ Test attribute parsing, when it has a key and value """
        k, v = self.sym.parse_attr('0 1 2 3 4 5 KEY=VAL')
        self.assertEqual(k, 'attr')
        self.assertEqual(v, ('KEY', 'VAL'))

    def test_attr_just_key(self):
        """ Test attribute parsing, when it has a key but no value """
        k, v = self.sym.parse_attr('0 1 2 3 4 5 KEY')
        self.assertEqual(k, 'attr')
        self.assertEqual(v, ('KEY', ''))

    def subtest_pin(self):
        """ Common tests for both pin test cases """
        k, v = self.sym.parse_pin('13 2 4 3 5 0 0 0')
        self.assertEqual(k, 'pin')
        self.assertEqual(v.p1, Point(3, 5))
        self.assertEqual(v.p2, Point(2, 4))
        self.assertEqual(v.pin_number, 13)
        return(v)

    def test_pin(self):
        """ Test parsing a simple pin """
        v = self.subtest_pin()
        self.assertTrue(v.label == None)

    def test_pin_with_label(self):
        """ Test parsing a pin with an attached label """
        self.sym.stream.f = iter(['L testlabel'])
        # create a fake label parser
        # NOTE not sure if this test is too coupled to internal
        # state/architecture. Fix it if there's a better way
        def fake_label(args):
            return ('label', Label(1, 2, args, 'left', 0))

        p = self.sym.parsenode
        def parsenode_shim(cmd):
            if cmd is 'L':
                return fake_label
            return p(cmd)
        self.sym.parsenode = parsenode_shim

        label = self.subtest_pin().label
        self.assertEqual(label.type, 'label')
        self.assertEqual((label.x, label.y), (1, 2))
        self.assertEqual(label.text, 'testlabel')
        self.assertEqual(label.align, 'left')
        self.assertEqual(label.rotation, 0)

    def test_label(self):
        """ Test parsing a text label """
        k, v = self.sym.parse_label('2 3 12 0 1 1 1 0 foobar')
        # values of 1 aren't used by parser
        self.assertEqual(k, 'label')
        self.assertEqual(v.type, 'label')
        self.assertEqual((v.x, v.y), (2, 3))
        self.assertEqual(v.text, 'foobar')
        self.assertEqual(v.align, 'left')
        self.assertEqual(v.rotation, 0)

    def test_label_inverted(self):
        """ Test parsing a label (for a pin) for an inverted signal """
        _k, v = self.sym.parse_label('2 3 12 0 1 1 1 1 foobar')
        # everything else already tested in test_label()
        self.assertEqual(v.text, '/foobar')

class ViewDrawSchTests(unittest.TestCase):
    """ Tests for a ViewDraw schematic sheet file """
    # TODO work out a sensible way to test connecting instances to nets.

    def setUp(self):
        stub_file_stack()
        self.sch = ViewDrawSch(None, 'foobar')
        self.sch.stream = FileStack('foo')

    def tearDown(self):
        unstub_file_stack()
        del self.sch

    def test_junc(self):
        """ Test the parsing of a single junction on a net """
        k, v = self.sch.parse_junc('2 3 4')
        self.assertEqual(k, 'netpoint')
        self.assertEqual((v.x, v.y), (2, 3))
        self.assertEqual(len(v.connected_points), 0)
        self.assertEqual(len(v.connected_components), 0)
        # Not checking v.point_id, as it is only spec'd to be a unique string

    def test_seg(self):
        """ Test the parsing of a net segment between two junctions """
        k, v = self.sch.parse_seg('6 5')
        self.assertEqual(k, 'segment')
        self.assertEqual(v, (6, 5))

    def test_basic_net(self):
        """ Basics for a net, no actual pi=oints placed """
        k, v = self.sch.parse_net('bar')
        self.assertEqual(k, 'net')
        self.assertEqual(v.net_id, 'bar')
        # make sure nothing got put in there
        self.assertEqual(len(v.points), 0)
        self.assertEqual(len(v.attributes), 0)
        self.assertEqual(len(v.annotations), 0)

    def netpt_helper(self, pts_dict, net):
        """ Checks that the netpoints we wanted were all created """
        self.assertEqual(len(net.points), len(pts_dict))
        for pt in net.points.values():
            # make sure pt is one of the ones we created
            self.assertTrue((pt.x, pt.y) in pts_dict)
            # make sure it's connected to the other point
            self.assertEqual(len(pt.connected_points),
                             len(pts_dict[(pt.x, pt.y)]))
            for ptid in pt.connected_points:
                otherpt = net.points[ptid]
                self.assertTrue((otherpt.x, otherpt.y) in pts_dict[(pt.x, pt.y)])
                self.assertEqual(len(pt.connected_components), 0)

    def test_net_two_points(self):
        """ Test a net with two points """
        pts_dict = {(13, 15): [(17, 19)],
                    (17, 19): [(13, 15)]}
        self.sch.stream.f = iter(['J 13 15 2\n',
                                  'J 17 19 2\n',
                                  'S 1 2\n'])
        k, v = self.sch.parse_net('bar')
        self.assertEqual(k, 'net')
        self.netpt_helper(pts_dict, v)
        self.assertEqual(v.net_id, 'bar')
        self.assertEqual(len(v.attributes), 0)
        self.assertEqual(len(v.annotations), 0)

    def test_net_three_points(self):
        """ Test a net with three points """
        pts_dict = {(1, 2): [(3, 4)],
                    (3, 4): [(1, 2), (5, 6)],
                    (5, 6): [(3, 4)]}
        segs = [('1 2', '2 1'), ('2 3', '3 2')]
        for (p, q, r) in [(a, b, c) for a in (0, 1) for b in (0, 1)
                          for c in (0, 1)]:
            self.sch.stream.f = iter(['J 1 2 2\n',
                                      'J 3 4 2\n',
                                      'J 5 6 2\n',
                                      'S %s\n' % segs[r][p],
                                      'S %s\n' % segs[1-r][q]])
            # run the different permutations to make sure different ordering of
            # connections doesn't matter
            k, v = self.sch.parse_net('bar')
            self.assertEqual(k, 'net')
            self.netpt_helper(pts_dict, v)
            self.assertEqual(v.net_id, 'bar')
            self.assertEqual(len(v.attributes), 0)
            self.assertEqual(len(v.annotations), 0)

    def test_net_label(self):
        """ Test a label added to a net """
        self.sch.stream.f = iter(['L 2 3 4 0 5 6 7 8 foo label\n'])
        _k, v = self.sch.parse_net('bar')
        self.assertEqual(len(v.annotations), 1)
        annot = v.annotations[0]
        self.assertEqual((annot.x, annot.y), (2, 3))
        self.assertEqual(annot.value, 'foo label')
        self.assertEqual(annot.visible, True)

    def test_simple_inst(self):
        """ Test a basic component instance """
        k, v = self.sch.parse_inst("1500 lib:file 5 4 3 2 1 '")
        self.assertEqual(k, 'inst')
        self.assertEqual(v.instance_id, '1500')
        self.assertEqual(v.library_id, 'lib:file.5')
        self.assertEqual(v.symbol_index, 0)
        self.assertEqual(len(v.symbol_attributes), 1)
        attrs = v.symbol_attributes[0]
        self.assertEqual((attrs.x, attrs.y), (4, 3))
        self.assertEqual(attrs.rotation, 1)
