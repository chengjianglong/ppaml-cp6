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
