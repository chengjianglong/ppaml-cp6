##
## simple class holding all the paths we expect to use
##

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

        # the image tables
        self.p1train_table_path = output_prefix+'/cp6_image_table_round_1_train.txt'
        self.p1test_table_path = output_prefix+'/cp6_image_table_round_1_test.txt'
        self.p2train_table_path = output_prefix+'/cp6_image_table_round_2_train.txt'
        self.p2test_table_path = output_prefix+'/cp6_image_table_round_2_test.txt'

        # the image indicator lookup table
        self.image_indicator_lut_path = output_prefix+"/cp6_image_indicator_lookup_table.txt"

        # the image indicator tables
        self.p1train_imgind_table_path = output_prefix+'/cp6_image_indicator_table_round_1_train.txt'
        self.p1test_imgind_table_path = output_prefix+'/cp6_image_indicator_table_round_1_test.txt'
        self.p2train_imgind_table_path = output_prefix+'/cp6_image_indicator_table_round_2_train.txt'
        self.p2test_imgind_table_path = output_prefix+'/cp6_image_indicator_table_round_2_test.txt'

        # the image edge tables
        self.p1train_img_edge_table_path = output_prefix+'/cp6_image_edge_table_round_1_train.txt'
        self.p1test_img_edge_table_path = output_prefix+'/cp6_image_edge_table_round_1_test.txt'
        self.p2train_img_edge_table_path = output_prefix+'/cp6_image_edge_table_round_2_train.txt'
        self.p2test_img_edge_table_path = output_prefix+'/cp6_image_edge_table_round_2_test.txt'
