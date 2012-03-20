import os
import re
import subprocess
import tarfile

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


# Requirements
# * Python
# * PyLint
# * PyChecker
# * PyFlakes
# * Nose


###################
# Builders
###################

def build_lint(target, source, env):
    args = ['pylint', '--rcfile=.pylintrc']
    args.extend([str(py) for py in source])
    return subprocess.call(args)
bld_lint = Builder(action=build_lint)

def build_check(target, source, env):
    args = ['pychecker', '--limit=100']
    args.extend([str(py) for py in source])
    return subprocess.call(args)
bld_check = Builder(action=build_check)

def build_pyflakes(target, source, env):
    args = ['pyflakes']
    args.extend([str(py) for py in source])
    return subprocess.call(args)
bld_pyflakes = Builder(action=build_pyflakes)

def build_test(target, source, env):
    args = ['nosetests', '--all-modules',
            'upconvert/core', 'upconvert/library', 'upconvert/parser', 'upconvert/writer']
    return subprocess.call(args)
bld_test = Builder(action=build_test)

def build_coverage(target, source, env):
    args = ['nosetests', '--with-coverage', '--all-modules',
            'upconvert/core', 'upconvert/library', 'upconvert/parser', 'upconvert/writer']
    return subprocess.call(args)
bld_coverage = Builder(action=build_coverage)


###################
# Filters
###################

def filter_non_python(top, names):
    for name in names[:]:
        path = os.path.join(top, name)
        if os.path.isdir(path):
            initpath = os.path.join(path, '__init__.py')
            if not os.path.exists(initpath):
                names.remove(name)

source_re = re.compile(r'.*\.py$')
def filter_source(arg, top, names):
    for name in names:
        if source_re.match(os.path.join(top, name)):
            arg.append(File(os.path.join(top, name)))
    filter_non_python(top, names)

test_re = re.compile(r'.*/(t|test)/.*_t\.py$')
def filter_test(arg, top, names):
    for name in names:
        if test_re.match(os.path.join(top, name)):
            arg.append(File(os.path.join(top, name)))
    filter_non_python(top, names)


###################
# File Lists
###################

core_source = []
os.path.walk('./upconvert/core', filter_source, core_source)

parser_source = []
os.path.walk('./upconvert/parser', filter_source, parser_source)

library_source = []
os.path.walk('./upconvert/library', filter_source, library_source)

writer_source = []
os.path.walk('./upconvert/writer', filter_source, writer_source)

all_source = []
all_source.extend([str(py) for py in core_source])
all_source.extend([str(py) for py in parser_source])
all_source.extend([str(py) for py in library_source])
all_source.extend([str(py) for py in writer_source])

core_tests = []
os.path.walk('./upconvert/core', filter_test, core_tests)

parser_tests = []
os.path.walk('./upconvert/parser', filter_test, parser_tests)

library_tests = []
os.path.walk('./upconvert/library', filter_test, library_tests)

writer_tests = []
os.path.walk('./upconvert/writer', filter_test, writer_tests)

all_tests = []
all_tests.extend([str(py) for py in core_tests])
all_tests.extend([str(py) for py in parser_tests])
all_tests.extend([str(py) for py in library_tests])
all_tests.extend([str(py) for py in writer_tests])


###################
# Environment
###################

env = Environment(BUILDERS = {'test': bld_test,
                              'lint': bld_lint,
                              'check': bld_check,
                              'pyflakes': bld_pyflakes,
                              'coverage': bld_coverage,
                             },
                  ENV = {'PATH' : os.environ['PATH']},
                  tools = ['default'])

lint = env.lint(['fake_target_to_force_lint'], all_source)
check = env.check(['fake_target_to_force_check'], all_source)
pyflakes = env.pyflakes(['fake_target_to_force_pyflakes'], all_source)
test = env.test(['fake_target_to_force_test'], all_tests)
coverage = env.coverage(['fake_target_to_force_coverage'], all_tests)

env.Alias('lint', lint)
env.Alias('check', check)
env.Alias('pyflakes', pyflakes)
env.Alias('test', test)
env.Alias('coverage', coverage)
env.Alias('all', '.')
