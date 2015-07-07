import sys

from cp6_paths import CP6Paths
from cp6_xml import CP6XML
from cp6_exifdata import CP6EXIFData
from cp6_split import CP6Split
from cp6_util import CP6Util
from cp6_image_indicator_lookup import CP6ImageIndicatorLookupTable, CP6ImageIndicator
from cp6_mcauley_edge_features import CP6McAuleyEdgeFeatures
from cp6_image_edge import CP6ImageEdge

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
            e = CP6EXIFData.from_file( exif_path )
            self.exifdata[ mir_id ] = e
            if e.valid:
                c_valid += 1
            else:
                c_invalid += 1

            labelset |= self.get_mirlabel_set( mir_id )

        self.labels = sorted( labelset )
        sys.stderr.write( 'Info: found %d valid, %d invalid EXIF files (sum: %d)\n' % \
                          (c_valid, c_invalid, c_valid+c_invalid))
        sys.stderr.write( 'Info: found %d labels\n' % len(self.labels))

        self.imglut = CP6ImageIndicatorLookupTable( self.paths.node_features_path, \
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
          CP6Split.get_splits( self )

    def get_mirlabel_set( self, id ):
        s = set()
        for n_labels in self.xmldata.mir_nodes[ id ].iter( 'labels' ):
            for label in n_labels:
                if label.get( 'source' ) == 'MIR':
                    s.add( label.text )
        return s

    def write_label_table( self ):
        with open( self.paths.label_table_path, 'w' ) as f:
            for index in range( 0, len(self.labels)):
                f.write( '%d %s\n' % ( index, CP6Util.qstr( self.labels[index] )))

        sys.stderr.write( 'Info: wrote %d labels to %s\n' % \
                          (len(self.labels), self.paths.label_table_path ))

    def get_label_vector_str( self, data_split, id ):
        s = ''
        if data_split.mode == CP6Split.TEST:
            for i in range( 0, len(self.labels)):
                if (self.labels[i] == 'structures') and (data_split.round == 1):
                    s += '-1,'
                else:
                    s += '-2,'
        else:
            my_labels = self.get_mirlabel_set( id )
            for i in range(0, len(self.labels)):
                if (self.labels[i] == 'structures') and (data_split.round == 1):
                    s += '-1,'
                else:
                    if self.labels[i] in my_labels:
                        s += '1,'
                    else:
                        s += '0,'
        return s.rstrip(',')


    def write_image_table( self, data_split, fn ):
        with open( fn, 'w' ) as f:
            for mir_id in sorted( data_split.ids ):
                photo = self.xmldata.mir_nodes[ mir_id ]
                exif = self.exifdata[ mir_id ]

                f.write( '%d ' % mir_id ) # 0
                f.write( '%d ' % int(photo.get('id'))) # 1
                f.write( '%s ' % CP6Util.qstr( photo.find('owner').get('nsid'))) # 2
                f.write( '%s ' % CP6Util.qstr( photo.find('title').text )) # 3
                f.write( '%s ' % CP6Util.qstr( photo.find('description').text )) # 4

                if (exif.valid):  # 5 6 7
                    f.write( '%s %s %s ' % (exif.exif_date, exif.exif_time, exif.exif_flash ))
                else:
                    f.write( 'none none U ')

                locality = photo.find('locality')
                if locality: # 8
                    f.write( '%s ' % CP6Util.qstr( locality.text ))
                else:
                    f.write( 'none ' )

                f.write( '%s\n' % self.get_label_vector_str( data_split, mir_id ))  #9

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
                self.imglut.add_to_indicator( imgind, 'G', g.get('id'), CP6ImageIndicator.IN_NONE )

        self.imglut.add_to_indicator( imgind, 'W', \
                                      CP6Data.textwrapper( photo.find('title')), \
                                      CP6ImageIndicator.IN_TITLE )
        self.imglut.add_to_indicator( imgind, 'W', \
                                      CP6Data.textwrapper( photo.find('description')), \
                                      CP6ImageIndicator.IN_DESC )
        for comments in photo.iter('comments'):
            for c in comments:
                self.imglut.add_to_indicator( imgind, 'W', \
                                              CP6Data.textwrapper( c ), \
                                              CP6ImageIndicator.IN_COMMENT )
        for tags in photo.iter('tags'):
            for t in tags:
                self.imglut.add_to_indicator( imgind, 'W', \
                                              CP6Data.textwrapper( t ), \
                                              CP6ImageIndicator.IN_TAG )

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
        self.write_label_table()
        self.imglut.write_image_indicator_lookup_table( self.paths.image_indicator_lut_path )

    def write_phase_table( self, phase_key ):
        s = self.splits[ phase_key ]
        t = self.p.phase_tables[ phase_key ]
        self.write_image_table( s, t.image_table )
        self.write_image_indicator_table( s, t.image_indicator_table )
        CP6ImageEdge.write_edge_table( t.image_edge_table, self.get_image_edges( s ))

if __name__ == '__main__':
    p = CP6Paths()
    d = CP6Data( p )
    d.set_splits()

    # d.write_global_tables()

    # d.write_phase_table( 'r1train' )
    # d.write_phase_table( 'r1test' )
    # d.write_phase_table( 'r2train' )
    # d.write_phase_table( 'r2test' )
