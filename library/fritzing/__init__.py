""" The upverter part library for Fritzing """

from os import listdir
from os.path import basename, dirname, exists, join

VERSIONS_DIR = join(dirname(__file__), 'versions')

all_versions = []


def lookup_part(path, fritzing_version):
    """ Given a path from a fritzing file and a fritzing
    version, attempt to locate a part in the library which
    matches the path. """

    if not all_versions:
        all_versions.extend((chunk_version(v), v) for v in listdir(VERSIONS_DIR))
        all_versions.sort()

    cur_version = chunk_version(fritzing_version)

    candidates = [name for (v, name) in all_versions if v >= cur_version]

    if not candidates:
        candidates = all_versions[-1][1]

    rel_path = part_relpath(path)

    for name in candidates:
        lib_path = join(VERSIONS_DIR, name, rel_path)
        if exists(lib_path):
            return lib_path

    return None


def chunk_version(fritzing_version):
    """ Turn a fritzing version string into a tuple """

    return tuple(int(part) if part.isdigit() else part
                 for part in fritzing_version.split('.'))


def part_relpath(path):
    """ Given a Fritzing path, return the relative path
    from the parts directory """

    path_parts = []

    while True:
        path_parts.insert(0, basename(path))
        if path_parts[0] == 'parts':
            break

        new_path = dirname(path)
        if new_path == path:
            break

        path = new_path

    return join(*path_parts)
