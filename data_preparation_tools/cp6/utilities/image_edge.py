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
##
##

import sys
from cp6.utilities.image_indicator import ImageIndicator

class ImageEdge:

    def __init__( self, id_a, id_b, sharedGroups, sharedWords, sharedWordTypes, \
                  same_user, same_location, shared_contact):
        self.image_A_id = id_a
        self.image_B_id = id_b
        self.shared_groups = sharedGroups
        self.shared_words = sharedWords
        self.shared_word_types = sharedWordTypes
        self.same_user_flag = same_user
        self.same_location_flag = same_location
        self.shared_contact_flag = shared_contact

    @classmethod
    def from_data( cls, imgIndA, imgIndB, sharedGroups, sharedWords, \
                   same_user, same_location, shared_contact):
        shared_word_types = list( [0] * len(sharedWords))
        for i in range(0,len(sharedWords )):
            index = sharedWords[i]
            a_flag = imgIndA.word_source_flags[ index ]
            b_flag = imgIndB.word_source_flags[ index ]
            if (a_flag == ImageIndicator.IN_NONE) or (b_flag == ImageIndicator.IN_NONE):
                raise AssertionError( 'Edge between %d and %d: shared word flags %d, %d\n' % \
                                      (imgIndA.id, imgIndB.id, a_flag, b_flag))

            # need to strip out the source flags
            a_src_flag = a_flag & ImageIndicator.SRC_FLAG_MASK
            b_src_flag = b_flag & ImageIndicator.SRC_FLAG_MASK

            # these should be the same
            if (a_src_flag != b_src_flag):
                raise AssertionError( 'Edge between %d and %d: inconsisitent source flags %d, %d\n' % (imgIndA.id, imdIndB.id, a_flag, b_flag))

            # strip
            a_flag &= ~a_src_flag
            b_flag &= ~b_src_flag

            shared_word_types[i] = a_flag + (b_flag * 16)

            # insert source flag back in
            shared_word_types[i] |= a_src_flag

        return cls( imgIndA.id, imgIndB.id, sharedGroups, sharedWords, \
                    shared_word_types, same_user, same_location, shared_contact )

    @staticmethod
    def get_shared_group_id_vector( imgIndA, imgIndB ):
        if imgIndA.group_keys is None:
            imgIndA.group_keys = set(imgIndA.group_list.keys())
        if imgIndB.group_keys is None:
            imgIndB.group_keys = set(imgIndB.group_list.keys())
        return list( imgIndA.group_keys & imgIndB.group_keys )

    @staticmethod
    def get_shared_word_id_vector( imgIndA, imgIndB ):
        if imgIndA.word_keys is None:
            imgIndA.word_keys = set(imgIndA.word_list.keys())
        if imgIndB.word_keys is None:
            imgIndB.word_keys = set(imgIndB.word_list.keys())
        return list( imgIndA.word_keys & imgIndB.word_keys )

    @staticmethod
    def canonical_flag( s ):
        if (s == '0') or (s == '1') or (s == '.'):
            return s
        else:
            return '1'

    @staticmethod
    def canonical_flag_int( s ):
        if (s == '0') or (s == '.'):
            return 0
        else:
            return 1


    @staticmethod
    def edges_in_nodeset( paths, phase_key, nodes ):
        fn = paths.phase_tables[phase_key].image_edge_table
        node_id_dict = dict( [id, True] for id in nodes)
        (nodes, edges) = CP6ImageEdge.read_edges_from_file( fn, node_id_dict )
        sys.stderr.write('Info: read %d edges\n' % len(edges))
        return edges


