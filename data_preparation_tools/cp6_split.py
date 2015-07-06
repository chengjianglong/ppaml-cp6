##
## keep track of which mir IDs are in which
## phase 1/2 test/train split
##

import sys
import datetime

class CP6Split:
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
        splits = [ CP6Split( [], 1, CP6Split.TEST), \
                CP6Split( [], 1, CP6Split.TRAIN), \
                CP6Split( [], 2, CP6Split.TEST), \
                CP6Split( [], 2, CP6Split.TRAIN) ]

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
            elif cp6data.exifdata[ id ].exif_caldate >= mode_split_date:
                # use for training
                offset = offset + 1

            splits[ offset ].ids.append( id )

        # round 2 inherits all of round 1's data
        splits[2].ids.extend( splits[0].ids )
        splits[3].ids.extend( splits[1].ids )

        for i in range(0, 4):
            sys.stderr.write('Info: %s\n' % splits[i] )

        return splits

