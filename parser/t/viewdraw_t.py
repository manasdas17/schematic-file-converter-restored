import unittest
from inspect import getargspec
from parser.viewdraw import FileStack, ViewDrawBase

from core.annotation import Annotation
from math import sin, cos, pi

class FileStackTests(unittest.TestCase):

    def setUp(self):
        """stub in a constructor that doesn't depend on filesystem"""
        def fake_init(self, filename):
            self.f = iter([filename + '\n', 'foo\n', 'bar\n', 'baz\n'])
            self.fstack = []
            self.line = 0

        self.real_init = FileStack.__init__
        FileStack.__init__ = fake_init
        self.fs = FileStack('test')


    def tearDown(self):
        """undo the FileStack.__init__ hack"""
        FileStack.__init__ = self.real_init
        del self.fs


    def test_subpop(self):
        """Ensure subpop() can iterate through the simplest case"""
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
    
    def setUp(self):
        def fake_init(self, filename):
            self.f = iter([])
            self.fstack = []
            self.line = 0

        self.real_init = FileStack.__init__
        FileStack.__init__ = fake_init
        self.base = ViewDrawBase('foo')
        self.base.stream = FileStack('bar')

    def tearDown(self):
        FileStack.__init__ = self.real_init
        del self.base

    def test_base_init(self):
        self.assertEqual(self.base.filename, 'foo')

    def test_parser_dispatch(self):
        valid_cmds = 'A L |R V Z c b T a l'.split()
        for cmd in valid_cmds:
            parser  = self.base.parsenode(cmd)
            # make sure it only needs two argument (self, args)
            self.assertEqual(len(getargspec(parser)[0]), 2)
        # currently not testing invalid commands, their behaviour can be
        # considered 'undefined'

    def test_label(self):
        args = '2 3 12 0 # # # # this is a text label'
        # `#` args are unhandled, but may be in the future
        k, v = self.base.parse_label(args)
        self.assertEqual(k, 'annot')
        self.assertTrue(isinstance(v, Annotation))
        self.assertEqual(v.x, 2)
        self.assertEqual(v.y, 3)
        self.assertEqual(v.value, 'this is a text label')

    def test_annot(self):
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
        k, v = self.base.parse_rev('timedate')
        self.assertEqual(k, 'annot')
        self.assertEqual(v.value, 'rev=timedate')
        self.assertFalse(v.visible)
        self.assertEqual(v.x, 0)
        self.assertEqual(v.y, 0)
        self.assertEqual(v.rotation, 0)

    def test_circle(self):
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
        k, v = self.base.parse_text('3 4 # # # hello world')
        self.assertEqual(k, 'shape')
        self.assertEqual(v.type, 'label')
        self.assertEqual((v.x, v.y), (3, 4))
        self.assertEqual(v.text, 'hello world')

    def test_version(self):
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
        self.assertEqual((p1.x, p1.y), (1, 3))
        self.assertEqual((p2.x, p2.y), (4, 7))

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
            self.assertEqual(pts[i], (line.p1.x, line.p1.y))
            self.assertEqual(pts[i + 1], (line.p2.x, line.p2.y))

    def test_arc(self):
        """Arc from noon to 6 o'clock"""
        x_c, y_c, radius = 2, 3, 50
        angles = ((0., 0.5, 1.),
                  (1.5, 0., 0.5),
                  (1., 1.25, 1.5))
        def angle2xy(theta):
            return [int(round(sin(theta * pi) * radius + x_c)),
                    int(round(cos(theta * pi) * radius + y_c))]
        def reflang(theta):
            return (theta + 0.5) % 2.0
            if 0.75 < theta < 1.75:
                return 2.5 - theta
            else:
                return (0.5 - theta + 2) % 2.0

        for ang in (angles):
            print ang
            pts = sum([angle2xy(th) for th in ang], [])

            k, v = self.base.parse_arc(' '.join([str(p) for p in pts]))
            print v.json()
            self.assertEqual(k, 'shape')
            self.assertEqual(v.type, 'arc')
            # allow for points to be off by up to one unit, to account for
            # rounding error in calculating center point, radius.
            self.assertLessEqual(abs(v.x - x_c), 1)
            self.assertLessEqual(abs(v.y - y_c), 1)
            self.assertLessEqual(abs(v.radius - radius), 1)
            self.assertLess(abs(reflang(v.start_angle) - (ang[0])), 0.01)
            self.assertLess(abs(reflang(v.end_angle) - (ang[2])), 0.01)
