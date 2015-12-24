#!/usr/bin/env python
#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

from common import write_fake_link

_python_ = TestSCons._python_

test = TestSCons.TestSCons()
_exe = TestSCons._exe

write_fake_link(test)

test.write('myfortran.py', r"""
import getopt
import sys
comment = '#' + sys.argv[1]
opts, args = getopt.getopt(sys.argv[2:], 'co:xy')
optstring = ''
for opt, arg in opts:
    if opt == '-o': out = arg
    else: optstring = optstring + ' ' + opt
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
outfile.write(optstring + "\n")
for l in infile.readlines():
    if l[:len(comment)] != comment:
        outfile.write(l)
sys.exit(0)
""")



test.write('SConstruct', """
env = Environment(LINK = r'%(_python_)s mylink.py',
                  LINKFLAGS = [],
                  F08 = r'%(_python_)s myfortran.py g08',
                  F08FLAGS = '-x',
                  FORTRAN = r'%(_python_)s myfortran.py fortran',
                  FORTRANFLAGS = '-y')
env.Program(target = 'test01', source = 'test01.f')
env.Program(target = 'test02', source = 'test02.F')
env.Program(target = 'test03', source = 'test03.for')
env.Program(target = 'test04', source = 'test04.FOR')
env.Program(target = 'test05', source = 'test05.ftn')
env.Program(target = 'test06', source = 'test06.FTN')
env.Program(target = 'test07', source = 'test07.fpp')
env.Program(target = 'test08', source = 'test08.FPP')
env.Program(target = 'test09', source = 'test09.f08')
env.Program(target = 'test10', source = 'test10.F08')
""" % locals())

test.write('test01.f',   "This is a .f file.\n#link\n#fortran\n")
test.write('test02.F',   "This is a .F file.\n#link\n#fortran\n")
test.write('test03.for', "This is a .for file.\n#link\n#fortran\n")
test.write('test04.FOR', "This is a .FOR file.\n#link\n#fortran\n")
test.write('test05.ftn', "This is a .ftn file.\n#link\n#fortran\n")
test.write('test06.FTN', "This is a .FTN file.\n#link\n#fortran\n")
test.write('test07.fpp', "This is a .fpp file.\n#link\n#fortran\n")
test.write('test08.FPP', "This is a .FPP file.\n#link\n#fortran\n")
test.write('test09.f08', "This is a .f08 file.\n#link\n#g08\n")
test.write('test10.F08', "This is a .F08 file.\n#link\n#g08\n")

test.run(arguments = '.', stderr = None)

test.must_match('test01' + _exe, " -c -y\nThis is a .f file.\n")
test.must_match('test02' + _exe, " -c -y\nThis is a .F file.\n")
test.must_match('test03' + _exe, " -c -y\nThis is a .for file.\n")
test.must_match('test04' + _exe, " -c -y\nThis is a .FOR file.\n")
test.must_match('test05' + _exe, " -c -y\nThis is a .ftn file.\n")
test.must_match('test06' + _exe, " -c -y\nThis is a .FTN file.\n")
test.must_match('test07' + _exe, " -c -y\nThis is a .fpp file.\n")
test.must_match('test08' + _exe, " -c -y\nThis is a .FPP file.\n")
test.must_match('test09' + _exe, " -c -x\nThis is a .f08 file.\n")
test.must_match('test10' + _exe, " -c -x\nThis is a .F08 file.\n")


fc = 'f08'
g08 = test.detect_tool(fc)


if g08:

    test.write("wrapper.py",
"""import os
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(" ".join(sys.argv[1:]))
""" % test.workpath('wrapper.out').replace('\\', '\\\\'))

    test.write('SConstruct', """
foo = Environment(F08 = '%(fc)s')
f08 = foo.Dictionary('F08')
bar = foo.Clone(F08 = r'%(_python_)s wrapper.py ' + f08, F08FLAGS = '-Ix')
foo.Program(target = 'foo', source = 'foo.f08')
bar.Program(target = 'bar', source = 'bar.f08')
""" % locals())

    test.write('foo.f08', r"""
      PROGRAM FOO
      PRINT *,'foo.f08'
      ENDPROGRAM FOO
""")

    test.write('bar.f08', r"""
      PROGRAM BAR
      PRINT *,'bar.f08'
      ENDPROGRAM FOO
""")


    test.run(arguments = 'foo' + _exe, stderr = None)

    test.run(program = test.workpath('foo'), stdout =  " foo.f08\n")

    test.must_not_exist('wrapper.out')

    import sys
    if sys.platform[:5] == 'sunos':
        test.run(arguments = 'bar' + _exe, stderr = None)
    else:
        test.run(arguments = 'bar' + _exe)

    test.run(program = test.workpath('bar'), stdout =  " bar.f08\n")

    test.must_match('wrapper.out', "wrapper.py\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
