import os
import re
import subprocess

# upconvert - A universal hardware design file format converter using
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

def build_sdist(target, source, env):
    args = ['python', 'setup.py', 'sdist']
    return subprocess.call(args)
bld_sdist = Builder(action=build_sdist)

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
            'upconvert/core', 'upconvert/library',
            'upconvert/parser', 'upconvert/writer']
    if 'UPCONVERT_TEST_STOP' in os.environ:
        args.append('--stop')
    return subprocess.call(args)
bld_test = Builder(action=build_test)

def build_coverage(target, source, env):
    args = ['nosetests', '--with-coverage', '--all-modules',
            'upconvert/core', 'upconvert/library',
            'upconvert/parser', 'upconvert/writer']
    return subprocess.call(args)
bld_coverage = Builder(action=build_coverage)

def build_regression(target, source, env):
    args = ['python', 'test/test.py']
    #args.extend([str(t) for t in source])
    return subprocess.call(args)
bld_regression = Builder(action=build_regression)


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

test_re = re.compile(r'.*/(t|test)/.*_t\.py$')
def filter_test(arg, top, names):
    for name in names:
        if test_re.match(os.path.join(top, name)):
            arg.append(File(os.path.join(top, name)))
    filter_non_python(top, names)

init_re = re.compile(r'.*/.*__init__\.py$')
gen_re = re.compile(r'.*_g\.py$')
def filter_lint(arg, top, names):
    for name in names:
        if source_re.match(os.path.join(top, name)) and \
           not test_re.match(os.path.join(top, name)) and \
           not init_re.match(os.path.join(top, name)) and \
           not gen_re.match(os.path.join(top, name)):
            arg.append(File(os.path.join(top, name)))
    filter_non_python(top, names)

sch_re = re.compile(r'.*\.sch$')
def filter_sch(arg, top, names):
    for name in names:
        if sch_re.match(os.path.join(top, name)):
            arg.append(File(os.path.join(top, name)))

fz_re = re.compile(r'.*\.fz$')
def filter_fz(arg, top, names):
    for name in names:
        if fz_re.match(os.path.join(top, name)):
            arg.append(File(os.path.join(top, name)))

fzz_re = re.compile(r'.*\.fzz$')
def filter_fzz(arg, top, names):
    for name in names:
        if fzz_re.match(os.path.join(top, name)):
            arg.append(File(os.path.join(top, name)))

ger_re = re.compile(r'.*\.ger$')
def filter_ger(arg, top, names):
    for name in names:
        if ger_re.match(os.path.join(top, name)):
            arg.append(File(os.path.join(top, name)))

upv_re = re.compile(r'.*\.upv$')
def filter_upv(arg, top, names):
    for name in names:
        if upv_re.match(os.path.join(top, name)):
            arg.append(File(os.path.join(top, name)))


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

linter_source = []
os.path.walk('./upconvert', filter_lint, linter_source)


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


eagle_sch_files = []
os.path.walk('./test/eagle', filter_sch, eagle_sch_files)

fritzing_fz_files = []
os.path.walk('./test/fritzing', filter_fz, fritzing_fz_files)

fritzing_fzz_files = []
os.path.walk('./test/fritzing', filter_fzz, fritzing_fzz_files)

geda_sch_files = []
os.path.walk('./test/geda', filter_sch, geda_sch_files)

gerber_ger_files = []
os.path.walk('./test/gerber', filter_ger, gerber_ger_files)

kicad_sch_files = []
os.path.walk('./test/kicad', filter_sch, kicad_sch_files)

upverter_upv_files = []
os.path.walk('./test/openjson', filter_upv, upverter_upv_files)

all_test_files = []
all_test_files.extend([str(t) for t in eagle_sch_files])
all_test_files.extend([str(t) for t in fritzing_fz_files])
all_test_files.extend([str(t) for t in fritzing_fzz_files])
all_test_files.extend([str(t) for t in geda_sch_files])
all_test_files.extend([str(t) for t in gerber_ger_files])
all_test_files.extend([str(t) for t in kicad_sch_files])
all_test_files.extend([str(t) for t in upverter_upv_files])

# Find the version number in the setup.py file
version = 'unknown'
version_re = re.compile(r"version='\([^']*\)'")
with open('setup.py', 'r') as setup_fh:
    for line in setup_fh:
        m = version_re.match(line)
        if m:
            version = m.group(1)


###################
# Environment
###################

env = Environment(BUILDERS = {'test': bld_test,
                              'lint': bld_lint,
                              'check': bld_check,
                              'pyflakes': bld_pyflakes,
                              'coverage': bld_coverage,
                              'regression': bld_regression,
                              'sdist': bld_sdist,
                             },
                  ENV = {'PATH' : os.environ['PATH']},
                  tools = ['default'])

lint = env.lint(['fake_target_to_force_lint'], linter_source)
check = env.check(['fake_target_to_force_check'], all_source)
pyflakes = env.pyflakes(['fake_target_to_force_pyflakes'], all_source)
test = env.test(['fake_target_to_force_test'], all_tests)
coverage = env.coverage(['fake_target_to_force_coverage'], all_tests)
regression = env.coverage(['fake_target_to_force_regression'], [])
sdist = env.sdist(['dist/python-upconvert-' + version + '.tar.gz'], all_source)

env.Alias('lint', lint)
env.Alias('check', check)
env.Alias('pyflakes', pyflakes)
env.Alias('test', test)
env.Alias('coverage', coverage)
env.Alias('regression', regression)
env.Alias('sdist', sdist)
env.Alias('all', '.')
