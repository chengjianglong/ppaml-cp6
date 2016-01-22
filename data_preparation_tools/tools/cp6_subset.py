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

#
# Take a list of image IDs, copy to sandbox directory
#

import sys
import os
import glob
import re
import shutil
import argparse
import random

from cp6.tables.edge_table import EdgeTable
from cp6.tables.image_table import ImageTable
from cp6.tables.image_indicator_table import ImageIndicatorTable

#
# src is a fully populated sandbox. given a set of image IDs (aka nodes)
# copy those nodes and edges over to a new sandbox.
#
# Sandbox structure is:
#
# .
# +-- eval_in
# |   +-- etc
# |   |   +-- caffe_dictionary.txt
# |   |   +-- image_indicator_lookup_table.txt
# |   |   +-- label_table.txt
# |   +-- testing
# |       +-- image_table.txt
# +-- eval_out
# +-- run_in
# |   +-- testing
# |   |   +-- caffe_histograms.txt
# |   |   +-- image_edge_table.txt
# |   |   +-- image_indicator_table.txt
# |   |   +-- image_table.txt
# |   |   +-- image_feature_group
# |   +-- training
# |       +-- caffe_histograms.txt
# |       +-- image_edge_table.txt
# |       +-- image_indicator_table.txt
# |       +-- image_table.txt
# |       +-- image_feature_group
# +-- run_out
#
# ... where "image_feature_group" are all the structurally identical
# various image-level feature tables.
#

class SandboxPaths:
    def __init__( self, src_dir ):
        self.dirs = dict()
        self.dirs[ 'root' ] = src_dir

        self.dirs[ 'eval_in' ] = os.path.join( src_dir, 'eval_in' )
        self.dirs[ 'etc' ] = os.path.join( self.dirs['eval_in'], 'etc' )
        self.dirs[ 'eval_testing' ] = os.path.join( self.dirs['eval_in'], 'testing' )

        self.dirs[ 'eval_out' ] = os.path.join( src_dir, 'eval_out' )

        self.dirs[ 'run_in' ] = os.path.join( src_dir, 'run_in' )
        self.dirs[ 'run_testing' ] = os.path.join( self.dirs['run_in'], 'testing' )
        self.dirs[ 'run_training' ] = os.path.join( self.dirs['run_in'], 'training' )

        self.dirs[ 'run_out' ] = os.path.join( src_dir, 'run_out' )

    def mkdirs( self ):
        if os.path.isdir( self.dirs['root']):
            sys.stderr.write('Info: removing existing sandbox root %s...\n' % self.dirs['root'] )
            shutil.rmtree( self.dirs['root'])

        # order matters
        for d in ['root', 'eval_in', 'etc', 'eval_testing', 'eval_out', 'run_in', 'run_testing', 'run_training', 'run_out'  ]:
            os.mkdir( self.dirs[d] )

class SandboxSubsetWorker:
    def __init__( self, s, d ):
        self.src = s
        self.dst = d
        self.image_table_train = None
        self.image_table_test = None
        self.edge_table = None

    def populate_etc( self ):
        # copy over the files which don't change
        for i in ['caffe_dictionary.txt', 'image_indicator_lookup_table.txt', 'label_table.txt' ]:
            src_fn = os.path.join( self.src.dirs['etc'], i )
            if not os.path.isfile( src_fn ):
                raise AssertionError( 'No file %s' % src_fn )
            shutil.copy( src_fn, os.path.join( self.dst.dirs['etc'], i ))
            sys.stderr.write('Info: copied %s\n' % i)

    def downsample_edge_file( self, table, dst_dir_tag, ids ):
        # dst_dir_tag is either run_training or run_testing. ids is
        # the list of image IDs to write.
        fn = os.path.join( self.dst.dirs[ dst_dir_tag ], 'image_edge_table.txt' )
        sys.stderr.write( 'Info: writing %s\n' % fn )
        (c_total, c_written) = table.write_to_file( fn, ids )
        sys.stderr.write( 'Info: wrote %d of %d edges to %s\n' % (c_written, c_total, fn ))

    def downsample_image_file( self, table, dst_dir_tag, ids, testing_mode_flag ):
        # dst_dir_tag is one of run_training, run_testing, or eval_testing; ids is the
        # list of image IDs to write; testing_mode_flag is true if the
        # output image table is 'testing' (contains true image labels)
        # or 'training' (true image labels are masked.)
        filter_package = (ids, testing_mode_flag )
        fn = os.path.join( self.dst.dirs[ dst_dir_tag ], 'image_table.txt' )
        sys.stderr.write( 'Info: writing %s\n' % fn )
        (c_total, c_written) = table.write_to_file( fn, filter_package )
        sys.stderr.write( 'Info: wrote %d of %d images to %s\n' % (c_written, c_total, fn ))

    def downsample_feature_files( self, dst_dir_tag, ids ):
        # These files can be subsampled without loading them into memory. dst_dir_tag is
        # either run_training or run_testing, ids is the list of image IDs to write.
        files = [ 'AutoColorCorrelogram.txt', 'CEDD.txt', 'ColorLayout.txt', 'EdgeHistogram.txt', 'FCTH.txt',\
                  'Gabor.txt', 'JCD.txt', 'JointHistogram.txt', 'JpegCoefficientHistogram.txt', 'LuminanceLayout.txt',\
                  'OpponentHistogram.txt', 'PHOG.txt', 'ScalableColor.txt', 'SimpleColorHistogram.txt', 'Tamura.txt',\
                  'caffe_histograms.txt' ]

        for fn in files:
            src = os.path.join( self.src.dirs[ dst_dir_tag ], fn )
            dst = os.path.join( self.dst.dirs[ dst_dir_tag ], fn )
            c = 0
            with open( src ) as f_in:
                with open (dst, 'w') as f_out:
                    while 1:
                        raw_line = f_in.readline()
                        if not raw_line:
                            break
                        d = raw_line.split()
                        id = int(d[0])
                        if id in ids:
                            f_out.write( raw_line )
                            c += 1
            sys.stderr.write('Info: wrote %d lines to %s\n' % (c, dst ))


    def cache_edge_tables( self, train_ids, test_ids ):
        # The edge tables can take a while to load.
        sys.stderr.write( 'Info: loading training edge table filtered to %d nodes...\n' % len(train_ids ))
        self.edge_table_train = EdgeTable.read_from_file( os.path.join( self.src.dirs['run_training'], 'image_edge_table.txt'), train_ids )
        sys.stderr.write( 'Info: loaded %d training edges\n' % len(self.edge_table_train.edges))

        sys.stderr.write( 'Info: loading testing edge table filtered to %d nodes...\n' % len(test_ids ))
        self.edge_table_test = EdgeTable.read_from_file( os.path.join( self.src.dirs['run_testing'], 'image_edge_table.txt'), test_ids )
        sys.stderr.write( 'Info: loaded %d testing edges\n' % len(self.edge_table_test.edges))


    def cache_image_tables( self ):
        sys.stderr.write( 'Info: loading source training image table...\n' )
        self.image_table_train = ImageTable.read_from_file( os.path.join( self.src.dirs['run_training'], 'image_table.txt' ))
        sys.stderr.write( 'Info: loading source testing image table...\n' )
        self.image_table_test = ImageTable.read_from_file( os.path.join( self.src.dirs['run_testing'], 'image_table.txt' ))
        sys.stderr.write( 'Info: loading source eval image table...\n' )
        self.image_table_eval = ImageTable.read_from_file( os.path.join( self.src.dirs['eval_testing'], 'image_table.txt' ))

#
#
#

class IDSelectorSource:
    (T_RAND, T_PCENT, T_FILE) = (0,1,2)
    def __init__( self, s, w ):
        self.flavor = None
        self.n = None
        self.ids = None
        self.which = w  # 'test' or 'train'
        m = re.search( '^([0-9]+)$', s )
        if m:
            self.flavor = IDSelectorSource.T_RAND;
            self.n = int( m.group(1) )
            return
        m = re.search( '^([0-9\.]+)p$', s )
        if m:
            self.flavor = IDSelectorSource.T_PCENT
            self.n = float( m.group(1) ) / 100.0
            return
        m = re.search( '^\@(.*)$', s )
        if m:
            self.flavor = IDSelectorSource.T_FILE
            self.ids = list()
            with open( m.group(1) ) as f:
                while 1:
                    raw_line = f.readline()
                    if not raw_line:
                        break
                    self.ids.append( int( raw_line.strip() ))
            sys.stderr.write('Info: read %d IDs from %s\n' % (len(self.ids), m.group(1)))
            return
        # else, unrecognized form
        sys.stderr.write('ERROR: Failed to parse ID selector "%s"; run with --ids help for more info\n' % s )
        sys.exit(1)

    def set_list_from_image_table( self, image_table ):
        if self.flavor == IDSelectorSource.T_FILE:
            found_ids = list()
            for id in self.ids:
                if id in image_table.entries:
                    found_ids.append( id )
            if len(found_ids) != len(self.ids):
                sys.stderr.write('Warn: %s id source only found %d of %d listed ids\n' % (self.which, len(found_ids), len(self.ids)))
            else:
                sys.stderr.write('Info: %s id source found %d of %d listed ids\n' % (self.which, len(found_ids), len(self.ids)))
            self.ids = found_ids
        else:
            if self.flavor == IDSelectorSource.T_PCENT:
                new_n = int( self.n * len(image_table.entries))
                self.n = new_n
            sys.stderr.write('Info: %s id source sampling %d from %d entries\n' % (self.which, self.n, len(image_table.entries)))
            if self.n > len(image_table.entries):
                sys.stderr.write('ERROR: %s id source requested more samples than available; exiting\n' % self.which)
                sys.exit(1)
            self.ids = random.sample( image_table.entries.keys(), self.n )

class IDSelector:
    def __init__( self, s ):
        m = re.search( '^(.*),(.*)$', s )
        if not m:
            sys.stderr.write( 'Error: ID selector "%s" is not of form tag1,tag2; run with "help" for more info\n' % s)
            sys.exit(1)
        self.ids_train = IDSelectorSource( m.group(1), 'train' )
        self.ids_test = IDSelectorSource( m.group(2), 'test' )

    @staticmethod
    def show_id_help():
        sys.stderr.write('''
The '--ids' option controls how the image IDs in the destination sandbox are chosen.
The format is two tags separated by a comma, e.g. '40,100', '30p,20p'.  The first
tag applies to the training data, the second tag applies to the test data.

Options for tags are:

- An integer, e.g. '200' : this number of images will be randomly chosen.
Use the --seed option for reproducibility. It is an error if this is more than
the number of images available.

- A float followed by 'p': this percentage of the available images will be randomly
chosen, e.g. '0.01p' randomly chooses 0.01% of the availble images.

- A string of the form '@filename': this opens filename and reads a list of image
IDs. If an ID is named in the filename but does not exist in the data a warning
is issued.

Examples:

    --ids @training.txt,5p : use the IDs in training.txt for training, randomly
    pick 5% of the available test data for testing.

    --ids 20,20 : select 20 random images from each of training and testing

Note that in no case is any attempt made to ensure that the label distribution in
the output sandbox resembles that of the input sandbox.
''')


if __name__ == '__main__':
    parser = argparse.ArgumentParser( description='PPAML CP6 sandbox subset tool' )
    parser.add_argument( '--src', required=True, help='source sandbox' )
    parser.add_argument( '--dst', required=True, help='destination sandbox (will be wiped and recreated each time)' )
    parser.add_argument( '--ids', required=True, help='ID selection policy; set to "help" for more details' )
    parser.add_argument( '--seed', help='Random number seed, for reproducibility' )
    args = parser.parse_args()
    if (args.ids == 'help'):
        IDSelector.show_id_help()
        sys.exit(0)

    ids = IDSelector( args.ids )

    if args.seed is not None:
        sys.stderr.write('Info: seeding random number generator with %d\n' % args.seed)
        random.seed( args.seed )

    src_sandbox = SandboxPaths( args.src )
    dst_sandbox = SandboxPaths( args.dst )
    dst_sandbox.mkdirs()

    w = SandboxSubsetWorker( src_sandbox, dst_sandbox )

    # first, load the source image tables so we can populate any pending ID lists
    w.cache_image_tables()
    ids.ids_train.set_list_from_image_table( w.image_table_train )
    ids.ids_test.set_list_from_image_table( w.image_table_test )

    # load only those edges we care about
    w.cache_edge_tables( ids.ids_train.ids, ids.ids_test.ids )

    # start writing!

    # copy files that don't change
    w.populate_etc()

    # image tables:
    # ...answer key
    w.downsample_image_file( w.image_table_eval, 'eval_testing', ids.ids_test.ids , False )
    # ...testing table
    w.downsample_image_file( w.image_table_test, 'run_testing', ids.ids_test.ids , True )
    # ....training
    w.downsample_image_file( w.image_table_train, 'run_training', ids.ids_train.ids , True )

    # edge tables:
    # ...testing
    w.downsample_edge_file( w.edge_table_test, 'run_testing', ids.ids_test.ids )
    # ...training
    w.downsample_edge_file( w.edge_table_train, 'run_training', ids.ids_train.ids )

    # image feature files
    # ...testing
    w.downsample_feature_files( 'run_testing', ids.ids_test.ids )
    # ...training
    w.downsample_feature_files( 'run_training', ids.ids_train.ids )

    # image indicator tables:
    # ...testing
    iit_train = ImageIndicatorTable.read_from_file( os.path.join( w.src.dirs['run_training'], 'image_indicator_table.txt' ))
    iit_train.write_to_file( os.path.join( w.dst.dirs['run_training'], 'image_indicator_table.txt' ), ids.ids_train.ids )
    sys.stderr.write( 'Downsampled training image_indicator_table\n' )
    iit_test = ImageIndicatorTable.read_from_file( os.path.join( w.src.dirs['run_testing'], 'image_indicator_table.txt' ))
    iit_test.write_to_file( os.path.join( w.dst.dirs['run_testing'], 'image_indicator_table.txt' ), ids.ids_test.ids )
    sys.stderr.write( 'Downsampled testing image_indicator_table\n' )

    ## all done!

