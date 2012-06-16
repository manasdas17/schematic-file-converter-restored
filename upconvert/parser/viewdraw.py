#!/usr/bin/env python2
""" The ViewDraw [5.x] format parser """

# upconvert.py - A universal hardware design file format converter using
# Format:       upverter.com/resources/open-json-format/
# Development:  github.com/upverter/schematic-file-converter
#
# Copyright 2011 Upverter, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from upconvert.core.net import Net, NetPoint, ConnectedComponent
from upconvert.core.annotation import Annotation
from upconvert.core.design import Design
from upconvert.core.components import Components, Component, Symbol, Body, Pin
from upconvert.core.component_instance import ComponentInstance, SymbolAttribute
from upconvert.core.shape import Circle, Line, Rectangle, Label, Arc
from os import listdir, sep as dirsep
from math import pi, sqrt, atan
from collections import defaultdict

# Notes:
# ViewDraw files are line-based, where the first character of a line is a
# command, and the rest of the line is arguments for that command. '|' was
# originally a comment, but seems to have ben co-opted to get even more commands
# out of the format, such that |R, |Q, |FNTSTL, and others are now also used.


class ViewDrawBase:
    '''The base class for the parsers. Includes parsing code for commands that
    are shared between the different files'''

    sheetsizes = ('ASIZE', 'BSIZE', 'CSIZE', 'DSIZE', 'ESIZE', 'A4', 'A3',
                  'A2', 'A1', 'A0', 'CUSTOM')

    @staticmethod
    def auto_detect(filename):
        """ Return our confidence that the given file is a viewdraw file """
        confidence = 0.
        with open(filename) as f:
            # as far as I've seen, the first two non-comment lines in a
            # viewdraw file are the version, and the mysterious K line
            version = f.readline().strip()
            while version.startswith('|'):
                version = f.readline().strip()
            kline = f.readline().strip()
            while kline.startswith('|'):
                kline = f.readline().strip()

            if version.startswith('V '):
                confidence += 0.2
                if version.split(' ')[1] in ('50', '51', '52', '53'):
                    # the only version numbers I've seen that match this format
                    confidence += 0.5
            if kline.startswith('K '):
                confidence += 0.2

        # result is that confidence is 0.9 if it's precisely what I expected,
        # and likely 0.4 if it's just in a related format (eg later versions
        # will report 'V 5.4' or similar)
        return confidence

    def __init__(self, filename):
        self.filename = filename
        self.stream = None
        self.parsers = {'A': 'parse_annot',
                        'L': 'parse_label',
                        '|R': 'parse_rev',
                        'V': 'parse_ver',
                        'Z': 'parse_size',
                        'c': 'parse_circle',
                        'b': 'parse_box',
                        'T': 'parse_text',
                        'a': 'parse_arc',
                        'l': 'parse_line',
                       }

    def parse(self):
        '''Returns a dict of elements that have been parsed out of the file'''
        self.stream = FileStack(self.filename)
        tree = defaultdict(list)
        for phrase in self.stream:
            cmd, _sep, args = phrase.partition(' ')
            k, v = self.parsenode(cmd)(args)
            tree[k].append(v)
        return tree

    def parsenode(self, cmd):
        '''Returns the method used to parse the given command. Parse methods
        return a key and a properly parsed element (unspecified type)'''
        # this would be the place to override or decorate if you want additional
        # info or control on every single action taken.
        parser = self.parsers.get(cmd, 'parse_null')
        return getattr(self, parser)

    def parse_null(self, args): # pylint: disable=W0613
        '''A do-nothing parser for commands to be ignored'''
        # override/decorate this if you have a method you want to have called
        # for every unhandled command.
        # get that token off the stack, and ignore it
        return (None, [])

    def parse_annot(self, args):
        """ Returns a parsed annotation. """
        x, y, _font_size, _rot, _anchor, viz, val = args.split(' ', 6)
        # anchor is 1,2,3: bottom,mid,top respectively
        # visibility is 0,1,2,3: invis, vis, name only, val only
        # FIXME use rotation
        self.sub_nodes(['Q'])
        # Q cmd is ignored for now anyway, but need to get it out of the way
        display = True
        if viz == '1':
            value = val
        elif viz == '2':
            value = val.split('=')[0]
        elif viz == '3':
            value = val.split('=', 1)[-1]
        else:
            value = val
            display = False
        return ('annot', Annotation(value, int(x), int(y), 0, display))

    def parse_label(self, args):
        """ Returns a parsed label. """
        args = args.split(' ', 8)
        x, y, _font_size, _rot, _anchor, _scope, _vis, _sense, text = args
        # treat them as annotations for now, I guess.
        # suspect that anchor and vis are as in parse_annot
        # According to other research, _scope is (0=local, 1=global) and _sense
        # might be logic sense (for overbars, 0=normal, 1=inverted)
        # FIXME use rot and vis
        return ('annot', Annotation(text, int(x), int(y), 0, True))

    def parse_rev(self, args):
        """ Returns the file revision date, parsed into an annotation. """
        # File revision date. Gahh, ugly.
        return ('annot', Annotation('rev=' + args, 0, 0, 0, False))

    def parse_size(self, args):
        """ Returns the sheet size. """
        size = int(args.split()[0])
        if size < len(self.sheetsizes):
            sheet = self.sheetsizes[size]
        else:
            sheet = 'unknown'
        return ('sheetsize', sheet)

    def parse_circle(self, args):
        """ Returns a parsed circle. """
        x, y, rad = [int(a) for a in args.split()]
        return ('shape', Circle(x, y, rad))

    def parse_box(self, args):
        """ Returns a parsed box. """
        x1, y1, x2, y2 = [int(a) for a in args.split()]
        return ('shape', Rectangle.from_corners(x1, y1, x2, y2))

    def parse_text(self, args):
        """ Parses a text label and returns as a Shape.Label. """
        x, y, _size, _rot, _anchor, text = args.split(' ', 5)
        # TODO sort out rotation, alignment
        return ('shape', Label(int(x), int(y), text, 'left', 0))

    def parse_ver(self, args):
        """ Returns the ViewDraw output file format version. """
        # Viewdraw file version. So far have only dealt with 50, 51.
        return ('fileversion', args)

    def parse_line(self, args):
        """ Returns a parsed line. """
        numpts, _sep, pts = args.partition(' ')
        pts = [int(p) for p in pts.split()]
        numpts = int(numpts)
        # this next bit would be much easier if open polygons were
        # explicitly acceptable
        # TODO yuck, and callers need to special-case this
        return ('lines', [Line((pts[i], pts[i + 1]),(pts[i + 2], pts[i + 3]))
                          for i in range(0, (numpts - 1) * 2, 2)])

    def parse_arc(self, args):
        """ Returns a parsed arc. """
        # ViewDraw saves arcs as three points along a circle. Start, mid, end
        # [not entirely sure that mid is a midpoint, but irrelevant here]. We
        # need to find the centre of that circle, and the angles of the start
        # and end points. Tracing from start to end, the arcs are always CCW.

        # To find the centre: construct two chords using the three points. Lines
        # drawn perpendicular to and bisecting these chords will intersect at
        # the circle's centre.
        x0, y0, x1, y1, x2, y2 = [float(pt) for pt in args.split()]
        # can't allow for infinite slopes (m_a and m_b), and can't allow m_a
        # to be a zero slope.
        while abs(x0 - x1) < 0.1 or abs(x1 - x2) < 0.1 or abs(y0 - y1) < 0.1:
            x0, y0, x1, y1, x2, y2 = x1, y1, x2, y2, x0, y0
        # slopes of the chords
        m_a, m_b = (y1-y0) / (x1-x0), (y2-y1) / (x2-x1)
        # find the centre
        xcenter = ((m_a * m_b * (y0 - y2) + m_b * (x0 + x1) - m_a * (x1 + x2))
                   / (2 * (m_b - m_a)))
        ycenter = (-1/m_a) * (xcenter - (x0+x1) / 2) + (y0+y1) / 2
        # radius is the distance from the centre to any of the three points
        rad = sqrt((xcenter-x0)**2 + (ycenter-y0)**2)

        # re-init xs,ys so that start and end points don't get confused.
        x0, y0, x1, y1, x2, y2 = [float(pt) for pt in args.split()]

        def angle(x, y):
            """ Calculate the angle from the center of the arc to (x, y). """
            # as parsed, the angle increases CCW. Here, we return an angle
            # increasing CW
            opp = y - ycenter
            adj = x - xcenter
            if abs(adj) < 0.01:
                # vertical line to x,y
                if opp > 0:
                    return 3 * pi / 2
                else:
                    return pi / 2

            ang = atan(opp/adj)
            # correct for ambiguity due to atan
            if adj < 0:
                ang += pi

            # restrict angle to (0, 2pi) range
            ang = ang % (2 * pi)
            # upverter uses CW angles, so...
            return 2 * pi - ang

        return ('shape', Arc(int(round(xcenter)), int(round(ycenter)),
                             angle(x2,y2) / pi, angle(x0,y0) / pi,
                             int(round(rad))))

    def sub_nodes(self, sub_cmds):
        """ Parse and return any commands that the parent needs.

        Returns a dict in the same style as parse() that the parent node can
        use. Any use of this sub-tree is left up to the caller. """
        subdata = defaultdict(list)
        for phrase in self.stream:
            cmd, _sep, args = phrase.partition(' ')
            if cmd not in sub_cmds:
                self.stream.push(phrase)
                break
            k, v = self.parsenode(cmd)(args)
            subdata[k].append(v)
        return subdata

class ViewDrawSch(ViewDrawBase):
    """ Parser for a single schematic file. """

    def __init__(self, lib, filename):
        ViewDrawBase.__init__(self, filename)
        self.parsers.update({'N': 'parse_net',
                             'J': 'parse_junc',
                             'S': 'parse_seg',
                             'B': 'parse_seg', # FIXME No! It is a bus!
                             'I': 'parse_inst',
                             'C': 'parse_conn',
                             'U': 'parse_attr',
                             'D': 'parse_bounds'
                            })
        self.lib = lib

    def parse(self):
        '''Returns a Design built up from a schematic file that represents one
        sheet of the original schematic'''
        tree = ViewDrawBase.parse(self)
        # tree['lines'] is a [list of [list of lines]]
        tree['shape'].extend(sum(tree['lines'], []))
        ckt = Design()
        # TODO little weak here, a copy instead?
        ckt.components = self.lib

        for net in tree['net']:
            ckt.add_net(net)
        for inst in tree['inst']:
            ckt.add_component_instance(inst)
            # hold on tight, this is ugly
            for (netid, netpt, pinid) in inst.conns:
                net = [n for n in ckt.nets if n.net_id == netid][0]
                comp = ConnectedComponent(inst.instance_id, pinid)
                net.ibpts[netpt - 1].add_connected_component(comp)
            del inst.conns
        for net in ckt.nets:
            del net.ibpts

        for shape in tree['shape']:
            ckt.add_shape(shape)
            if isinstance(shape, Label):
                ann = Annotation(shape.text, shape.x, shape.y,
                                 shape.rotation, True)
                ckt.design_attributes.add_annotation(ann)

        for k, v, annot in tree['attr']:
            ckt.design_attributes.add_attribute(k, v)
            ckt.design_attributes.add_annotation(annot)

        return ckt

    def parse_net(self, args):
        """ Assembles a net from a list of junctions, segments, and labels. """
        thisnet = Net(args)
        subdata = self.sub_nodes('J S A L Q B'.split())
        # finish building thisnet
        for netpt in subdata['netpoint'][:]:
            # using a copy so that we can modify subdata['netpoint'] inside loop
            if netpt.point_id not in thisnet.points:
                thisnet.add_point(netpt)
            else:
                # oh yeah, a net can have a point more than once, because that
                # makes *great* sense.
                for point in netpt.connected_points:
                    thisnet.points[netpt.point_id].add_connected_point(point)
                for comp in netpt.connected_components:
                    thisnet.points[netpt.point_id].add_connected_component(comp)
                # update subdata['netpoint'] so that ref to netpt points to the
                # new combined point
                i = subdata['netpoint'].index(netpt)
                subdata['netpoint'][i] = thisnet.points[netpt.point_id]

        # yuck, passing in-band
        thisnet.ibpts = subdata['netpoint']

        for pt_a, pt_b in subdata['segment']:
            thisnet.connect((subdata['netpoint'][pt_a - 1],
                             subdata['netpoint'][pt_b - 1]))
        for annot in subdata['annot']:
            thisnet.add_annotation(annot)
            if '=' in annot.value:
                thisnet.add_attribute(*(annot.value.split('=', 1)))
        return ('net', thisnet)

    def parse_junc(self, args):
        """ Parses a junction on the net as a NetPoint. """
        x, y, _unknown = args.split()
        # unknown is suspected to be drawing style for the net at this
        # point (right-angle corner? T-section? Solder dot?) ATM not very
        # useful, not really our responsibility.
        return ('netpoint', NetPoint(x + 'x' + y, int(x), int(y)))

    def parse_seg(self, args):
        """ Returns a parsed net segment """
        pt_a, pt_b = [int(n) for n in args.split()]
        return ('segment', (pt_a, pt_b))

    def parse_inst(self, args):
        """ Returns a parsed component instance. """
        inst, libname, libnum, x, y, rot, _scale, _unknown = args.split()
        # scale is a floating point scaling constant. Also, evil.
        thisinst = ComponentInstance(inst, self.lookup(libname, libnum), 0)
        if int(rot) > 3:
            # part is flipped around y-axis. When applying transforms, flip it
            # first, then rotate it.
            rot = str(int(rot) - 4)
            # flip = True

        thisinst.add_symbol_attribute(SymbolAttribute(int(x), int(y),
                                                      float(rot) / 2))
        subdata = self.sub_nodes('|R A C'.split())
        for annot in subdata['annot']:
            thisinst.symbol_attributes[0].add_annotation(annot)
            if '=' in annot.value:
                thisinst.add_attribute(*(annot.value.split('=', 1)))

        # Turns out C can reference a net before it's been created via
        # the N command. Really don't like passing stuff inband like this. Ugh.
        thisinst.conns = subdata['conn']
        return ('inst', thisinst)

    def parse_conn(self, args):
        """ Returns a parsed connection between component and net. """
        netid, segpin, pin, _unknown = args.split()
        # as far as has been observed, _unknown is always 0
        # segpin is the netpoint on the net
        # TODO I have no faith in pin variable here
        return ('conn', (netid, int(segpin), pin))

    def parse_bounds(self, args):
        """ Parses the bounds of this schematic sheet. """
        # Not sure if this is quite valid.
        return ('Dbounds', [int(a) for a in args.split()])

    def parse_attr(self, args):
        """ Returns a parsed attribute. """
        keyval = args.split(' ', 6)[-1]
        # need to keep the attribute key/val pair, as it may be clobbered while
        # creating the annotation.
        k, _sep, v = keyval.partition('=')
        # make an annotation out of it too, so that it displays on the design
        return ('attr', (k, v, self.parse_annot(args)[1]))

    def lookup(self, libname, num):
        """ Given a component name and version, returns the filename """
        return libname.lower() + '.' + num


class ViewDrawSym(ViewDrawBase):
    """ Parser for a library symbol file. """
    symtypes = ('composite', 'module', 'annotate', 'pin', 'power')
    # TODO A command

    def __init__(self, libdir, filename):
        ViewDrawBase.__init__(self, libdir + filename)
        self.parsers.update({'Y': 'parse_type',
                             'U': 'parse_attr',
                             'P': 'parse_pin',
                             'L': 'parse_label',
                            })
        self.libdir = libdir

    def parse(self):
        """ Parses a component from the library, returns a Compenent. """
        part = Component(self.filename)
        part.add_symbol(Symbol())
        part.symbols[0].add_body(Body())

        tree = ViewDrawBase.parse(self)
        for k, v in tree['attr']:
            part.add_attribute(k, v)
        for shape in tree['shape'] + sum(tree['lines'], []):
            part.symbols[0].bodies[0].add_shape(shape)
        for pin in tree['pin']:
            part.symbols[0].bodies[0].add_pin(pin)

        return part

    def parse_type(self, args):
        """ Returns a parsed symbol type. """
        if int(args) < len(self.symtypes):
            symtype = self.symtypes[int(args)]
        else:
            symtype = 'unknown'
        return ('attr', ('symtype', symtype))

    def parse_attr(self, args):
        """ Returns a parsed attribute. """
        # part properties, some of which look in need of further
        # processing to properly extract the part
        key, _sep, val = args.split(' ', 6)[-1].partition('=')
        # I have seen some properties that have no value set, and don't
        # have '=' in the string. partition() will set val = ''

        #TODO are those properties names user-controlled? should I make
        # sure they don't collide with other attributes?
        return ('attr', (key, val))

    def parse_pin(self, args):
        """ Returns a parsed pin. """
        # Pin declaration, seems to only be done once per pin
        pid, x1, y1, x0, y0, _rot, _side, _inv = [int(a) for a in args.split()]
        # _rot and _side are not needed, because the x-y data tells us what we
        # need to know. _inv is used to draw the little inverted signal cirles.
        thispin = Pin(pid, (x0, y0), (x1, y1))
        subdata = self.sub_nodes(['L'])
        if len(subdata['label']) > 0:
            # I suppose if there's more than one label, just go with the first
            thispin.label = subdata['label'][0]
        return ('pin', thispin)

    def parse_label(self, args):
        """ Returns a parsed label. """
        # So far, only seen it for labelling pins, in the symmbol files
        # at least.
        x, y, _pts, rot, _anchor, _scope, _vis, inv, text = args.split()
        if inv == '1':
            # cheap-o overbar
            text = '/' + text
        return ('label', Label(int(x), int(y), text, 'left', int(rot) * 0.5))
        # I have a feeling the alignment will break, but anchor is a
        # vertical alignment thing


class ViewDraw:
    """ The viewdraw parser. """

    def __init__(self, schdir, symdirs):
        # symdirs is a dict; k,v = libname,directory
        # ^-that could be parsed out of a viewdraw.ini some day
        self.schdir, self.symdirs = schdir, symdirs

    @staticmethod
    def inifile(projdir, inidirsep='\\'):
        """ Attempt to get project info from a viewdraw.ini file

        No guarantees, but it should return a (schdir, symdirs) tuple that
        would work fine if passed to the ViewDraw constructor """

        with open(projdir + 'viewdraw.ini') as f:
            dirlines = [li.strip() for li in f.readlines() if
                        li.strip().startswith('DIR ')]
            schdir, symdirs = projdir + 'sym' + dirsep, {}
            for line in dirlines:
                # DIR [p] .\directory\to\lib (lib_name)
                _cmd, mode, vals = line.split(' ', 2)
                # libname might not exist, but if it does it's <= 32 chars, and
                # enclosed by parens
                libname = None
                if vals.endswith(')') and len(vals.rsplit('(', 1)[1]) <= 33:
                    dirname, libname = vals.rsplit('(', 1)
                    dirname, libname = dirname[:-1], libname[:-1]
                else:
                    dirname = vals
                # dirname can be quoted
                if dirname[0] == '"' and dirname[-1] == '"':
                    dirname = dirname[1:-1]
                dirname = dirname.replace(inidirsep, dirsep) + dirsep
                if 'p' in mode:
                    schdir = projdir + dirname + 'sch' + dirsep
                if libname is not None:
                    symdirs[libname] = projdir + dirname + 'sym' + dirsep
            return (schdir, symdirs)

    @staticmethod
    def auto_detect(filename): # pylint: disable=W0613
        """ Return our confidence that the given file is an viewdraw file """
        # I'm not sure what you'd throw this at right now, there is no "project
        # file" you could check. Maybe if/when viewdraw.ini parsing happens?
        return 0


    def parse(self):
        """ Parses a viewdraw project and returns a list of sheets. """
        lib = Components()
        # All the symbol files I have seen have a filename like partname.n
        # where n is a number, for multi-versioned parts I'm guessing
        for libname, libdir in self.symdirs.items():
            files = [f for f in listdir(libdir)
                     if f.rpartition('.')[-1].isdigit()]

            for f in files:
                lib.add_component((libname + ':' + f).lower(),
                                  ViewDrawSym(libdir, f).parse())

        sheets = list()
        schfiles = [f for f in listdir(self.schdir)
                    if f.split('.')[-1].isdigit()]
        for sch in sorted(schfiles, key=lambda s: int(s.split('.')[-1])):
            sheets.append(ViewDrawSch(lib, self.schdir + sch).parse())

        # For now, we'll return a list of designs, each one represents one
        # sheet in the viewdraw schematic.
        return sheets


class FileStack:
    """ Handles a file as a stack of lines, to be able to push back lines"""
    # Two reasons for this:
    # 1) Line continuations are signaled at the beginning of the continuing
    #   line. This means you can't know if line n is the entirety of a statement
    #   until you've checked line n+1
    # 2) Some commands are affected by preceeding commands, so need to check if
    #   the next command is of concern. If not, need to be able to send it back.

    def __init__(self, filename):
        self.f = open(filename)
        self.fstack = []
        self.line = 0

    def __iter__(self):
        return self

    def next(self):
        """ Returns the next command. Continuations handled transparently. """
        tok = self.subpop()
        try:
            nexttok = self.subpop()
            while nexttok.startswith(' ') or nexttok.startswith('+'):
                tok = self.continuation(tok, nexttok)
                nexttok = self.subpop()
            self.push(nexttok)
        except(StopIteration):
            # don't want to pass that up the chain if tok is valid
            pass
        return tok.strip('\r\n')

    def subpop(self):
        """ Next line, from the pushed-back stack if applicable. """
        if len(self.fstack) > 0:
            retval = self.fstack.pop()
        else:
            retval = self.f.next()
        # need to increment after iterators have had a chance to StopIteration
        self.line += 1
        return retval

    def continuation(self, tok, cont):
        """ Tie together multi-line commands. """
        if cont.startswith('+'):
            cont = cont[2:]
        return tok.strip('\r\n') + cont

    def push(self, tok):
        """ Push line back on the stack (before what would be the next line) """
        self.line -= 1
        self.fstack.append(tok)
