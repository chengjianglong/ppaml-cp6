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

from collections import defaultdict

from cp6.utilities.paths import Paths
from cp6.utilities.data_split import DataSplit
from cp6.utilities.util import Util
from cp6.bootstrap.cp6_xml import CP6XML
from cp6.utilities.exifdata import EXIFData
from cp6.tables.cp6_image_indicator_lookup import ImageIndicatorLookupTable, ImageIndicator
from cp6.tables.label_table import LabelTable
from cp6.bootstrap.cp6_mcauley_edge_features import CP6McAuleyEdgeFeatures
from cp6.tables.cp6_image_edge import CP6ImageEdge
from cp6.tables.image_table import ImageTable, ImageTableEntry

class CP6Data:

    def __init__( self, cp6paths ):
        self.paths = cp6paths
        sys.stderr.write( 'Info: Loading XML...\n' )
        self.xmldata = CP6XML( cp6paths.xml_path )
        self.n_mir_ids = len(self.xmldata.mir_nodes)
        sys.stderr.write( 'Info: Associating EXIF data...\n' )
        self.exifdata = dict()
        (c_valid, c_invalid) = (0, 0)
        labelset = set()
        for mir_id in self.xmldata.mir_nodes:
            exif_path = '%s/exif%d.txt' % (self.paths.exif_dir, mir_id )
            e = EXIFData.read_from_file( exif_path )
            self.exifdata[ mir_id ] = e
            if e.valid:
                c_valid += 1
            else:
                c_invalid += 1

            labelset |= self.get_mirlabel_set( mir_id )

        self.label_table = LabelTable.set_from_vector( sorted( labelset ) )
        sys.stderr.write( 'Info: found %d valid, %d invalid EXIF files (sum: %d)\n' % \
                          (c_valid, c_invalid, c_valid+c_invalid))
        sys.stderr.write( 'Info: found %d labels\n' % self.label_table.nlabels() )

        self.imglut = ImageIndicatorLookupTable()
        self.imglut.set_from_mcauley( self.paths.node_features_path, \
                                      self.paths.stopwords_path )
        sys.stderr.write( 'Info: Image Indicator LUT has %d groups, %d words\n' % \
                          ( len(self.imglut.groups), len(self.imglut.words) ))

        self.image_indicators = dict()
        (c_iit_groups, c_iit_words, n) = (0,0,0)
        for mir_id in self.xmldata.mir_nodes:
            n += 1
            if n % 1000 == 0:
                sys.stderr.write( 'Info: image indicator %d of %d...\n' % (n, self.n_mir_ids ))
            self.image_indicators[ mir_id ] = self.get_image_indicator( mir_id )
            c_iit_groups += len( self.image_indicators[ mir_id ].group_list )
            c_iit_words += len( self.image_indicators[ mir_id ].word_list )
        sys.stderr.write( 'Info: Image Indicators average %.2f groups, %.2f words\n' % \
                           ( c_iit_groups * 1.0 / self.n_mir_ids, c_iit_words * 1.0 / self.n_mir_ids ))

        self.mcauley_edge_features = CP6McAuleyEdgeFeatures( self.paths.edge_features_path )
        self.splits = dict()

    def set_splits( self ):
        (self.splits['r1test'], self.splits['r1train'], self.splits['r2test'], self.splits['r2train']) = \
          DataSplit.get_splits( self )

    def count_labels_in_split( self, data_split ):
        label_count_map = defaultdict( int )
        for mir_id in data_split.ids:
            for label in self.get_mirlabel_set( mir_id ):
                label_count_map[ label ] += 1
        return label_count_map

    def write_debug_label_count_csv( self, fn ):
        counts = dict()
        for split in self.splits:
            counts[ split ] = self.count_labels_in_split( self.splits[ split ])

        with open( fn, 'w') as f:
            f.write('label,r1rain,r1test,r2train,r2test,total\n');
            for label in self.label_table.label2id:
                f.write('%s,' % label)
                sum = 0
                for s in ('r1train','r1test','r2train','r2test'):
                    n = counts[s][label]
                    f.write('%d,' % n)
                    sum += n
                f.write('%d\n' % sum)

    def get_mirlabel_set( self, id ):
        s = set()
        for n_labels in self.xmldata.mir_nodes[ id ].iter( 'labels' ):
            for label in n_labels:
                if label.get( 'source' ) == 'MIR':
                    s.add( label.text )
        return s

    def set_label_vector_from_split( self, data_split, id ):
        v = []
        if data_split.mode == DataSplit.TEST:
            for i in self.label_table.idset:
                if (self.label_table.id2label[i] == 'structures') and (data_split.round == 1):
                    v.append( -1 )
                else:
                    v.append( -2 )
        else:
            my_labels = self.get_mirlabel_set( id )
            for i in self.label_table.idset:
                if (self.label_table.id2label[i] == 'structures') and (data_split.round == 1):
                    v.append( -1 )
                else:
                    if self.label_table.id2label[i] in my_labels:
                        v.append( 1 )
                    else:
                        v.append( 0 )
        return v


    def image_table_from_split( self, data_split ):
        t = ImageTable()
        for mir_id in data_split.ids:
            photo = self.xmldata.mir_nodes[ mir_id ]

            e = ImageTableEntry()

            e.mir_id = mir_id
            e.flickr_id = int( photo.get('id') )
            e.flickr_owner = photo.find('owner').get('nsid')
            e.flickr_title = photo.find('title').text
            e.flickr_descr = photo.find('description').text
            e.exif_data = self.exifdata[ mir_id ]

            locality = photo.find('locality')
            if locality:
                e.flickr_locality = locality.text
            else:
                e.flickr_locality = None

            e.label_vector = self.set_label_vector_from_split( data_split, mir_id )

            t.add_entry( e )

        return t

    @staticmethod
    def textwrapper( node ):
        if node == None:
            return None
        return node.text

    def get_image_indicator( self, id ):
        imgind = self.imglut.init_indicator( id )
        photo = self.xmldata.mir_nodes[ id ]

        for groups in photo.iter('groups'):
            for g in groups:
                self.imglut.add_to_indicator( imgind, 'G', g.get('id'), ImageIndicator.IN_NONE )

        self.imglut.add_to_indicator( imgind, 'W', \
                                      CP6Data.textwrapper( photo.find('title')), \
                                      ImageIndicator.IN_TITLE )
        self.imglut.add_to_indicator( imgind, 'W', \
                                      CP6Data.textwrapper( photo.find('description')), \
                                      ImageIndicator.IN_DESC )
        for comments in photo.iter('comments'):
            for c in comments:
                self.imglut.add_to_indicator( imgind, 'W', \
                                              CP6Data.textwrapper( c ), \
                                              ImageIndicator.IN_COMMENT )
        for tags in photo.iter('tags'):
            for t in tags:
                self.imglut.add_to_indicator( imgind, 'W', \
                                              CP6Data.textwrapper( t ), \
                                              ImageIndicator.IN_TAG )

        return imgind

    def write_image_indicator_table( self, data_split, fn ):
        with open( fn, 'w' ) as f:
            for mir_id in sorted( data_split.ids ):
                imgind = self.image_indicators[ mir_id ]
                group_str = ','.join(map(str,imgind.group_list.keys())) if (len(imgind.group_list)) else 'none'
                word_str = ','.join(map(str,imgind.word_list.keys())) if (len(imgind.word_list)) else 'none'
                f.write( '%d %s %s\n' % ( mir_id, group_str, word_str ))

    def get_image_edges( self, data_split ):
        #
        # An edge has two sources: McAuley's edge table, which contains
        # the contact info, and our shared_{group,word}_id_vectors.
        #

        edges = list()
        sorted_ids = sorted( data_split.ids )
        (n_possible_edges, n_found_edges) = (0,0)
        (n_mcauley_missed_user_flag, n_empty_group_word) = (0,0)
        for a_index in range( 0, len(sorted_ids) ):
            if a_index % 100 == 0:
                sys.stderr.write('Info: Edge %d of %d: %d found, %d possible\n' % \
                                 (a_index, len(sorted_ids), n_found_edges, n_possible_edges))
            a = sorted_ids[ a_index ]
            a_flickr_id = int(self.xmldata.mir_nodes[a].get('id'))
            for b_index in range(a_index+1, len(sorted_ids)):
                b = sorted_ids[ b_index ]
                b_flickr_id = int(self.xmldata.mir_nodes[b].get('id'))
                n_possible_edges += 1

                if a_flickr_id < b_flickr_id:
                    key = '%d:%d' % (a_flickr_id, b_flickr_id)
                else:
                    key = '%d:%d' % (b_flickr_id, a_flickr_id)
                in_mcauley = (key in self.mcauley_edge_features.edgemap)
                mcauley_flags_nonzero = False
                if in_mcauley:
                    e = self.mcauley_edge_features.edgemap[ key ]
                    (loc_flag, user_flag, friend_flag) = \
                      (e.location_flag, e.user_flag, e.friend_flag)
                    mcauley_flags_nonzero = (loc_flag != '0') or (user_flag != '0') or (friend_flag != '0')
                else:
                    (loc_flag, user_flag, friend_flag) = ('.','.','.')

                group_id_vector = \
                  CP6ImageEdge.get_shared_group_id_vector( self.image_indicators[ a ], \
                                                           self.image_indicators[ b ] )
                word_id_vector = \
                  CP6ImageEdge.get_shared_word_id_vector( self.image_indicators[ a ], \
                                                          self.image_indicators[ b ] )
                edge_is_present = mcauley_flags_nonzero or len(group_id_vector) or len(word_id_vector)

                if edge_is_present:
                    if mcauley_flags_nonzero:
                        # trust, but verify
                        xml_user_flag = \
                          self.xmldata.mir_nodes[ a ].find('owner').get('nsid') == \
                          self.xmldata.mir_nodes[ b ].find('owner').get('nsid')
                        user_flag_bool = (user_flag != '0')
                        if xml_user_flag != user_flag_bool:
                            if (not user_flag_bool) and xml_user_flag:
                                n_mcauley_missed_user_flag += 1
                            else:
                                sys.stderr.write('WARN: %d / %d user flag mismatch: mcauley %s, xml %s; going with xml\n' % (a_flickr_id, b_flickr_id, user_flag, xml_user_flag))
                            user_flag = xml_user_flag

                    n_found_edges += 1
                    if (len(group_id_vector)==0) and (len(word_id_vector)==0):
                        n_empty_group_word += 1
                    edges.append( CP6ImageEdge.from_data( \
                                                self.image_indicators[ a ], \
                                                self.image_indicators[ b ], \
                                                group_id_vector, \
                                                word_id_vector, \
                                                user_flag, \
                                                loc_flag, \
                                                friend_flag ))

        sys.stderr.write('Info: Found %d of %d possible edges\n' % (n_found_edges, n_possible_edges))
        sys.stderr.write('Info: Found %d missed McAuley user flags; %d edges with no words or groups\n' % (n_mcauley_missed_user_flag, n_empty_group_word))
        return edges

    def write_global_tables( self ):
        self.label_table.write_to_file( self.paths.label_table_path )
        self.imglut.write_to_file( self.paths.image_indicator_lut_path )

    def write_phase_table( self, phase_key ):
        s = self.splits[ phase_key ]
        t = self.paths.phase_tables[ phase_key ]
        img_table = self.image_table_from_split( s )
        img_table.write_to_file( t.image_table )
        self.write_image_indicator_table( s, t.image_indicator_table )
        CP6ImageEdge.write_edge_table( t.image_edge_table, self.get_image_edges( s ))

if __name__ == '__main__':
    p = Paths()
    d = CP6Data( p )
    d.set_splits()

    d.write_debug_label_count_csv( 'labelcount.csv' )
    d.write_global_tables()

    d.write_phase_table( 'r1train' )
    # d.write_phase_table( 'r1test' )
    # d.write_phase_table( 'r2train' )
    # d.write_phase_table( 'r2test' )
