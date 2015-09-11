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
from cp6.utilities.image_edge import ImageEdge

class EdgeTable:

    def __init__( self, e ):
        self.edges = e

    def write_to_file( self, fn ):
        with open(fn, 'w') as f:
            for e in self.edges:
                f.write( '%d %d %d %d ' % (e.image_A_id, e.image_B_id, len(e.shared_groups), len(e.shared_words)))
                group_str = ','.join(map(str,e.shared_groups)) if len(e.shared_groups) else 'none'
                word_str = ','.join(map(str,e.shared_words)) if len(e.shared_words) else 'none'
                word_type_str = ','.join(map(str,e.shared_word_types)) if len(e.shared_word_types) else 'none'
                f.write( '%s %s %s ' % (group_str, word_str, word_type_str))
                f.write( '%s %s %s\n' % (ImageEdge.canonical_flag( e.same_user_flag ), \
                                         ImageEdge.canonical_flag( e.same_location_flag ), \
                                         ImageEdge.canonical_flag( e.shared_contact_flag )))

    @staticmethod
    def read_from_file( fn ):
        edges = dict()
        node_ids = dict()
        c_line = 0
        with open(fn) as f:
            while 1:
                raw_line = f.readline()
                if not raw_line:
                    break
                c_line += 1
                fields = raw_line.strip().split()
                if len(fields) != 10:
                    raise AssertionError( '%s line %d: expected 10 fields, got %d' % \
                                          (fn, c_line, len(fields) ))
                (image_A_id, image_B_id) = (int(fields[0]), int(fields[1]))
                if (len(nodes_to_keep)==0) or \
                   ( (image_A_id in nodes_to_keep) and (image_B_id in nodes_to_keep)):
                    # n_groups = fields[2], n_words = fields[3]
                    sharedGroups = map( int, fields[4].split(',')) if fields[4] != 'none' else list()
                    sharedWords = map( int, fields[5].split(',')) if fields[5] != 'none' else list()
                    sharedWordTypes = map( int, fields[6].split(',')) if fields[6] != 'none' else list()
                    edges.append( ImageEdge( image_A_id, image_B_id, \
                                  sharedGroups, sharedWords, sharedWordTypes, \
                                  fields[7], fields[8], fields[9] ))
                    node_ids[ image_A_id ] = True
                    node_ids[ image_B_id ] = True
        return EdgeTable( edges )

