# Copyright 2015 Kitware, Inc.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.

#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

#  * Neither name of Kitware, Inc. nor the names of any contributors may be used
#    to endorse or promote products derived from this software without specific
#    prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Part of the DARPA PPAML CP6 toolset; poc: roddy.collins@kitware.com
#

import sys

from cp6.utilities.util import Util

class LabelTable:
    def __init__( self, L2I, I2L ):
        self.label2id = L2I
        self.id2label = I2L
        self.idset = sorted( I2L.keys() )

    def nlabels( self ):
        return len( self.idset )

    def write_to_file( self, fn ):
        with open( fn, 'w' ) as f:
            for index in self.idset:
                f.write( '%d %s\n' % ( index, Util.qstr( self.id2label[index] )))

    @staticmethod
    def set_from_vector( v ):
        L2I = dict()
        I2L = dict()
        for i in range(0, len(v)):
            L2I[ v[i] ] = i
            I2L[ i ] = v[i]
        return LabelTable( L2I, I2L )

    @staticmethod
    def read_from_file( fn ):
        L2I = dict()
        I2L = dict()
        with open( fn, 'r' ) as f:
            while 1:
                raw_line = f.readline()
                if not raw_line:
                    break
                fields = Util.qstr_split( raw_line )
                I2L[ int(fields[0]) ] = fields[1]
                L2I[ fields[1] ] = int(fields[0])
        return LabelTable( L2I, I2L)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: $0 input-label-table output-label-table\n')
        sys.exit(0)
    t = LabelTable.read_from_file( sys.argv[1] )
    sys.stderr.write('Info: label table has %d entries\n' % len(t.idset))
    t.write_to_file( sys.argv[2] )
