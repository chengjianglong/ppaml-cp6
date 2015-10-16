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
from cp6.tables.edge_table import EdgeTable
from cp6.utilities.image_edge import ImageEdge

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
            nTags = len( ii_lookup_table.tag_text_lut )
            nLabels = len( label_table.label2id )
            f.write('%d %d %d\n' % ( nGroups, nTags, nLabels ))

            c = 0

            # write the group lines [2]

            for i in sorted( ii_lookup_table.group_text_lut.iteritems(), key=lambda x:x[1] ):
                (entry_id, entry_text) = (i[1], i[0])
                f.write( '%d %s\n' % ( c, entry_text ))
                c += 1

            # write the tag lines [3] .. not sure how McAuley's code handles UTF-8?

            for i in sorted( ii_lookup_table.tag_text_lut.iteritems(), key=lambda x:x[1] ):
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

    @staticmethod
    def write_edge_features( fn, edge_table ):
        # #
        # # edgeFeatures, trainingEdgeFeatures:
        # # genericdata.cpp:450
        # #
        #
        #
        # [1] nEdges nEdgeFeatures
        # [2] img_id_1 img_id_2 feature-list
        #
        # Multiplicities:
        #
        # [1] x 1
        # [2] x nEdges
        #
        # The feature-list, from McAuley page 10:
        #
        # nTags nGroups nCollections nGalleries flagLoc flUser flFriend
        #
        # n{Tags,Groups,Collections}: "The number of common tags, groups, collections, and galleries"
        #
        # flLoc: "An indicator for whether both photos were taken in the same
        # location (GPS coordinates are organized into distinct 'localities' by
        # Flickr)"
        #
        # flUser: "An indicator for whether both photos were taken by the same user"
        #
        # flFriend: "An indicator for whether both photos were taken by contacts/friends"
        #
        # Example (edgeFeaturesPASCAL.txt), syntax: {label} (line-number) payload
        #
        # {a} (1) 2684742 7
        # {b} (2) 106998777 15256584 0 2 0 0 0 0 0
        # {c} (2684743) 2110031507 1116386773 0 1 0 0 0 0 0
        #
        # ...so:
        #
        # {a} is 1 x [1]
        # {b}..{c} is 2684742 x [2]
        #
        # We don't record collections or galleries, only groups.
        #

        with open(fn, 'w') as f:

            # write the header line [1]

            f.write('%d 7\n' % len( edge_table.edges ))  # always write seven features

            # write the edges [2]

            for e in edge_table.edges:
                f.write('%d %d ' % (e.image_A_id, e.image_B_id))
                f.write('%d %d 0 0 ' % (len(e.shared_words), len(e.shared_groups)))
                f.write('%d %d %d\n' % (ImageEdge.canonical_flag_int( e.same_location_flag ), \
                                       ImageEdge.canonical_flag_int( e.same_user_flag ), \
                                       ImageEdge.canonical_flag_int( e.shared_contact_flag )))

            # all done

    @staticmethod
    def write_text_features( fn, image_table, image_indicator_table ):
        #
        # from genericdata.cpp:292: nWords is set, and nWords are parsed but
        # discarded. Then nPhotos are loaded, each line (:310) is:
        #
        # photoID userID nFeatures {nFeatures x '%d:%d'}
        #
        # ...where (key,val) = %d:%d are:
        #
        # ...... key is the index of the word-to-use
        #
        # ...... val is an int multiplied by 1/nwords (:326).
        # ...... For the pascal examples, val is always '1'.
        # ...... Also always '1' in trainingTextMIR.txt.
        #
        # These are read into the nodeFeatures array (see :316.)
        #
        # so the file we write is:
        #
        #
        # [1] nwords
        # [2] word
        # [3] photoID userID nFeatures {nFeatures x '%d:1'}
        #
        # [1] x 1
        # [2] x nwords
        # [3] x nPhotos from node features file
        #
        # Interestingly, [1] and [2] are discarded, so we can minimize them here.
        #
        # I don't see how this isn't redundant vis-a-vis the node features file.
        #

        with open(fn, 'w') as f:

            # write a fake [1] and [2]

            f.write( '1\n' )
            f.write( 'this_word_is_not_used\n' )

            # write [3]

            for i in sorted( image_table.entries.iteritems(), key=lambda x:x[1] ):
                (img_id, user) = (i[1].mir_id, i[1].flickr_owner)
                ii = image_indicator_table.image_indicators[ img_id ]
                n = len(ii.word_list)
                f.write('%d %s %d ' % (img_id, user, n))
                for j in ii.word_list.keys():
                    f.write('%d:1 ' % j )
                f.write('\n')
            # all done

    @staticmethod
    def write_id_file( fn, image_table, image_indicator_table ):
        #
        # genericdata.cpp:80 ... this is the "group ID" file (training only)
        #
        # [1] label_id
        # [2] name nGroups nTags
        # [3] groupID:flag (%d:%f)
        # [4] tagID:flag (%d:%f)
        #
        # ...[1], [2], [3], [4] repeated for each label. Within each label, [3]
        # repeated for each group associated with the label. flag value
        # needs to be >2. Ditto [4], repeated for each tag (word) associated with
        # the label.
        #
        # We reconstruct this by first building a label-to-image list, then
        # for each label, flagging the groups associated with the images.
        # Ditto for tags.
        #

        label2group = dict()  # key: label ID; val: set of group IDs
        label2word = dict()   # key: label ID; val: set of word IDs

        for (img_id, img) in image_table.entries.iteritems():
            ii = image_indicator_table.image_indicators[ img_id ]
            lv = img.label_vector
            if len(label2group) == 0:
                for i in range(0,len(lv)):
                    label2group[i] = set()
                    label2word[i] = set()
            for label_index in range(0, len(lv)):
                if lv[label_index] != 1:
                    continue
                # we now know that img_id is associated with label_index
                # (assumes label_index == label_id, hmm)
                for i in ii.group_list.iteritems():
                    label2group[label_index].add( i[0] )
                for i in ii.word_list.iteritems():
                    label2word[label_index].add( i[0] )

        with open(fn, 'w') as f:
            for i in sorted( label2group.iteritems(), key=lambda x:x[1] ):
                label_index = i[0]
                (g, w) = (label2group[label_index], label2word[label_index])
                f.write('%d labelname-not-used %d %d ' % (i[0], len(g), len(w)))
                for j in g:
                    f.write('%d:3 ' % j)
                for j in w:
                    f.write('%d:3 ' % j)
                f.write('\n')

        # all done

    @staticmethod
    def write_text_id_file( fn, x ):
        #
        # genericdata.cpp:145
        #
        # [1] label_id
        # [2] name nWords
        # [3] wordID:flag (%d:%f)
        #
        # ...[1], [2], [3] repeated for each label. Within each label, [3]
        # repeated for each word associated with the label. flag value
        # needs to be >2. 

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
    et = EdgeTable.read_from_file( os.path.join( in_dir, 'image_edge_table.txt' ))
    sys.stderr.write('Info: loaded edge table\n')

    SandboxAdapter.write_node_features( os.path.join( out_dir, 'node_features.txt' ), iilut, lt, it, iit )
    SandboxAdapter.write_edge_features( os.path.join( out_dir, 'edge_features.txt' ), et)
    SandboxAdapter.write_text_features( os.path.join( out_dir, 'text_features.txt' ), it, iit )
    SandboxAdapter.write_id_file( os.path.join( out_dir, 'id_file.txt' ), it, iit )
