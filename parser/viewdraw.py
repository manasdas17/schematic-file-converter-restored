from core.net import Net, NetPoint, ConnectedComponent
from core.annotation import Annotation
from core.design import Design
from core.components import Components, Component, Symbol, Body, Pin
from core.component_instance import ComponentInstance, SymbolAttribute
from core.shape import Circle, Line, Rectangle, Label, Arc
from os import listdir
from math import pi, sqrt, atan
from collections import defaultdict

# ViewDraw files are line-based, where the first character of a line is a
# command, and the rest of the line is arguments for that command. '|' was
# originally a comment, but seems to have ben co-opted to get even more commands
# out of the format, such that |R, |Q, |FNTSTL, and others are now also used.

class vdparser:
    '''base class for the parsers. Includes parsing code for commands that are
    shared between the different files'''
    sheetsizes = ('ASIZE', 'BSIZE', 'CSIZE', 'DSIZE', 'ESIZE', 'A4', 'A3',
                  'A2', 'A1', 'A0', 'CUSTOM')
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
            cmd, sep, args = phrase.partition(' ')
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

    def parse_null(self, args):
        '''A do-nothing parser for commands to be ignored'''
        # override/decorate this if you have a method you want to have called
        # for every unhandled command.
        # get that token off the stack, and ignore it
        return (None, [])

    def parse_annot(self, args):
        x, y, font_size, rot, anchor, viz, val = args.split(' ', 6)
        # anchor is 1,2,3: bottom,mid,top respectively
        # visibility is 0,1,2,3: invis, vis, name only, val only
        # FIXME use rotation
        subdata = defaultdict(list)
        for phrase in self.stream:
            cmd, sep, args = phrase.partition(' ')
            if cmd not in ('Q'):
                self.stream.push(phrase)
                break
            # Q cmd is ignored for now anyway, but need to get it out of the way
            k, v = self.parsenode(cmd)(args)
            subdata[k].append(v)
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
        x, y, font_size, rot, c, d, e, f, text = args.split(' ', 8)
        # treat them as annotations for now, I guess.
        # suspect that c, e are anchor and vis, as in parse_annot
        # According to other research, d is scope (0=local, 1=global) and f
        # might be logic sense (for overbars, 0=normal, 1=inverted)
        # FIXME use rot and vis
        return ('annot', Annotation(text, int(x), int(y), 0, True))

    def parse_rev(self, args):
        # File revision date. Gahh, ugly.
        return ('annot', Annotation('rev=' + args, 0, 0, 0, False))

    def parse_size(self, args):
        size = int(args.split()[0])
        return ('sheetsize', (size < len(self.sheetsizes) and
                              self.sheetsizes[size] or 'unknown'))

    def parse_circle(self, args):
        x, y, r = [int(a) for a in args.split()]
        return ('shape', Circle(x, y, r))

    def parse_box(self, args):
        x1, y1, x2, y2 = [int(a) for a in args.split()]
        return ('shape', Rectangle.from_corners(x1, y1, x2, y2))

    def parse_text(self, args):
        x, y, size, rot, anchor, text = args.split(' ', 5)
        # TODO sort out rotation, alignment
        return ('shape', Label(int(x), int(y), text, 'left', 0))

    def parse_ver(self, args):
        # Viewdraw file version. So far have only dealt with 50, 51.
        return ('fileversion', args)

    def parse_line(self, args):
        numpts, sep, pts = args.partition(' ')
        pts = [int(p) for p in pts.split()]
        numpts = int(numpts)
        # this next bit would be much easier if open polygons were
        # explicitly acceptable
        # TODO yuck, and callers need to special-case this
        return ('lines', [Line((pts[i], pts[i + 1]),(pts[i + 2], pts[i + 3]))
                          for i in range(0, (numpts - 1) * 2, 2)])

    def parse_arc(self, args):
        # ViewDraw saves arcs as three points along a circle. Start, mid, end
        # [not entirely sure that mid is a midpoint, but irrelevant here]. We
        # need to find the centre of that circle, and the angles of the start
        # and end points. Tracing from start to end, the arcs are always CCW.

        # To find the centre: construct two chords using the three points. Lines
        # drawn perpendicular to and bisecting these chords will intersect at
        # the circle's centre.
        x0, y0, x1, y1, x2, y2 = [float(pt) for pt in args.split()]
        # can't allow for infinite slopes (ma and mb), and can't allow ma to be
        # a zero slope.
        while abs(x0 - x1) < 0.1 or abs(x1 - x2) < 0.1 or abs(y0 - y1) < 0.1:
            x0, y0, x1, y1, x2, y2 = x1, y1, x2, y2, x0, y0
        # slopes of the chords
        ma, mb = (y1-y0)/(x1-x0), (y2-y1)/(x2-x1)
        # find the centre
        xc = (ma*mb*(y0-y2) + mb*(x0+x1) - ma*(x1+x2)) / (2*(mb-ma))
        yc = (-1/ma) * (xc - (x0+x1)/2) + (y0+y1)/2
        # radius is the distance from the centre to any of the three points
        r = sqrt((xc-x0)**2 + (yc-y0)**2)

        # re-init xs,ys so that start and end points don't get confused.
        x0, y0, x1, y1, x2, y2 = [float(pt) for pt in args.split()]

        def angle(x, y):
            # correcting for the y-origin will flip the angle through the y=x
            # line, so theta=0 is high noon, angle increases CW now, after
            # correct_y theta=0 is 3 o'clock and angle increases CCW.
            opp = y - yc
            adj = x - xc
            if abs(adj) < 0.01:
                # vertical line to x,y
                if opp > 0:
                    return 3 * pi / 2
                else:
                    return pi / 2
            ang = atan(opp/adj) - pi/2
            if adj < 0:
                ang += pi
            ang = (3 * pi / 2) - ang
            if ang < 0:
                ang += 2 * pi
            return ang

        return ('shape', Arc(int(round(xc)), int(round(yc)),
                             angle(x0,y0), angle(x2,y2),
                             int(round(r))))

class ViewDrawSch(vdparser):
    def __init__(self, lib, filename):
        vdparser.__init__(self, filename)
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
        tree = vdparser.parse(self)
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
                cc = ConnectedComponent(inst.instance_id, pinid)
                net.ibpts[netpt - 1].add_connected_component(cc)
            del inst.conns
        for net in ckt.nets:
            del net.ibpts

        # too bad designs don't have top-level shapes (yet?)
        #map(ckt.add_shape, tree['shape'])
        
        for lbl in [s for s in tree['shapes'] if isinstance(s, Label)]:
            ann = Annotation(lbl.text, lbl.x, lbl.y, lbl.rotation, True)
            ckt.design_attributes.add_annotation(ann)
        
        for k, v in tree['attr']:
            ckt.design_attributes.add_attribute(k, v)

        self.correct_y(ckt, tree['Dbounds'][0])
        return ckt

    def parse_net(self, args):
        thisnet = Net(args)
        subdata = defaultdict(list)
        for phrase in self.stream:
            cmd, sep, args = phrase.partition(' ')
            if cmd not in ('J', 'S', 'A', 'L', 'Q', 'B'):
                self.stream.push(phrase)
                break
            k, v = self.parsenode(cmd)(args)
            subdata[k].append(v)
        # finish building thisnet
        for netpt in subdata['netpoint'][:]:
            # using a copy so that we can modify subdata['netpoint'] inside loop
            if netpt.point_id not in thisnet.points:
                thisnet.add_point(netpt)
            else:
                # oh yeah, a net can have a point more than once, because that
                # makes *great* sense.
                for pt in netpt.connected_points:
                    thisnet.points[netpt.point_id].add_connected_point(pt)
                for comp in netpt.connected_components:
                    thisnet.points[netpt.point_id].add_connected_component(comp)
                # update subdata['netpoint'] so that ref to netpt points to the
                # new combined point
                i = subdata['netpoint'].index(netpt)
                subdata['netpoint'][i] = thisnet.points[netpt.point_id]

        # yuck, passing in-band
        thisnet.ibpts = subdata['netpoint']

        for a, b in subdata['segment']:
            thisnet.connect((subdata['netpoint'][a - 1],
                             subdata['netpoint'][b - 1]))
        for annot in subdata['annot']:
            thisnet.add_annotation(annot)
            if '=' in annot.value:
                thisnet.add_attribute(*(annot.value.split('=', 1)))
        return ('net', thisnet)

    def parse_junc(self, args):
        x, y, unknown = args.split()
        # unknown is suspected to be drawing style for the net at this
        # point (right-angle corner? T-section? Solder dot?) ATM not very
        # useful, not really our responsibility.
        return ('netpoint', NetPoint(x + 'x' + y, int(x), int(y)))

    def parse_seg(self, args):
        a, b = [int(n) for n in args.split()]
        return ('segment', (a, b))

    def parse_inst(self, args):
        inst, libname, libnum, x, y, rot, scale, b = args.split()
        # scale is a floating point scaling constant. Also, evil.
        thisinst = ComponentInstance(inst, self.lookup(libname, libnum), 0)
        if int(rot) > 3:
            # part is flipped around y-axis. When applying transforms, flip it
            # first, then rotate it.
            rot = str(int(rot) - 4)
            # flip = True

        thisinst.add_symbol_attribute(SymbolAttribute(int(x), int(y),
                                                      float(rot) / 2))
        subdata = defaultdict(list)
        for phrase in self.stream:
            cmd, sep, args = phrase.partition(' ')
            if cmd not in ('|R', 'A', 'C'):
                self.stream.push(phrase)
                break
            k, v = self.parsenode(cmd)(args)
            subdata[k].append(v)
        for annot in subdata['annot']:
            thisinst.symbol_attributes[0].add_annotation(annot)
            if '=' in annot.value:
                thisinst.add_attribute(*(annot.value.split('=', 1)))

        # Turns out C can reference a net before it's been created via
        # the N command. Really don't like passing stuff inband like this. Ugh.
        thisinst.conns = subdata['conn']
        return ('inst', thisinst)

    def parse_conn(self, args):
        netid, segpin, pin, a = args.split()
        # as far as has been observed, a is always 0
        # segpin is the netpoint on the net
        # TODO I have no faith in pin variable here
        return ('conn', (netid, int(segpin), pin))
    
    def parse_bounds(self, args):
        # Not sure if this is quite valid.
        return ('Dbounds', [int(a) for a in args.split()])

    def parse_attr(self, args):
        x, y, font_size, rot, anchor, viz, kv = args.split(' ', 6)
        k, sep, v = kv.partition('=')
        # TODO want to do anything with the rest of the info?
        # TODO at least add in the label
        return ('attr', (k, v))

    def lookup(self, libname, num):
        return libname.lower() + '.' + num

    def correct_y(self, des, (xmin, ymin, xmax, ymax)):
        for ann in des.design_attributes.annotations:
            ann.y = ymax - ann.y
        # someday, this will happen
        #for sh in des.shapes:
        #    for pt in sh.points:
        #        pt.y = ymax - pt.y
        for ci in des.component_instances:
            for sym in ci.symbol_attributes:
                sym.y = ymax - sym.y
                for ann in sym.annotations:
                    ann.y = ymax - ann.y
        for net in des.nets:
            for pt in net.points.values():
                pt.y = ymax - pt.y
                pt.point_id = str(pt.x) + 'x' + str(pt.y)
            for pt in net.points.values():
                # yes, this needs to be two-pass
                # update all the point_ids, n.points still indexes them by their
                # old point_ids
                pt.connected_points = [net.points[p].point_id for p in
                                       pt.connected_points]
            net.points = dict([(pt.point_id, pt) for pt in net.points.values()])
            for ann in net.annotations:
                ann.y = ymax - ann.y

class ViewDrawSym(vdparser):
    symtypes = ('composite', 'module', 'annotate', 'pin', 'power')
    # TODO A command

    def __init__(self, libdir, filename):
        vdparser.__init__(self, libdir + filename)
        self.parsers.update({'Y': 'parse_type',
                             'U': 'parse_attr',
                             'P': 'parse_pin',
                             'L': 'parse_label',
                            })
        self.libdir = libdir

    def parse(self):
        part = Component(self.filename)
        part.add_symbol(Symbol())
        part.symbols[0].add_body(Body())
        
        tree = vdparser.parse(self)
        for attr in tree['attr']:
            part.add_attribute(*attr)
        for shape in tree['shape'] + sum(tree['lines'], []):
            part.symbols[0].bodies[0].add_shape(shape)
        for pin in tree['pin']:
            part.symbols[0].bodies[0].add_pin(pin)

        self.correct_y(part)
        return part

    def parse_type(self, args):
        return ('attr', ('symtype', (int(args) < len(self.symtypes) and
                                     self.symtypes[int(args)] or 'unknown')))

    def parse_attr(self, args):
        # part properties, some of which look in need of further
        # processing to properly extract the part
        key, sep, val = args.split(' ', 6)[-1].partition('=')
        # I have seen some properties that have no value set, and don't
        # have '=' in the string. partition() will set val = ''

        #TODO are those properties names user-controlled? should I make
        # sure they don't collide with other attributes?
        return ('attr', (key, val))

    def parse_pin(self, args):
        # Pin declaration, seems to only be done once per pin
        pid, xe, ye, xb, yb, rot, side, inv = [int(a) for a in args.split()]
        thispin = Pin(pid, (xb, yb), (xe, ye))
        subdata = defaultdict(list)
        for phrase in self.stream:
            cmd, sep, args = phrase.partition(' ')
            if cmd not in ('L'):
                self.stream.push(phrase)
                break
            k, v = self.parsenode(cmd)(args)
            subdata[k].append(v)
        if len(subdata['label']) > 0:
            # I suppose if there's more than one label, just go with the first
            thispin.label = subdata['label'][0]
        return ('pin', thispin)

    def parse_label(self, args):
        # So far, only seen it for labelling pins, in the symmbol files
        # at least.
        x, y, pts, rot, anchor, scope, vis, inv, text = args.split()
        return ('label', Label(int(x), int(y),
                         # cheap-o overbar
                         (inv == '1' and '/' or '') + text,
                         'left', int(rot) * 0.5))
        # I have a feeling the alignment  will break, but anchor is a
        # vertical alignment thing

    def correct_y(self, comp):
        for sym in comp.symbols:
            for bod in sym.bodies:
                for pin in bod.pins:
                    pin.p1.y = -pin.p1.y
                    pin.p2.y = -pin.p2.y
                for shape in bod.shapes:
                    if isinstance(shape, (Arc, Circle, Label, Rectangle)):
                        shape.y = -shape.y
                    if isinstance(shape, Rectangle):
                        shape.height = -shape.height
                    if isinstance(shape, Line):
                        shape.p1.y = -shape.p1.y
                        shape.p2.y = -shape.p2.y

class ViewDraw:
    def __init__(self, schdir, symdirs):
        # symdirs is a dict; k,v = libname,directory
        # ^-that could be parsed out of a viewdraw.ini some day
        self.schdir, self.symdirs = schdir, symdirs

    def parse(self):
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
    def __init__(self, filename):
        self.f = open(filename)
        self.fstack = []
        self.line = 0
    
    def __iter__(self):
        return self

    def next(self):
        tok = self.subpop()
        nexttok = self.subpop()
        while nexttok.startswith(' ') or nexttok.startswith('+'):
            tok = self.continuation(tok, nexttok)
            nexttok = self.subpop()
        self.push(nexttok)
        return tok.strip('\r\n')

    def subpop(self):
        self.line += 1
        if len(self.fstack) > 0:
            return self.fstack.pop()
        return self.f.next()

    def continuation(self, tok, cont):
        if cont.startswith('+'):
            cont = cont[2:]
        return tok.strip('\r\n') + cont

    def push(self, tok):
        self.line -= 1
        self.fstack.append(tok)
