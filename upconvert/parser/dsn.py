from inspect import isclass


def pop_type(args, t):
    if len(args) > 0 and isinstance(args[0], t):
        return args.pop(0)
    return None

class DsnClass:
    function = None
    def __repr__(self):
        return '\n%s%s\n' % (self.__class__.__name__, repr(self.__dict__))

class Ancestor(DsnClass):
    """ ancestor_file_descriptor """
    function = 'ancestor'

    def __init__(self, args):
        assert len(args) in (2, 3)
        assert args[1][0] == 'created_time'

        self.file_path_name = args[0]
        self.created_time = args[1][1]

        if len(args) == 3:
            assert args[2][0] == 'comment'
            self.comment = args[2][1]
        else:
            self.comment = None

class Attach(DsnClass):
    """ attach_descriptor """
    function = 'attach'

    def __init__(self, args):
        assert len(args) in (1, 2)
        assert args[0] in ('off', 'on')

        self.attach = args[0]
        if len(args) == 2:
            assert args[1][0] == 'use_via'
            self.use_via = args[1][1]
        else:
            self.use_via = None

class Bond(DsnClass):
    """ bond_shape_descriptor """
    function = 'bond'

    def __init__(self, args):
        assert len(args) == 6
        assert args[4] in ('front', 'back')

        self.pin_reference = args[0]
        self.padstack_id = args[1]
        self.vertex = (int(args[2]), int(args[3]))
        self.front_back = args[4]
        self.bond_shape_rotation = args[5]

class Boundary(DsnClass):
    """ boundary_descriptor """
    function = 'boundary'

    def __init__(self, args):
        self.path = []
        self.rectangle = None
        self.rule = None
        for arg in args:
            pass
            '''
            if isinstance(arg, Path):
                self.path.append(arg)
            elif isinstance(arg, Rectangle):
                self.rectangle = arg
            elif isinstance(arg, Rule):
                self.rule = arg
            else:
                assert not 'Unexpected type'
            '''

class Bundle(DsnClass):
    """ bundle_descriptor """
    function = 'bundle'

    class Gap(DsnClass):
        function = 'gap'
        def __init__(self, args):
            assert len(args) >= 1
            self.gap = int(args[0])
            self.layer = []
            for arg in args[1:]:
                assert arg[0] == 'layer'
                # FIXME
                self.layer = arg[1:]

    def __init__(self, args):
        assert len(args) >= 2
        assert args[1][0] == 'nets'

        self.bundle_id = args[0]
        self.nets = args[1][1:]
        self.gap = []
        for arg in args[2:]:
            assert arg[0] == 'gap'
            self.gap.append(Bundle.Gap(arg[1:]))

class CapacitanceResolution(DsnClass):
    """ capacitance_resolution_descriptor """
    function = 'capacitance_resolution'

    def __init__(self, args):
        assert len(args) == 2
        assert args[0] in ('farad', 'mfarad', 'ufarad', 'nfarad', 'pfarad', 'ffarad')

        self.farad = args[0]
        self.value = int(args[1])

class CheckingTrim(DsnClass):
    """ checking_trim_descriptor """
    function = 'checking_trim_by_pin'

    def __init__(self, args):
        assert len(args) == 1
        assert args[0] in ('on', 'off')

        checking_trim_by_pin = args[0]

class Circle(DsnClass):
    """ circle_descriptor """
    function = 'circle'

    def __init__(self, args):
        assert len(args) in (2, 4)
        self.layer_id = args[0]
        self.diameter = float(args[1])
        if len(args) == 4:
            self.vertex = (int(args[2]), int(args[3]))
        else:
            self.vertex = ()

class Circuit(DsnClass):
    """ circuit_descriptor """
    
    def __init__(self, args):
        self.circuit = args
##############################################################


class Placement(DsnClass):
    """ placement_descriptor """    
    function = 'placement'

    def __init__(self, args):

        self.components = []


class Component(DsnClass):
    """ component_instance """
    function = 'component'

    def __init__(self, args):
        assert len(args) >= 2
        self.image_id = args[0]
        self.placement = args[1:]

class Place(DsnClass):
    """ placement_reference """
    function = 'place'

    def __init__(self, args):
        assert len(args) >= 1
        self.component_id = args[0]

        pos = 1
        if isinstance(args[1], basestring):
            self.vertex = (int(args[1]), int(args[2]))
            self.side = args[3]
            self.rotation = int(args[4])
            pos += 4
        else:
            self.vertex = ()
            self.side = None
            self.rotation = None

        self.part_number = None
        for arg in args[pos:]:
            if isinstance(arg, PartNumber):
                self.part_number = arg

class PartNumber(DsnClass):
    """ part_number """
    function = 'PN'
    def __init__(self, args):
        assert len(args) == 1
        self.part_number = args[0]

class Net(DsnClass):
    """ net_descriptor """
    function = 'net'

    def __init__(self, args):
        assert len(args) >= 1
        self.net_id = pop_type(args, basestring)

        self.pins = []
        for arg in args:
            if isinstance(arg, Pins):
                self.pins.append(arg)

class Network(DsnClass):
    """ network_descriptor """
    function = 'network'

    def __init__(self, args):
        assert len(args) > 0
        self.nets = args[:]

class Pins(DsnClass):
    """ pins """
    function = 'pins'

    def __init__(self, args):
        assert len(args) > 0
        self.pin_reference = args[:]

class Library(DsnClass):
    """ library_descriptor """
    function = 'library'

    def __init__(self, args):
        self.image = []
        while True:
            img = pop_type(args, Image)
            if img is None: break
            self.image.append(img)

class Image(DsnClass):
    """ image_descriptor """
    function = 'image'

    def __init__(self, args):
        assert len(args) >= 1

        self.image_id = args[0]
        pos, length = 1, len(args)

        if pos < length and isinstance(args[pos], Side):
            self.side = args[pos]
            pos += 1
        else:
            self.side = None

        if pos < length and isinstance(args[pos], Outline):
            self.outline = args[pos]
            pos += 1
        else:
            self.outline = None


class Side(DsnClass):
    """ side """
    function = 'side'

    def __init__(self, args):
        assert len(args) == 1
        assert args[0] in ('front', 'back', 'both')

        self.side = pop_type(args, basestring)

class Outline(DsnClass):
    """ outline_descriptor """
    function = 'outline'

    def __init__(self, args):
        assert len(args) == 1
        self.shape = args[0]

class Path(DsnClass):
    """ path_descriptor """
    function = 'path'

    def __init__(self, args):
        assert len(args) >= 2

        self.layer_id = pop_type(args, basestring)
        self.aperture_width = pop_type(args, basestring)
        self.vertex = []

        while True:
            x, y = pop_type(args, basestring), pop_type(args, basestring)
            if x is None: break
            self.vertex.append((float(x), float(y)))
        
        self.aperture_type = pop_type(args, ApertureType)
        assert len(args) == 0

class ApertureType(DsnClass):
    """ aperture_type """
    function = 'aperture_type'

    def __init__(self, args):
        assert len(args) == 1
        assert args[0] in ('round', 'square')

        self.aperture_type = args[0]

##############################################################

all_functions = dict([(s.function, s) for s in globals().values() if isclass(s) and issubclass(s, DsnClass)])
