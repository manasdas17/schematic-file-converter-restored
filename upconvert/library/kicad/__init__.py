""" The upverter part library for KiCAD """

from os.path import dirname, exists, join

PARTS_DIR = join(dirname(__file__), 'parts')

ALL_COMPONENTS = {} # { libname: { KiCADLibrary } }


def lookup_part(name, libs):
    """
    Given the name of a KiCAD part, attempt to locate a part in the
    first library which matches it. Return the Component if
    successful, None otherwise.
    """
    for lib in libs:
        if lib not in ALL_COMPONENTS:
            ALL_COMPONENTS[lib] = read_library(lib)

        if name in ALL_COMPONENTS[lib]:
            return ALL_COMPONENTS[lib][name]


def read_library(lib):
    """
    Read the library with the given name if it exists and return a
    KiCADLibrary object. Otherwise return an empty dict.
    """

    libfile = join(PARTS_DIR, lib + '.lib')

    if exists(libfile):
        from upconvert.parser.kicad import KiCADLibrary
        library = KiCADLibrary()
        library.parse(libfile)
        return library.name2cpt
    else:
        return {}
