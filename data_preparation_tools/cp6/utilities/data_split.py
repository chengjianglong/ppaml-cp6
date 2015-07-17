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
## keep track of which mir IDs are in which
## phase 1/2 test/train split
##

import sys
import datetime

class DataSplit:
    (TEST, TRAIN) = (0, 1)

    def __init__( self, ids, r, m ):
        self.ids = ids
        self.round = r
        self.mode = m # test or train

    def __str__( self ):
        tag = "test" if self.mode == self.TEST else "train"
        return 'split %s round %d with %d ids' % (tag, self.round, len(self.ids))

    @staticmethod
    def get_splits( cp6data ):
        splits = [ DataSplit( [], 1, DataSplit.TEST), \
                DataSplit( [], 1, DataSplit.TRAIN), \
                DataSplit( [], 2, DataSplit.TEST), \
                DataSplit( [], 2, DataSplit.TRAIN) ]

        mode_split_date = datetime.date( 2007, 12, 1 )

        for id in cp6data.xmldata.mir_nodes:
            offset = 0
            labelset = cp6data.get_mirlabel_set( id )
            if 'structures' in labelset:
                # round 2: splits 2 or 3
                offset = 2
            else:
                # round 1: splits 0 or 1
                offset = 0

            if not cp6data.exifdata[ id ].valid:
                # add data without valid EXIF to training
                offset = offset + 1
            elif cp6data.exifdata[ id ].exif_caldate < mode_split_date:
                # use for training
                offset = offset + 1

            splits[ offset ].ids.append( id )

        # round 2 inherits all of round 1's data
        splits[2].ids.extend( splits[0].ids )
        splits[3].ids.extend( splits[1].ids )

        for i in range(0, 4):
            sys.stderr.write('Info: %s\n' % splits[i] )

        return splits

