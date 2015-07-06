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
