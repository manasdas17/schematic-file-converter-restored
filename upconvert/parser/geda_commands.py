
class GEDACommand(object):
    TYPE = None
    PARAMETERS = ()

    @classmethod
    def generate_command(cls, **kwargs):
        command = [self.TYPE]
        for parameter in self.PARAMETERS:
            command.append("%%(%s)s" % parameter.name)
        return " ".join(command)


class GEDAParameter(object):
    TYPE = ''

    def __init__(self, name, datatype=int, default=None):
        self._name = name
        self.datatype = datatype
        self.default = default

    @property
    def name(self):
        return self._name


class GEDAStyleParameter(GEDAParameter):
    TYPE = 'style'

    @property
    def name(self):
        return "%s_%s" % (self.TYPE, self._name)


class GEDALineCommand(object):
    TYPE = 'L'
    PARAMETERS = (
        GEDAParameter('x1'),
        GEDAParameter('y1'),
        GEDAParameter('x2'),
        GEDAParameter('y2'),
        GEDAStyleParameter('color'),
        GEDAStyleParameter('width'),
        GEDAStyleParameter('capstyle'),
        GEDAStyleParameter('dashstyle'),
        GEDAStyleParameter('dashlength'),
        GEDAStyleParameter('dashspace'),
    )


class GEDABoxCommand(object):
    TYPE = "B"
    PARAMETERS = (
        GEDAParameter('x'),
        GEDAParameter('y'),
        GEDAParameter('width'),
        GEDAParameter('height'),
        GEDAStyleParameter('color'),
        GEDAStyleParameter('width'),
        GEDAStyleParameter('capstyle'),
        GEDAStyleParameter('dashstyle'),
        GEDAStyleParameter('dashlength'),
        GEDAStyleParameter('dashspace'),
        GEDAStyleParameter('filltype'),
        GEDAStyleParameter('fillwidth'),
        GEDAStyleParameter('angle1'),
        GEDAStyleParameter('pitch1'),
        GEDAStyleParameter('angle2'),
        GEDAStyleParameter('pitch2'),
    )


class GEDACircleCommand(object):
    TYPE = 'V'
    PARAMETERS = (
        GEDAParameter('x'),
        GEDAParameter('y'),
        GEDAParameter('radius'),
        GEDAStyleParameter('color'),
        GEDAStyleParameter('width'),
        GEDAStyleParameter('capstyle'),
        GEDAStyleParameter('dashstyle'),
        GEDAStyleParameter('dashlength'),
        GEDAStyleParameter('dashspace'),
        GEDAStyleParameter('filltype'),
        GEDAStyleParameter('fillwidth'),
        GEDAStyleParameter('angle1'),
        GEDAStyleParameter('pitch1'),
        GEDAStyleParameter('angle2'),
        GEDAStyleParameter('pitch2'),
    )


class GEDAArcCommand(object):
    TYPE = 'A'
    PARAMETERS = (
        GEDAParameter('x'),
        GEDAParameter('y'),
        GEDAParameter('radius'),
        GEDAParameter('startangle'),
        GEDAParameter('sweepangle'),
        GEDAStyleParameter('color'),
        GEDAStyleParameter('width'),
        GEDAStyleParameter('capstyle'),
        GEDAStyleParameter('dashstyle'),
        GEDAStyleParameter('dashlength'),
        GEDAStyleParameter('dashspace'),
    )


class GEDATextCommand(object):
    TYPE = 'T'
    PARAMETERS = (
        GEDAParameter('x'),
        GEDAParameter('y'),
        GEDAStyleParameter('color'),
        GEDAStyleParameter('size'),
        GEDAParameter('visibility'),
        GEDAParameter('show_name_value'),
        GEDAParameter('angle'),
        GEDAParameter('alignment'),
        GEDAParameter('num_lines', default=1),
    )


class GEDASegmentCommand(object):
    TYPE = 'N'
    PARAMETERS = (
        GEDAParameter('x1'),
        GEDAParameter('y1'),
        GEDAParameter('x2'),
        GEDAParameter('y2'),
        GEDAStyleParameter('color'),
    )


class GEDAPinCommand(object):
    TYPE = 'P'
    PARAMETERS = (
        GEDAParameter('x1'),
        GEDAParameter('y1'),
        GEDAParameter('x2'),
        GEDAParameter('y2'),
        GEDAStyleParameter('color'),
        GEDAStyleParameter('pintype'),
        GEDAParameter('whichend'),
    )


class GEDAComponentCommand(object):
    TYPE = 'C'
    PARAMETERS = (
        GEDAParameter('x'),
        GEDAParameter('y'),
        GEDAParameter('selectable'),
        GEDAParameter('angle'),
        GEDAParameter('mirror'),
        GEDAParameter('basename', datatype=str),
    )


class GEDAPathCommand(object):
    TYPE = "H"
    PARAMETERS = (
        GEDAStyleParameter('color'),
        GEDAStyleParameter('width'),
        GEDAStyleParameter('capstyle'),
        GEDAStyleParameter('dashstyle'),
        GEDAStyleParameter('dashlength'),
        GEDAStyleParameter('dashspace'),
        GEDAStyleParameter('filltype'),
        GEDAStyleParameter('fillwidth'),
        GEDAStyleParameter('angle1'),
        GEDAStyleParameter('pitch1'),
        GEDAStyleParameter('angle2'),
        GEDAStyleParameter('pitch2'),
        GEDAParameter('num_lines'),
    )


class GEDAVersionCommand(object):
    TYPE = 'v'
    PARAMETERS = (
            GEDAParameter('version'),
            GEDAParameter('fileformat_version'),
    )


class GEDABusCommand(GEDACommand):
    TYPE = 'U'
    PARAMETERS = (
        GEDAParameter('x1'),
        GEDAParameter('y1'),
        GEDAParameter('x2'),
        GEDAParameter('y2'),
        GEDAStyleParameter('color'),
        GEDAParameter('ripperdir'),
    )


class GEDAPictureCommand(GEDACommand):
    TYPE = 'G'
    PARAMETERS = ()


class GEDAEmbeddedEnvironmentCommand(GEDACommand):
    TYPE = '['
    PARAMETERS = ()


class GEDAAttributeEnvironmentCommand(GEDACommand):
    TYPE = '{'
    PARAMETERS = ()


class GEDACommand(GEDACommand):
    TYPE = 'U'
    PARAMETERS = ()
