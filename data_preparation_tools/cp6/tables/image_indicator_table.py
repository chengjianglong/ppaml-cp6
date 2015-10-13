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
from cp6.utilities.image_indicator import ImageIndicator

class ImageIndicatorTable:

    def __init__( self ):
        self.image_indicators = dict()

    def write_to_file( self, fn, id_list = None ):
        if not id_list:
            sys.stderr.write( 'Debug: %s passed null id_list, sorting %d keys' % (fn, len(self.image_indicators.keys)))
            id_list = sorted( self.image_indicators.keys() )
        else:
            sys.stderr.write( 'Debug: %s passed %d id_list' % (fn, len(id_list)))
        with open( fn, 'w' ) as f:
            for mir_id in sorted( id_list ):
                imgind = self.image_indicators[ mir_id ]
                group_str = ','.join(map(str, sorted( imgind.group_list.keys() ))) if (len(imgind.group_list)) else 'none'
                word_str = ','.join(map(str, sorted( imgind.word_list.keys() ))) if (len(imgind.word_list)) else 'none'
                f.write( '%d %s %s\n' % ( mir_id, group_str, word_str ))

    @staticmethod
    def read_from_file( fn, id_list = None ):
        #
        # note that this just reads the text from the file and recreates the
        # data structure. It does not enforce consistency with any instance
        # of an Image Indicator Lookup Table.
        #
        t = ImageIndicatorTable()
        c_line = 0
        with open( fn, 'r' ) as f:
            while 1:
                raw_line = f.readline()
                if not raw_line:
                    break
                c_line += 1
                fields = raw_line.strip().split()
                if len(fields) != 3:
                    raise AssertionError( '%s line %d: expected 3 fields, got %d' % \
                                        (fn, c_line, len(fields)))
                id = int( fields[0] )
                if (id_list is not None) and (id not in id_list):
                    next
                ii = ImageIndicator( id )
                if fields[1] != 'none':
                    ii.group_list = { x: True for x in fields[1].split(',') }
                if fields[2] != 'none':
                    ii.word_list = { x: True for x in fields[2].split(',') }

                t.image_indicators[ id ] = ii
        return t