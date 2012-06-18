from inspect import isclass

def pop_type(args, t):
    ''' Reads argument of type from args '''
    if len(args) > 0 and isinstance(args[0], t):
        return args.pop(0)
    return None

def pop_types(args, t):
    ''' Reads list of types from args '''
    lst = []
    while True:
        arg = pop_type(args, t)
        if arg is None: break
        lst.append(arg)
    return lst

def pop_string(args):
    return pop_type(args, basestring)

def pop_vertex(args):
    x, y = pop_string(args), pop_string(args)
    if x is None or y is None:
        return None
    return (float(x), float(y))

def pop_vertexes(args):
    lst = []
    while True:
        arg = pop_vertex(args)
        if arg is None: break
        lst.append(arg)
    return lst

class DsnClass:
    function = None
    def __repr__(self):
        return '\n%s%s\n' % (self.__class__.__name__, repr(self.__dict__))

class ShapeBase(DsnClass):
    pass

class Shape(DsnClass):
    """ shape """
    function = 'shape'

    def __init__(self, args):
        assert len(args) >= 0
        self.shape = pop_type(args, ShapeBase)
        #assert len(args) == 0

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
        self.rectangle = pop_type(args, Rectangle)

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

class Circle(ShapeBase):
    """ circle_descriptor """
    function = 'circle'

    def __init__(self, args):
        assert len(args) in (2, 4)
        self.layer_id = args[0]
        self.diameter = float(args[1])
        if len(args) == 4:
            self.vertex = (float(args[2]), float(args[3]))
        else:
            self.vertex = (0, 0)

class Circuit(DsnClass):
    """ circuit_descriptor """
    
    def __init__(self, args):
        self.circuit = args
##############################################################


class Placement(DsnClass):
    """ placement_descriptor """    
    function = 'placement'

    def __init__(self, args):
        assert len(args) >= 1
        self.component = pop_types(args, Component)
        #FIXME
        #assert len(args) == 0

class Component(DsnClass):
    """ component_instance """
    function = 'component'

    def __init__(self, args):
        assert len(args) >= 2
        self.image_id = pop_string(args)
        self.place = pop_types(args, Place)
        assert len(args) == 0

class Place(DsnClass):
    """ placement_reference """
    function = 'place'

    def __init__(self, args):
        assert len(args) >= 1
        self.component_id = pop_string(args)
        self.vertex = pop_vertex(args)
        self.side = pop_string(args)
        self.rotation = int(pop_string(args))
        self.part_number = pop_type(args, PartNumber)
        #  FIXME
        #assert len(args) == 0

class PartNumber(DsnClass):
    """ part_number """
    function = 'PN'
    def __init__(self, args):
        assert len(args) == 1
        self.part_number = pop_string(args)
        assert len(args) == 0

class Net(DsnClass):
    """ net_descriptor """
    function = 'net'

    def __init__(self, args):
        assert len(args) >= 1
        self.net_id = pop_string(args)
        self.pins = pop_types(args, Pins)
#assert len(args) == 0

class Network(DsnClass):
    """ network_descriptor """
    function = 'network'

    def __init__(self, args):
        assert len(args) > 0
        self.net = pop_types(args, Net)
        #assert len(args) == 0

class Pins(DsnClass):
    """ pins """
    function = 'pins'

    def __init__(self, args):
        assert len(args) >= 0
        self.pin_reference = args[:]

class Library(DsnClass):
    """ library_descriptor """
    function = 'library'

    def __init__(self, args):
        self.image = pop_types(args, Image)
        self.padstack = pop_types(args, Padstack)
        assert len(args) == 0


class Padstack(DsnClass):
    """ padstack_descriptor """
    function = 'padstack'
    
    def __init__(self, args):
        assert len(args) >= 1
        self.padstack_id = pop_string(args)
        self.shape = pop_types(args, Shape)
        self.attach = pop_type(args, Attach)
#assert len(args) == 0

class Pin(DsnClass):
    """ pin """
    function = 'pin'

    def __init__(self, args):
        assert len(args) >= 1

        self.padstack_id = pop_string(args)
        self.rotation = pop_type(args, Rotate)
        self.pin_id = pop_string(args)
        self.vertex = pop_vertex(args)
        #self.array = pop_type(args, Array)
        #self.property = pop_type(args, Property)

class Rotate(DsnClass):
    """ rotate """
    function = 'rotate'

    def __init__(self, args):
        assert len(args) == 1
        self.rotation = pop_string(args)
        assert len(args) == 0

class Image(DsnClass):
    """ image_descriptor """
    function = 'image'

    def __init__(self, args):
        assert len(args) >= 1
        self.image_id = pop_string(args)
        self.side = pop_type(args, Side)
        self.outline = pop_types(args, Outline)
        self.pin = pop_types(args, Pin)
        #assert len(args) == 0

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

class Rectangle(ShapeBase):
    """ rectangle_descriptor """
    function = 'rect'

    def __init__(self, args):
        assert len(args) == 5
        self.layer_id = pop_string(args)
        self.vertex1 = pop_vertex(args)
        self.vertex2 = pop_vertex(args)
        assert len(args) == 0

class Path(ShapeBase):
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

class Pcb(DsnClass):
    """ pcb """
    function = 'pcb'

    def __init__(self, args):
        assert len(args) >= 1
        self.pcb_id = pop_string(args)
        #self.placement = pop_type(args, Placement)
        self.structure = [x for x in args if isinstance(x, Structure)][0]
        self.placement = [x for x in args if isinstance(x, Placement)][0]
        self.library = [x for x in args if isinstance(x, Library)][0]

class PCB(Pcb):
    """ pcb """
    function = 'PCB'

class Structure(DsnClass):
    """ structure_descriptor """
    function = 'structure'

    def __init__(self, args):
        self.boundary = [x for x in args if isinstance(x, Boundary)][0]

'''
  (placement
    (place_control (flip_style rotate_first))
'''
##############################################################

all_functions = dict([(s.function, s) for s in globals().values() if isclass(s) and issubclass(s, DsnClass)])
