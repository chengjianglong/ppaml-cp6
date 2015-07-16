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

##
## Hold the EXIF data from e.g.
## /Users/collinsr/work/ppaml/2015-03-cp6-proposal/mir-merge/exif-12k/exif111.txt
##

import sys
import re
import datetime

class CP6EXIFData:
    def __init__( self, id, v, edate, etime, eflash ):
        self.mir_id = id
        self.valid = v
        if not self.valid:
            return
        self.exif_date = edate
        self.exif_time = etime
        self.exif_flash = eflash
        m = re.search( '(\d{4}):(\d{2}):(\d{2})', edate )
        if m:
            try:
                self.exif_caldate = datetime.date( int( m.group(1) ), int( m.group(2) ), int(m.group(3) ))
            except ValueError as e:
                sys.stderr.write( "WARN: Couldn't construct date from '%s' in %d: %s; skipping\n" % (edate, id, e))
                self.valid = False
        else:
            sys.stderr.write( "WARN: Couldn't parse edate %s in id %d; skipping\n" % (edate, id ) )
            self.valid = False

    def __str__( self ):
        if self.valid:
            return 'exif %d: %s %s flash? %s caldate %s' % (self.mir_id, self.exif_date, self.exif_time, self.exif_flash, self.exif_caldate )
        else:
            return 'exif %d: invalid' % self.mir_id

    @staticmethod
    def parsableDatetime( dt ):
        m = re.search( '(\d{4}:\d{2}:\d{2}) (\d{2}:\d{2}:\d{2})', dt )
        if m and m.group(1) != '0000:00:00':
            return (m.group(1), m.group(2))
        else:
            return (None, None)

    @classmethod
    def from_file( cls, fn ):
        m = re.search( 'exif(\d+).txt$', fn )
        if not m:
            raise AssertionError( 'Failed to parse MIR id from "%s"' % fn )
        id = int(m.group(1))

        tags = dict()
        with open( fn ) as f:
            while 1:
                raw_line = f.readline()
                if not raw_line:
                    break
                line = raw_line.strip()
                if line == '-Date and Time':
                    key = 'dnt'
                elif line == '-Date and Time (Original)':
                    key = 'dntOrig'
                elif line == '-Date and Time (Digitized)':
                    key = 'dntDig'
                elif line == '-Flash':
                    key = 'flash'
                else:
                    continue

                val = f.readline().strip()
                tags[key] = val

        if len(tags)==0:
            return cls( id, False, None, None, None )

        eflash = 'U'  # unknown
        if 'flash' in tags:
            if re.search( 'Flash did not fire', tags['flash'] ):
                eflash = 'N'
            else:
                eflash = 'Y'

        datetime = None
        if ('dntOrig' in tags) and CP6EXIFData.parsableDatetime( tags['dntOrig'] ):
            datetime = tags['dntOrig']
        elif ('dntDig' in tags) and CP6EXIFData.parsableDatetime( tags['dntDig'] ):
            datetime = tags['dntDig']
        elif 'dnt' in tags and CP6EXIFData.parsableDatetime( tags['dnt'] ):
            datetime = tags['dnt']
        else:
            sys.stderr.write( 'WARN: unparsable date/time in %s; skipping\n' % fn )
            return cls( id, False, None, None, None )

        (edate, etime) = CP6EXIFData.parsableDatetime( datetime )
        if not (edate and etime):
            return cls( id, False, None, None, None )

        return cls( id, True, edate, etime, eflash )

if __name__ == "__main__":
    e = CP6EXIFData.from_file( sys.argv[1] )
    print e
