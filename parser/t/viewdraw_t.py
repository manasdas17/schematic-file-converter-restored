import unittest
from parser.viewdraw import FileStack

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
