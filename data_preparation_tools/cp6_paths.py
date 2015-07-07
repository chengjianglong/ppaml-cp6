##
## simple class holding all the paths we expect to use
##

class CP6PhaseTable:
    def __init__( self, prefix, tag ):
        self.image_table = '%s/cp6_image_table_%s.txt' % (prefix, tag )
        self.image_indicator_table = '%s/cp6_image_indicator_table_%s.txt' % (prefix, tag )
        self.image_edge_table = '%s/cp6_image_edge_table_%s.txt' % (prefix, tag )

class CP6Paths:

    def __init__( self ):
        prefix = '/Users/collinsr/work/ppaml/2015-06-cp6-prep'

        # directory of the original 25k MIRFLICKR exif files
        self.exif_dir = prefix+'/src_data/exif'

        # path to the "augmented" photosMIR.xml file
        self.xml_path = prefix+'/step01/augmented.xml'

        # path to the stopwords list
        self.stopwords_path = prefix+'/src_data/stopwords.txt'

        # path to McAuley's node-level training data
        self.node_features_path = prefix+'/src_data/nodeFeaturesMIR.txt'

        # path to McAuley's edge feature data
        self.edge_features_path = prefix+'/src_data/trainingEdgeFeaturesMIR.txt'

        output_prefix = '/Users/collinsr/work/ppaml/2015-06-cp6-prep/ppaml-tables'

        # path to the label table
        self.label_table_path = output_prefix+'/cp6_label_table.txt'

        # the image indicator lookup table
        self.image_indicator_lut_path = output_prefix+"/cp6_image_indicator_lookup_table.txt"

        self.phase_tables = dict()
        self.phase_tables['r1train'] = CP6PhaseTable( output_prefix, 'round_1_train' )
        self.phase_tables['r1test'] = CP6PhaseTable( output_prefix, 'round_1_test' )
        self.phase_tables['r2train'] = CP6PhaseTable( output_prefix, 'round_2_train' )
        self.phase_tables['r2test'] = CP6PhaseTable( output_prefix, 'round_2_test' )
