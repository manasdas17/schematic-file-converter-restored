class GEDAColor:
    """ Enumeration of gEDA colors """
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


class GEDAParameter(object):
    TYPE = ''

    def __init__(self, name, datatype=int, default=None):
        self._name = name
        self.datatype = datatype
        self.default = default

    @property
    def name(self):
        if self.TYPE:
            return "%s_%s" % (self.TYPE, self._name)
        return self._name


class GEDAStyleParameter(GEDAParameter):
    """ Style parameter """
    TYPE = 'style'


class GEDAExtraParameter(GEDAParameter):
    """ Extra parameter """
    TYPE = 'extra'


class GEDACommand(object):
    """ Command """
    TYPE = None
    PARAMETERS = ()
    EXTRA_PARAMETERS = ()

    def parameters(self):
        return self.PARAMETERS + self.EXTRA_PARAMETERS

    def get_style_keywords(self):
        style_type = GEDAStyleParameter.TYPE
        return [p.name for p in self.PARAMETERS
                        if p.name.startswith(style_type)]

    def update_default_kwargs(self, **kwargs):
        default_kwargs = {}
        for parameter in self.parameters():
            default_kwargs[parameter.name] = parameter.default
        default_kwargs.update(kwargs)
        return default_kwargs

    def generate_command(self, **kwargs):
        kwargs = self.update_default_kwargs(**kwargs)
        command = [self.TYPE]
        for parameter in self.PARAMETERS:
            command.append("%%(%s)s" % parameter.name)
        return [" ".join(command) % kwargs]


class GEDALineCommand(GEDACommand):
    """ Line command """
    TYPE = 'L'
    PARAMETERS = (
        GEDAParameter('x1'),
        GEDAParameter('y1'),
        GEDAParameter('x2'),
        GEDAParameter('y2'),
        GEDAStyleParameter('color', default=GEDAColor.GRAPHIC_COLOR),
        GEDAStyleParameter('width', default=10),
        GEDAStyleParameter('capstyle', default=0),
        GEDAStyleParameter('dashstyle', default=0),
        GEDAStyleParameter('dashlength', default=-1),
        GEDAStyleParameter('dashspace', default=-1),
    )


class GEDABoxCommand(GEDACommand):
    """ Box command """
    TYPE = "B"
    PARAMETERS = (
        GEDAParameter('x'),
        GEDAParameter('y'),
        GEDAParameter('width'),
        GEDAParameter('height'),
        GEDAStyleParameter('color', default=GEDAColor.GRAPHIC_COLOR),
        GEDAStyleParameter('width', default=10),
        GEDAStyleParameter('capstyle', default=0),
        GEDAStyleParameter('dashstyle', default=0),
        GEDAStyleParameter('dashlength', default=-1),
        GEDAStyleParameter('dashspace', default=-1),
        GEDAStyleParameter('filltype', default=0),
        GEDAStyleParameter('fillwidth', default=-1),
        GEDAStyleParameter('angle1', default=-1),
        GEDAStyleParameter('pitch1', default=-1),
        GEDAStyleParameter('angle2', default=-1),
        GEDAStyleParameter('pitch2', default=-1),
    )


class GEDACircleCommand(GEDACommand):
    """ Circle command """
    TYPE = 'V'
    PARAMETERS = (
        GEDAParameter('x'),
        GEDAParameter('y'),
        GEDAParameter('radius'),
        GEDAStyleParameter('color', default=GEDAColor.GRAPHIC_COLOR),
        GEDAStyleParameter('width', default=10),
        GEDAStyleParameter('capstyle', default=0),
        GEDAStyleParameter('dashstyle', default=0),
        GEDAStyleParameter('dashlength', default=-1),
        GEDAStyleParameter('dashspace', default=-1),
        GEDAStyleParameter('filltype', default=0),
        GEDAStyleParameter('fillwidth', default=-1),
        GEDAStyleParameter('angle1', default=-1),
        GEDAStyleParameter('pitch1', default=-1),
        GEDAStyleParameter('angle2', default=-1),
        GEDAStyleParameter('pitch2', default=-1),
    )


class GEDAArcCommand(GEDACommand):
    """ Arc command """
    TYPE = 'A'
    PARAMETERS = (
        GEDAParameter('x'),
        GEDAParameter('y'),
        GEDAParameter('radius'),
        GEDAParameter('startangle'),
        GEDAParameter('sweepangle'),
        GEDAStyleParameter('color', default=GEDAColor.GRAPHIC_COLOR),
        GEDAStyleParameter('width', default=10),
        GEDAStyleParameter('capstyle', default=0),
        GEDAStyleParameter('dashstyle', default=0),
        GEDAStyleParameter('dashlength', default=-1),
        GEDAStyleParameter('dashspace', default=-1),
    )


class GEDATextCommand(GEDACommand):
    """ Text command """
    TYPE = 'T'
    PARAMETERS = (
        GEDAParameter('x'),
        GEDAParameter('y'),
        GEDAStyleParameter('color', default=GEDAColor.TEXT_COLOR),
        GEDAStyleParameter('size', default=10),
        GEDAParameter('visibility', default=1),
        GEDAParameter('show_name_value', default=1),
        GEDAParameter('angle', default=0),
        GEDAParameter('alignment', default=0),
        GEDAParameter('num_lines', default=1),
    )


class GEDASegmentCommand(GEDACommand):
    """ Segment command """
    TYPE = 'N'
    PARAMETERS = (
        GEDAParameter('x1'),
        GEDAParameter('y1'),
        GEDAParameter('x2'),
        GEDAParameter('y2'),
        GEDAStyleParameter('color', default=GEDAColor.NET_COLOR),
    )


class GEDAPinCommand(GEDACommand):
    """ Pin command """
    TYPE = 'P'
    PARAMETERS = (
        GEDAParameter('x1'),
        GEDAParameter('y1'),
        GEDAParameter('x2'),
        GEDAParameter('y2'),
        GEDAStyleParameter('color', default=GEDAColor.PIN_COLOR),
        # pin type is always 0
        GEDAStyleParameter('pintype', default=0),
        # first point is active/connected pin
        GEDAParameter('whichend', default=0),
    )


class GEDAComponentCommand(GEDACommand):
    """ Component command """
    TYPE = 'C'
    PARAMETERS = (
        GEDAParameter('x'),
        GEDAParameter('y'),
        GEDAParameter('selectable', default=0),
        GEDAParameter('angle'),
        GEDAParameter('mirror'),
        GEDAParameter('basename', datatype=str),
    )


class GEDAPathCommand(GEDACommand):
    """ Path command """
    TYPE = "H"
    PARAMETERS = (
        GEDAStyleParameter('color', default=GEDAColor.GRAPHIC_COLOR),
        GEDAStyleParameter('width', default=10),
        GEDAStyleParameter('capstyle', default=0),
        GEDAStyleParameter('dashstyle', default=0),
        GEDAStyleParameter('dashlength', default=-1),
        GEDAStyleParameter('dashspace', default=-1),
        GEDAStyleParameter('filltype', default=0),
        GEDAStyleParameter('fillwidth', default=-1),
        GEDAStyleParameter('angle1', default=-1),
        GEDAStyleParameter('pitch1', default=-1),
        GEDAStyleParameter('angle2', default=-1),
        GEDAStyleParameter('pitch2', default=-1),
        GEDAParameter('num_lines'),
    )
    EXTRA_PARAMERTERS = (
        GEDAExtraParameter('id'),
    )


class GEDAVersionCommand(GEDACommand):
    """ Version command """
    TYPE = 'v'
    PARAMETERS = (
        GEDAParameter('version'),
        GEDAParameter('fileformat_version'),
    )


class GEDABusCommand(GEDACommand):
    """ Bus command """
    TYPE = 'U'
    PARAMETERS = (
        GEDAParameter('x1'),
        GEDAParameter('y1'),
        GEDAParameter('x2'),
        GEDAParameter('y2'),
        GEDAStyleParameter('color', default=GEDAColor.BUS_COLOR),
        GEDAParameter('ripperdir', default=0),
    )


class GEDAPictureCommand(GEDACommand):
    """ Picture command """
    TYPE = 'G'
    PARAMETERS = ()


class GEDAEmbeddedEnvironmentCommand(GEDACommand):
    """ Embeded command """
    TYPE = '['
    PARAMETERS = ()


class GEDAAttributeEnvironmentCommand(GEDACommand):
    """ Attribute environment command """
    TYPE = '{'
    PARAMETERS = ()


class GEDACommand(GEDACommand):
    """ Command """
    TYPE = 'U'
    PARAMETERS = ()
