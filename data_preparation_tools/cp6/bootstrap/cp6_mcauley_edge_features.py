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

class CP6McAuleyEdge:
    def __init__( self, ntags, ngroups, ncollections, ngalleries, loc, user, friend ):
        self.n_tags = ntags
        self.n_groups = ngroups
        self.n_collections = ncollections
        self.n_galleries = ngalleries
        self.location_flag = loc
        self.user_flag = user
        self.friend_flag = friend

    def __eq__(self, other):
        return self.n_tags == other.n_tags and \
          self.n_groups == other.n_groups and \
          self.n_collections == other.n_collections and \
          self.n_galleries == other.n_galleries and \
          self.location_flag == other.location_flag and \
          self.user_flag == other.user_flag and \
          self.friend_flag == other.friend_flag

class CP6McAuleyEdgeFeatures:
    def __init__( self, fn ):
        self.edgemap = dict()  # key: 'id_a:id_b' s.t. id_a < id_b; val: CP6McauleyEdge
        (c_dupes, c_conflicts) = (0, 0)
        with open( fn ) as f:
            header_line = f.readline()
            while 1:
                raw_line = f.readline()
                if not raw_line:
                    break
                line = raw_line.strip()
                fields = line.split()
                if len(fields) != 9:
                    raise AssertionError('Got %d fields (expected 9) from "%s"\n' % \
                                         (len(fields), line))
                e = CP6McAuleyEdge( fields[2], fields[3], fields[4], fields[5], fields[6], fields[7], fields[8] )
                (id_a, id_b) = (int(fields[0]), int(fields[1]))
                if id_a < id_b:
                    key = '%d:%d' % (id_a, id_b)
                else:
                    key = '%d:%d' % (id_b, id_a)
                if key in self.edgemap:
                    if not e == self.edgemap[key]:
                        c_conflicts += 1
                    else:
                        c_dupes += 1
                else:
                    self.edgemap[key] = e
        sys.stderr.write('Info: read %d edges (skipped %d duplicates, %d conflicts)\n' % (len(self.edgemap), c_dupes, c_conflicts))
