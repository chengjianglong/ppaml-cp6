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
## This script creates a toy PPAML sandbox based on a file of fake image data.
## Images with even IDs are used for training, and odd IDs are used for testing.
##
## arg1 is the text file; arg2 is the directory where the toy sandbox will be
## created.
##
## The file format is:
##
## id user-string true-label,true-label,... title-word tag,tag,.. description
##
## Blank lines and comment lines (starting with '#') are allowed.
##
## For example, the line
##
## 159 user1 trees,travel vacation seattle,java,trips I went to seattle good coffee
##
## would create entries for:
## -- an image with ID 159 (odd, thus used for testing)
## -- created by 'user1'
## -- with true labels "trees" and "travel"
## -- titled "vacation"  (the title can only be a single word)
## -- tagged with "seattle", "java", and "trips"
## -- and the description "I went to seattle good coffee"
##
## No group, EXIF, or location tags are simulated.
##


import sys
import os

from cp6.utilities.image_indicator import ImageIndicator
from cp6.utilities.image_table_entry import ImageTableEntry
from cp6.utilities.image_edge import ImageEdge
from cp6.utilities.exifdata import EXIFData

from cp6.tables.label_table import LabelTable
from cp6.tables.image_indicator_lookup_table import ImageIndicatorLookupTable
from cp6.tables.image_indicator_table import ImageIndicatorTable
from cp6.tables.image_table import ImageTable
from cp6.tables.edge_table import EdgeTable

class DemoLine:

    def __init__( self, fields ):
        self.photo_id = int(fields[0])
        self.user_id = fields[1]
        self.labels = fields[2].split(',')
        self.title = fields[3]
        self.tags = fields[4].split(',')
        self.text = fields[5:]

    def __str__( self ):
        return 'id %d user %s labels %s title %s tags %s text "%s"' % (self.photo_id, self.user_id, ','.join(self.labels),self.title,','.join(self.tags),','.join(self.text))

    @staticmethod
    def parse_from_file( fn ):
        lines = list()
        with open(fn) as f:
            while 1:
                raw_line = f.readline()
                if not raw_line:
                    break
                fields = raw_line.strip().split()
                if (len(fields)>0) and (fields[0] != '#'):
                    lines.append( DemoLine(fields) )
                    sys.stderr.write('Dbg: %s\n' % lines[-1] )

        sys.stderr.write('Info: read %d demo lines\n' % len(lines))
        return lines

def ensure_dir( path_components ):
    full_path = ''
    for p in path_components:
        full_path = p if len(full_path)==0 else os.path.join( full_path, p )
        if not os.path.isdir(full_path):
            os.mkdir(full_path)
    return full_path

def make_edge_table( imgtbl, iit ):
    edges = list()
    sorted_ids = sorted( imgtbl.entries.keys() )
    for a_index in range( 0, len(sorted_ids )):
        a = sorted_ids[ a_index ]
        for b_index in range( a_index+1, len(sorted_ids)):
            b = sorted_ids[ b_index ]

            ai = iit.image_indicators[a]
            bi = iit.image_indicators[b]

            # approximate McAuley "edge flags" by checking for same user
            loc_flag = '0'
            friend_flag = '0'
            user_flag = '1' if imgtbl.entries[a].flickr_owner == imgtbl.entries[b].flickr_owner else '0'

            group_id_vector = ImageEdge.get_shared_group_id_vector( ai, bi )
            word_id_vector = ImageEdge.get_shared_word_id_vector( ai, bi )

            if len(group_id_vector) or len(word_id_vector) or user_flag != '0':
                edges.append( ImageEdge.from_data( ai, bi, group_id_vector, word_id_vector, user_flag, loc_flag, friend_flag ))

    return EdgeTable( edges )

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: $0 demo-file.txt output-prefix\n')
        sys.exit(0)

    (demo_fn, output_prefix) = sys.argv[1:3]
    demolines = DemoLine.parse_from_file( sys.argv[1] )

    # construct the label table (one of these)
    L2I = dict()
    I2L = dict()
    label_index = 0
    for d in demolines:
        for dl in d.labels:
            if dl not in L2I:
                L2I[ dl ] = label_index
                I2L[ label_index ] = dl
                label_index +=1
    lt = LabelTable( L2I, I2L )
    sys.stderr.write('Info: %d labels\n' % len(L2I))

    # construct IILUT- no groups, just tags & words (one of these)
    iilut = ImageIndicatorLookupTable()
    tw_lut = dict()  # tags and words -> index
    tw_src = dict()  # index-> (T)ag, (W)ord, or (B)oth
    lut_index = 0
    for d in demolines:
        words = [d.title] + d.text
        for w in words:
            if not w in tw_lut:
                tw_lut[ w ] = lut_index
                tw_src[ lut_index ] = 'W'
                lut_index += 1
        for t in d.tags:
            if not t in tw_lut:
                tw_lut[ t ] = lut_index
                tw_src[ lut_index ] = 'T'
                lut_index += 1
            else:
                i = tw_lut[ t ]
                tw_src[ i ] = 'B'
    iilut.tag_word_text_lut = tw_lut
    iilut.tag_word_text_src = tw_src
    sys.stderr.write('Info: %d iilut entries\n' % len(tw_lut))

    # construct image indicator table (one train, one test)
    test_iit = ImageIndicatorTable()
    train_iit = ImageIndicatorTable()

    for d in demolines:
        it = ImageIndicator( d.photo_id )
        iilut.add_to_indicator( it, 'W', d.title, ImageIndicator.IN_TITLE )
        for w in d.text:
            iilut.add_to_indicator( it, 'W', w, ImageIndicator.IN_DESC )
        for t in d.tags:
            iilut.add_to_indicator( it, 'W', t, ImageIndicator.IN_TAG )
        if ( d.photo_id % 2 == 0):
            train_iit.image_indicators[ d.photo_id ] = it
        else:
            test_iit.image_indicators[ d.photo_id ] = it

    sys.stderr.write('Info: %d / %d train / test image indicator entries\n' % (len(train_iit.image_indicators), len(test_iit.image_indicators)))

    # construct image table (one train, one test)
    train_imgtbl = ImageTable()
    test_imgtbl = ImageTable()
    for d in demolines:
        ite = ImageTableEntry()
        ite.mir_id = d.photo_id
        ite.flickr_id = d.photo_id
        ite.flickr_title = d.title
        ite.flickr_descr = ' '.join( d.text )
        ite.flickr_owner = d.user_id
        ite.exif_data = EXIFData( ite.mir_id, False, 'none', 'none', 'U' )
        ite.flickr_locality = None
        ite.label_vector = [0] * len(lt.label2id)
        for label in d.labels:
            ite.label_vector[ lt.label2id[ label ]] = 1
        if (d.photo_id % 2 == 0):
            train_imgtbl.entries[ d.photo_id ] = ite
        else:
            test_imgtbl.entries[ d.photo_id ] = ite

    sys.stderr.write('Info: %d / %d train / test image table entries\n' % (len(train_imgtbl.entries), len(test_imgtbl.entries)))

    # construct edge table (one train, one test )
    train_et = make_edge_table( train_imgtbl, train_iit )
    test_et = make_edge_table( test_imgtbl, test_iit )
    sys.stderr.write('Info: %d / %d train / test edges\n' % (len(train_et.edges), len(test_et.edges)))

    # write 'em out
    p1 = ensure_dir( [output_prefix, 'eval_in', 'etc' ] )
    p2 = ensure_dir( [output_prefix, 'run_in', 'training' ])
    p3 = ensure_dir( [output_prefix, 'eval_in', 'testing' ])
    p4 = ensure_dir( [output_prefix, 'run_in', 'testing' ])

    lt.write_to_file( os.path.join( p1, 'label_table.txt' ))
    iilut.write_to_file( os.path.join( p1, 'image_indicator_lookup_table.txt' ))

    # hmm, this is a little clunky
    train_imgtbl.write_to_file( os.path.join( p2, 'image_table.txt' ) )
    all_test_ids = sorted( test_imgtbl.entries.keys() )
    test_imgtbl.write_to_file( os.path.join( p4, 'image_table.txt' ), [ all_test_ids, True ])
    test_imgtbl.write_to_file( os.path.join( p3, 'image_table.txt' ), [ all_test_ids, False ])

    train_iit.write_to_file( os.path.join( p2, 'image_indicator_table.txt' ))
    test_iit.write_to_file( os.path.join( p4, 'image_indicator_table.txt' ))
    train_et.write_to_file( os.path.join( p2, 'image_edge_table.txt' ))
    test_et.write_to_file( os.path.join( p4, 'image_edge_table.txt' ))
