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

import os
import sys

from cp6.tables.image_table import ImageTable
from cp6.tables.image_indicator_table import ImageIndicatorTable
from cp6.tables.image_indicator_lookup_table import ImageIndicatorLookupTable
from cp6.tables.label_table import LabelTable

class SandboxAdapter:

    @staticmethod
    def write_node_features( fn, ii_lookup_table, label_table, \
                             image_table, image_indicator_table ):
        #
        # The nodeFeatures file has the following layout:
        #
        # [1] nGroups nTags nLabels
        # [2] group_id group_name
        # [3] tag_id tag_name
        # [4] label_id label_name
        # [5] nPhotos
        # [6] photo_id user_id indicator
        #
        # Multiplicities:
        #
        # [1] x 1
        # [2] x nGroups
        # [3] x nTags
        # [4] x nLabels
        # [5] x 1
        # [6] x nPhotos
        #
        # [2] and [3] are from our ImageIndicatorLookupTable. [4] is
        # our label table (I think.) [6] can be (cp6_id, fake_user,
        # indicator), where indicator is a string of length
        # nGroups+nTags+nLabels. Each character is either '.', '0', or
        # '1'.  Looking at genericdata.cpp:284, chars are either '1'
        # or not '1' for groups and tags. Labels are '0' if negative,
        # '1' if positive.
        #
        # Note that group_id, tag_id, label_id are all sequential:
        # the first tag_id is the last group_id + 1.
        #

        with open(fn, 'w') as f:

            # write the header line [1]

            nGroups = len( ii_lookup_table.group_text_lut )
            nTags = len( ii_lookup_table.word_text_lut )
            nLabels = len( label_table.label2id )
            f.write('%d %d %d\n' % ( nGroups, nTags, nLabels ))

            c = 0

            # write the group lines [2]

            for i in sorted( ii_lookup_table.group_text_lut.iteritems(), key=lambda x:x[1] ):
                (entry_id, entry_text) = (i[1], i[0])
                f.write( '%d %s\n' % ( c, entry_text ))
                c += 1

            # write the tag lines [3] .. not sure how McAuley's code handles UTF-8?

            for i in sorted( ii_lookup_table.word_text_lut.iteritems(), key=lambda x:x[1] ):
                (entry_id, entry_text) = (i[1], i[0])
                f.write( '%d %s\n' % ( c, entry_text ))
                c += 1

            # write the label lines [4]

            for i in sorted( label_table.label2id.iteritems(), key=lambda x:x[1] ):
                (entry_id, entry_text) = (i[1], i[0])
                f.write( '%d %s\n' % (c, entry_text ))
                c += 1

            # write the header line [5]

            nImages = len( image_table.entries )
            f.write('%d\n' % nImages )

            # write the image indicator lines [6]

            for i in sorted( image_table.entries.iteritems(), key=lambda x:x[1] ):
                (img_id, user) = (i[1].mir_id, i[1].flickr_owner)
                ii = image_indicator_table.image_indicators[ img_id ]
                s = ''
                for i in range(0, nGroups):
                    if i in ii.group_list:
                        s += '1'
                    else:
                        s += '.'
                for i in range(0, nTags):
                    if i in ii.word_list:
                        s += '1'
                    else:
                        s += '.'
                lv = image_table.entries[ img_id ].label_vector
                for i in range(0, nLabels):
                    v = lv[i]
                    if v == 1:
                        s += '1'
                    elif v == 0:
                        s += '0'
                    else:
                        s += '.'
                    f.write('%d %s %s\n' %( img_id, user, s ))

            # all done


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: $0 output-dir input-dir\n')
        sys.exit(0)
    (out_dir, in_dir) = (sys.argv[1], sys.argv[2])
    lt = LabelTable.read_from_file( os.path.join( in_dir, 'label_table.txt' ))
    sys.stderr.write('Info: loaded label table\n')
    it = ImageTable.read_from_file( os.path.join( in_dir, 'image_table.txt' ))
    sys.stderr.write('Info: loaded image table\n')
    iit = ImageIndicatorTable.read_from_file( os.path.join( in_dir, 'image_indicator_table.txt' ))
    sys.stderr.write('Info: loaded image indicator table\n')
    iilut = ImageIndicatorLookupTable.read_from_file( os.path.join( in_dir, 'image_indicator_lookup_table.txt' ))
    sys.stderr.write('Info: loaded IILUT\n')

    m_node_table = os.path.join( out_dir, 'node_features.txt' )
    SandboxAdapter.write_node_features( m_node_table, iilut, lt, it, iit )
