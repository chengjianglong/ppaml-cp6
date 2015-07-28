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

from cp6.utilities.util import Util
from cp6.utilities.exifdata import EXIFData

class ImageTableEntry:

    def __init__( self ):
        self.mir_id = None
        self.flickr_id = None
        self.flickr_owner = None
        self.flickr_title = None
        self.flickr_descr = None
        self.exif_data = None
        self.flickr_locality = None
        self.label_vector = None

class ImageTable:

    def __init__( self ):
        self.entries = dict()

    def add_entry( self, e ):
        if e.mir_id in self.entries:
            raise AssertionError( 'Double-add of %d in image table' % e.mir_id )
        self.entries[ e.mir_id ] = e

    def write_to_file( self, fn ):
        with open( fn, 'w' ) as f:
            for mir_id in sorted( self.entries ):
                e = self.entries[ mir_id ]
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

                f.write( '%s\n' % ','.join(map(str, e.label_vector))) # 9

