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
import codecs
import copy

from cp6.utilities.util import Util
from cp6.utilities.exifdata import EXIFData
from cp6.utilities.image_table_entry import ImageTableEntry

class ImageTable:

    def __init__( self ):
        self.entries = dict()

    def add_entry( self, e ):
        if e.mir_id in self.entries:
            raise AssertionError( 'Double-add of %d in image table' % e.mir_id )
        self.entries[ e.mir_id ] = e

    def write_to_file( self, fn, filter_package = None ):
        write_label_vector_as_testing = False
        if filter_package is not None:
            write_label_vector_as_testing = filter_package[1]

        sys.stderr.write('Info: writing image table %s; label vectors as testing? %d\n' % (fn, write_label_vector_as_testing ))
        (c_total, c_written, c_neg2_but_not_testing) = (0,0,0)
        with codecs.open( fn, 'w', encoding='UTF-8' ) as f:
            for mir_id in sorted( self.entries ):
                e = self.entries[ mir_id ]
                c_total += 1
                write_this_edge = (filter_package is None) or \
                                  (e.mir_id in filter_package[0])
                if not write_this_edge:
                    continue

                c_written += 1
                f.write( '%d ' % e.mir_id ) # 0
                f.write( '%d ' % e.flickr_id ) # 1
                f.write( '%s ' % Util.qstr( e.flickr_owner )) # 2
                f.write( '%s ' % Util.qstr( e.flickr_title )) # 3
                f.write( '%s ' % Util.qstr( e.flickr_descr )) # 4

                f.write( '%s ' % e.exif_data.to_table_str() ) # 5,6,7

                if e.flickr_locality: # 8
                    f.write( '%s ' % Util.qstr( e.flickr_locality ))
                else:
                    f.write( 'none ' )

                v = copy.copy( e.label_vector )
                if write_label_vector_as_testing:
                    # set all non -1 values to -2
                    for i in range(0, len(v)):
                        if v[i] != -1:
                            v[i] = -2
                else:
                    # sanity check: if this is NOT testing, there should be no -2 values
                    if v.count(-2):
                        c_neg2_but_not_testing += 1

                f.write( '%s\n' % ','.join(map(str, v))) # 9
        if c_neg2_but_not_testing != 0:
            sys.stderr.write('WARNING\nWARNING\nWARNING: %s not written as testing, but contained %d (of %d) images with -2 in the label vector\nWARNING\WARNING\n'\
                              % (fn, c_neg2_but_not_testing, c_written))
        return (c_total, c_written)

    @staticmethod
    def read_from_file( fn, id_dict_to_keep=None ):
        c = 0
        t = ImageTable()
        with codecs.open( fn, 'r', encoding='utf-8' ) as f:
            while 1:
                raw_line = f.readline()
                if not raw_line:
                    break
                c += 1
                fields = Util.qstr_split( raw_line.strip() )
                if len(fields) != 10:
                    raise AssertionError( 'Image table %s:%d: found %d fields, expecting 10' % (fn, c, len(fields)))
                id = int( fields[0] )
                if not ( (id_dict_to_keep is None) or (id in id_dict_to_keep) ):
                    continue
                e = ImageTableEntry()
                e.mir_id = int( id )
                e.flickr_id = int( fields[1] )
                e.flickr_owner = fields[2] if (fields[2] != 'none') else None
                e.flickr_title = fields[3] if (fields[3] != 'none') else None
                e.flickr_descr = fields[4] if (fields[4] != 'none') else None
                if (fields[5] == 'none') and \
                   (fields[6] == 'none') and \
                   (fields[7] == 'U'):
                    e.exif_data = EXIFData( e.mir_id, False, 'none', 'none', 'U' )
                else:
                    e.exif_data = EXIFData( e.mir_id, True, fields[5], fields[6], fields[7])
                e.flickr_locality = fields[8] if fields[8] != 'none' else None
                e.label_vector = map(int, fields[9].split(','))
                t.add_entry( e )
        return t


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: $0 input-img-table output-img-table\n')
        sys.exit(0)
    t = ImageTable.read_from_file( sys.argv[1] )
    sys.stderr.write('Info: image table has %d entries\n' % len(t.entries))
    t.write_to_file( sys.argv[2] )
